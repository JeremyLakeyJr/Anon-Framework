# Anon-Framework

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-blue.svg)

A comprehensive cross-platform framework for enhancing user anonymity and privacy. Anon-Framework provides unified tools to manage VPNs, handle privacy-focused services, reduce OS-level telemetry, and enable secure communication channels.

## Features

### 🔒 VPN Management
- **Multi-Provider Support**: Seamlessly manage NordVPN, Mullvad, and Tor VPN connections
- **Unified Interface**: Common API across different VPN providers
- **Status Monitoring**: Real-time connection status and health checks

### 🛡️ Privacy Enhancement
- **OS Telemetry Disabling**: Reduce data collection on Windows, macOS, and Linux
- **Tor Integration**: Built-in Tor service management for anonymous browsing
- **Privacy-First Design**: All features designed with privacy as a core principle

### 🌐 Service Integration
- **I2P Support**: Manage I2P router service for darknet access
- **qBittorrent API**: Search and manage torrents through the qBittorrent web interface
- **IRC Client**: Anonymous IRC communication with Tor support

### 💬 Secure Communication
- **IRC Client**: Modern async IRC client with TLS and Tor proxy support
- **Channel Management**: Join, leave, search, and manage IRC channels
- **Identity Protection**: Nickname management and identity switching

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package installer)

### From Source

```bash
# Clone the repository
git clone https://github.com/JeremyLakeyJr/Anon-Framework.git
cd Anon-Framework

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Dependencies
The framework requires the following Python packages:
- `pysocks` - SOCKS proxy support
- `pydle` - Modern IRC library
- `psutil` - Process and system utilities
- `requests` - HTTP library
- `pyyaml` - YAML configuration parser

## Usage

Anon-Framework provides a command-line interface with multiple sub-commands:

### VPN Management

```bash
# Connect to a VPN
anon-framework vpn nord connect
anon-framework vpn mullvad connect
anon-framework vpn tor connect

# Check VPN status
anon-framework vpn nord status

# Disconnect from VPN
anon-framework vpn nord disconnect
```

### Privacy Settings

```bash
# Disable OS-level telemetry
anon-framework privacy disable-telemetry

# Manage Tor service
anon-framework privacy start-tor
anon-framework privacy stop-tor
```

### Services

```bash
# Search torrents via qBittorrent
anon-framework services qbittorrent search "Ubuntu ISO"

# Manage I2P service
anon-framework services i2p start
anon-framework services i2p status
anon-framework services i2p stop
```

### Secure Communication

```bash
# Connect to IRC (without Tor)
anon-framework communicate irc --nickname YourNick --channel "#your-channel"

# Connect to IRC through Tor
anon-framework communicate irc --nickname AnonUser --channel "#privacy" --tor
```

## Configuration

### VPN Prerequisites

**NordVPN**: Install the [NordVPN CLI tool](https://nordvpn.com/download/linux/)
```bash
sudo apt install nordvpn  # Debian/Ubuntu
```

**Mullvad**: Install the [Mullvad CLI](https://mullvad.net/en/download/)
```bash
# Follow instructions on Mullvad's website
```

**Tor**: Install Tor service
```bash
sudo apt install tor  # Debian/Ubuntu
brew install tor      # macOS
```

### qBittorrent Setup

1. Install qBittorrent and enable the Web UI
2. Configure credentials in your application

### I2P Setup

1. Install I2P router from [geti2p.net](https://geti2p.net)
2. Configure as a system service (Linux)

## Architecture

```
anon_framework/
├── vpn/              # VPN provider implementations
│   ├── base_vpn.py   # Abstract base class
│   ├── nord.py       # NordVPN wrapper
│   ├── mullvad.py    # Mullvad wrapper
│   └── tor.py        # Tor service manager
├── privacy/          # Privacy enhancement tools
│   └── telemetry.py  # OS telemetry disabling
├── services/         # Service integrations
│   ├── i2p.py        # I2P router management
│   ├── qbittorrent.py # qBittorrent API client
│   └── communication/ # Communication clients
│       ├── irc.py    # IRC client
│       └── menu.py   # Interactive menu system
└── utils/            # Utility functions
    └── helpers.py    # Helper functions
```

## Security Considerations

- **Root Privileges**: Some operations (VPN management, service control) may require sudo/administrator privileges
- **Credentials**: Store credentials securely, never commit them to version control
- **Tor Configuration**: Ensure Tor is properly configured before using Tor-dependent features
- **VPN Leaks**: Test for DNS/IP leaks after connecting to VPNs
- **Logging**: Be aware of system and application logs that may contain sensitive information

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/JeremyLakeyJr/Anon-Framework.git
cd Anon-Framework

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This framework is provided for educational and legitimate privacy purposes only. Users are responsible for complying with all applicable laws and regulations in their jurisdiction. The authors and contributors are not responsible for any misuse of this software.

## Acknowledgments

- Built with Python 3
- Uses [pydle](https://github.com/Shizmob/pydle) for IRC functionality
- Inspired by the need for better privacy tools

## Support

If you encounter any issues or have questions:
- Open an issue on [GitHub](https://github.com/JeremyLakeyJr/Anon-Framework/issues)
- Check existing documentation
- Review the code examples

## Roadmap

- [ ] Add more VPN providers (ProtonVPN, ExpressVPN)
- [ ] Implement configuration file support
- [ ] Add GUI interface
- [ ] Expand telemetry disabling features
- [ ] Add more communication protocols (Matrix, XMPP)
- [ ] Implement automated testing
- [ ] Add Docker support
- [ ] Create detailed documentation site
