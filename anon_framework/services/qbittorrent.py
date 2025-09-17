import requests
import time

class QBittorrentClient:
    """
    A client for interacting with the qBittorrent Web API.
    """
    def __init__(self, host='localhost', port=8080, username=None, password=None):
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
        if username and password:
            self._login(username, password)

    def _login(self, username, password):
        """Logs into the qBittorrent Web UI."""
        login_url = f"{self.base_url}/api/v2/auth/login"
        try:
            response = self.session.post(login_url, data={'username': username, 'password': password})
            response.raise_for_status()
            if response.text == "Ok.":
                print("Successfully logged into qBittorrent.")
                return True
            else:
                print("Failed to log into qBittorrent: Invalid credentials.")
                return False
        except requests.RequestException as e:
            print(f"Error connecting to qBittorrent: {e}")
            return False

    def search(self, query, plugin='all', category='all'):
        """
        Starts a search job and returns the results.

        Args:
            query (str): The search term.
            plugin (str): The search plugin to use (e.g., 'enabled', 'all').
            category (str): The category to search in.

        Returns:
            list: A list of dictionaries, where each dictionary is a search result.
        """
        search_url = f"{self.base_url}/api/v2/search/start"
        try:
            # Start the search job
            response = self.session.post(search_url, data={'pattern': query, 'plugins': plugin, 'category': category})
            response.raise_for_status()
            job = response.json()
            job_id = job.get('id')
            if job_id is None:
                print("Failed to start search job.")
                return []

            print(f"Search job started with ID: {job_id}")

            # Poll for results
            results_url = f"{self.base_url}/api/v2/search/results"
            while True:
                time.sleep(1)
                status_response = self.session.get(f"{self.base_url}/api/v2/search/status", params={'id': job_id})
                status_response.raise_for_status()
                status = status_response.json()[0]

                if status['status'] == 'Running':
                    continue
                
                if status['status'] == 'Stopped':
                    results_response = self.session.get(results_url, params={'id': job_id, 'limit': 50}) # Limit to 50 results
                    results_response.raise_for_status()
                    results = results_response.json()
                    print(f"Found {results.get('total')} results.")
                    
                    # Stop the job
                    self.session.post(f"{self.base_url}/api/v2/search/delete", data={'id': job_id})
                    return results.get('results', [])
        
        except requests.RequestException as e:
            print(f"An error occurred during search: {e}")
            return []
