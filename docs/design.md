# Design Document

## 1. Architecture Overview
NetGuard is a single Python package (`netguard/`) with one module per
feature. A single CLI entry point (`cli.py`) parses arguments with
`argparse` and dispatches to the relevant module. There is no persistent
server or database component; each invocation is a one-off operation
against live network targets.

netguard/
├── cli.py # argparse entry point; parses args, dispatches, handles errors
├── discovery.py # Host discovery (ICMP ping sweep)
├── scanner.py # TCP port scanner + port range parsing
├── banner.py # Banner grabbing over TCP sockets
├── arp_scan.py # ARP scanning (scapy)
├── sniffer.py # Packet sniffing (scapy)
├── validators.py # Input validation (IP/subnet/port), hostname resolution
├── report.py # JSON/HTML report generation
├── logger.py # Logging configuration (file + console handlers)
└── config.py # netguard.cfg loading and default generation


## 2. Module Responsibilities

- **cli.py**: Owns the user-facing contract (flags, subcommands, help text).
  Catches `ValidationError`, `PermissionError`, `OSError`, and
  `KeyboardInterrupt` at the top level so no module below it needs to handle
  user-facing error presentation.
- **validators.py**: Single source of truth for what counts as valid input.
  Every command validates its target/port arguments here before calling
  into feature modules, so feature modules can assume well-formed input.
- **discovery.py / scanner.py**: Use `concurrent.futures.ThreadPoolExecutor`
  for concurrency, since both are I/O-bound (waiting on network responses)
  rather than CPU-bound.
- **arp_scan.py / sniffer.py**: Depend on `scapy`, which requires raw socket
  access. These modules raise `PermissionError`/`OSError` with instructive
  messages when raw socket access is unavailable, rather than letting the
  underlying scapy exception surface directly.
- **report.py**: Pure function of a results dict in, a file on disk out.
  Has no knowledge of which command produced the data.
- **logger.py**: Configured once at CLI startup; other modules do not
  configure logging themselves.
- **config.py**: Provides defaults with a layered fallback (built-in
  defaults, overridden by `netguard.cfg` if present). Feature modules do not
  read config directly; `cli.py` reads config values and passes them as
  function arguments.

## 3. Data Flow (example: `scan` command)
1. `cli.py` parses `scan <target> -p <ports> [-o file] [-f format]`.
2. `validators.validate_ip` resolves/validates the target.
3. `validators.validate_port_range` validates the port string.
4. `scanner.scan_ports` parses the range and performs the threaded scan.
5. Results are printed to console and logged via `logger`.
6. If `--output` was given, `report.generate_report` writes the results to
   disk in the requested format.

## 4. Error Handling Strategy
All feature modules raise standard Python exceptions
(`ValueError`, `PermissionError`, `OSError`) or the custom
`validators.ValidationError`. `cli.py` is the single location that catches
these and converts them into user-facing messages and exit codes. This
keeps error presentation consistent across all five commands.

## 5. Known Constraints
- Raw-socket features (`arp`, `sniff`) require Npcap on Windows and
  elevated privileges on all platforms; this is a constraint of the
  underlying OS/library, not a design choice NetGuard can remove.
- The system scans one target per invocation; batch/multi-target scanning
  is not implemented.
