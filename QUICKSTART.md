# Quick Start Guide

This guide will help you get started with Anon-Framework quickly.

## Installation

### 1. Install Python 3.6+

Make sure you have Python 3.6 or higher installed:

```bash
python3 --version
```

### 2. Clone the Repository

```bash
git clone https://github.com/JeremyLakeyJr/Anon-Framework.git
cd Anon-Framework
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Configuration (Optional)

Create a configuration file for custom settings:

```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your preferred settings
```

## Basic Usage

### Check VPN Status

```bash
# Check Tor VPN status
python3 -m anon_framework.main vpn tor status

# Check NordVPN status (requires nordvpn CLI installed)
python3 -m anon_framework.main vpn nord status
```

### Manage Tor Service

```bash
# Start Tor
python3 -m anon_framework.main privacy start-tor

# Stop Tor
python3 -m anon_framework.main privacy stop-tor
```

### Search Torrents (qBittorrent)

First, make sure qBittorrent is running with Web UI enabled.

```bash
# Search for torrents
python3 -m anon_framework.main services qbittorrent search "Ubuntu ISO"
```

### IRC Communication

```bash
# Connect to IRC
python3 -m anon_framework.main communicate irc --nickname MyNick --channel "#mychannel"

# Connect via Tor
python3 -m anon_framework.main communicate irc --nickname AnonUser --channel "#privacy" --tor
```

## Prerequisites

### For VPN Features

- **NordVPN**: Install [NordVPN CLI](https://nordvpn.com/download/)
- **Mullvad**: Install [Mullvad CLI](https://mullvad.net/en/download/)
- **Tor**: Install Tor service
  ```bash
  # Debian/Ubuntu
  sudo apt install tor
  
  # macOS
  brew install tor
  ```

### For qBittorrent Features

1. Install qBittorrent
2. Enable Web UI in preferences
3. Configure credentials in `config.yaml`

### For I2P Features

1. Download and install I2P from [geti2p.net](https://geti2p.net)
2. Configure as a system service (Linux)

## Getting Help

```bash
# General help
python3 -m anon_framework.main --help

# Help for specific commands
python3 -m anon_framework.main vpn --help
python3 -m anon_framework.main services --help
python3 -m anon_framework.main privacy --help
python3 -m anon_framework.main communicate --help
```

## Common Issues

### Module Not Found Errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Permission Denied Errors

Some operations require elevated privileges:
```bash
sudo python3 -m anon_framework.main privacy start-tor
```

### VPN CLI Not Found

Make sure the VPN CLI tools are installed and in your PATH:
```bash
# Check if nordvpn is available
which nordvpn

# Check if mullvad is available
which mullvad

# Check if tor is installed
which tor
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
- Review [SECURITY.md](SECURITY.md) for security best practices
- Create a `config.yaml` from `config.example.yaml` for custom settings

## Support

If you encounter issues:
1. Check this guide and the README
2. Review existing GitHub issues
3. Open a new issue with details about your problem

## Privacy & Security Tips

1. **Always test VPN connections** for DNS/IP leaks
2. **Never commit credentials** to version control
3. **Review system changes** before running privileged operations
4. **Keep software updated** for security patches
5. **Use Tor Browser** for web browsing when using Tor

Happy anonymous computing! 🔒
