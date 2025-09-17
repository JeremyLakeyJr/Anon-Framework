import subprocess
from .base_vpn import BaseVPN

class MullvadVPN(BaseVPN):
    """A wrapper for the Mullvad VPN command-line tool."""

    def connect(self):
        """Connects to Mullvad VPN."""
        try:
            subprocess.run(["mullvad", "connect"], check=True)
            print("Mullvad VPN connected successfully.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error connecting to Mullvad VPN: {e}")
            return False

    def disconnect(self):
        """Disconnects from Mullvad VPN."""
        try:
            subprocess.run(["mullvad", "disconnect"], check=True)
            print("Mullvad VPN disconnected successfully.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error disconnecting from Mullvad VPN: {e}")
            return False

    def get_status(self):
        """Gets the connection status of Mullvad VPN."""
        try:
            result = subprocess.run(
                ["mullvad", "status"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error getting Mullvad VPN status: {e}")
            return "Status unavailable"
