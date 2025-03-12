from dotenv import load_dotenv
load_dotenv()

from pydantic_settings import BaseSettings
from pydantic import Field
import os
from typing import List

cors_origins_env = os.getenv("CORS_ORIGINS")


class Settings(BaseSettings):
    # FastAPI Settings
    port: int = Field(
        default=int(os.getenv("PORT", 8000)),
        description="Port number for the FastAPI server"
    )
    host: str = Field(
        default=os.getenv("HOST", "0.0.0.0"),
        description="Host address for the FastAPI server"
    )
    debug: bool = Field(
        default=bool(os.getenv("DEBUG", True)),
        description="Debug mode flag"
    )
    reload: bool = Field(
        default=bool(os.getenv("RELOAD", True)),
        description="Auto-reload mode flag"
    )

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

    # CORS Settings
    cors_origins: List[str] = Field(
    default=cors_origins_env.split(",") if cors_origins_env else [],
    description="Allowed origins for CORS"
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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
