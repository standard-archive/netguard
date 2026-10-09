"""NetGuard CLI entry point."""

import argparse
import sys

from netguard import __version__
from netguard.utils.validators import (
    network_cidr,
    port_list,
    positive_float,
    positive_int,
    target_host,
)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="netguard",
        description="NetGuard: network security toolkit",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"NetGuard {__version__}"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable verbose output"
    )

    sub = parser.add_subparsers(dest="command", required=True, metavar="command")

    discover = sub.add_parser("discover", help="find live hosts on a network")
    discover.add_argument("network", type=network_cidr, help="CIDR range, e.g. 192.168.1.0/24")
    discover.add_argument("-t", "--timeout", type=positive_float, default=1.0,
                          help="seconds to wait per host (default: 1.0)")

    scan = sub.add_parser("scan", help="scan a host for open TCP ports")
    scan.add_argument("target", type=target_host, help="IP address or hostname")
    scan.add_argument("-p", "--ports", type=port_list, default=port_list("1-1024"),
                      help="ports to scan, e.g. 22,80,443 or 1-1024 (default: 1-1024)")
    scan.add_argument("-t", "--timeout", type=positive_float, default=1.0,
                      help="seconds to wait per port (default: 1.0)")
    scan.add_argument("--threads", type=positive_int, default=100,
                      help="number of worker threads (default: 100)")

    arp = sub.add_parser("arp", help="ARP scan the local network")
    arp.add_argument("network", type=network_cidr, help="CIDR range, e.g. 192.168.1.0/24")

    sniff = sub.add_parser("sniff", help="capture packets")
    sniff.add_argument("-i", "--interface", help="network interface to listen on")
    sniff.add_argument("-c", "--count", type=positive_int, default=20,
                       help="number of packets to capture (default: 20)")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    # Each command gets wired up to its real module on the days ahead.
    if args.command == "scan":
        print(f"[scan] {args.target}: {len(args.ports)} ports, "
              f"{args.threads} threads (not implemented yet)")
    else:
        print(f"[{args.command}] not implemented yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
