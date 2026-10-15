# Changelog

All notable changes to this project are documented here.

## [Unreleased]
### Changed
- scan, discover and banner now honor max_workers and timeout settings from netguard.cfg (previously only default_ports and default_count were read)

### Added
- Unit tests for config loading and host discovery
- Startup validation of netguard.cfg: clear errors for non-numeric, zero/negative or non-finite values, invalid port ranges and malformed files
- netguard --init-config now works even when the existing config is broken
- Configuration section in the README
- scan --top-ports N: scan the N most common ports (1-100), mutually exclusive with -p
- Service names for 19 more common ports (VNC, Redis, MongoDB, LDAP and others)
- Unit and end-to-end tests for --top-ports

## [1.0.0] - 2026-09-21
### Added
- CLI entry point with argparse and subcommands (discover, scan, banner, arp, sniff)
- Multithreaded ping sweep for host discovery
- Multithreaded TCP port scanner with service name mapping
- Banner grabbing for service fingerprinting
- ARP scanner for local network device discovery (MAC addresses)
- Packet sniffer with per-packet protocol summaries
- Input validation module for IPs, subnets, and ports
- Graceful error handling across all CLI commands
- JSON and HTML report generator with --output/--format flags
- Unit test suite (pytest) for validators and port range parsing
- Logging module with daily rotating file logs and console warnings
- Config file support (netguard.cfg) with --init-config flag
- pyproject.toml for pip-installable packaging with netguard console command
- CONTRIBUTING.md with setup and contribution guidelines
- Full usage guide and example report screenshot in README
- Project wiki with Installation, Usage, Architecture, and Troubleshooting pages

### Removed
- Unused early draft scaffolding (netguard/scanners, netguard/utils)
