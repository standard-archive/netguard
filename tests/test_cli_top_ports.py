"""
End-to-end checks for the scan --top-ports option.
Runs the real CLI against localhost in a throwaway directory.
"""

from tests.test_cli_config import run_cli


def test_top_ports_scans_the_requested_number_of_ports(tmp_path):
    result = run_cli(tmp_path, "scan", "127.0.0.1", "--top-ports", "5")
    assert result.returncode == 0
    assert "Scanning 5 ports on 127.0.0.1" in result.stdout


def test_top_ports_conflicts_with_ports_flag(tmp_path):
    result = run_cli(tmp_path, "scan", "127.0.0.1", "-p", "80", "--top-ports", "5")
    assert result.returncode == 2
    assert "not allowed with" in result.stderr


def test_top_ports_zero_is_rejected_cleanly(tmp_path):
    result = run_cli(tmp_path, "scan", "127.0.0.1", "--top-ports", "0")
    assert result.returncode == 1
    assert "Invalid input" in result.stdout
    assert "Traceback" not in result.stderr


def test_top_ports_above_list_size_is_rejected_cleanly(tmp_path):
    result = run_cli(tmp_path, "scan", "127.0.0.1", "--top-ports", "101")
    assert result.returncode == 1
    assert "between 1 and 100" in result.stdout
