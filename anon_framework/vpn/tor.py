from .base_vpn import BaseVPN
from anon_framework.utils.helpers import run_command, get_os
import psutil


class TorVPN(BaseVPN):
    """
    Manages the Tor service as a VPN layer.

    Note: This assumes Tor is installed as a system service.
    """

    def __init__(self):
        """Initialize Tor VPN client."""
        super().__init__()

    def _get_service_name(self) -> str:
        """
        Gets the service name for Tor based on the OS.
        
        Returns:
            str: Service name for Tor
            
        Raises:
            NotImplementedError: If OS is not supported
        """
        os_type = get_os()
        if os_type in ('linux', 'darwin', 'windows'):
            return 'tor'
        else:
            raise NotImplementedError(f"Tor service management not supported on {os_type}")

    def _is_process_running(self) -> bool:
        """
        Check if the tor process is running.
        
        Returns:
            bool: True if Tor process is running, False otherwise
        """
        try:
            for proc in psutil.process_iter(['name']):
                if 'tor' in proc.info['name'].lower():
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return False

    def connect(self) -> bool:
        """
        Starts the Tor system service.
        
        Returns:
            bool: True if service started successfully, False otherwise
        """
        os_type = get_os()
        service = self._get_service_name()
        
        print(f"Attempting to start Tor service on {os_type}...")
        
        try:
            if os_type == 'linux':
                stdout, stderr, code = run_command(['sudo', 'systemctl', 'start', service], timeout=30)
            elif os_type == 'darwin':
                stdout, stderr, code = run_command(['brew', 'services', 'start', service], timeout=30)
            elif os_type == 'windows':
                stdout, stderr, code = run_command(['net', 'start', service], timeout=30)
            else:
                error = f"Unsupported OS: {os_type}"
                self._set_error(error)
                print(error)
                return False

            if code == 0:
                self._is_connected = True
                self._last_error = None
                print("Tor service started successfully.")
                return True
            else:
                error = f"Failed to start Tor service: {stderr}"
                self._set_error(error)
                print(f"Error starting Tor service:\n{stderr}")
                return False
        except Exception as e:
            error = f"Unexpected error starting Tor: {str(e)}"
            self._set_error(error)
            print(error)
            return False

    def disconnect(self) -> bool:
        """
        Stops the Tor system service.
        
        Returns:
            bool: True if service stopped successfully, False otherwise
        """
        os_type = get_os()
        service = self._get_service_name()

        print(f"Attempting to stop Tor service on {os_type}...")
        
        try:
            if os_type == 'linux':
                stdout, stderr, code = run_command(['sudo', 'systemctl', 'stop', service], timeout=30)
            elif os_type == 'darwin':
                stdout, stderr, code = run_command(['brew', 'services', 'stop', service], timeout=30)
            elif os_type == 'windows':
                stdout, stderr, code = run_command(['net', 'stop', service], timeout=30)
            else:
                error = f"Unsupported OS: {os_type}"
                self._set_error(error)
                print(error)
                return False

            if code == 0:
                self._is_connected = False
                self._last_error = None
                print("Tor service stopped successfully.")
                return True
            else:
                error = f"Failed to stop Tor service: {stderr}"
                self._set_error(error)
                print(f"Error stopping Tor service:\n{stderr}")
                return False
        except Exception as e:
            error = f"Unexpected error stopping Tor: {str(e)}"
            self._set_error(error)
            print(error)
            return False

    def get_status(self) -> str:
        """
        Checks if the Tor process is running.
        
        Returns:
            str: Status message
        """
        is_running = self._is_process_running()
        self._is_connected = is_running
        
        if is_running:
            return "Status: Connected (Tor process is running)"
        else:
            return "Status: Disconnected (Tor process is not running)"


