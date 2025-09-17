# Anon-Framework Project Plan

## 1. Project Goal

To create a cross-platform framework for enhancing user anonymity and privacy. The framework will provide tools to manage VPNs, handle services like I2P and qBittorrent, and reduce OS-level telemetry.

## 2. Core Technology

- **Language:** Python 3
- **Reasoning:** Python is an ideal choice for this project due to its excellent cross-platform compatibility, extensive standard library for system interaction (`subprocess`, `os`), and a rich ecosystem of third-party libraries for tasks like process management (`psutil`) and API communication (`requests`).

## 3. Proposed Project Structure

A modular structure will be used to keep the codebase organized and maintainable.

```
/Anon-Framework/
├───anon_framework/               # Main source code package
│   ├───__init__.py
│   ├───main.py                   # Main CLI entry point
│   ├───config.py                 # Configuration management
│   │
│   ├───vpn/                      # VPN management module
│   │   ├───__init__.py
│   │   ├───base_vpn.py           # Abstract base class for VPNs
│   │   ├───nord.py               # NordVPN implementation
│   │   ├───mullvad.py            # Mullvad implementation
│   │   └───tor.py                # Tor network implementation
│   │
│   ├───privacy/                  # Privacy enhancement module
│   │   ├───__init__.py
│   │   └───telemetry.py          # OS-specific telemetry disabling
│   │
│   ├───services/                 # External services integration
│   │   ├───__init__.py
│   │   ├───i2p.py                # I2P router management
│   │   ├───qbittorrent.py        # qBittorrent API client
│   │   └───tor_browser.py        # Tor Browser launcher
│   │
│   └───utils/                    # Utility functions
│       ├───__init__.py
│       └───helpers.py            # e.g., run_command, check_os
│
├───scripts/                      # Helper scripts (install, setup)
├───docs/                         # Project documentation
├───tests/                        # Unit and integration tests
│
├───.gitignore                    # Git ignore file
├───LICENSE                       # Project license (already present)
├───README.md                     # Project README (already present)
├───gemini.md                     # This planning document
└───requirements.txt              # Python dependencies
```

## 4. Implementation Strategy

- **VPN Management:** Create a unified interface that wraps the native command-line tools for NordVPN, Mullvad, and Tor. This provides a consistent way to control different VPN services.
- **Telemetry Disabling:** This is highly OS-dependent. The `telemetry.py` module will have separate logic for Windows, macOS, and Linux to disable known telemetry agents.
- **Service Integration:**
    - **I2P & Tor Browser:** The framework will manage the lifecycle of these applications (start, stop, configure).
    - **qBittorrent:** Interact with the qBittorrent web API to manage torrents and settings.

## 5. Progress (As of 2025-09-17)

- **Project Scaffolding:**
    - The complete directory structure has been created.
    - All initial files (`__init__.py`, `main.py`, etc.) have been touched.
    - A comprehensive `.gitignore` file for Python projects has been added.
    - `requirements.txt` has been created.

- **Core Modules Implemented (Initial Versions):**
    - **`anon_framework/vpn/base_vpn.py`:** An abstract base class `BaseVPN` was defined to ensure a consistent interface for all VPN implementations.
    - **`anon_framework/vpn/nord.py`:** A basic wrapper for the `nordvpn` command-line tool has been implemented.
    - **`anon_framework/vpn/mullvad.py`:** A basic wrapper for the `mullvad` command-line tool has been implemented.
    - **`anon_framework/vpn/tor.py`:** Implemented a manager for the system Tor service, with OS-specific controls.
    - **`anon_framework/utils/helpers.py`:** Added an OS detection function (`get_os`) and a generic command execution function (`run_command`).
    - **`anon_framework/privacy/telemetry.py`:** Created the initial structure with placeholder functions to disable telemetry on Windows, Linux, and macOS.
    - **`anon_framework/services/qbittorrent.py`:** Implemented a client for the qBittorrent Web API, including search functionality.
    - **`anon_framework/services/i2p.py`:** Implemented a manager for the I2P service and added a placeholder for I2P-based torrent searching.

- **CLI Integration:**
    - **`anon_framework/main.py`:** The main entry point has been significantly updated with a robust argument parser (`argparse`) to handle sub-commands for the VPN, services, and privacy modules. The implemented modules are now executable from the command line.

## 6. Next Steps

1.  Flesh out the OS-specific logic in `privacy/telemetry.py`.
2.  Implement the `tor_browser.py` module to manage the Tor Browser lifecycle.
3.  Develop a configuration system in `config.py` to handle settings like qBittorrent credentials.
4.  Add comprehensive unit and integration tests.
