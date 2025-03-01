from .base_client import BaseAIClient, ChatRequest
from openai import OpenAI
from typing import Dict

class OpenAIClient(BaseAIClient):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def chat_completion(self, request: ChatRequest) -> Dict:
        response = self.client.chat.completions.create(
            messages=[{"role": m.role, "content": m.content} for m in request.messages],
            model=request.model
        )
        return {
            "provider": "OpenAI",
            "request_id": response._request_id,
            "content": response.choices[0].message.content
        }
