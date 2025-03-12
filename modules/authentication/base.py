"""
Authentication Base Module

Defines the abstract base class for authentication clients. All authentication
clients should implement this interface.

Classes:
    AuthClientBase: Abstract base class for authentication clients
"""

# external imports
from abc import ABC, abstractmethod
from modules.authentication.schemas import AuthenticatedUser

# Abstract base class for authentication clients
class AuthClientBase(ABC):
    """
    Abstract base class for authentication clients.
    
    Methods:
        authenticate: Authenticate a user using the provided token
    """
    @abstractmethod
    def get_user_from_api_key(self, api_key: str) -> AuthenticatedUser:
        """
        Verify API key from the database.
        """
        pass
    
    @abstractmethod
    def get_user_from_bearer_token(self, access_token: str, organization_id: str) -> AuthenticatedUser:
        """
        Verify Bearer token from the database.
        """
        pass
