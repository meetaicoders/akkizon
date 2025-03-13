"""
Authentication Handlers Module

This module contains the AuthenticationHandler class which manages the authentication
process using the configured authentication client. It acts as an intermediary between
the authentication client and the API routes.

Classes:
    AuthenticationHandler: Manages the authentication process
"""

# external imports
from fastapi import HTTPException
from typing import Optional

# internal imports
from modules.authentication.clients import SupabaseAuthClient, OrganizationClient
from modules.authentication.schemas import  AuthenticatedUser, Organization
from core.logger import setup_logger

logger = setup_logger(__name__)

class AuthenticationHandler:
    """
    Handles authentication using both Bearer tokens and API keys.
    
    This class provides a unified interface for authentication, supporting multiple
    authentication methods and handling errors appropriately.

    Attributes:
        auth_client: The authentication client implementation

    Methods:
        authenticate: Authenticate a user using the provided token
        authenticate_without_org: Authenticate a user using the provided token without organization ID requirement
    """

    def __init__(self, auth_client: SupabaseAuthClient):
        """
        Initialize the AuthenticationHandler with an authentication client.
        
        Args:
            auth_client: Implementation of AuthClientBase to use for authentication
        """
        self.auth_client = auth_client

    def authenticate(
        self,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> AuthenticatedUser:
        """
        Authenticates the user based on the provided credentials.
        - If an API Key is provided → SDK Access
        - If a Bearer Token is provided → Dashboard Access
        
        Args:
            api_key: Optional API key for SDK access
            access_token: Optional Bearer token for dashboard access
            organization_id: Required for Bearer token authentication
            
        Returns:
            AuthenticatedUser: Contains authenticated user information
            
        Raises:
            HTTPException: If authentication fails
        """
        if api_key:
            return self.auth_client.get_user_from_api_key(api_key)
        
        if access_token:
            if not organization_id:
                raise HTTPException(
                    status_code=400,
                    detail="Organization ID is required for Bearer token authentication"
                )
            return self.auth_client.get_user_from_bearer_token(access_token, organization_id)

        raise HTTPException(status_code=401, detail="Authentication required")

    def authenticate_without_org(
        self,
        access_token: str
    ) -> AuthenticatedUser:
        """
        Authenticates the user based on Bearer token without organization ID requirement.
        
        Args:
            access_token: Bearer token for authentication
            
        Returns:
            AuthenticatedUser: Contains authenticated user information
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            user = self.auth_client.get_user_from_bearer_token(access_token, None)
            return user
        except Exception as e:
            raise HTTPException(status_code=401, detail="Authentication failed")

class OrganizationHandler:
    def __init__(self, organization_client: OrganizationClient):
        self.organization_client = organization_client

    def generate_organization_for_user(self, user: AuthenticatedUser, organization: Organization):
        return self.organization_client.generate_organization_for_user(user, organization)
    
    def get_user_organizations(self, user: AuthenticatedUser):
        return self.organization_client.get_user_organizations(user)
