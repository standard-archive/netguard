"""
Unit tests for netguard.discovery (no real pings are sent).
"""

from netguard import discovery


def test_discover_hosts_passes_timeout_to_each_ping(monkeypatch):
    seen = []

    def fake_ping(ip, timeout_ms=1000):
        seen.append(timeout_ms)
        return False

    monkeypatch.setattr(discovery, "ping_host", fake_ping)
    discovery.discover_hosts("192.168.1.0/30", max_workers=2, timeout_ms=250)
    assert seen == [250, 250]  # a /30 has two usable hosts


def test_discover_hosts_returns_only_live_hosts(monkeypatch):
    monkeypatch.setattr(discovery, "ping_host", lambda ip, timeout_ms=1000: ip.endswith(".1"))
    assert discovery.discover_hosts("192.168.1.0/30") == ["192.168.1.1"]
