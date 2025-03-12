"""
Authentication Clients Module

Implements the Supabase authentication client that supports both Bearer tokens
and API keys.

Classes:
    SupabaseAuthClient: Implementation of AuthClientBase using Supabase
"""

# external imports
from supabase import create_client, Client
from fastapi import HTTPException

# internal imports
from core.config import settings
from core.logger import setup_logger
from modules.authentication.base import AuthClientBase
from modules.authentication.schemas import AuthenticatedUser
logger = setup_logger(__name__)

class SupabaseAuthClient(AuthClientBase):
    """
    Supabase authentication client for both API keys and Bearer tokens.
    
    Methods:
        authenticate: Authenticate using either Bearer token or API key
        _verify_bearer_token: Verify JWT Bearer token from Supabase Auth
        _verify_api_key: Verify API key from the database
    """
    
    def __init__(self):
        """Initialize the Supabase client."""
        self.client: Client = create_client(settings.supabase_url, settings.supabase_key)


    def get_user_from_api_key(self, api_key: str) -> AuthenticatedUser:
        """
        Verify API key from the database.
        
        Args:
            api_key: The API key to verify
            
        Returns:
            AuthenticatedUser object containing user information
            
        Raises:
            HTTPException: If API key is invalid
        """
        try:
            response = self.client.table("api_keys").select("user_id, organization_id").eq("key", api_key).execute()
            if not response.data:
                logger.warning(f"Invalid API key: {api_key}")
                raise HTTPException(status_code=401, detail="Invalid API key")
            return AuthenticatedUser(
                success=True,
                user_id=response.data[0]["user_id"],
                organization_id=response.data[0]["organization_id"],
            )
        except Exception as e:
            logger.error(f"Failed to authenticate API key: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to verify API key")
    
    def get_user_from_bearer_token(self, access_token: str, organization_id: str) ->  AuthenticatedUser:
        """Authenticate user via Bearer Token and check if they belong to the requested organization.
        
        Args:
            access_token: The Bearer token to verify
            organization_id: The organization ID to check
            
        Returns:
            AuthenticatedUser object containing user information

        Raises:
            HTTPException: If Bearer token is invalid or user does not belong to the organization
        """
        try:
            user = self.client.auth.get_user(access_token).user
            if not user:
                logger.warning("Invalid Bearer Token")
                raise HTTPException(status_code=401, detail="Invalid Bearer Token")

            user_id = user.id
            user_organization = (
                self.client.table("user_organizations")
                .select("*")
                .eq("user_id", user_id)
                .eq("organization_id", organization_id)
                .execute()
            )
            if not user_organization.data:
                logger.warning(f"User {user_id} does not belong to organization {organization_id}")
                raise HTTPException(status_code=401, detail="Unauthorized Organization Access")
            
            return AuthenticatedUser(success=True, user_id=user_id, organization_id=organization_id)
        except Exception as e:
            logger.error(f"Multi-Organization Authentication Failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to verify token")

