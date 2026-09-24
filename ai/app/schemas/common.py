from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class TestRequest(BaseModel):
    message: str = Field(..., description="Message to send to the AI")

class TextRequest(BaseModel):
    text: str = Field(..., description="Raw text to be analyzed")

class TestResponse(BaseModel):
    status: str = Field(..., description="Status of the response")
    reply: str = Field(..., description="AI reply message")
    original_message: str = Field(..., description="The original message sent")

class GitHubRequest(BaseModel):
    username: str = Field(..., description="GitHub username to analyze", min_length=1)

class LeetCodeRequest(BaseModel):
    username: str = Field(..., description="LeetCode username to analyze", min_length=1)
