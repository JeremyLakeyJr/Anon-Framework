import platform
from .base_vpn import BaseVPN
from anon_framework.utils.helpers import run_command, get_os
import psutil

class TorVPN(BaseVPN):
    """
    Manages the Tor service as a VPN layer.

    Note: This assumes Tor is installed as a system service.
    """

    def _get_service_name(self):
        """Gets the service name for Tor based on the OS."""
        os_type = get_os()
        if os_type == 'linux':
            # Common on Debian/Ubuntu
            return 'tor'
        elif os_type == 'darwin':
            # Common when installed with Homebrew
            return 'tor'
        elif os_type == 'windows':
            # Default service name for the Tor expert bundle
            return 'tor'
        else:
            raise NotImplementedError(f"Tor service management not supported on {os_type}")

    def _is_process_running(self):
        """Check if the tor process is running."""
        for proc in psutil.process_iter(['name']):
            if 'tor' in proc.info['name']:
                return True
        return False

    def connect(self):
        """Starts the Tor system service."""
        os_type = get_os()
        service = self._get_service_name()
        
        print(f"Attempting to start Tor service on {os_type}...")
        if os_type == 'linux':
            stdout, stderr, code = run_command(['sudo', 'systemctl', 'start', service])
        elif os_type == 'darwin':
            stdout, stderr, code = run_command(['brew', 'services', 'start', service])
        elif os_type == 'windows':
            stdout, stderr, code = run_command(['net', 'start', service])
        else:
            print(f"Unsupported OS: {os_type}")
            return False

        if code == 0:
            print("Tor service started successfully.")
            return True
        else:
            print(f"Error starting Tor service:\n{stderr}")
            return False

    def disconnect(self):
        """Stops the Tor system service."""
        os_type = get_os()
        service = self._get_service_name()

        print(f"Attempting to stop Tor service on {os_type}...")
        if os_type == 'linux':
            stdout, stderr, code = run_command(['sudo', 'systemctl', 'stop', service])
        elif os_type == 'darwin':
            stdout, stderr, code = run_command(['brew', 'services', 'stop', service])
        elif os_type == 'windows':
            stdout, stderr, code = run_command(['net', 'stop', service])
        else:
            print(f"Unsupported OS: {os_type}")
            return False

        if code == 0:
            print("Tor service stopped successfully.")
            return True
        else:
            print(f"Error stopping Tor service:\n{stderr}")
            return False

    def get_status(self):
        """Checks if the Tor process is running."""
        if self._is_process_running():
            return "Status: Connected (Tor process is running)"
        else:
            return "Status: Disconnected (Tor process is not running)"

