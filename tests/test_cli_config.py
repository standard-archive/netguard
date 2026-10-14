"""
End-to-end checks that a broken netguard.cfg fails gracefully (NFR2).
Runs the CLI in a throwaway directory so no logs or configs touch the repo.
"""

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_cli(cwd, *args):
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    return subprocess.run(
        [sys.executable, "-m", "netguard.cli", *args],
        cwd=cwd, env=env, capture_output=True, text=True, timeout=30,
    )


def test_bad_config_value_gives_clear_error_not_traceback(tmp_path):
    (tmp_path / "netguard.cfg").write_text("[scan]\ntimeout = abc\n")
    result = run_cli(tmp_path, "scan", "127.0.0.1")
    assert result.returncode == 1
    assert "Invalid config" in result.stdout
    assert "Traceback" not in result.stderr


def test_malformed_config_file_gives_clear_error(tmp_path):
    (tmp_path / "netguard.cfg").write_text("timeout = 1\n")  # no [section] header
    result = run_cli(tmp_path, "scan", "127.0.0.1")
    assert result.returncode == 1
    assert "Invalid config" in result.stdout
    assert "Traceback" not in result.stderr


def test_init_config_repairs_a_broken_config(tmp_path):
    (tmp_path / "netguard.cfg").write_text("[scan]\ntimeout = abc\n")
    result = run_cli(tmp_path, "--init-config")
    assert result.returncode == 0
    assert "timeout = 0.5" in (tmp_path / "netguard.cfg").read_text()
