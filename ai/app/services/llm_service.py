import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class BaseLLMProvider(ABC):
    """Abstract base class for LLM Providers."""
    
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate plain text from a prompt."""
        pass
    
    @abstractmethod
    def generate_json(self, prompt: str, **kwargs) -> str:
        """Generate a JSON string from a prompt."""
        pass

class MockLLMProvider(BaseLLMProvider):
    """A mock provider for testing and development without API keys."""
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        logger.info(f"MockLLM generating text for prompt: {prompt[:50]}...")
        return "This is a mock response from the LLM."
        
    def generate_json(self, prompt: str, **kwargs) -> str:
        logger.info(f"MockLLM generating JSON for prompt: {prompt[:50]}...")
        
        if "TestRequest" in prompt or "Hello AI" in prompt:
            return '{"status": "success", "reply": "Hello from Mock AI", "original_message": "Hello AI"}'
            
        if "MentorChatResponse" in prompt or "mentor" in prompt.lower():
            return json.dumps({
                "answer": "Based on your 90-day roadmap and current profile as an AI/ML Engineer, today you should focus on practicing Dynamic Programming on LeetCode and refining your PyTorch FastAPI project.",
                "evidence": ["LeetCode weak topic: Dynamic Programming", "Target Role: AI/ML Engineer"],
                "recommended_actions": ["Solve 2 DP Medium problems on LeetCode", "Add API documentation to Neural Vision Classifier project"],
                "related_skills": ["Dynamic Programming", "PyTorch", "FastAPI"],
                "confidence": 0.92
            })

        if "LLMResumeExtraction" in prompt or "extract resume" in prompt.lower():
            return json.dumps({
                "skills": {
                    "languages": ["Python", "C++", "SQL"],
                    "frameworks": ["PyTorch", "FastAPI", "Scikit-Learn"],
                    "tools": ["Docker", "Git", "Linux"],
                    "other": ["Data Structures", "Algorithms"]
                },
                "education": [
                    {"institution": "Synthetic Institute of Technology (DEMO)", "degree": "B.Tech Computer Science", "graduation_date": "2026", "gpa": "8.4"}
                ],
                "experience": [
                    {
                        "company": "Synthetic AI Labs (DEMO)",
                        "role": "AI/ML Research Intern",
                        "duration": "3 months",
                        "bullets": ["Optimized computer vision inference latency by 25% using PyTorch."]
                    }
                ],
                "projects": [
                    {
                        "name": "Neural Vision Classifier",
                        "description": "CNN image classifier with FastAPI containerized with Docker",
                        "technologies": ["Python", "PyTorch", "FastAPI", "Docker"],
                        "bullets": ["Achieved 92% test accuracy and deployed API processing 150 req/sec"],
                        "has_metrics": True
                    }
                ],
                "certifications": ["Deep Learning Specialization"],
                "achievements": ["Dean's List 2024"],
                "missing_sections": [],
                "weak_bullets": [],
                "repeated_words": [],
                "generic_phrases": [],
                "keyword_gaps": ["Kubernetes"]
            })

        if "LLMGitHubInterpretation" in prompt or "github interpretation" in prompt.lower():
            return json.dumps({
                "overall_summary": "Active GitHub profile with solid evidence of Python, PyTorch, and Docker containerized deployments.",
                "strengths": ["Strong Python repo volume", "High README coverage (87.5%)"],
                "gaps": ["No automated CI/CD workflows"],
                "recommended_improvements": ["Add GitHub Actions for testing and linting"]
            })

        if "LLMSynthesisOutput" in prompt or "skill gap synthesis" in prompt.lower():
            return json.dumps({
                "summary": "Targeted skill gap analysis for AI/ML Engineer role.",
                "item_explanations": [
                    {
                        "skill": "PyTorch",
                        "explanation": "Required level is Intermediate, student shows Intermediate proficiency.",
                        "recommended_action": "Practice advanced model optimization and distributed training."
                    }
                ]
            })

        return '{"status": "success", "message": "mock LLM response"}'

class LLMService:
    """Core LLM Service that abstracts away the specific provider."""
    
    def __init__(self):
        provider_name = os.getenv("LLM_PROVIDER", "mock").lower()
        api_key = os.getenv("LLM_API_KEY", "")
        
        # In a real app, instantiate different providers based on provider_name
        if provider_name == "openai":
            # self.provider = OpenAILLMProvider(api_key=api_key)
            self.provider = MockLLMProvider() # Fallback for now
        elif provider_name == "gemini":
            # self.provider = GeminiLLMProvider(api_key=api_key)
            self.provider = MockLLMProvider() # Fallback for now
        else:
            self.provider = MockLLMProvider()
            
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate unstructured text."""
        return self.provider.generate_text(prompt, **kwargs)
        
    def generate_structured(self, prompt: str, response_model: Type[T], max_retries: int = 2, **kwargs) -> T:
        """
        Generate structured output validated against a Pydantic model.
        If validation fails, it attempts to repair by feeding the error back to the LLM.
        """
        current_prompt = prompt
        
        for attempt in range(max_retries + 1):
            try:
                # Add instructions for JSON output
                if attempt == 0:
                    current_prompt += f"\n\nReturn ONLY valid JSON that matches this schema: {response_model.model_json_schema()}"
                
                json_str = self.provider.generate_json(current_prompt, **kwargs)
                
                # Strip markdown code blocks if present
                json_str = json_str.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                json_str = json_str.strip()
                
                # Parse JSON
                parsed_data = json.loads(json_str)
                
                # Validate with Pydantic
                return response_model.model_validate(parsed_data)
                
            except json.JSONDecodeError as e:
                logger.warning(f"Attempt {attempt + 1}: Invalid JSON returned by LLM: {e}")
                error_msg = f"Your previous response was not valid JSON. Error: {str(e)}. Please try again and return ONLY valid JSON."
                current_prompt = f"{prompt}\n\n{error_msg}"
                
            except ValidationError as e:
                logger.warning(f"Attempt {attempt + 1}: Pydantic validation failed: {e}")
                error_msg = f"Your previous JSON did not match the required schema. Validation errors:\n{e.json()}\nFix these errors and return valid JSON."
                current_prompt = f"{prompt}\n\n{error_msg}"
                
        # If we exceed max_retries
        raise ValueError(f"Failed to generate valid structured output after {max_retries + 1} attempts.")
        
    def analyze(self, text: str, analysis_type: str, **kwargs) -> str:
        """A higher level wrapper for specific analysis tasks."""
        prompt = f"Perform {analysis_type} analysis on the following text:\n\n{text}"
        return self.generate_text(prompt, **kwargs)
