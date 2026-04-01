import ipaddress
import math


def read_positive_int(prompt: str) -> int:
	while True:
		raw = input(prompt).strip()
		try:
			value = int(raw)
			if value <= 0:
				raise ValueError
			return value
		except ValueError:
			print("Please enter a positive integer.")


def parse_network() -> ipaddress.IPv4Network:
	while True:
		raw = input("Enter base network in CIDR form (example: 121.37.10.64/26): ").strip()
		try:
			network = ipaddress.ip_network(raw, strict=False)
			if not isinstance(network, ipaddress.IPv4Network):
				print("Only IPv4 addresses are supported.")
				continue
			return network
		except ValueError:
			print("Invalid CIDR input. Try again.")


def first_last_usable(network: ipaddress.IPv4Network):
	if network.num_addresses <= 2:
		return "N/A", "N/A"
	first = network.network_address + 1
	last = network.broadcast_address - 1
	return str(first), str(last)


def print_range(label: str, network: ipaddress.IPv4Network):
	first, last = first_last_usable(network)
	usable_hosts = max(network.num_addresses - 2, 0)
	print(f"{label}")
	print(f"  Network IP      : {network.network_address}")
	print(f"  Prefix/Mask     : /{network.prefixlen} ({network.netmask})")
	print(f"  Broadcast IP    : {network.broadcast_address}")
	print(f"  First Host IP   : {first}")
	print(f"  Last Host IP    : {last}")
	print(f"  Total Addresses : {network.num_addresses}")
	print(f"  Usable Hosts    : {usable_hosts}")


def run_flsm(base_network: ipaddress.IPv4Network):
	print("\n=== Fixed Length Subnet Masking (FLSM) ===")
	requested_subnets = read_positive_int("How many fixed-length subnets are required? ")

	borrowed_bits = math.ceil(math.log2(requested_subnets)) if requested_subnets > 1 else 0
	new_prefix = base_network.prefixlen + borrowed_bits

	if new_prefix > 30:
		print("Cannot create that many FLSM subnets from the given base network.")
		return

	possible_subnets = 2 ** borrowed_bits
	subnet_list = list(base_network.subnets(new_prefix=new_prefix))

	print("\nFLSM Summary")
	print(f"  Base Network               : {base_network}")
	print(f"  Requested Subnets          : {requested_subnets}")
	print(f"  Borrowed Host Bits         : {borrowed_bits}")
	print(f"  New Prefix                 : /{new_prefix}")
	print(f"  Subnets Formed             : {possible_subnets}")
	print(f"  Addresses per Subnet       : {subnet_list[0].num_addresses}")
	print(f"  Usable Hosts per Subnet    : {max(subnet_list[0].num_addresses - 2, 0)}")

	print("\nSubnet Details")
	for idx, subnet in enumerate(subnet_list, start=1):
		print_range(f"Subnet {idx}: {subnet}", subnet)

	if possible_subnets > requested_subnets:
		print(
			f"\nNote: {possible_subnets - requested_subnets} subnet(s) are extra because "
			"subnet count must be a power of 2 in FLSM."
		)


def smallest_block_prefix(required_hosts: int) -> int:
	total_needed = required_hosts + 2
	block_size = 1
	while block_size < total_needed:
		block_size <<= 1
	return 32 - int(math.log2(block_size))


def summarize_free_ranges(base_network: ipaddress.IPv4Network, used_networks):
	if not used_networks:
		return [base_network]

	free_ranges = []
	cursor = int(base_network.network_address)
	end = int(base_network.broadcast_address)

	for net in sorted(used_networks, key=lambda n: int(n.network_address)):
		start_used = int(net.network_address)
		end_used = int(net.broadcast_address)

		if cursor < start_used:
			free_ranges.extend(
				ipaddress.summarize_address_range(
					ipaddress.IPv4Address(cursor),
					ipaddress.IPv4Address(start_used - 1),
				)
			)
		cursor = end_used + 1

	if cursor <= end:
		free_ranges.extend(
			ipaddress.summarize_address_range(
				ipaddress.IPv4Address(cursor),
				ipaddress.IPv4Address(end),
			)
		)

	return free_ranges


def run_vlsm(base_network: ipaddress.IPv4Network):
	print("\n=== Variable Length Subnet Masking (VLSM) ===")
	network_count = read_positive_int("How many variable-length subnets are required? ")

	requests = []
	for i in range(1, network_count + 1):
		hosts = read_positive_int(f"Enter required host count for network {i}: ")
		requests.append({"name": f"Net-{i}", "hosts": hosts})

	requests.sort(key=lambda item: item["hosts"], reverse=True)

	allocations = []
	used_addresses = 0
	cursor = int(base_network.network_address)
	base_end = int(base_network.broadcast_address)

	for req in requests:
		prefix = smallest_block_prefix(req["hosts"])
		block_size = 2 ** (32 - prefix)
		needed = req["hosts"] + 2

		if cursor + block_size - 1 > base_end:
			print("\nVLSM Allocation Failed")
			print(
				f"  Not enough space for {req['name']} (hosts requested: {req['hosts']}, "
				f"minimum addresses needed with +2 overhead: {needed})."
			)
			print(f"  Remaining addresses in base network: {max(base_end - cursor + 1, 0)}")
			return

		subnet = ipaddress.ip_network((cursor, prefix))
		allocations.append(
			{
				"name": req["name"],
				"required_hosts": req["hosts"],
				"reserved_hosts": needed,
				"subnet": subnet,
				"block_size": block_size,
				"usable_hosts": max(block_size - 2, 0),
				"wastage": max(block_size - needed, 0),
			}
		)

		used_addresses += block_size
		cursor += block_size

	print("\nVLSM Summary")
	print(f"  Base Network                 : {base_network}")
	print(f"  Requested Subnets            : {network_count}")
	print(f"  Total Addresses Available    : {base_network.num_addresses}")
	print(f"  Total Addresses Allocated    : {used_addresses}")
	print(f"  Total Addresses Leftover     : {base_network.num_addresses - used_addresses}")

	print("\nAllocation Details (sorted by host requirement, descending)")
	for idx, item in enumerate(allocations, start=1):
		subnet = item["subnet"]
		first, last = first_last_usable(subnet)
		print(f"{idx}. {item['name']} -> {subnet}")
		print(f"   Required Hosts              : {item['required_hosts']}")
		print(f"   Reserved (+2 N/B)           : {item['reserved_hosts']}")
		print(f"   Block Size                  : {item['block_size']}")
		print(f"   Usable Hosts in Block       : {item['usable_hosts']}")
		print(f"   Wasted Addresses            : {item['wastage']}")
		print(f"   Network IP                  : {subnet.network_address}")
		print(f"   Broadcast IP                : {subnet.broadcast_address}")
		print(f"   First Host                  : {first}")
		print(f"   Last Host                   : {last}")

	free_ranges = summarize_free_ranges(base_network, [a["subnet"] for a in allocations])
	print("\nLeftover Ranges")
	if free_ranges:
		for i, rng in enumerate(free_ranges, start=1):
			print_range(f"Free Range {i}: {rng}", rng)
	else:
		print("  No leftover ranges. Entire base network is allocated.")


def main():
	print("Subnetting Tool: FLSM + VLSM")
	base_network = parse_network()

	print("\nBase Network Details")
	print_range(f"Base: {base_network}", base_network)

	run_flsm(base_network)
	run_vlsm(base_network)


if __name__ == "__main__":
	main()
