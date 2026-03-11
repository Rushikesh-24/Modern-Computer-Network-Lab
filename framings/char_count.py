# framings/char_count.py

from typing import List, Tuple


def _hex(b: bytes) -> str:
    return " ".join(f"{x:02x}" for x in b)


def _bin(b: bytes) -> str:
    return " ".join(f"{x:08b}" for x in b)


def encode(payload: bytes) -> bytes:
    n = len(payload)
    if n >= 65536:
        raise ValueError("payload too large for 2-byte length")

    length_bytes = n.to_bytes(2, "big")
    framed = length_bytes + payload

    print("\n[ENCODE]")
    print("Length (n):", n)
    print("Length prefix HEX:", _hex(length_bytes))
    print("Length prefix BIN:", _bin(length_bytes))
    print("Payload HEX:", _hex(payload))
    print("Full Frame HEX:")
    print(f"[{_hex(length_bytes)}] {_hex(payload)}")
    print("Full Frame BIN:")
    print(f"[{_bin(length_bytes)}] {_bin(payload)}")

    return framed


def decode(stream: bytes) -> Tuple[List[bytes], bytes]:
    msgs = []
    i = 0
    L = len(stream)

    print("\n[DECODE STREAM]")
    print("Raw Stream HEX:", _hex(stream))
    print("Raw Stream BIN:", _bin(stream))

    while i + 2 <= L:
        length_bytes = stream[i : i + 2]
        length = int.from_bytes(length_bytes, "big")

        print("\nReading Length Prefix:")
        print("HEX:", _hex(length_bytes))
        print("BIN:", _bin(length_bytes))
        print("Decoded Length:", length)

        if i + 2 + length <= L:
            payload = stream[i + 2 : i + 2 + length]
            print("Extracted Payload HEX:", _hex(payload))
            print("Extracted Payload BIN:", _bin(payload))
            msgs.append(payload)
            i += 2 + length
        else:
            print("Incomplete frame, waiting...")
            break

    return msgs, stream[i:]