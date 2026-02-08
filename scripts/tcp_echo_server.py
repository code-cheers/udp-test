#!/usr/bin/env python3
import argparse
import socket


def parse_args():
    parser = argparse.ArgumentParser(description="TCP echo server")
    parser.add_argument("--host", default="0.0.0.0", help="bind host")
    parser.add_argument("--port", type=int, default=9000, help="bind port")
    parser.add_argument("--size", type=int, default=8, help="payload size bytes")
    parser.add_argument("--quiet", action="store_true", help="suppress per-packet logs")
    return parser.parse_args()


def read_exact(sock, size):
    buf = b""
    while len(buf) < size:
        chunk = sock.recv(size - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def handle_conn(conn, addr, size, quiet):
    if not quiet:
        print(f"tcp_echo_server connection from {addr[0]}:{addr[1]}")
    try:
        while True:
            data = read_exact(conn, size)
            if not data:
                break
            conn.sendall(data)
            if not quiet:
                print(f"echo {len(data)} bytes to {addr[0]}:{addr[1]}")
    finally:
        conn.close()


def main():
    args = parse_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.host, args.port))
    sock.listen(5)

    if not args.quiet:
        print(f"tcp_echo_server listening on {args.host}:{args.port}")

    try:
        while True:
            conn, addr = sock.accept()
            handle_conn(conn, addr, args.size, args.quiet)
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()


if __name__ == "__main__":
    main()
