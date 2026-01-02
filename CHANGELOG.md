# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-02

### Added
- Comprehensive README.md with detailed documentation, installation instructions, and usage examples
- CONTRIBUTING.md with contribution guidelines and code standards
- SECURITY.md with security best practices and vulnerability reporting procedures
- QUICKSTART.md for quick setup and basic usage
- Configuration system with YAML support (configuration.py)
- Example configuration file (config.example.yaml)
- Logging framework throughout the application
- Type hints across all modules for better code maintainability
- .editorconfig for consistent code style across editors
- Input validation for security-critical inputs
- Error tracking in all service and VPN modules
- Timeouts for all network and system operations
- Better status reporting for VPN connections

### Changed
- Updated requirements.txt with version constraints for all dependencies
- Enhanced setup.py with proper metadata and dependency management
- Improved all VPN modules (NordVPN, Mullvad, Tor) with better error handling
- Enhanced qBittorrent client with timeout support and better error messages
- Improved I2P service with comprehensive error tracking
- Refactored main CLI with config integration and logging
- Updated BaseVPN with connection state management and error tracking
- Optimized helper functions with better performance and security

### Fixed
- Path traversal vulnerability in configuration saving
- Bare except clause that could catch system exceptions
- Regex compilation performance issue in input validation
- Package structure conflict between config module and directory
- Missing dependencies in requirements.txt

### Security
- Added input validation to prevent injection attacks
- Implemented proper error handling to avoid information leakage
- Added comprehensive security documentation
- Fixed potential path traversal in config file handling

### Removed
- Duplicate main.py file from root directory
- Placeholder implementations without proper error handling

## [0.1.0] - Initial Release

### Added
- Basic VPN management (NordVPN, Mullvad, Tor)
- I2P service management
- qBittorrent API client
- IRC client with Tor support
- OS telemetry disabling (placeholder)
- Basic CLI interface
- MIT License

[0.2.0]: https://github.com/JeremyLakeyJr/Anon-Framework/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/JeremyLakeyJr/Anon-Framework/releases/tag/v0.1.0
