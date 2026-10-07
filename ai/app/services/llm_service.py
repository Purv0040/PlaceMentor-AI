import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

def _build_grounded_github_interpretation(prompt: str) -> Dict[str, Any]:
    """
    Parses PORTFOLIO DATA from prompt to construct evidence-grounded GitHub insights.
    Guarantees zero hallucinations (no PyTorch, Docker, FastAPI, or fake metrics unless in data).
    """
    primary_lang = "None detected"
    if "Primary Language:" in prompt:
        primary_lang = prompt.split("Primary Language:")[1].split("\n")[0].strip()

    all_langs_str = ""
    if "All Languages Used:" in prompt:
        all_langs_str = prompt.split("All Languages Used:")[1].split("\n")[0].strip()

    username = "student"
    if "Username:" in prompt:
        username = prompt.split("Username:")[1].split("\n")[0].strip()

    detected_cats = []
    if "Detected Technical Categories" in prompt:
        cat_section = prompt.split("Detected Technical Categories")[1].split("Repository Complexity")[0]
        for line in cat_section.splitlines():
            line = line.strip()
            if line.startswith("- ") and ":" in line and "None detected" not in line:
                cat_name = line.split("- ")[1].split(":")[0].strip()
                detected_cats.append(cat_name)

    strengths = []
    if primary_lang and primary_lang != "None detected":
        strengths.append(f"Demonstrated primary language proficiency in {primary_lang}.")
    if all_langs_str and all_langs_str not in ("None", "None detected"):
        strengths.append(f"Technical portfolio spanning languages: {all_langs_str}.")
    if detected_cats:
        strengths.append(f"Verified project evidence in technical areas: {', '.join(detected_cats)}.")
    if not strengths:
        strengths = ["Active public GitHub profile with repository contributions."]

    gaps = []
    if "Docker / Containerization" not in detected_cats:
        gaps.append("No containerization evidence (Docker/Dockerfile) detected in repository configurations.")
    if "Deployment / DevOps" not in detected_cats:
        gaps.append("No automated CI/CD workflows or cloud deployment manifests observed.")
    if "Testing" not in detected_cats:
        gaps.append("Limited automated unit testing suites detected across public repositories.")

    technical_patterns = []
    if detected_cats:
        technical_patterns.append(f"Architecture focus aligns with {', '.join(detected_cats)}.")
    else:
        technical_patterns.append("General software development with standard repository organization.")
    if primary_lang and primary_lang != "None detected":
        technical_patterns.append(f"Primary implementation language centered around {primary_lang}.")

    recommendations = []
    if "Docker / Containerization" not in detected_cats:
        recommendations.append("Add a Dockerfile and docker-compose.yml to containerize core applications.")
    if "Deployment / DevOps" not in detected_cats:
        recommendations.append("Implement GitHub Actions workflows (.github/workflows) for automated linting and testing.")
    if "Testing" not in detected_cats:
        recommendations.append("Include unit test suites (e.g., pytest, jest) with clear test instructions in README.")

    cat_summary = f"Detected technical domains include {', '.join(detected_cats)}." if detected_cats else "No specialized technical categories were detected."
    evidence_summary = (
        f"GitHub portfolio for @{username} features {primary_lang if primary_lang != 'None detected' else 'general'} code. "
        f"{cat_summary} Insights are strictly grounded in observable repository evidence."
    )

    return {
        "strengths": strengths,
        "gaps": gaps,
        "technical_patterns": technical_patterns,
        "recommendations": recommendations,
        "evidence_summary": evidence_summary,
    }


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

        if "LLMGitHubInterpretation" in prompt or ("github" in prompt.lower() and "interpretation" in prompt.lower()):
            grounded_data = _build_grounded_github_interpretation(prompt)
            return json.dumps(grounded_data)

        if "LLMResumeExtraction" in prompt or "extract resume" in prompt.lower():
            from app.services.dynamic_extractor import parse_resume_dynamically
            extracted_data = parse_resume_dynamically(prompt)
            return json.dumps(extracted_data)

        if "LLMSynthesisOutput" in prompt or "skill gap synthesis" in prompt.lower():
            import re
            role_m = re.search(r"target role:\s*['\"]?([^'\"\n\r]+)['\"]?", prompt, re.IGNORECASE)
            detected_role = role_m.group(1).strip() if role_m else "Target Role"
            return json.dumps({
                "summary": f"Targeted skill gap analysis for {detected_role} role.",
                "item_explanations": [
                    {
                        "skill": "Core Proficiency",
                        "explanation": f"Evaluating student proficiency for {detected_role}.",
                        "recommended_action": f"Focus on foundational competencies aligned with {detected_role} requirements."
                    }
                ]
            })

        if "MentorChatResponse" in prompt or "mentor_chat" in prompt.lower() or "chat response" in prompt.lower():
            return json.dumps({
                "answer": "Based on your 90-day roadmap and current profile as an AI/ML Engineer, today you should focus on practicing Dynamic Programming on LeetCode and refining your PyTorch FastAPI project.",
                "evidence": ["LeetCode weak topic: Dynamic Programming", "Target Role: AI/ML Engineer"],
                "recommended_actions": ["Solve 2 DP Medium problems on LeetCode", "Add API documentation to Neural Vision Classifier project"],
                "related_skills": ["Dynamic Programming", "PyTorch", "FastAPI"],
                "confidence": 0.92
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
        last_error_detail = ""
        last_raw_json = ""
        
        for attempt in range(max_retries + 1):
            try:
                # Add instructions for JSON output
                if attempt == 0:
                    current_prompt += f"\n\nReturn ONLY valid JSON that matches this schema: {response_model.model_json_schema()}"
                
                json_str = self.provider.generate_json(current_prompt, **kwargs)
                last_raw_json = json_str
                
                # Strip markdown code blocks if present
                json_str = json_str.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                elif json_str.startswith("```"):
                    json_str = json_str[3:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                json_str = json_str.strip()
                
                # Parse JSON
                parsed_data = json.loads(json_str)
                
                # Validate with Pydantic
                return response_model.model_validate(parsed_data)
                
            except json.JSONDecodeError as e:
                last_error_detail = f"JSONDecodeError: {str(e)}"
                logger.warning(
                    f"[Attempt {attempt + 1}/{max_retries + 1}] Invalid JSON from LLM: {e}. Raw snippet: {last_raw_json[:200]!r}"
                )
                error_msg = f"Your previous response was not valid JSON. Error: {str(e)}. Please try again and return ONLY valid JSON."
                current_prompt = f"{prompt}\n\n{error_msg}"
                
            except ValidationError as e:
                last_error_detail = f"ValidationError: {e.errors()}"
                logger.warning(
                    f"[Attempt {attempt + 1}/{max_retries + 1}] Pydantic validation failed for {response_model.__name__}: {e}. Raw JSON: {last_raw_json[:300]!r}"
                )
                error_msg = f"Your previous JSON did not match the required schema. Validation errors:\n{e.json()}\nFix these errors and return valid JSON."
                current_prompt = f"{prompt}\n\n{error_msg}"
                
        # If we exceed max_retries
        logger.error(
            f"Failed to generate valid structured output for model {response_model.__name__} after {max_retries + 1} attempts. "
            f"Last Error: {last_error_detail} | Last Raw Response: {last_raw_json!r}"
        )
        raise ValueError(
            f"Failed to generate valid structured output after {max_retries + 1} attempts. Detail: {last_error_detail}"
        )
        
    def analyze(self, text: str, analysis_type: str, **kwargs) -> str:
        """A higher level wrapper for specific analysis tasks."""
        prompt = f"Perform {analysis_type} analysis on the following text:\n\n{text}"
        return self.generate_text(prompt, **kwargs)
