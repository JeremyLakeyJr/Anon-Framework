from abc import ABC, abstractmethod

class BaseVPN(ABC):
    """Abstract base class for a VPN implementation."""

    @abstractmethod
    def connect(self):
        """Connect to the VPN service."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the VPN service."""
        pass

    @abstractmethod
    def get_status(self):
        """Get the current connection status."""
        pass
