"""
NetGuard CLI
Entry point for the network security toolkit.
"""

import argparse
import sys

from netguard.discovery import discover_hosts
from netguard.scanner import scan_ports
from netguard.banner import grab_banner
from netguard.arp_scan import arp_scan
from netguard.sniffer import start_sniffer
from netguard.report import generate_report
from netguard.logger import setup_logger
from netguard.config import load_config, generate_default_config_file
from netguard.validators import (
    ValidationError,
    validate_ip,
    validate_subnet,
    validate_port,
    validate_port_range,
)

logger = setup_logger()
config = load_config()


def add_output_args(subparser):
    """Add shared --output/--format flags to a subcommand parser."""
    subparser.add_argument("-o", "--output", help="Save results to a file")
    subparser.add_argument(
        "-f", "--format", choices=["json", "html"], default="json",
        help="Report format when using --output (default: json)"
    )


def build_parser():
    parser = argparse.ArgumentParser(
        prog="netguard",
        description="NetGuard - A Python network security toolkit"
    )
    parser.add_argument(
        "-v", "--version", action="version", version="NetGuard 1.0.0"
    )
    parser.add_argument(
        "--init-config", action="store_true",
        help="Generate a default netguard.cfg file and exit"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    discover_parser = subparsers.add_parser("discover", help="Discover live hosts on a network")
    discover_parser.add_argument("target", help="Target subnet, e.g. 192.168.1.0/24")
    add_output_args(discover_parser)

    default_ports = config.get("scan", "default_ports", fallback="1-1024")
    scan_parser = subparsers.add_parser("scan", help="Scan ports on a target host")
    scan_parser.add_argument("target", help="Target IP address")
    scan_parser.add_argument("-p", "--ports", default=default_ports, help=f"Port range (default from config: {default_ports})")
    add_output_args(scan_parser)

    banner_parser = subparsers.add_parser("banner", help="Grab service banners from open ports")
    banner_parser.add_argument("target", help="Target IP address")
    banner_parser.add_argument("port", type=int, help="Target port")
    add_output_args(banner_parser)

    arp_parser = subparsers.add_parser("arp", help="Perform an ARP scan on the local network")
    arp_parser.add_argument("target", help="Target subnet, e.g. 192.168.1.0/24")
    add_output_args(arp_parser)

    default_count = config.getint("sniff", "default_count", fallback=20)
    sniff_parser = subparsers.add_parser("sniff", help="Sniff packets on a network interface")
    sniff_parser.add_argument("-i", "--interface", help="Network interface to sniff on")
    sniff_parser.add_argument("-c", "--count", type=int, default=default_count, help=f"Number of packets (default from config: {default_count})")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.init_config:
        generate_default_config_file()
        sys.exit(0)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    logger.info(f"Command started: {args.command} (args: {vars(args)})")

    try:
        if args.command == "discover":
            validate_subnet(args.target)
            live_hosts = discover_hosts(args.target)
            logger.info(f"Discovery finished: {len(live_hosts)} host(s) up on {args.target}")
            print(f"\n[*] Discovery complete. {len(live_hosts)} host(s) up.")
            if args.output:
                generate_report({"target": args.target, "live_hosts": live_hosts}, args.output, args.format)

        elif args.command == "scan":
            validate_ip(args.target)
            validate_port_range(args.ports)
            open_ports = scan_ports(args.target, args.ports)
            logger.info(f"Scan finished: {len(open_ports)} open port(s) on {args.target}")
            print(f"\n[*] Scan complete. {len(open_ports)} open port(s) found.")
            if args.output:
                generate_report({"target": args.target, "open_ports": open_ports}, args.output, args.format)

        elif args.command == "banner":
            validate_ip(args.target)
            validate_port(args.port)
            result = grab_banner(args.target, args.port)
            logger.info(f"Banner grabbed from {args.target}:{args.port}")
            print(f"[{args.target}:{args.port}] {result}")
            if args.output:
                generate_report({"target": args.target, "port": args.port, "banner": result}, args.output, args.format)

        elif args.command == "arp":
            validate_subnet(args.target)
            devices = arp_scan(args.target)
            logger.info(f"ARP scan finished: {len(devices)} device(s) found on {args.target}")
            print(f"\n[*] ARP scan complete. {len(devices)} device(s) found.")
            if args.output:
                generate_report({"target": args.target, "devices": devices}, args.output, args.format)

        elif args.command == "sniff":
            logger.info(f"Sniffing started (interface={args.interface}, count={args.count})")
            start_sniffer(interface=args.interface, count=args.count)
            logger.info("Sniffing finished")

        else:
            print(f"[NetGuard] Command '{args.command}' recognized. Implementation coming soon.")

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        print(f"[!] Invalid input: {e}")
        sys.exit(1)
    except PermissionError as e:
        logger.error(f"Permission error: {e}")
        print(f"[!] Permission error: {e}")
        sys.exit(1)
    except OSError as e:
        logger.error(f"OS/network error: {e}")
        print(f"[!] Network/system error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\n[*] Interrupted by user. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
