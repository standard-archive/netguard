"""
Unit tests for netguard.validators
"""

import pytest
from netguard.validators import (
    ValidationError,
    validate_ip,
    validate_subnet,
    validate_port,
    validate_port_range,
)


def test_validate_ip_valid():
    assert validate_ip("192.168.1.1") == "192.168.1.1"
    assert validate_ip("8.8.8.8") == "8.8.8.8"
    assert validate_ip("::1") == "::1"


def test_validate_ip_invalid():
    with pytest.raises(ValidationError):
        validate_ip("999.999.999.999")
    with pytest.raises(ValidationError):
        validate_ip("not-an-ip")


def test_validate_subnet_valid():
    assert validate_subnet("192.168.1.0/24") == "192.168.1.0/24"
    assert validate_subnet("10.0.0.0/8") == "10.0.0.0/8"


def test_validate_subnet_invalid():
    with pytest.raises(ValidationError):
        validate_subnet("not-a-subnet")
    with pytest.raises(ValidationError):
        validate_subnet("192.168.1.0/99")


def test_validate_port_valid():
    assert validate_port(1) == 1
    assert validate_port(80) == 80
    assert validate_port(65535) == 65535


def test_validate_port_invalid():
    with pytest.raises(ValidationError):
        validate_port(0)
    with pytest.raises(ValidationError):
        validate_port(70000)
    with pytest.raises(ValidationError):
        validate_port(-1)


def test_validate_port_range_valid():
    assert validate_port_range("1-1024") == "1-1024"
    assert validate_port_range("80,443,8080") == "80,443,8080"
    assert validate_port_range("22") == "22"


def test_validate_port_range_invalid():
    with pytest.raises(ValidationError):
        validate_port_range("abc")
    with pytest.raises(ValidationError):
        validate_port_range("1000-1")
    with pytest.raises(ValidationError):
        validate_port_range("99999")


def test_validate_ip_resolves_hostname():
    # localhost should always resolve, regardless of network state
    result = validate_ip("localhost")
    assert result in ("127.0.0.1", "::1")


def test_validate_ip_rejects_unresolvable_hostname():
    with pytest.raises(ValidationError):
        validate_ip("this-domain-does-not-exist-12345.invalid")
