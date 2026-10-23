"""
End-to-end checks for the discover, banner and error-handling paths of the CLI.
No internet, admin rights or real devices needed: banner tests talk to a tiny
server started on localhost, and invalid-input tests fail before any scan.
"""

import json
import socket
import threading

import pytest

from tests.test_cli_config import run_cli


@pytest.fixture
def banner_server():
    """A localhost TCP server that greets one client like an SSH service."""
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    def serve():
        try:
            conn, _ = server.accept()
            conn.sendall(b"SSH-2.0-NetGuardTest\r\n")
            conn.close()
        except OSError:
            pass

    threading.Thread(target=serve, daemon=True).start()
    yield port
    server.close()


def closed_port():
    """Return a localhost port that nothing is listening on."""
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def test_no_command_prints_help_and_exits_1(tmp_path):
    result = run_cli(tmp_path)
    assert result.returncode == 1
    assert "usage:" in result.stdout


def test_version_flag_reports_the_tool_name(tmp_path):
    result = run_cli(tmp_path, "--version")
    assert result.returncode == 0
    assert "NetGuard" in result.stdout


def test_banner_reads_the_service_greeting(tmp_path, banner_server):
    result = run_cli(tmp_path, "banner", "127.0.0.1", str(banner_server))
    assert result.returncode == 0
    assert f"[127.0.0.1:{banner_server}] SSH-2.0-NetGuardTest" in result.stdout


def test_banner_result_can_be_saved_as_json(tmp_path, banner_server):
    result = run_cli(tmp_path, "banner", "127.0.0.1", str(banner_server),
                     "-o", "banner.json")
    assert result.returncode == 0
    report = json.loads((tmp_path / "banner.json").read_text(encoding="utf-8"))
    assert report["results"]["banner"] == "SSH-2.0-NetGuardTest"
    assert report["results"]["port"] == banner_server


def test_banner_on_a_closed_port_does_not_crash(tmp_path):
    port = closed_port()
    result = run_cli(tmp_path, "banner", "127.0.0.1", str(port))
    assert result.returncode == 0
    assert f"[127.0.0.1:{port}]" in result.stdout
    assert "Traceback" not in result.stderr


def test_banner_rejects_out_of_range_port(tmp_path):
    result = run_cli(tmp_path, "banner", "127.0.0.1", "70000")
    assert result.returncode == 1
    assert "Invalid input" in result.stdout


def test_banner_rejects_unresolvable_host(tmp_path):
    result = run_cli(tmp_path, "banner", "no-such-host-12345.invalid", "80")
    assert result.returncode == 1
    assert "Invalid input" in result.stdout
    assert "Traceback" not in result.stderr


def test_discover_rejects_invalid_subnet(tmp_path):
    result = run_cli(tmp_path, "discover", "not-a-subnet")
    assert result.returncode == 1
    assert "Invalid input" in result.stdout
    assert "Traceback" not in result.stderr


def test_discover_single_host_completes_and_saves_json(tmp_path):
    result = run_cli(tmp_path, "discover", "127.0.0.1/32", "-o", "hosts.json")
    assert result.returncode == 0
    assert "Discovery complete" in result.stdout
    report = json.loads((tmp_path / "hosts.json").read_text(encoding="utf-8"))
    assert report["results"]["target"] == "127.0.0.1/32"
    assert isinstance(report["results"]["live_hosts"], list)


def test_arp_rejects_invalid_subnet(tmp_path):
    result = run_cli(tmp_path, "arp", "300.1.1.0/24")
    assert result.returncode == 1
    assert "Invalid input" in result.stdout


def test_scan_rejects_invalid_port_range(tmp_path):
    result = run_cli(tmp_path, "scan", "127.0.0.1", "-p", "99999")
    assert result.returncode == 1
    assert "Invalid input" in result.stdout
    assert "Traceback" not in result.stderr
