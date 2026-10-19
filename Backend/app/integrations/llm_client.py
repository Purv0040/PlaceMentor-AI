import logging
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Client wrapper for Groq LLM API calls."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL or "openai/gpt-oss-120b"

    async def generate_completion(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        if not self.api_key:
            logger.info("LLMClient: No Groq API key configured; returning stub response.")
            return "LLM response stub"

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.2,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(
                        "Groq API error (status %d): %s",
                        response.status_code,
                        response.text,
                    )
                    return "Error generating completion from Groq API"
        except Exception as e:
            logger.error("LLMClient: Exception during Groq completion: %s", e)
            return "Error communicating with Groq API"

