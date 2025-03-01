"""
AI Provider Adapter Module

Provides a unified interface for various AI service providers through a common adapter pattern.
"""

from enum import Enum
from typing import Dict, Type, Optional
from .base_client import BaseAIClient, ChatMessage, ChatRequest
from .deepseek_client import DeepSeekClient
from .openai_client import OpenAIClient



class Provider(Enum):
    """Enumeration of supported AI service providers.
    
    Attributes:
        DEEPSEEK: DeepSeek AI service provider
        OPENAI: OpenAI API service provider

    Example:
        >>> Provider.DEEPSEEK
        <Provider.DEEPSEEK: 'deepseek'>
    """
    DEEPSEEK = "deepseek"
    OPENAI = "openai"

    def __str__(self) -> str:
        return self.value

class Models:
    """Supported models organized by provider"""
    
    class OPENAI(Enum):
        GPT4 = "gpt-4"
        GPT4O = "gpt-4o"
        GPT35 = "gpt-3.5-turbo"

    class DEEPSEEK(Enum):
        CHAT = "deepseek-chat"
        CODER = "deepseek-coder"

    @classmethod
    def get_default(cls, provider: Provider) -> str:
        """Get default model for a provider"""
        return {
            Provider.OPENAI: cls.OPENAI.GPT4.value,
            Provider.DEEPSEEK: cls.DEEPSEEK.CHAT.value
        }[provider]

PROVIDERS = [member.value for member in Provider]  # Supported provider identifiers


class MultiProviderClient:
    """Client factory for AI service providers with unified interface.
    
    Args:
        provider: Selected provider from Provider enum
        api_key: Authentication key for the provider's API
        model: Optional model override for the provider

    Raises:
        TypeError: If provider argument is not a Provider enum member
        ValueError: For unsupported providers, invalid credentials, or unsupported models

    Example:
        >>> client = MultiProviderClient(Provider.OPENAI, "sk-...")
        >>> request = ChatRequest(...)
        >>> response = client.chat_completion(request)
    """

    _client_map: Dict[Provider, Type[BaseAIClient]] = {
        Provider.DEEPSEEK: DeepSeekClient,
        Provider.OPENAI: OpenAIClient,
    }

    def __init__(self, provider: Provider, api_key: str, model: str = None) -> None:
        if not isinstance(provider, Provider):
            raise TypeError(f"Provider must be a Provider enum member. Received {type(provider)}")

        self.provider = provider
        self.api_key = api_key
        self.model = model or Models.get_default(provider)
        
        self._validate_model()
        self._initialize_client()

    def _validate_model(self):
        """Validate model compatibility with provider"""
        provider_models = {
            Provider.OPENAI: [m.value for m in Models.OPENAI],
            Provider.DEEPSEEK: [m.value for m in Models.DEEPSEEK]
        }
        
        if self.model not in provider_models[self.provider]:
            raise ValueError(
                f"Model '{self.model}' not supported by {self.provider.value}. "
                f"Supported: {provider_models[self.provider]}"
            )

    def _initialize_client(self):
        """Initialize the provider-specific client"""
        client_class = self._client_map.get(self.provider)
        if not client_class:
            raise ValueError(f"Unsupported provider: {self.provider.value}")

        try:
            self.client = client_class(api_key=self.api_key, model=self.model)
        except Exception as e:
            raise ValueError(
                f"Failed to initialize {self.provider.value} client: {str(e)}"
            ) from e

    def chat_completion(self, request: ChatRequest) -> Dict:
        """Execute chat completion request through configured provider.
        
        Args:
            request: ChatRequest object containing model and messages
            
        Returns:
            Dictionary with provider-specific response format
            
        Raises:
            ProviderAPIError: For errors in the underlying provider API
        """
        return self.client.chat_completion(request)


__all__ = [
    'Provider',
    'Models',
    'PROVIDERS',
    'MultiProviderClient',
    'ChatMessage', 
    'ChatRequest',
    'DeepSeekClient',
    'OpenAIClient'
] 