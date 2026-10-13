"""
NetGuard - Host Discovery Module
Performs a ping sweep across a target subnet to find live hosts.
"""

import ipaddress
import platform
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


def ping_host(ip: str, timeout_ms: int = 1000) -> bool:
    """
    Ping a single host. Returns True if it responds, False otherwise.
    Works cross-platform (Windows vs Linux/macOS ping syntax differs).
    """
    system = platform.system().lower()

    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(timeout_ms), ip]
    else:
        timeout_sec = str(max(1, timeout_ms // 1000))
        cmd = ["ping", "-c", "1", "-W", timeout_sec, ip]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=(timeout_ms / 1000) + 1,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def discover_hosts(subnet: str, max_workers: int = 50, timeout_ms: int = 1000) -> list:
    """
    Sweep a subnet (e.g. '192.168.1.0/24') and return a list of live IPs.
    """
    try:
        network = ipaddress.ip_network(subnet, strict=False)
    except ValueError as e:
        raise ValueError(f"Invalid subnet '{subnet}': {e}")

    live_hosts = []
    hosts = list(network.hosts())

    print(f"[*] Scanning {len(hosts)} hosts in {subnet}...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {
            executor.submit(ping_host, str(ip), timeout_ms): str(ip) for ip in hosts
        }
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            if future.result():
                print(f"[+] Host up: {ip}")
                live_hosts.append(ip)

    return live_hosts
