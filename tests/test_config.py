"""
Unit tests for netguard.config.
"""

import pytest

from netguard.config import (
    ConfigError,
    generate_default_config_file,
    load_config,
    validate_config,
)


def test_defaults_used_when_file_missing(tmp_path):
    cfg = load_config(str(tmp_path / "missing.cfg"))
    assert cfg.getint("scan", "max_workers") == 100
    assert cfg.getfloat("scan", "timeout") == 0.5
    assert cfg.getint("discover", "timeout_ms") == 1000
    assert cfg.getfloat("banner", "timeout") == 2.0


def test_file_overrides_defaults(tmp_path):
    path = tmp_path / "custom.cfg"
    path.write_text("[scan]\ntimeout = 2.5\n")
    cfg = load_config(str(path))
    assert cfg.getfloat("scan", "timeout") == 2.5
    assert cfg.getint("scan", "max_workers") == 100  # untouched key falls back


def test_generated_config_round_trips(tmp_path):
    path = tmp_path / "generated.cfg"
    generate_default_config_file(str(path))
    cfg = load_config(str(path))
    assert cfg.get("scan", "default_ports") == "1-1024"
    assert cfg.getint("sniff", "default_count") == 20


def _cfg(tmp_path, text):
    path = tmp_path / "test.cfg"
    path.write_text(text)
    return load_config(str(path))


def test_validate_accepts_defaults(tmp_path):
    validate_config(load_config(str(tmp_path / "missing.cfg")))


def test_validate_rejects_non_numeric_timeout(tmp_path):
    with pytest.raises(ConfigError, match="timeout"):
        validate_config(_cfg(tmp_path, "[scan]\ntimeout = abc\n"))


def test_validate_rejects_fractional_worker_count(tmp_path):
    with pytest.raises(ConfigError, match="max_workers"):
        validate_config(_cfg(tmp_path, "[scan]\nmax_workers = 2.5\n"))


@pytest.mark.parametrize("bad", ["0", "-5", "nan", "inf"])
def test_validate_rejects_non_positive_or_non_finite(tmp_path, bad):
    with pytest.raises(ConfigError):
        validate_config(_cfg(tmp_path, f"[discover]\ntimeout_ms = {bad}\n"))


def test_validate_rejects_bad_default_ports(tmp_path):
    with pytest.raises(ConfigError, match="default_ports"):
        validate_config(_cfg(tmp_path, "[scan]\ndefault_ports = 99999\n"))


def test_load_config_raises_config_error_on_malformed_file(tmp_path):
    with pytest.raises(ConfigError, match="could not parse"):
        _cfg(tmp_path, "timeout = 1\n")  # no [section] header


def test_load_config_tolerates_utf8_bom(tmp_path):
    path = tmp_path / "bom.cfg"
    path.write_bytes(b"\xef\xbb\xbf[scan]\ntimeout = 3\n")  # Windows Notepad style
    assert load_config(str(path)).getfloat("scan", "timeout") == 3.0
