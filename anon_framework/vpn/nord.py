import subprocess
from .base_vpn import BaseVPN

class NordVPN(BaseVPN):
    """A wrapper for the NordVPN command-line tool."""

    def connect(self):
        """Connects to NordVPN."""
        try:
            subprocess.run(["nordvpn", "connect"], check=True)
            print("NordVPN connected successfully.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error connecting to NordVPN: {e}")
            return False

    def disconnect(self):
        """Disconnects from NordVPN."""
        try:
            subprocess.run(["nordvpn", "disconnect"], check=True)
            print("NordVPN disconnected successfully.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error disconnecting from NordVPN: {e}")
            return False

    def get_status(self):
        """Gets the connection status of NordVPN."""
        try:
            result = subprocess.run(
                ["nordvpn", "status"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error getting NordVPN status: {e}")
            return "Status unavailable"
