from dotenv import load_dotenv
load_dotenv()

from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
