import argparse
import importlib
import socket
import struct
import sys


def load_framer(name: str):
    return importlib.import_module(f"framings.{name}")


def hex_dump(b: bytes):
    return " ".join(f"{x:02x}" for x in b)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", type=int, default=3000)
    p.add_argument("--mode", default="char_count")

    p.add_argument("--string")
    p.add_argument("--int", type=int)
    p.add_argument("--float", type=float)
    p.add_argument("--file")

    args = p.parse_args()
    fr = load_framer(args.mode)

    if args.string is not None:
        payload = b"\x01" + args.string.encode()

    elif args.int is not None:
        payload = b"\x02" + struct.pack("!I", args.int)

    elif args.float is not None:
        payload = b"\x03" + struct.pack("!f", args.float)

    elif args.file:
        with open(args.file, "rb") as fh:
            payload = b"\x04" + fh.read()

    else:
        print("Provide one of --string, --int, --float, --file")
        sys.exit(2)

    framed = fr.encode(payload)

    print("\n[SENDER RAW OUTPUT]")
    print("Final bytes sent HEX:", hex_dump(framed))
    print("Final bytes sent RAW:", framed)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.host, args.port))
        s.sendall(framed)


if __name__ == "__main__":
    main()