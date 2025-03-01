"""
Base Definitions for AI Provider Adapters

Defines core interfaces and data structures for AI service provider implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ChatMessage:
    """Represents a single message in a chat conversation.
    
    Attributes:
        role: Participant role (e.g., 'user', 'assistant', 'system')
        content: Text content of the message

    Example:
        >>> ChatMessage(role="user", content="Hello AI!")
        ChatMessage(role='user', content='Hello AI!')
    """
    role: str
    content: str

@dataclass
class ChatRequest:
    """Container for chat completion request parameters.
    
    Attributes:
        model: Identifier for the AI model to use
        messages: List of chat messages forming the conversation history

    Example:
        >>> request = ChatRequest(
        ...     model="gpt-4",
        ...     messages=[ChatMessage(role="user", content="Hi!")]
        ... )
    """
    model: str
    messages: List[ChatMessage] = field(default_factory=list)

class BaseAIClient(ABC):
    """Abstract base class defining the interface for AI provider clients.
    
    All concrete AI client implementations must inherit from this class and
    implement the chat_completion method.
    
    Subclasses should handle:
    - Provider-specific API communication
    - Error handling
    - Response formatting
    """

    @abstractmethod
    def chat_completion(self, request: ChatRequest) -> Dict:
        """Execute a chat completion request through the provider's API.
        
        Args:
            request: ChatRequest containing model and message history
            
        Returns:
            Dictionary containing:
            - 'content': Primary response text
            - Additional provider-specific metadata
            
        Raises:
            NotImplementedError: If subclass doesn't implement this method
            ProviderAPIError: For provider-specific communication errors
            
        Example:
            >>> client = ConcreteClient(api_key="...")
            >>> response = client.chat_completion(request)
            >>> print(response['content'])
        """
        raise NotImplementedError("Subclasses must implement chat_completion")
