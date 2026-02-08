#!/usr/bin/env python3
import argparse
import os
import re
import subprocess

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser(description="Loss sweep + P99 plot")
    parser.add_argument(
        "--loss-levels",
        default="1 3 6",
        help="loss levels in percent (space or comma separated)",
    )
    parser.add_argument("--count", type=int, default=200, help="probe count")
    parser.add_argument("--interval-ms", type=float, default=16.0, help="probe interval")
    parser.add_argument("--timeout", type=float, default=1.0, help="probe timeout seconds")
    parser.add_argument("--port", type=int, default=9000, help="echo port")
    parser.add_argument("--tcp-size", type=int, default=8, help="tcp payload size bytes")
    parser.add_argument(
        "--output",
        default="plots/loss_sweep_p99.png",
        help="output image path",
    )
    return parser.parse_args()


def split_levels(text):
    parts = re.split(r"[ ,]+", text.strip())
    levels = []
    for part in parts:
        if not part:
            continue
        levels.append(float(part))
    return levels


def extract_p99(output):
    p99 = {}
    current = None
    for line in output.splitlines():
        line = line.strip()
        if line in ("UDP", "TCP"):
            current = line
            continue
        if current and line.startswith("rtt_ms"):
            match = re.search(r"p99=([0-9.]+)", line)
            if match:
                p99[current] = float(match.group(1))
                current = None
    return p99


def strip_noise(output):
    lines = []
    for line in output.splitlines():
        if "Error setting resource limits" in line:
            continue
        lines.append(line)
    return "\n".join(lines)


def run_once(loss, args):
    cmd = [
        "python3",
        "scripts/mn_latency.py",
        "--loss",
        str(loss),
        "--count",
        str(args.count),
        "--interval-ms",
        str(args.interval_ms),
        "--timeout",
        str(args.timeout),
        "--port",
        str(args.port),
        "--protocol",
        "both",
        "--tcp-size",
        str(args.tcp_size),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = (result.stdout or "") + (result.stderr or "")
    output = strip_noise(output)
    print(f"LOSS={loss}%")
    print(output.strip())
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    return output


def plot(losses, udp_p99, tcp_p99, output_path):
    plt.figure(figsize=(7, 4))
    plt.plot(losses, udp_p99, marker="o", linewidth=2, label="UDP P99")
    plt.plot(losses, tcp_p99, marker="s", linewidth=2, label="TCP P99")
    plt.title("P99 RTT vs Packet Loss (loss only)")
    plt.xlabel("Loss (%)")
    plt.ylabel("P99 RTT (ms)")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)


def main():
    args = parse_args()
    losses = split_levels(args.loss_levels)
    udp_p99 = []
    tcp_p99 = []

    for loss in losses:
        output = run_once(loss, args)
        p99 = extract_p99(output)
        if "UDP" not in p99 or "TCP" not in p99:
            raise SystemExit("failed to parse p99 from output")
        udp_p99.append(p99["UDP"])
        tcp_p99.append(p99["TCP"])

    plot_path = os.path.abspath(args.output)
    plot(losses, udp_p99, tcp_p99, plot_path)
    print(f"plot_saved={plot_path}")


if __name__ == "__main__":
    main()
