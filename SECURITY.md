# Security Policy

## Supported Versions

Currently, we are in early development. Security updates will be applied to the latest version.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Disclose Publicly

Please do **not** open a public GitHub issue for security vulnerabilities. This could put users at risk.

### 2. Report Privately

Send details about the vulnerability to the project maintainers via:
- GitHub Security Advisories (preferred)
- Direct message to project maintainers

### 3. Include Details

When reporting, please include:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if you have one)
- Your contact information for follow-up

### 4. Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix Timeline**: Depends on severity
  - Critical: Within 1 week
  - High: Within 2 weeks
  - Medium: Within 1 month
  - Low: Next release cycle

## Security Best Practices for Users

### Credential Management
- **Never commit credentials** to version control
- Use the `config.yaml` file (which is gitignored) for storing credentials
- Consider using environment variables for sensitive data
- Rotate credentials regularly

### VPN Usage
- **Test for leaks**: Always test for DNS and IP leaks after connecting to a VPN
- **Kill switch**: Consider using a VPN with a kill switch feature
- **Split tunneling**: Be aware of which applications use the VPN connection

### Tor Configuration
- **Check circuit**: Verify your Tor circuit is working correctly
- **Tor Browser**: For web browsing, use Tor Browser instead of regular browsers with Tor
- **Exit node country**: Be aware of which country your Tor exit node is in

### System Modifications
- **Backup first**: Always backup important data before running system modification scripts
- **Review code**: Review telemetry disabling scripts before running them
- **Understand changes**: Make sure you understand what system changes are being made
- **Root access**: Be cautious when granting root/sudo access

### Network Security
- **HTTPS**: Always use HTTPS when possible
- **Certificate validation**: Don't disable certificate validation in production
- **Proxy configuration**: Verify proxy settings are correct
- **Port security**: Don't expose unnecessary ports

### Application Security
- **Keep updated**: Keep Anon-Framework and all dependencies updated
- **Minimal permissions**: Run with minimal required permissions
- **Separate environments**: Consider using virtual machines or containers for testing
- **Log security**: Be aware that logs may contain sensitive information

## Known Security Considerations

### 1. Root/Sudo Access
Many features (VPN management, service control, telemetry disabling) require elevated privileges. Users should:
- Review code before running with sudo
- Consider using dedicated user accounts
- Audit system changes after running privileged operations

### 2. Credential Storage
Currently, credentials can be stored in `config.yaml`. Future improvements:
- Integration with system keychains
- Encrypted credential storage
- Support for credential managers

### 3. Logging
Application logs may contain:
- IP addresses
- Timestamps
- Command history
- Error messages with system information

Users should secure log files and consider disabling logging for sensitive operations.

### 4. Network Metadata
Even with VPNs and Tor:
- Network metadata (timing, size) can leak information
- DNS queries may occur before VPN connects
- Some applications may bypass VPN/Tor

### 5. System Fingerprinting
- System modifications for privacy may create unique fingerprints
- Balance privacy improvements with anonymity requirements

## Dependencies

We regularly audit our dependencies for security issues. Users can check for vulnerabilities:

```bash
pip install safety
safety check -r requirements.txt
```

## Security Features Roadmap

- [ ] Encrypted configuration file support
- [ ] Integration with system keychains
- [ ] DNS leak protection
- [ ] VPN kill switch support
- [ ] Automatic security updates
- [ ] Security audit logging
- [ ] Two-factor authentication support
- [ ] Digital signature verification

## Acknowledgments

We appreciate security researchers and users who report vulnerabilities responsibly. Contributors to security improvements will be acknowledged (with permission) in our release notes.

## Questions?

If you have questions about security but haven't found a vulnerability, you can:
- Open a general discussion on GitHub
- Check our documentation
- Review existing security issues

Thank you for helping keep Anon-Framework secure!
