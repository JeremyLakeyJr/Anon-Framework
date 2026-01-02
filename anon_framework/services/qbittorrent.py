import requests
import time
from typing import List, Dict, Any, Optional


class QBittorrentClient:
    """
    A client for interacting with the qBittorrent Web API.
    """
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8080,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize qBittorrent client.
        
        Args:
            host: qBittorrent web UI host
            port: qBittorrent web UI port
            username: Authentication username (optional)
            password: Authentication password (optional)
            timeout: Request timeout in seconds
        """
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
        self.timeout = timeout
        self._authenticated = False
        
        if username and password:
            self._authenticated = self._login(username, password)

    def _login(self, username: str, password: str) -> bool:
        """
        Logs into the qBittorrent Web UI.
        
        Args:
            username: Login username
            password: Login password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        login_url = f"{self.base_url}/api/v2/auth/login"
        try:
            response = self.session.post(
                login_url,
                data={'username': username, 'password': password},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            if response.text == "Ok.":
                print("Successfully logged into qBittorrent.")
                return True
            else:
                print("Failed to log into qBittorrent: Invalid credentials.")
                return False
        except requests.Timeout:
            print("Error: Connection to qBittorrent timed out.")
            return False
        except requests.ConnectionError:
            print("Error: Could not connect to qBittorrent. Is it running?")
            return False
        except requests.RequestException as e:
            print(f"Error connecting to qBittorrent: {e}")
            return False

    def is_authenticated(self) -> bool:
        """
        Check if client is authenticated.
        
        Returns:
            bool: True if authenticated
        """
        return self._authenticated

    def search(
        self,
        query: str,
        plugin: str = 'all',
        category: str = 'all',
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Starts a search job and returns the results.

        Args:
            query: The search term.
            plugin: The search plugin to use (e.g., 'enabled', 'all').
            category: The category to search in.
            max_results: Maximum number of results to return.

        Returns:
            list: A list of dictionaries, where each dictionary is a search result.
        """
        if not query or not query.strip():
            print("Error: Search query cannot be empty.")
            return []
        
        search_url = f"{self.base_url}/api/v2/search/start"
        try:
            # Start the search job
            response = self.session.post(
                search_url,
                data={'pattern': query, 'plugins': plugin, 'category': category},
                timeout=self.timeout
            )
            response.raise_for_status()
            job = response.json()
            job_id = job.get('id')
            
            if job_id is None:
                print("Failed to start search job.")
                return []

            print(f"Search job started with ID: {job_id}")

            # Poll for results with timeout
            results_url = f"{self.base_url}/api/v2/search/results"
            max_wait = 60  # Maximum 60 seconds
            elapsed = 0
            
            while elapsed < max_wait:
                time.sleep(1)
                elapsed += 1
                
                try:
                    status_response = self.session.get(
                        f"{self.base_url}/api/v2/search/status",
                        params={'id': job_id},
                        timeout=self.timeout
                    )
                    status_response.raise_for_status()
                    status_list = status_response.json()
                    
                    if not status_list:
                        print("Search job not found.")
                        return []
                    
                    status = status_list[0]

                    if status['status'] == 'Running':
                        continue
                    
                    if status['status'] == 'Stopped':
                        results_response = self.session.get(
                            results_url,
                            params={'id': job_id, 'limit': max_results},
                            timeout=self.timeout
                        )
                        results_response.raise_for_status()
                        results = results_response.json()
                        
                        total = results.get('total', 0)
                        result_list = results.get('results', [])
                        
                        print(f"Found {total} results (showing {len(result_list)}).")
                        
                        # Stop the job
                        try:
                            self.session.post(
                                f"{self.base_url}/api/v2/search/delete",
                                data={'id': job_id},
                                timeout=self.timeout
                            )
                        except Exception:
                            pass  # Ignore cleanup errors
                        
                        return result_list
                except requests.RequestException as e:
                    print(f"Error checking search status: {e}")
                    break
            
            print("Search timed out.")
            return []
        
        except requests.Timeout:
            print("Error: Request timed out.")
            return []
        except requests.ConnectionError:
            print("Error: Could not connect to qBittorrent.")
            return []
        except requests.RequestException as e:
            print(f"An error occurred during search: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

