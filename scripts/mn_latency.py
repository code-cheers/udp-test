#!/usr/bin/env python3
import argparse
import os
import shlex
import time

from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.net import Mininet


def parse_args():
    parser = argparse.ArgumentParser(description="Mininet TCP/UDP loss test")
    parser.add_argument("--loss", type=float, default=0.0, help="packet loss percent")
    parser.add_argument("--count", type=int, default=20, help="probe count")
    parser.add_argument("--interval-ms", type=float, default=50.0, help="probe interval")
    parser.add_argument("--timeout", type=float, default=1.0, help="probe timeout seconds")
    parser.add_argument("--port", type=int, default=9000, help="echo port")
    parser.add_argument("--protocol", choices=["udp", "tcp", "both"], default="both")
    parser.add_argument("--tcp-size", type=int, default=8, help="tcp payload size bytes")
    parser.add_argument("--client-verbose", action="store_true", help="per-probe output")
    parser.add_argument("--verbose", action="store_true", help="mininet info logs")
    return parser.parse_args()


def build_link_opts(args):
    opts = {
        "loss": args.loss,
    }
    return opts


def main():
    args = parse_args()
    if os.geteuid() != 0:
        raise SystemExit("Mininet requires root privileges (try sudo).")
    setLogLevel("info" if args.verbose else "warning")

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    udp_server_path = os.path.join(repo_root, "scripts", "udp_echo_server.py")
    udp_client_path = os.path.join(repo_root, "scripts", "udp_echo_client.py")
    tcp_server_path = os.path.join(repo_root, "scripts", "tcp_echo_server.py")
    tcp_client_path = os.path.join(repo_root, "scripts", "tcp_echo_client.py")

    net = Mininet(
        controller=None,
        link=TCLink,
        autoSetMacs=True,
        autoStaticArp=True,
    )
    h1 = net.addHost("h1")
    h2 = net.addHost("h2")

    link_opts = build_link_opts(args)
    net.addLink(h1, h2, **link_opts)

    net.build()
    net.start()

    def run_udp():
        server_log = "/tmp/udp_echo_server.log"
        server_cmd = (
            f"python3 {shlex.quote(udp_server_path)} --host {h2.IP()} --port {args.port} "
            f"--quiet > {server_log} 2>&1 & echo $!"
        )
        server_pid = h2.cmd(server_cmd).strip()
        time.sleep(0.4)

        client_cmd = (
            f"python3 {shlex.quote(udp_client_path)} --host {h2.IP()} --port {args.port} "
            f"--count {args.count} --interval-ms {args.interval_ms} --timeout {args.timeout}"
        )
        if args.client_verbose:
            client_cmd += " --verbose"

        output = h1.cmd(client_cmd)
        if server_pid:
            h2.cmd(f"kill {server_pid}")
        return output.strip()

    def run_tcp():
        server_log = "/tmp/tcp_echo_server.log"
        server_cmd = (
            f"python3 {shlex.quote(tcp_server_path)} --host {h2.IP()} --port {args.port} "
            f"--size {args.tcp_size} --quiet > {server_log} 2>&1 & echo $!"
        )
        server_pid = h2.cmd(server_cmd).strip()
        time.sleep(0.4)

        client_cmd = (
            f"python3 {shlex.quote(tcp_client_path)} --host {h2.IP()} --port {args.port} "
            f"--count {args.count} --interval-ms {args.interval_ms} --timeout {args.timeout} "
            f"--size {args.tcp_size}"
        )
        if args.client_verbose:
            client_cmd += " --verbose"

        output = h1.cmd(client_cmd)
        if server_pid:
            h2.cmd(f"kill {server_pid}")
        return output.strip()

    if args.protocol in ("udp", "both"):
        print("UDP")
        print(run_udp())
    if args.protocol in ("tcp", "both"):
        print("TCP")
        print(run_tcp())

    net.stop()


if __name__ == "__main__":
    main()
