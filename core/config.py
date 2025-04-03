from dotenv import load_dotenv
load_dotenv()

from pydantic_settings import BaseSettings
from pydantic import Field
import os
from typing import List


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = Field(
        default=os.getenv("OPENAI_API_KEY", ""),
        description="OpenAI API key for accessing their services"
    )
    deepseek_api_key: str = Field(
        default=os.getenv("DEEPSEEK_API_KEY", ""),
        description="DeepSeek API key for their AI services"
    )
    groq_api_key: str = Field(
        default=os.getenv("GROQ_API_KEY", ""),
        description="Groq API key for their accelerated AI models"
    )

    # Database Settings
    supabase_url: str = Field(
        default=os.getenv("SUPABASE_URL", ""),
        description="Supabase URL"
    )
    supabase_key: str = Field(
        default=os.getenv("SUPABASE_KEY", ""),
        description="Supabase Key"
    )
    supabase_service_role_key: str = Field(
        default=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        description="Supabase Service Role Key"
    )
    supabase_jwt_secret: str = Field(
        default=os.getenv("SUPABSE_JWT_SECRET", ""),
        description="Supabase JWT Secret"
    )

    # HubSpot Settings
    hubspot_app_id: str = Field(
        default=os.getenv("HUBSPOT_APP_ID", ""),
        description="This is your app's unique ID. You'll need it to make certain API calls."
    )
    hubspot_client_id: str = Field(
        default=os.getenv("HUBSPOT_CLIENT_ID", ""),
        description="This ID is unique to your app and is used for initiating OAuth."
    )
    hubspot_client_secret: str = Field(
        default=os.getenv("HUBSPOT_CLIENT_SECRET", ""),
        description="Used to establish and refresh OAuth authentication."
    )
    hubspot_redirect_uri: str = Field(
        default=os.getenv("HUBSPOT_REDIRECT_URI", ""),
        description="The URI to redirect to after OAuth flow is complete."
    )
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
