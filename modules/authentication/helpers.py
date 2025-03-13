# external imports
from functools import lru_cache
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from typing import Optional

# internal imports
from modules.authentication.clients import SupabaseAuthClient
from modules.authentication.handlers import AuthenticationHandler
from modules.authentication.schemas import AuthenticatedUser
from core.logger import setup_logger

logger = setup_logger(__name__)

# Security dependencies
auth_scheme = HTTPBearer(auto_error=False)  # Make Bearer optional
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

@lru_cache()
def get_auth_handler() -> AuthenticationHandler:
    return AuthenticationHandler(SupabaseAuthClient())

def get_authenticated_user(
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme),
    api_key: Optional[str] = Depends(api_key_header),
    organization_id: Optional[str] = Header(None, alias="X-Organization-ID")
) -> AuthenticatedUser:
    """
    Authenticate user using either Bearer token or API key.
    Organization ID is required for Bearer token authentication.
    
    Args:
        auth_header: Optional Bearer token
        api_key: Optional API key
        organization_id: Organization ID from headers (required for Bearer token)
        
    Returns:
        AuthenticatedUser: Contains authenticated user information
        
    Raises:
        HTTPException: If authentication fails or organization ID is missing for Bearer token
    """
    auth_handler = get_auth_handler()
    
    try:
        # Use Bearer token if present
        if auth_header:
            return auth_handler.authenticate(
                access_token=auth_header.credentials,
                organization_id=organization_id
            )
        
        # Use API key if present
        if api_key:
            return auth_handler.authenticate(api_key=api_key)
            
        raise HTTPException(status_code=401, detail="No authentication credentials provided")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during authentication")

def get_authenticated_user_without_org(
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme),
    api_key: Optional[str] = Depends(api_key_header)
) -> AuthenticatedUser:
    """
    Authenticate user using either Bearer token or API key.
    This version does not require organization ID for Bearer token authentication.
    
    Args:
        auth_header: Optional Bearer token
        api_key: Optional API key
        
    Returns:
        AuthenticatedUser: Contains authenticated user information
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_handler = get_auth_handler()
    
    try:
        # Use Bearer token if present
        if auth_header:
            return auth_handler.authenticate_without_org(
                access_token=auth_header.credentials
            )
        
        # Use API key if present
        if api_key:
            return auth_handler.authenticate(api_key=api_key)
            
        raise HTTPException(status_code=401, detail="No authentication credentials provided")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during authentication")