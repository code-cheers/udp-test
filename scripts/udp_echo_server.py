#!/usr/bin/env python3
import argparse
import socket


def parse_args():
    parser = argparse.ArgumentParser(description="UDP echo server")
    parser.add_argument("--host", default="0.0.0.0", help="bind host")
    parser.add_argument("--port", type=int, default=9000, help="bind port")
    parser.add_argument("--buf", type=int, default=2048, help="recv buffer size")
    parser.add_argument("--quiet", action="store_true", help="suppress per-packet logs")
    return parser.parse_args()


def main():
    args = parse_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))

    if not args.quiet:
        print(f"udp_echo_server listening on {args.host}:{args.port}")

    try:
        while True:
            data, addr = sock.recvfrom(args.buf)
            if not data:
                continue
            sock.sendto(data, addr)
            if not args.quiet:
                print(f"echo {len(data)} bytes to {addr[0]}:{addr[1]}")
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()


if __name__ == "__main__":
    main()
