"""
NetGuard - Configuration Module
Loads user-defined defaults from a netguard.cfg file, falling back to
sensible built-in defaults if the file is missing or incomplete.
"""

import configparser
import os


DEFAULT_CONFIG = {
    "scan": {
        "default_ports": "1-1024",
        "max_workers": "100",
        "timeout": "0.5",
    },
    "discover": {
        "max_workers": "50",
        "timeout_ms": "1000",
    },
    "banner": {
        "timeout": "2.0",
    },
    "sniff": {
        "default_count": "20",
    },
}

CONFIG_FILENAME = "netguard.cfg"


def load_config(path: str = CONFIG_FILENAME) -> configparser.ConfigParser:
    """
    Load config from a .cfg file if present, layered on top of built-in
    defaults so missing sections/keys always fall back safely.
    """
    parser = configparser.ConfigParser()
    parser.read_dict(DEFAULT_CONFIG)

    if os.path.exists(path):
        try:
            parser.read(path, encoding="utf-8-sig")
        except configparser.Error as e:
            raise ConfigError(f"could not parse {path}: {e}")

    return parser


def generate_default_config_file(path: str = CONFIG_FILENAME):
    """
    Write out a netguard.cfg file populated with the default values,
    so users have a starting point to customize.
    """
    parser = configparser.ConfigParser()
    parser.read_dict(DEFAULT_CONFIG)
    with open(path, "w", encoding="utf-8") as f:
        parser.write(f)
    print(f"[*] Default config written to {path}")


class ConfigError(Exception):
    """Raised when netguard.cfg contains an invalid value."""


# (section, key, type) for every numeric setting that must be a positive number
NUMERIC_SETTINGS = [
    ("scan", "max_workers", int),
    ("scan", "timeout", float),
    ("discover", "max_workers", int),
    ("discover", "timeout_ms", int),
    ("banner", "timeout", float),
    ("sniff", "default_count", int),
]


def validate_config(cfg: configparser.ConfigParser) -> configparser.ConfigParser:
    """
    Check every setting up front so a bad netguard.cfg produces a clear
    error message instead of a traceback halfway through a command.
    """
    import math

    from netguard.validators import ValidationError, validate_port_range

    for section, key, kind in NUMERIC_SETTINGS:
        raw = cfg.get(section, key)
        try:
            value = kind(raw)
        except ValueError:
            expected = "a whole number" if kind is int else "a number"
            raise ConfigError(f"[{section}] {key} must be {expected}, got '{raw}'")
        if not math.isfinite(value) or value <= 0:
            raise ConfigError(f"[{section}] {key} must be greater than 0, got '{raw}'")

    try:
        validate_port_range(cfg.get("scan", "default_ports"))
    except ValidationError as e:
        raise ConfigError(f"[scan] default_ports is invalid: {e}")

    return cfg
