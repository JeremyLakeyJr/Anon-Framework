# Contributing to Anon-Framework

Thank you for your interest in contributing to Anon-Framework! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates.

**When reporting a bug, include:**
- Clear and descriptive title
- Steps to reproduce the behavior
- Expected behavior vs. actual behavior
- Your environment (OS, Python version, etc.)
- Any relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:
- Clear description of the proposed feature
- Use cases and benefits
- Any implementation ideas you have

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Commit your changes** with clear, descriptive messages
6. **Push to your fork** and submit a pull request

## Development Guidelines

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Anon-Framework.git
cd Anon-Framework

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Coding Standards

- **Python Version**: Target Python 3.6+
- **Style Guide**: Follow PEP 8 guidelines
- **Docstrings**: Use clear docstrings for all public functions and classes
- **Type Hints**: Add type hints where appropriate
- **Error Handling**: Always handle exceptions appropriately
- **Comments**: Write clear comments for complex logic

### Code Style Example

```python
def example_function(param: str) -> bool:
    """
    Brief description of what the function does.
    
    Args:
        param: Description of the parameter.
        
    Returns:
        Description of the return value.
        
    Raises:
        ValueError: When invalid input is provided.
    """
    if not param:
        raise ValueError("Parameter cannot be empty")
    
    # Implementation here
    return True
```

### Commit Message Guidelines

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests when relevant

**Examples:**
```
Add support for ProtonVPN
Fix Tor connection timeout issue
Update README with installation instructions
Refactor VPN base class for better extensibility
```

### Testing

While we're building out our test suite, please:
- Manually test your changes thoroughly
- Test on different operating systems if possible
- Verify your changes don't break existing functionality
- Document any new test procedures

## Module-Specific Guidelines

### VPN Modules
- Implement the `BaseVPN` abstract class
- Handle connection failures gracefully
- Provide clear status messages
- Test with actual VPN services when possible

### Privacy Modules
- Be extremely careful with system modifications
- Provide rollback mechanisms where possible
- Document all system changes clearly
- Test on fresh systems when possible

### Service Integrations
- Handle API errors gracefully
- Provide clear error messages
- Document required external setup
- Test with actual services

### Communication Modules
- Prioritize security and privacy
- Handle network failures gracefully
- Support Tor proxying
- Validate all user inputs

## Security

- **Never commit credentials** or API keys
- **Report security vulnerabilities** privately before public disclosure
- **Follow secure coding practices**
- **Sanitize all user inputs**
- **Be cautious with system-level operations**

## Documentation

When contributing, please update:
- Code docstrings
- README.md (if adding features)
- This CONTRIBUTING.md (if changing processes)
- Any relevant examples or guides

## Questions?

If you have questions about contributing:
- Check existing documentation
- Look at similar implementations in the codebase
- Open an issue for clarification
- Reach out to maintainers

## Recognition

All contributors will be recognized in our project documentation. Thank you for helping make Anon-Framework better!
