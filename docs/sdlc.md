# SDLC Process Overview

This document maps NetGuard's actual development history to standard SDLC
phases, with pointers to the real artifacts produced at each stage.

## 1. Planning
- Defined as a solo coursework project for a Cybersecurity elective.
- Scope fixed upfront: five core network tools (discover, scan, banner,
  arp, sniff), delivered incrementally.

## 2. Requirements
- See [requirements.md](requirements.md) for the functional and
  non-functional requirements, derived from the features actually
  implemented and tested.

## 3. Design
- See [design.md](design.md) for module responsibilities, data flow, and
  error handling strategy.

## 4. Implementation
- Features were implemented incrementally, one module per feature, each
  wired into the CLI and tested manually against real local-network
  targets before moving to the next feature.
- Full history of implementation commits is in the repository's git log
  and summarized in [CHANGELOG.md](../CHANGELOG.md).

## 5. Testing
- Automated unit tests cover input validation and port-range parsing
  (`tests/test_validators.py`, `tests/test_scanner.py`), run via `pytest`.
- Manual/live testing was performed against real targets for every feature
  (localhost port scans, real subnet discovery, real ARP responses, live
  packet capture, and live HTTP banner grabs).
- Continuous integration (`.github/workflows/tests.yml`) runs the test
  suite automatically on every push to `main`.

## 6. Deployment / Packaging
- Packaged as an installable Python package via `pyproject.toml`,
  installable with `pip install -e .` and exposing a `netguard` console
  command.

## 7. Maintenance
- Ongoing small fixes and additions are tracked in
  [CHANGELOG.md](../CHANGELOG.md) (e.g. the hostname-resolution fix to
  `validate_ip`).
- Project documentation (README, wiki, this `docs/` folder) is kept in
  sync with the current feature set as changes are made.
