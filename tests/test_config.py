"""
Unit tests for netguard.config.
"""

from netguard.config import generate_default_config_file, load_config


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
