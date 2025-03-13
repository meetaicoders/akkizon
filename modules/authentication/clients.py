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
import string
import secrets

# internal imports
from core.config import settings
from core.logger import setup_logger
from modules.authentication.base import AuthClientBase
from modules.authentication.schemas import (
    AuthenticatedUser, 
    Organization, 
    UserOrganization, 
    APIKey,
    BearerToken,
    OrganizationWithRole
)

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
    
    def get_user_from_bearer_token(self, access_token: str, organization_id: str = None) ->  AuthenticatedUser:
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

            if organization_id is not None:
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
        
    def sign_in(self, email: str, password: str) -> BearerToken:
        """Sign in a user and return access/refresh tokens."""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # Extract access and refresh tokens from the session
            access_token = response.session.access_token
            refresh_token = response.session.refresh_token
            
            return BearerToken(
                access_token=access_token,
                refresh_token=refresh_token
            )
        except Exception as e:
            logger.error(f"Failed to sign in: {str(e)}", exc_info=True)
            raise
        
class OrganizationClient:
    """
    Client for managing organizations.
    """
    def __init__(self):
        logger.info(f"Initializing OrganizationClient")
        self.client: Client = create_client(settings.supabase_url, settings.supabase_key)

    def generate_organization_for_user(self, user: AuthenticatedUser, organization: Organization) -> Organization:
        """Generate an organization for a user."""
        logger.info(f"Generating organization for user: {user.user_id}")
        new_organization = self.add_organization(organization)  # Capture the returned organization
        self.add_user_to_organization(user, new_organization)  # Use the new organization
        self.generate_api_key(user, new_organization)  # Use the new organization
        return new_organization  # Return the updated organization

    def add_organization(self, organization: Organization) -> Organization:
        """Add an organization to the database."""
        try:
            logger.info(f"Adding organization: {organization.name}")
            response = self.client.table("organizations").insert({
                "name": organization.name,
            }).execute()
            new_organization = Organization(**response.data[0])  # Changed variable name for clarity
            return new_organization
        except Exception as e:
            logger.error(f"Failed to add organization: {str(e)}", exc_info=True)
            raise
    
    def add_user_to_organization(self, user: AuthenticatedUser, organization: Organization) -> UserOrganization:
        """Add a user to the specified organization."""
        try:
            logger.info(f"Adding {user.user_id} to {organization.id}")

            response = self.client.table("user_organizations").insert({
                "user_id": user.user_id,
                "organization_id": organization.id
            }).execute()
            user_organization = UserOrganization(**response.data[0])
            return user_organization
        except Exception as e:
            logger.error(f"Failed to add user to organization: {str(e)}", exc_info=True)
            raise
    
    def generate_api_key(self, user: AuthenticatedUser, organization: Organization) -> APIKey:
        """Generate an API key for the user in the specified organization."""
        logger.info(f"Generating API key for {user.user_id}")
        characters = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(characters) for _ in range(32))  # 32 characters long
        try:
            response = self.client.table("api_keys").insert({
                "user_id": user.user_id,
                "organization_id": organization.id,
                "key": api_key
            }).execute() 
            api_key_object = APIKey(**response.data[0])  # Changed variable name for clarity
            return api_key_object
        except Exception as e:
            logger.error(f"Failed to generate API key: {str(e)}", exc_info=True)
            raise
    
    def get_user_organizations(self, user: AuthenticatedUser):
        """Get all organizations for a user as a list with roles."""
        try:
            logger.info(f"Getting organizations for {user.user_id}")
            # Use a join to fetch both user_organizations and organizations data
            response = self.client.table("user_organizations").select(
                """
                organization_id,
                role,
                organizations (id, name, created_at, updated_at)
                """
            ).eq("user_id", str(user.user_id)).execute()
            
            # Build the list of organizations with the role included
            organizations = [
                OrganizationWithRole(
                    id=org["organizations"]["id"],
                    name=org["organizations"]["name"],
                    role=org["role"],
                    created_at=org["organizations"]["created_at"],
                    updated_at=org["organizations"]["updated_at"]
                )
                for org in response.data
            ]
            
            return organizations
        except Exception as e:
            logger.error(f"Failed to get user organizations: {str(e)}", exc_info=True)
            raise 
    