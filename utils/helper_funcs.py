# external imports
from supabase import Client, create_client
import time
import jwt
from functools import lru_cache
from fastapi import HTTPException

# internal imports
from core.config import settings
from core.logger import setup_logger
logger = setup_logger(__name__)


def generate_user_jwt(user_id: str) -> str:
    """
    Generate a JWT for a user.
    """
    try:
        payload = {
            "sub": user_id,
            "role": "authenticated",
            "aud": "authenticated",
            "exp": int(time.time()) + 300
        }
        return jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")
    except jwt.PyJWTError as e:
        logger.error(f"JWT generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate authentication token"
        )
    except Exception as e:
        logger.error(f"Unexpected error in JWT generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Unexpected error during authentication"
        )
    

def get_anon_supabase_client() -> Client:
    """
    Get the anonymous supabase client.
    """
    return create_client(settings.supabase_url, settings.supabase_key)

def get_supabase_client() -> Client:
    """
    Get the supabase client from the API key.
    """
    
    client = create_client(
        settings.supabase_url,
        settings.supabase_key
    )
    return client

# @lru_cache()
# def get_supabase_client(user_id: str) -> Client:
#     """
#     Get the authenticated supabase client.
#     args:
#         user_id: str
#     returns:
#         supabase_client: Client
#     """
#     if not user_id:
#         logger.error("User ID is required")
#         raise HTTPException(
#             status_code=400,
#             detail="User ID is required"
#         )
    
#     try:
#         # Create admin client for user validation
#         admin_client = create_client(
#             settings.supabase_url,
#             settings.supabase_service_role_key
#         )
        
#         # Get user with service role
#         user = admin_client.auth.admin.get_user_by_id(user_id).user

#         # Security checks
#         if not user:
#             logger.error(f"User not found: {user_id}")
#             raise HTTPException(status_code=404, detail="User not found")
            
#         if user.aud != "authenticated":
#             logger.warning(f"Invalid audience for user {user_id}: {user.aud}")
#             raise HTTPException(status_code=403, detail="Invalid audience")
            
#         if not user.email_confirmed_at:
#             logger.warning(f"Email not verified for user {user_id}")
#             raise HTTPException(status_code=403, detail="Email not verified")
            
#         # Create RLS client
#         client = create_client(
#             settings.supabase_url,
#             settings.supabase_key
#         )
        
#         # Set JWT for RLS context
#         return client.postgrest.auth(generate_user_jwt(user_id))
       
#     except HTTPException:
#         # Re-raise already handled exceptions
#         raise
#     except Exception as e:
#         logger.error(f"Authentication failed: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=500, 
#             detail="Internal server error during authentication"
#         )

def get_user_id_from_api_key(api_key: str) -> str:
    """
    Get the user ID from the API key.
    """
    client = get_supabase_client(api_key)
    return client.auth.admin.get_user_by_id(api_key).user.id
