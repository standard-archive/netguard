# NetGuard 🛡️

![Tests](https://github.com/standard-archive/netguard/actions/workflows/tests.yml/badge.svg)
![Status](https://img.shields.io/badge/status-v1.0.0%20released-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A Python-based network security toolkit for host discovery, port scanning,
banner grabbing, ARP scanning, and packet sniffing — built as part of my
Cybersecurity elective coursework.

## Status
✅ v1.0.0 released. All 5 core features are implemented and tested.
See [CHANGELOG.md](CHANGELOG.md) for full release history.

## Features
- [x] Host discovery (multithreaded ping sweep)
- [x] TCP port scanner (multithreaded, with service name mapping)
- [x] Banner grabbing (service fingerprinting)
- [x] ARP scanner (local network device discovery with MAC addresses)
- [x] Packet sniffer (live capture with protocol summaries)
- [x] HTML/JSON report generation (`--output` / `--format`)
- [x] Unit tests (pytest, run on every push via GitHub Actions)

## Requirements
- Python 3.10+
- Npcap (Windows only, required for ARP scanning and packet sniffing) - https://npcap.com/#download
- Administrator/root privileges (required for ARP scanning and packet sniffing)

## Setup

Install as a package (recommended, gives you a `netguard` command):
```bash
git clone https://github.com/standard-archive/netguard.git
cd netguard
pip install -e .
netguard --help
```

Or run without installing:
```bash
git clone https://github.com/standard-archive/netguard.git
cd netguard
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Run commands as a module from the project root:
```bash
python -m netguard.cli --help
```

### Host Discovery
Sweep a subnet to find live hosts:
```bash
python -m netguard.cli discover 192.168.0.0/24
```

### Port Scanning
Scan a target host for open TCP ports:
```bash
python -m netguard.cli scan 192.168.0.1 -p 1-1024
python -m netguard.cli scan 192.168.0.1 -p 80,443,8080
```

Scan the N most common ports instead of a range:
```bash
python -m netguard.cli scan 192.168.0.1 --top-ports 20
```
`--top-ports` accepts 1-100 and cannot be combined with `-p`.

### Banner Grabbing
Grab the service banner from an open port:
```bash
python -m netguard.cli banner 192.168.0.1 80
```

### ARP Scanning
Discover devices on the local network with their MAC addresses:
```bash
python -m netguard.cli arp 192.168.0.0/24
```
> Requires Administrator/root privileges and Npcap (Windows).

### Packet Sniffing
Capture and summarize live packets on a network interface:
```bash
python -m netguard.cli sniff -c 20
```
> Requires Administrator/root privileges and Npcap (Windows).

## Configuration

NetGuard reads optional defaults from `netguard.cfg` in the directory you run it from.
Generate a starting file with (this overwrites an existing `netguard.cfg`):

```bash
netguard --init-config
```

| Section | Key | Default | Meaning |
|---------|-----|---------|---------|
| scan | default_ports | 1-1024 | Ports to scan when `-p` is omitted |
| scan | max_workers | 100 | Concurrent connection threads |
| scan | timeout | 0.5 | Seconds to wait per port |
| discover | max_workers | 50 | Concurrent pings |
| discover | timeout_ms | 1000 | Milliseconds to wait per ping |
| banner | timeout | 2.0 | Seconds to wait for a banner |
| sniff | default_count | 20 | Packets to capture when `-c` is omitted |

Missing keys fall back to these defaults. Invalid values (for example
`timeout = abc` or `max_workers = 0`) stop NetGuard with a clear error
message instead of a traceback.

## Example Report Output

![HTML Report Example](screenshots/html_report_example.png)

## ⚠️ Legal Notice
Only use NetGuard against hosts and networks you own or have explicit
permission to test. Unauthorized scanning of devices you don't control
may be illegal in your jurisdiction.

## Documentation

- [Requirements Specification](docs/requirements.md)
- [Design Document](docs/design.md)
- [SDLC Process Overview](docs/sdlc.md)
- [Project Wiki](https://github.com/standard-archive/netguard/wiki)

## License
MIT
