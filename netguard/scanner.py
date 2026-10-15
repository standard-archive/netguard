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
    111: "RPCbind",
    135: "MS-RPC",
    139: "NetBIOS",
    161: "SNMP",
    389: "LDAP",
    465: "SMTPS",
    587: "SMTP-Submission",
    636: "LDAPS",
    993: "IMAPS",
    995: "POP3S",
    1433: "MSSQL",
    1521: "Oracle",
    1723: "PPTP",
    5900: "VNC",
    6379: "Redis",
    8443: "HTTPS-Alt",
    9200: "Elasticsearch",
    11211: "Memcached",
    27017: "MongoDB",
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


# Curated list of commonly used TCP ports, most prevalent first. This is a
# practical shortlist for quick scans, not an official ranking.
TOP_PORTS = [
    80, 443, 22, 21, 25, 23, 3389, 110, 445, 139,
    143, 53, 135, 3306, 8080, 1723, 111, 995, 993, 5900,
    587, 465, 8443, 1433, 5432, 389, 636, 161, 5985, 6379,
    27017, 9200, 11211, 2049, 873, 902, 1521, 1883, 5672, 5000,
    8000, 8008, 8081, 8088, 8888, 9000, 9090, 10000, 81, 3000,
    119, 123, 137, 138, 162, 179, 500, 514, 515, 548,
    554, 631, 1080, 1194, 1434, 2082, 2083, 2181, 2375, 2376,
    3128, 3268, 3690, 4443, 4444, 4848, 5001, 5060, 5222, 9100,
    5555, 5601, 5800, 5984, 5986, 6000, 6443, 6667, 7001, 7070,
    9042, 9092, 9300, 9418, 9999, 18080, 27018, 50000, 8009, 8180,
]
