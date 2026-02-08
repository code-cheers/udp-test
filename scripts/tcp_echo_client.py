#!/usr/bin/env python3
import argparse
import math
import socket
import time


def parse_args():
    parser = argparse.ArgumentParser(description="TCP echo client (RTT probe)")
    parser.add_argument("--host", required=True, help="server host")
    parser.add_argument("--port", type=int, default=9000, help="server port")
    parser.add_argument("--count", type=int, default=20, help="number of probes")
    parser.add_argument("--interval-ms", type=float, default=50.0, help="interval between probes")
    parser.add_argument("--timeout", type=float, default=1.0, help="socket timeout seconds")
    parser.add_argument("--size", type=int, default=8, help="payload size bytes")
    parser.add_argument("--verbose", action="store_true", help="print per-probe stats")
    return parser.parse_args()


def percentile(values, p):
    if not values:
        return None
    data = sorted(values)
    k = (len(data) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return data[int(k)]
    return data[f] + (data[c] - data[f]) * (k - f)


def read_exact(sock, size):
    buf = b""
    while len(buf) < size:
        chunk = sock.recv(size - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def connect_with_retry(host, port, timeout, retries=5, delay=0.05):
    last_err = None
    for attempt in range(retries):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
            return sock
        except (socket.timeout, OSError) as err:
            last_err = err
            try:
                sock.close()
            except OSError:
                pass
            if attempt < retries - 1:
                time.sleep(delay)
    raise last_err


def build_payload(seq, size):
    text = str(seq)
    if len(text) > size:
        raise SystemExit("payload size too small for seq value")
    return text.rjust(size, "0").encode("ascii")


def main():
    args = parse_args()
    sock = connect_with_retry(args.host, args.port, args.timeout)

    rtts = []
    lost = 0

    for seq in range(1, args.count + 1):
        payload = build_payload(seq, args.size)
        send_time = time.monotonic()
        try:
            sock.sendall(payload)
            data = read_exact(sock, args.size)
            if not data:
                raise socket.timeout()
            rtt_ms = (time.monotonic() - send_time) * 1000.0
            rtts.append(rtt_ms)
            if args.verbose:
                print(f"seq={seq} rtt_ms={rtt_ms:.3f}")
        except socket.timeout:
            lost += 1
            if args.verbose:
                print(f"seq={seq} timeout")
            try:
                sock.close()
            except OSError:
                pass
            sock = connect_with_retry(args.host, args.port, args.timeout)

        if args.interval_ms > 0:
            time.sleep(args.interval_ms / 1000.0)

    sock.close()

    sent = args.count
    received = len(rtts)
    loss_pct = (lost / sent) * 100.0
    print(f"sent={sent} received={received} loss_pct={loss_pct:.1f}")
    if received:
        min_v = min(rtts)
        avg_v = sum(rtts) / received
        max_v = max(rtts)
        p50 = percentile(rtts, 50)
        p95 = percentile(rtts, 95)
        p99 = percentile(rtts, 99)
        print(
            "rtt_ms "
            f"min={min_v:.3f} avg={avg_v:.3f} p50={p50:.3f} "
            f"p95={p95:.3f} p99={p99:.3f} max={max_v:.3f}"
        )
    else:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
