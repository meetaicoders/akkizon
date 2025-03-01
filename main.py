from dotenv import load_dotenv
load_dotenv()

from core.config import settings
from core.adapter import MultiProviderClient, Provider, ChatRequest, ChatMessage
import os

def test_openai():
    # Get API key from environment (or replace with your key)
    api_key = settings.openai_api_key
    
    # Initialize client
    client = MultiProviderClient(
        provider=Provider.OPENAI,
        api_key=api_key
    )
    
    # Create test request
    request = ChatRequest(
        model="gpt-4",
        messages=[
            ChatMessage(role="system", content="Hello, how are you today?")
        ]
    )
    
    try:
        # Get completion
        response = client.chat_completion(request)
        print("\nAI Response:")
        print(response['content'])
        print(f"\nRequest ID: {response['request_id']}")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_openai()
