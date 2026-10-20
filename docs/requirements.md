# Requirements Specification

## 1. Purpose
NetGuard is a command-line network security toolkit providing host discovery,
port scanning, banner grabbing, ARP scanning, and packet sniffing, with
results exportable to JSON, HTML, CSV, or Markdown.

## 2. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | The system shall discover live hosts on a given subnet via ICMP ping sweep (`discover` command). |
| FR2 | The system shall scan a target host for open TCP ports over a given port range or list (`-p`), or over the N most common ports (`--top-ports N`, 1-100, mutually exclusive with `-p`) (`scan` command). |
| FR3 | The system shall attempt to read a service banner from a given target:port (`banner` command). |
| FR4 | The system shall discover devices on the local network segment via ARP requests, returning IP and MAC address pairs (`arp` command). |
| FR5 | The system shall capture a fixed number of live packets on a network interface and print a per-packet protocol summary (`sniff` command). |
| FR6 | The system shall validate IP addresses, subnets, port inputs, and the `--top-ports` value before executing a command, rejecting invalid input with a clear error message. |
| FR7 | The system shall resolve hostnames to IP addresses when a hostname is supplied in place of an IP address. |
| FR8 | The system shall optionally export the results of discover, scan, banner, and arp commands to a file in JSON, HTML, CSV, or Markdown format (`--output` flag, with `--format` set to `json`, `html`, `csv`, or `md`). |
| FR9 | The system shall log command execution (start, result, and errors) to a dated log file. |
| FR10 | The system shall allow default values (port range, worker counts, timeouts) to be configured via a `netguard.cfg` file, generated with `--init-config`. |
| FR11 | The system shall report its own version via `--version`. |
| FR12 | The system shall validate `netguard.cfg` at startup: `max_workers`, `timeout`, `timeout_ms`, and `default_count` must be positive finite numbers, `default_ports` must be a valid port range, and an unparsable file shall be rejected with a clear message and exit code 1. |
| FR13 | CSV reports shall neutralize values that a spreadsheet would run as formulas (for example a value starting with `=`), because report data such as banners comes from untrusted hosts. |
| FR14 | HTML reports shall escape special characters in scan data so that banner text cannot break or inject into the page. |

## 3. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR1 | Host discovery and port scanning shall use concurrent execution (threading) to scan multiple targets/ports in parallel. |
| NFR2 | The system shall fail gracefully on invalid input or runtime errors (permission, network, OS errors), without raising unhandled exceptions to the user. |
| NFR3 | ARP scanning and packet sniffing require elevated (Administrator/root) privileges and the Npcap driver on Windows; this is documented as a prerequisite, not silently handled. |
| NFR4 | The system shall be installable as a Python package via `pip install -e .`, exposing a `netguard` console command. |
| NFR5 | The system's core logic (input validation, port range parsing, configuration loading and validation, scan and discovery timeouts, and report generation) and its CLI behavior for configuration, report formats, and `--top-ports` shall be covered by automated tests under `tests/`, runnable via `pytest`. |
| NFR6 | Automated tests shall run on every push to the repository via continuous integration (GitHub Actions). |
| NFR7 | The system targets Python 3.10 and above.

## 4. Out of Scope
The following are explicitly not implemented and are not assumed as requirements:
- A graphical user interface
- Vulnerability scanning or exploitation features
- Scheduled/automated recurring scans
- Multi-host concurrent scanning in a single `scan` invocation (one target per invocation)
