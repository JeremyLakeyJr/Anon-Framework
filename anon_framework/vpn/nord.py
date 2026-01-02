import subprocess
from .base_vpn import BaseVPN


class NordVPN(BaseVPN):
    """A wrapper for the NordVPN command-line tool."""

    def __init__(self):
        """Initialize NordVPN client."""
        super().__init__()

    def connect(self) -> bool:
        """
        Connects to NordVPN.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["nordvpn", "connect"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            self._is_connected = True
            self._last_error = None
            print("NordVPN connected successfully.")
            return True
        except subprocess.TimeoutExpired:
            error = "Connection timeout: NordVPN took too long to connect"
            self._set_error(error)
            print(f"Error: {error}")
            return False
        except subprocess.CalledProcessError as e:
            error = f"NordVPN command failed: {e.stderr if e.stderr else str(e)}"
            self._set_error(error)
            print(f"Error connecting to NordVPN: {error}")
            return False
        except FileNotFoundError:
            error = "NordVPN CLI not found. Please install it first."
            self._set_error(error)
            print(f"Error: {error}")
            return False
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            self._set_error(error)
            print(f"Error connecting to NordVPN: {error}")
            return False

    def disconnect(self) -> bool:
        """
        Disconnects from NordVPN.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["nordvpn", "disconnect"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            self._is_connected = False
            self._last_error = None
            print("NordVPN disconnected successfully.")
            return True
        except subprocess.TimeoutExpired:
            error = "Disconnection timeout: NordVPN took too long to disconnect"
            self._set_error(error)
            print(f"Error: {error}")
            return False
        except subprocess.CalledProcessError as e:
            error = f"NordVPN command failed: {e.stderr if e.stderr else str(e)}"
            self._set_error(error)
            print(f"Error disconnecting from NordVPN: {error}")
            return False
        except FileNotFoundError:
            error = "NordVPN CLI not found."
            self._set_error(error)
            print(f"Error: {error}")
            return False
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            self._set_error(error)
            print(f"Error disconnecting from NordVPN: {error}")
            return False

    def get_status(self) -> str:
        """
        Gets the connection status of NordVPN.
        
        Returns:
            str: Connection status message
        """
        try:
            result = subprocess.run(
                ["nordvpn", "status"],
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
            return "Status unavailable: NordVPN CLI not found"
        except Exception as e:
            return f"Status unavailable: {str(e)}"

