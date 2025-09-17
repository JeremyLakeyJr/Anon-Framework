import sys
import subprocess

def get_os():
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

def run_command(command):
    """
    Runs a shell command and returns its output.

    Args:
        command (list): The command to execute as a list of strings.

    Returns:
        tuple: A tuple containing (stdout, stderr, returncode).
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False  # Set to False to handle non-zero exit codes manually
        )
        return (result.stdout.strip(), result.stderr.strip(), result.returncode)
    except FileNotFoundError as e:
        return (None, f"Command not found: {e}", 1)
    except Exception as e:
        return (None, f"An unexpected error occurred: {e}", 1)