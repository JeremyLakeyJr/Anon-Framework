from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseVPN(ABC):
    """Abstract base class for a VPN implementation."""

    def __init__(self):
        """Initialize the VPN client."""
        self._is_connected = False
        self._last_error: Optional[str] = None

    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the VPN service.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the VPN service.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        pass

    @abstractmethod
    def get_status(self) -> str:
        """
        Get the current connection status.
        
        Returns:
            str: Human-readable status message
        """
        pass

    def is_connected(self) -> bool:
        """
        Check if currently connected to VPN.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._is_connected

    def get_last_error(self) -> Optional[str]:
        """
        Get the last error message.
        
        Returns:
            Optional[str]: Last error message or None
        """
        return self._last_error

    def _set_error(self, error: str) -> None:
        """
        Set the last error message.
        
        Args:
            error: Error message to store
        """
        self._last_error = error

    def get_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the VPN connection.
        
        Returns:
            Dict containing connection information
        """
        return {
            'connected': self.is_connected(),
            'status': self.get_status(),
            'last_error': self.get_last_error(),
        }

