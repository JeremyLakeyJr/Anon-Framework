import sys
import subprocess
import re
from typing import Tuple, List, Optional

# Compile regex pattern for input validation
_ALLOWED_CHARS_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]+$')


def get_os() -> str:
    """
    Determines the operating system.

    Returns:
        str: 'linux', 'windows', or 'darwin' (for macOS).
    """
    if sys.platform.startswith('linux'):
        return 'linux'
    elif sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'darwin'
    else:
        return sys.platform


def run_command(
    command: List[str],
    timeout: Optional[int] = 30
) -> Tuple[Optional[str], Optional[str], int]:
    """
    Runs a shell command and returns its output.

    Args:
        command: The command to execute as a list of strings.
        timeout: Command timeout in seconds. None for no timeout.

    Returns:
        tuple: A tuple containing (stdout, stderr, returncode).
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,  # Set to False to handle non-zero exit codes manually
            timeout=timeout
        )
        return (result.stdout.strip(), result.stderr.strip(), result.returncode)
    except subprocess.TimeoutExpired:
        return (None, f"Command timed out after {timeout} seconds", 1)
    except FileNotFoundError as e:
        return (None, f"Command not found: {e}", 1)
    except Exception as e:
        return (None, f"An unexpected error occurred: {e}", 1)


def validate_input(
    value: str,
    allowed_chars: Optional[str] = None,
    max_length: Optional[int] = None,
    min_length: Optional[int] = None
) -> bool:
    """
    Validate user input for security.
    
    Args:
        value: The input value to validate
        allowed_chars: String of allowed characters. If None, allows alphanumeric, dash, underscore
        max_length: Maximum allowed length
        min_length: Minimum required length
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not value:
        return False
    
    # Check length constraints
    if min_length and len(value) < min_length:
        return False
    if max_length and len(value) > max_length:
        return False
    
    # Check character constraints
    if allowed_chars is None:
        # Default: alphanumeric, dash, underscore, and dot
        if not _ALLOWED_CHARS_PATTERN.match(value):
            return False
    else:
        for char in value:
            if char not in allowed_chars:
                return False
    
    return True