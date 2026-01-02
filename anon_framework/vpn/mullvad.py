import subprocess
from .base_vpn import BaseVPN


class MullvadVPN(BaseVPN):
    """A wrapper for the Mullvad VPN command-line tool."""

    def __init__(self):
        """Initialize Mullvad VPN client."""
        super().__init__()

    def connect(self) -> bool:
        """
        Connects to Mullvad VPN.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["mullvad", "connect"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            self._is_connected = True
            self._last_error = None
            print("Mullvad VPN connected successfully.")
            return True
        except subprocess.TimeoutExpired:
            error = "Connection timeout: Mullvad VPN took too long to connect"
            self._set_error(error)
            print(f"Error: {error}")
            return False
        except subprocess.CalledProcessError as e:
            error = f"Mullvad command failed: {e.stderr if e.stderr else str(e)}"
            self._set_error(error)
            print(f"Error connecting to Mullvad VPN: {error}")
            return False
        except FileNotFoundError:
            error = "Mullvad CLI not found. Please install it first."
            self._set_error(error)
            print(f"Error: {error}")
            return False
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            self._set_error(error)
            print(f"Error connecting to Mullvad VPN: {error}")
            return False

    def disconnect(self) -> bool:
        """
        Disconnects from Mullvad VPN.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["mullvad", "disconnect"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            self._is_connected = False
            self._last_error = None
            print("Mullvad VPN disconnected successfully.")
            return True
        except subprocess.TimeoutExpired:
            error = "Disconnection timeout: Mullvad VPN took too long to disconnect"
            self._set_error(error)
            print(f"Error: {error}")
            return False
        except subprocess.CalledProcessError as e:
            error = f"Mullvad command failed: {e.stderr if e.stderr else str(e)}"
            self._set_error(error)
            print(f"Error disconnecting from Mullvad VPN: {error}")
            return False
        except FileNotFoundError:
            error = "Mullvad CLI not found."
            self._set_error(error)
            print(f"Error: {error}")
            return False
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            self._set_error(error)
            print(f"Error disconnecting from Mullvad VPN: {error}")
            return False

    def get_status(self) -> str:
        """
        Gets the connection status of Mullvad VPN.
        
        Returns:
            str: Connection status message
        """
        try:
            result = subprocess.run(
                ["mullvad", "status"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            # Update connected status based on output
            status_text = result.stdout.strip()
            self._is_connected = "Connected" in status_text
            return status_text
        except subprocess.TimeoutExpired:
            return "Status check timeout"
        except subprocess.CalledProcessError as e:
            return f"Status unavailable: {e.stderr if e.stderr else 'Command failed'}"
        except FileNotFoundError:
            return "Status unavailable: Mullvad CLI not found"
        except Exception as e:
            return f"Status unavailable: {str(e)}"

