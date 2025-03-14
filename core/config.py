from dotenv import load_dotenv
load_dotenv()

from pydantic_settings import BaseSettings
from pydantic import Field
import os
from typing import List
from pydantic import field_validator


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

    # CORS Settings
    cors_origins: List[str] = Field(
        default=os.getenv("CORS_ORIGINS", ""),
        description="Allowed origins for CORS",
    )

    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

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
