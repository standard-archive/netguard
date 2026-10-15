"""
Unit tests for netguard.scanner (pure parsing logic only, no live sockets).
"""

import pytest
from netguard.scanner import parse_port_range


def test_parse_single_port():
    assert parse_port_range("80") == [80]


def test_parse_comma_separated():
    assert parse_port_range("80,443,8080") == [80, 443, 8080]


def test_parse_range():
    assert parse_port_range("1-5") == [1, 2, 3, 4, 5]


def test_parse_mixed():
    result = parse_port_range("22,80-82,443")
    assert result == [22, 80, 81, 82, 443]


def test_parse_deduplicates():
    result = parse_port_range("80,80,443")
    assert result == [80, 443]


def test_parse_invalid_range_raises():
    with pytest.raises(ValueError):
        parse_port_range("100-1")


def test_parse_out_of_bounds_raises():
    with pytest.raises(ValueError):
        parse_port_range("70000")


def test_scan_ports_passes_timeout_to_each_port(monkeypatch):
    from netguard import scanner

    seen = []

    def fake_scan_port(target, port, timeout=0.5):
        seen.append(timeout)
        return False

    monkeypatch.setattr(scanner, "scan_port", fake_scan_port)
    scanner.scan_ports("127.0.0.1", "80-82", max_workers=2, timeout=0.1)
    assert seen == [0.1, 0.1, 0.1]


def test_top_ports_are_unique_valid_and_ordered():
    from netguard.scanner import TOP_PORTS

    assert len(TOP_PORTS) == 100
    assert len(set(TOP_PORTS)) == len(TOP_PORTS)
    assert all(1 <= p <= 65535 for p in TOP_PORTS)
    assert TOP_PORTS[:3] == [80, 443, 22]


def test_top_20_ports_all_have_service_names():
    from netguard.scanner import COMMON_PORTS, TOP_PORTS

    assert all(port in COMMON_PORTS for port in TOP_PORTS[:20])
