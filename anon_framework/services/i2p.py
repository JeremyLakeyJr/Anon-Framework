from anon_framework.utils.helpers import run_command, get_os
import psutil
from typing import List, Dict, Any


class I2PService:
    """
    Manages the I2P router service.
    """

    def __init__(self):
        """Initialize I2P service manager."""
        self._last_error = None

    def _get_service_name(self) -> str:
        """
        Gets the service name for I2P based on the OS.
        
        Returns:
            str: Service name for I2P
            
        Raises:
            NotImplementedError: If OS is not supported
        """
        os_type = get_os()
        if os_type == 'linux':
            # Assumes a systemd service is set up
            return 'i2p'
        else:
            raise NotImplementedError(f"I2P service management not supported on {os_type}")

    def _is_process_running(self) -> bool:
        """
        Check if the i2prouter process is running.
        
        Returns:
            bool: True if I2P is running, False otherwise
        """
        try:
            for proc in psutil.process_iter(['name', 'cmdline']):
                # Check for 'i2prouter' in name or if 'i2prouter' is in the command line
                proc_name = proc.info.get('name', '').lower()
                cmdline = proc.info.get('cmdline', [])
                
                if 'i2prouter' in proc_name:
                    return True
                    
                if 'java' in proc_name and cmdline:
                    if any('i2prouter' in str(arg).lower() for arg in cmdline):
                        return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        return False

    def start(self) -> bool:
        """
        Starts the I2P service.
        
        Returns:
            bool: True if service started successfully, False otherwise
        """
        os_type = get_os()
        print(f"Attempting to start I2P service on {os_type}...")
        
        try:
            if os_type == 'linux':
                stdout, stderr, code = run_command(
                    ['sudo', 'systemctl', 'start', self._get_service_name()],
                    timeout=30
                )
                if code == 0:
                    print("I2P service started successfully.")
                    self._last_error = None
                    return True
                else:
                    error = f"Error starting I2P service: {stderr}"
                    self._last_error = error
                    print(error)
                    return False
            else:
                error = f"Unsupported OS: {os_type}"
                self._last_error = error
                print(error)
                return False
        except NotImplementedError as e:
            self._last_error = str(e)
            print(str(e))
            return False
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            self._last_error = error
            print(error)
            return False

    def stop(self) -> bool:
        """
        Stops the I2P service.
        
        Returns:
            bool: True if service stopped successfully, False otherwise
        """
        os_type = get_os()
        print(f"Attempting to stop I2P service on {os_type}...")
        
        try:
            if os_type == 'linux':
                stdout, stderr, code = run_command(
                    ['sudo', 'systemctl', 'stop', self._get_service_name()],
                    timeout=30
                )
                if code == 0:
                    print("I2P service stopped successfully.")
                    self._last_error = None
                    return True
                else:
                    error = f"Error stopping I2P service: {stderr}"
                    self._last_error = error
                    print(error)
                    return False
            else:
                error = f"Unsupported OS: {os_type}"
                self._last_error = error
                print(error)
                return False
        except NotImplementedError as e:
            self._last_error = str(e)
            print(str(e))
            return False
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            self._last_error = error
            print(error)
            return False

    def get_status(self) -> str:
        """
        Checks if the I2P router process is running.
        
        Returns:
            str: Status message
        """
        if self._is_process_running():
            return "Status: Connected (I2P process is running)"
        else:
            return "Status: Disconnected (I2P process is not running)"

    def get_last_error(self) -> str:
        """
        Get the last error message.
        
        Returns:
            str: Last error message or empty string
        """
        return self._last_error or ""

    def search_torrents(self, query: str) -> List[Dict[str, Any]]:
        """
        Searches for torrents on the I2P network.

        Args:
            query: Search query string

        Returns:
            List of search results (currently a placeholder)
            
        Note:
            This is a placeholder for a more complex implementation.
            A real implementation would need to:
            1. Know the addresses of I2P torrent search eepsites
            2. Make HTTP requests through the I2P proxy (localhost:4444)
            3. Parse HTML responses to extract magnet links
        """
        if not query or not query.strip():
            print("Error: Search query cannot be empty.")
            return []
        
        print(f"Searching I2P torrent trackers for: '{query}' (placeholder)...")
        
        # Example implementation outline:
        # proxies = {'http': 'http://127.0.0.1:4444', 'https': 'http://127.0.0.1:4444'}
        # response = requests.get("http://<i2p-tracker-address>/search", 
        #                        params={'q': query}, proxies=proxies)
        # ... parse response ...
        
        print("Note: I2P torrent search is not yet fully implemented.")
        return []

