import argparse
import importlib
import socket
import struct


def load_framer(name: str):
    return importlib.import_module(f"framings.{name}")


def hex_dump(b: bytes):
    return " ".join(f"{x:02x}" for x in b)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=3000)
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--mode", default="char_count")
    args = p.parse_args()

    fr = load_framer(args.mode)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((args.host, args.port))
        srv.listen(5)

        print(f"Listening on {args.host}:{args.port}")

        while True:
            conn, addr = srv.accept()
            with conn:
                print("\nConnection from", addr)
                buffer = b""

                while True:
                    data = conn.recv(4096)
                    if not data:
                        print("Connection closed")
                        break

                    print("\n[RAW RECEIVED DATA]")
                    print("HEX:", hex_dump(data))
                    print("RAW:", data)

                    buffer += data
                    msgs, buffer = fr.decode(buffer)

                    for m in msgs:
                        msg_type = m[0]
                        body = m[1:]

                        if msg_type == 1:
                            print("<STRING>", body.decode())

                        elif msg_type == 2:
                            value = struct.unpack("!I", body)[0]
                            print("<INT>", value)

                        elif msg_type == 3:
                            value = struct.unpack("!f", body)[0]
                            print("<FLOAT>", value)

                        elif msg_type == 4:
                            print("<BINARY>", body)

                        else:
                            print("<UNKNOWN>", m)


if __name__ == "__main__":
    main()