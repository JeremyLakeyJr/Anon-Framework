"""Configuration management for Anon-Framework."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Configuration manager for Anon-Framework."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, searches for
                        config.yaml in standard locations.
        """
        self.config_data: Dict[str, Any] = {}
        self.config_path = config_path or self._find_config_file()
        self.load()
    
    def _find_config_file(self) -> Optional[str]:
        """
        Search for config.yaml in standard locations.
        
        Returns:
            Path to config file if found, None otherwise.
        """
        search_paths = [
            Path.cwd() / "config.yaml",
            Path.home() / ".config" / "anon-framework" / "config.yaml",
            Path(__file__).parent / "config.yaml",
        ]
        
        for path in search_paths:
            if path.exists():
                return str(path)
        
        return None
    
    def load(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path or not os.path.exists(self.config_path):
            # Use default configuration
            self.config_data = self._default_config()
            return
        
        try:
            with open(self.config_path, 'r') as f:
                self.config_data = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Failed to load config from {self.config_path}: {e}")
            self.config_data = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """
        Return default configuration.
        
        Returns:
            Dictionary with default configuration values.
        """
        return {
            'qbittorrent': {
                'host': 'localhost',
                'port': 8080,
                'username': None,
                'password': None,
            },
            'i2p': {
                'service_name': 'i2p',
                'proxy_host': '127.0.0.1',
                'proxy_port': 4444,
            },
            'tor': {
                'socks_proxy': '127.0.0.1',
                'socks_port': 9050,
                'service_name': 'tor',
            },
            'irc': {
                'default_nickname': 'anon_user',
                'default_channel': '#anon-framework',
            },
            'vpn': {
                'preferred_provider': 'tor',
                'auto_connect': False,
            },
            'privacy': {
                'auto_disable_telemetry': False,
                'prefer_tor': True,
            },
            'logging': {
                'level': 'INFO',
                'file': 'anon_framework.log',
                'console': True,
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'qbittorrent.host')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        data = self.config_data
        
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        data[keys[-1]] = value
    
    def save(self, path: Optional[str] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            path: Path to save to. If None, uses loaded config path.
        """
        save_path = path or self.config_path
        
        if not save_path:
            raise ValueError("No config path specified for saving")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'w') as f:
            yaml.safe_dump(self.config_data, f, default_flow_style=False)


# Global config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance.
    
    Returns:
        Global Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
