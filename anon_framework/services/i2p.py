from anon_framework.utils.helpers import run_command, get_os
import psutil

class I2PService:
    """
    Manages the I2P router service.
    """

    def _get_service_name(self):
        """Gets the service name for I2P based on the OS."""
        os_type = get_os()
        if os_type == 'linux':
            # Assumes a systemd service is set up
            return 'i2p'
        # Add other OS-specific service names here
        else:
            raise NotImplementedError(f"I2P service management not supported on {os_type}")

    def _is_process_running(self):
        """Check if the i2prouter process is running."""
        for proc in psutil.process_iter(['name', 'cmdline']):
            # Check for 'i2prouter' in name or if 'i2prouter' is in the command line
            if 'i2prouter' in proc.info['name'] or ('java' in proc.info['name'] and any('i2prouter' in s for s in proc.info['cmdline'])):
                return True
        return False

    def start(self):
        """Starts the I2P service."""
        os_type = get_os()
        print(f"Attempting to start I2P service on {os_type}...")
        if os_type == 'linux':
            stdout, stderr, code = run_command(['sudo', 'systemctl', 'start', self._get_service_name()])
            if code == 0:
                print("I2P service started successfully.")
                return True
            else:
                print(f"Error starting I2P service:\n{stderr}")
                return False
        else:
            print(f"Unsupported OS: {os_type}")
            return False

    def stop(self):
        """Stops the I2P service."""
        os_type = get_os()
        print(f"Attempting to stop I2P service on {os_type}...")
        if os_type == 'linux':
            stdout, stderr, code = run_command(['sudo', 'systemctl', 'stop', self._get_service_name()])
            if code == 0:
                print("I2P service stopped successfully.")
                return True
            else:
                print(f"Error stopping I2P service:\n{stderr}")
                return False
        else:
            print(f"Unsupported OS: {os_type}")
            return False

    def get_status(self):
        """Checks if the I2P router process is running."""
        if self._is_process_running():
            return "Status: Connected (I2P process is running)"
        else:
            return "Status: Disconnected (I2P process is not running)"

    def search_torrents(self, query):
        """
        Searches for torrents on the I2P network.

        (This is a placeholder for a more complex implementation)
        """
        print(f"Searching I2P torrent trackers for: '{query}' (placeholder)...")
        #
        # **Implementation Notes:**
        # This is a non-trivial task. It would likely involve:
        # 1. Knowing the addresses of one or more I2P torrent search eepsites (e.g., Postman's tracker).
        # 2. Making an HTTP request through the local I2P proxy (e.g., localhost:4444).
        # 3. The `requests` library can be configured to use this proxy.
        # 4. Scraping the HTML response from the eepsite to extract magnet links and other info.
        #
        # Example:
        # proxies = {'http': 'http://127.0.0.1:4444', 'https': 'http://127.0.0.1:4444'}
        # response = requests.get("http://<i2p-tracker-address>/search", params={'q': query}, proxies=proxies)
        # ... parse response ...
        #
        return []
