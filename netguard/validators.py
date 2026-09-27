"""
NetGuard - Input Validation Module
Shared validation helpers used across CLI commands to fail gracefully
with clear error messages instead of raw tracebacks.
"""

import ipaddress
import socket


class ValidationError(Exception):
    """Raised when user input fails validation."""
    pass


def validate_ip(value: str) -> str:
    """
    Validate that a string is a well-formed IP address, or a resolvable
    hostname. Returns an IP address string in either case.
    """
    try:
        ipaddress.ip_address(value)
        return value
    except ValueError:
        pass

    try:
        resolved = socket.gethostbyname(value)
        return resolved
    except socket.gaierror:
        raise ValidationError(
            f"'{value}' is not a valid IP address or resolvable hostname."
        )


def validate_subnet(value: str) -> str:
    """
    Validate that a string is a well-formed CIDR subnet (e.g. 192.168.1.0/24).
    """
    try:
        ipaddress.ip_network(value, strict=False)
        return value
    except ValueError:
        raise ValidationError(
            f"'{value}' is not a valid subnet. Expected format like 192.168.1.0/24."
        )


def validate_port(value: int) -> int:
    """
    Validate that a value is a valid port number (1-65535).
    """
    if not (1 <= value <= 65535):
        raise ValidationError(f"Port {value} is out of range. Must be between 1 and 65535.")
    return value


def validate_port_range(value: str) -> str:
    """
    Validate a port range string like '1-1024' or '80,443,8080'
    without fully parsing it (scanner.py does the detailed parsing).
    """
    for part in value.split(","):
        part = part.strip()
        if "-" in part:
            pieces = part.split("-")
            if len(pieces) != 2 or not all(p.isdigit() for p in pieces):
                raise ValidationError(f"Invalid port range segment: '{part}'")
            start, end = int(pieces[0]), int(pieces[1])
            validate_port(start)
            validate_port(end)
            if start > end:
                raise ValidationError(f"Invalid range: start ({start}) > end ({end})")
        else:
            if not part.isdigit():
                raise ValidationError(f"Invalid port value: '{part}'")
            validate_port(int(part))
    return value
