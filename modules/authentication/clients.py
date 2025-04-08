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
from httpx import AsyncClient
from urllib.parse import urlencode
from typing import Dict, Any, List

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
    OrganizationWithRole,
    UserProfile,
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
            logger.info(f"Getting user from api key")
            response = self.client.table("api_keys").select("user_id, organization_id").eq("key", api_key).execute()
            if not response.data:
                logger.warning(f"Invalid API key provided")
                raise HTTPException(status_code=401, detail="Invalid API key")
            user_id = response.data[0]["user_id"]
            organization_id = response.data[0]["organization_id"]
            logger.info(f"Authenticated user: {user_id} with organization: {organization_id}")
            return AuthenticatedUser(
                success=True,
                user_id=user_id,
                organization_id=organization_id,
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
            logger.info(f"Getting user from bearer token")
            user = self.client.auth.get_user(access_token).user
            if not user:
                logger.warning("Invalid Bearer Token provided")
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
            logger.info(f"Authenticated user: {user_id} with organization: {organization_id}")
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

class BigDataOAuthClient:
    def __init__(self, client: Client, **kwargs):
        """
        Initializes an OAuth client for different integrations.

        Args:
        - client (Client): Database or API client (e.g., Supabase).
        - kwargs: Optional OAuth parameters (client_id, client_secret, redirect_uri, etc.)
        """
        self.client = client
        self.params = kwargs  # Store all optional parameters dynamically

    def get_param(self, key: str, default=None):
        """Helper to retrieve parameters safely.
        
        Args:
            key: The key to retrieve
            default: The default value to return if the key is not found
            
        Returns:
            The value of the key or the default value if the key is not found
        """
        return self.params.get(key, default)
    async def store_oauth_state(self, state: str):
        """Store OAuth state for CSRF protection.
        
        Args:
            state: The state to store
        """
        try:
            self.client.table("oauth_states").insert({"state": state}).execute()
        except Exception as e:
            logger.error(f"Error storing OAuth state: {e}")

    async def fetch_oauth_state(self, state: str) -> List[Dict[str, Any]]:
        """Fetch OAuth state from the database.
        
        Args:
            state: The state to fetch
            
        Returns:
            The OAuth state from the database
        """
        response = self.client.table("oauth_states").select("*").eq("state", state).execute()
        return response.data
    
    async def initiate_oauth_flow(self) -> str:
        """Generate OAuth URL with state for CSRF protection.
        
        Returns:
            The OAuth URL
        """
        state = secrets.token_urlsafe(32)  # Generate secure random state
        
        # Store the state in the database for CSRF protection
        await self.store_oauth_state(state)

        params = {
            'client_id': self.get_param("client_id"),
            'redirect_uri': self.get_param("redirect_uri"),
            'response_type': 'code',
            'scope': self.get_param("scope", "oauth"),
            'state': state
        }

        auth_url = f"{self.get_param('auth_url')}?{urlencode(params)}"
        return auth_url
    
    async def exchange_code(self, 
                            code: str, 
                            state: str, 
                            connector_id: str, 
                            organization_id: str, 
                            user_id: str, 
                            project_id: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens.
        Args:
            code: The authorization code
            state: The state to exchange
            
        Returns:
            The tokens from the database
        """
        oauth_state = await self.fetch_oauth_state(state)
        if not oauth_state:
            raise Exception("Invalid OAuth state")
        if not code:
            raise Exception("No authorization code provided")
        
        token_url = self.get_param("token_url")
        data = {
            "grant_type": "authorization_code",
            "client_id": self.get_param("client_id"),
            "client_secret": self.get_param("client_secret"),
            "redirect_uri": self.get_param("redirect_uri"),
            "code": code
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
        
        async with AsyncClient() as client:
            response = await client.post(token_url, data=data, headers=headers)
            
            if response.status_code != 200:
                error_data = response.json()
                logger.error(f"Token exchange failed: {error_data}")
                raise Exception(f"Token exchange failed: {error_data}")

            token_data = response.json()
            await self.store_tokens(
                token_data=token_data, 
                connector_id=connector_id, 
                organization_id=organization_id, 
                user_id=user_id, 
                project_id=project_id)
            return token_data

    async def store_tokens(self, 
                           token_data: Dict[str, Any], 
                           connector_id: str, 
                           organization_id: str, 
                           user_id: str, 
                           project_id: str):
        """Store access and refresh tokens in the database.
        Args:
            token_data: The tokens to store
            connector_id: The connector ID
            organization_id: The organization ID
            user_id: The user ID
            project_id: The project ID
        """
        if not token_data:
            raise Exception("No token data provided")
        if not connector_id:
            raise Exception("No connector ID provided")
        if not organization_id:
            raise Exception("No organization ID provided")
        if not user_id:
            raise Exception("No user ID provided")
        if not project_id:
            raise Exception("No project ID provided")
        
        try:
            self.client.table("user_connectors").upsert({
                "connector_id": connector_id,
                "organization_id": organization_id,
                "user_id": user_id,
                "project_id": project_id,
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_at": token_data.get("expires_at"),
                "scope": token_data.get("scope")
            }).execute()
        except Exception as e:
            logger.error(f"Error storing tokens: {e}")

    async def refresh_access_token(self, 
                                   connector_id: str, 
                                   organization_id: str, 
                                   user_id: str, 
                                   project_id: str) -> Dict[str, Any]:
        """Refresh access token using the refresh token.
        
        Args:
            connector_id: The connector ID
            organization_id: The organization ID
            user_id: The user ID
            project_id: The project ID
        """
        token_url = self.get_param("token_url")
        # Fetch refresh token from the database
        refresh_token = self.get_refresh_token(connector_id, organization_id, user_id, project_id)

        if not refresh_token:
            raise Exception("No refresh token found. Re-authentication required.")

        data = {
            "grant_type": "refresh_token",
            "client_id": self.get_param("client_id"),
            "client_secret": self.get_param("client_secret"),
            "refresh_token": refresh_token
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}

        async with AsyncClient() as client:
            response = await client.post(token_url, data=data, headers=headers)

            if response.status_code != 200:
                error_data = response.json()
                logger.error(f"Token refresh failed: {error_data}")
                raise Exception("Token refresh failed")

            new_token_data = response.json()
            await self.store_tokens(new_token_data)
            return new_token_data
    
    async def get_access_token(self, 
                               connector_id: str, 
                               organization_id: str, 
                               user_id: str, 
                               project_id: str) -> Dict[str, Any]:
        """Get the OAuth token for the user.
        
        Args:
            connector_id: The connector ID
            organization_id: The organization ID
            user_id: The user ID
            project_id: The project ID
        """
        response = (
            self.client.table("user_connectors")
            .select("access_token")
            .eq("connector_id", connector_id)
            .eq("organization_id", organization_id)
            .eq("user_id", user_id)
            .eq("project_id", project_id)
            .single()
            .execute()
        )
        return response.data[0]["access_token"]

    async def get_refresh_token(self, 
                                connector_id: str, 
                                organization_id: str, 
                                user_id: str, 
                                project_id: str) -> Dict[str, Any]:
        """Get the OAuth refresh token for the user.
        
        Args:
            connector_id: The connector ID
            organization_id: The organization ID
            user_id: The user ID
            project_id: The project ID
        """
        response = (
            self.client.table("user_connectors")
            .select("refresh_token")
            .eq("connector_id", connector_id)
            .eq("organization_id", organization_id)
            .eq("user_id", user_id)
            .eq("project_id", project_id)
            .single()
            .execute()
        )
        return response.data[0]["refresh_token"]
    

class ProfileClient:
    def __init__(self, client: Client, table_name: str = "user_profiles"):
        self.client = client
        self.table_name = table_name

    def fetch_user_profile(self, user_id: str) -> UserProfile:
        response = self.client.table(self.table_name).select("*").eq("id", user_id).execute()
        return response.data

    def add_user_profile(self, user_id: str, user_name: str, default_organization: str) -> UserProfile:
        response = self.client.table(self.table_name).insert({
            "id": user_id,
            "name": user_name,
            "default_organization": default_organization
        }).execute()
        return response.data