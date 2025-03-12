from supabase import Client, create_client
import os
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

@lru_cache()
def get_supabase_client() -> Client:
    """
    Get the supabase client.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    client = create_client(supabase_url, supabase_key)
    logger.info(f"Supabase client initialized Successfully")
    return client

