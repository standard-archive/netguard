"""
NetGuard - Port Scanner Module
Performs a multithreaded TCP connect scan against a target host.
"""

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP-Alt",
}


def parse_port_range(port_str: str) -> list:
    """
    Parse a port range string like '1-1024' or '80,443,8080' into a list of ints.
    """
    ports = set()

    for part in port_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            start, end = int(start), int(end)
            if start < 1 or end > 65535 or start > end:
                raise ValueError(f"Invalid port range: {part}")
            ports.update(range(start, end + 1))
        else:
            port = int(part)
            if port < 1 or port > 65535:
                raise ValueError(f"Invalid port: {part}")
            ports.add(port)

    return sorted(ports)


def scan_port(target: str, port: int, timeout: float = 0.5) -> bool:
    """
    Attempt a TCP connect to a single port. Returns True if open.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((target, port))
            return result == 0
    except socket.error:
        return False


def scan_ports(target: str, port_range: str, max_workers: int = 100, timeout: float = 0.5) -> list:
    """
    Scan a range of ports on a target host. Returns a list of open ports.
    """
    ports = parse_port_range(port_range)
    open_ports = []

    print(f"[*] Scanning {len(ports)} ports on {target}...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {
            executor.submit(scan_port, target, port, timeout): port for port in ports
        }
        for future in as_completed(future_to_port):
            port = future_to_port[future]
            if future.result():
                service = COMMON_PORTS.get(port, "unknown")
                print(f"[+] Port {port} open ({service})")
                open_ports.append(port)

    return sorted(open_ports)
