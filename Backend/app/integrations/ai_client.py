import logging
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIClientError(Exception):
    """Exception raised when communication with external AI service fails."""
    pass


class AIClient:
    """HTTP Client integration to communicate with the external ai/ microservice."""

    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = (base_url or settings.AI_SERVICE_URL).rstrip("/")

    async def check_health(self) -> bool:
        """Check if AI service health endpoint responds."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/health")
                return res.status_code == 200
        except Exception as e:
            logger.warning("AI Service health check failed: %s", e)
            return False

    async def analyze_resume_pdf(self, pdf_bytes: bytes, filename: str = "resume.pdf") -> Dict[str, Any]:
        """Upload PDF bytes to AI service /api/ai/resume/analyze and return structured analysis."""
        url = f"{self.base_url}/api/ai/resume/analyze"
        logger.info("Calling AI Service PDF analysis endpoint: %s", url)

        files = {
            "file": (filename, pdf_bytes, "application/pdf")
        }

        try:
            # 60s timeout for LLM extraction
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, files=files)
                
                if res.status_code == 400:
                    detail = res.json().get("detail", "Invalid file content")
                    raise AIClientError(f"AI Service validation failed: {detail}")
                elif res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")

                analysis_data = res.json()
                if not isinstance(analysis_data, dict):
                    raise AIClientError("AI Service returned non-dictionary analysis payload.")

                logger.info("Successfully received structured resume analysis from AI Service.")
                return analysis_data

        except httpx.RequestError as e:
            logger.error("Network error communicating with AI Service: %s", e)
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")
        except Exception as e:
            if isinstance(e, AIClientError):
                raise e
            logger.error("Unexpected error in AI Client: %s", e)
            raise AIClientError(f"AI Service call failed: {str(e)}")

    async def analyze_resume_text(self, text: str) -> Dict[str, Any]:
        """Send extracted resume text to AI service /api/ai/resume/analyze-text."""
        url = f"{self.base_url}/api/ai/resume/analyze-text"
        logger.info("Calling AI Service text analysis endpoint: %s", url)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json={"text": text})
                if res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")
                return res.json()
        except httpx.RequestError as e:
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")

    async def analyze_github(self, username: str) -> Dict[str, Any]:
        """Send GitHub username to AI service /api/ai/github/analyze for structured intelligence."""
        url = f"{self.base_url}/api/ai/github/analyze"
        logger.info("Calling AI Service GitHub analysis endpoint for '%s': %s", username, url)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json={"username": username})
                if res.status_code == 404:
                    raise AIClientError(f"GitHub user '{username}' not found by AI service.")
                elif res.status_code == 429:
                    raise AIClientError("GitHub API rate limit hit on AI service.")
                elif res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")
                return res.json()
        except httpx.RequestError as e:
            logger.error("Network error communicating with AI Service GitHub endpoint: %s", e)
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")

    async def analyze_leetcode(self, username: str) -> Dict[str, Any]:
        """Send LeetCode username to AI service /api/ai/leetcode/analyze for structured intelligence."""
        url = f"{self.base_url}/api/ai/leetcode/analyze"
        logger.info("Calling AI Service LeetCode analysis endpoint for '%s': %s", username, url)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json={"username": username})
                if res.status_code == 404:
                    raise AIClientError(f"LeetCode user '{username}' not found by AI service.")
                elif res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")
                return res.json()
        except httpx.RequestError as e:
            logger.error("Network error communicating with AI Service LeetCode endpoint: %s", e)
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")

    async def analyze_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send project details to AI service /api/ai/project/analyze for AST & technical evaluation."""
        url = f"{self.base_url}/api/ai/project/analyze"
        logger.info("Calling AI Service Project analysis endpoint for '%s': %s", project_data.get("title", ""), url)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=project_data)
                if res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")
                return res.json()
        except httpx.RequestError as e:
            logger.error("Network error communicating with AI Service Project endpoint: %s", e)
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")

    async def calculate_readiness(self, readiness_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send aggregated student profile & module data to AI service /api/ai/readiness/calculate."""
        url = f"{self.base_url}/api/ai/readiness/calculate"
        logger.info("Calling AI Service Placement Readiness calculation endpoint: %s", url)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=readiness_payload)
                if res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")
                return res.json()
        except httpx.RequestError as e:
            logger.error("Network error communicating with AI Service Readiness endpoint: %s", e)
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")

    async def analyze_skill_gaps(self, skill_gap_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send student profile and target role to AI service /api/ai/skills/analyze for LLM synthesis."""
        url = f"{self.base_url}/api/ai/skills/analyze"
        logger.info("Calling AI Service Skill Gap analysis endpoint: %s", url)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=skill_gap_payload)
                if res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")
                return res.json()
        except httpx.RequestError as e:
            logger.error("Network error communicating with AI Service Skill Gap endpoint: %s", e)
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")

    async def generate_roadmap(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call AI service /api/ai/roadmap/generate to create personalized 90-day roadmap."""
        url = f"{self.base_url}/api/ai/roadmap/generate"
        logger.info("Calling AI Service Roadmap Generation endpoint: %s", url)
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")
                return res.json()
        except httpx.RequestError as e:
            logger.error("Network error calling AI Service Roadmap endpoint: %s", e)
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")

    async def get_today_tasks(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call AI service /api/ai/tasks/today to fetch or calculate today's tasks."""
        url = f"{self.base_url}/api/ai/tasks/today"
        logger.info("Calling AI Service Today Tasks endpoint: %s", url)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")
                return res.json()
        except httpx.RequestError as e:
            logger.error("Network error calling AI Service Tasks endpoint: %s", e)
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")

    async def generate_interview_question(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call AI service /api/ai/interview/generate-question."""
        url = f"{self.base_url}/api/ai/interview/generate-question"
        logger.info("Calling AI Service Generate Interview Question endpoint: %s", url)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")
                return res.json()
        except httpx.RequestError as e:
            logger.error("Network error calling AI Service Generate Question endpoint: %s", e)
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")

    async def evaluate_interview_answer(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call AI service /api/ai/interview/evaluate-answer."""
        url = f"{self.base_url}/api/ai/interview/evaluate-answer"
        logger.info("Calling AI Service Evaluate Answer endpoint: %s", url)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")
                return res.json()
        except httpx.RequestError as e:
            logger.error("Network error calling AI Service Evaluate Answer endpoint: %s", e)
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")

    async def complete_interview(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call AI service /api/ai/interview/complete."""
        url = f"{self.base_url}/api/ai/interview/complete"
        logger.info("Calling AI Service Complete Interview endpoint: %s", url)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")
                return res.json()
        except httpx.RequestError as e:
            logger.error("Network error calling AI Service Complete Interview endpoint: %s", e)
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")

    async def analyze_communication(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call AI service /api/ai/communication/analyze."""
        url = f"{self.base_url}/api/ai/communication/analyze"
        logger.info("Calling AI Service Communication Analysis endpoint: %s", url)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")
                return res.json()
        except httpx.RequestError as e:
            logger.error("Network error calling AI Service Communication Analysis endpoint: %s", e)
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")

    async def chat_mentor(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call AI service /api/ai/mentor/chat."""
        url = f"{self.base_url}/api/ai/mentor/chat"
        logger.info("Calling AI Service Mentor Chat endpoint: %s", url)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    raise AIClientError(f"AI Service error HTTP {res.status_code}: {res.text[:200]}")
                return res.json()
        except httpx.RequestError as e:
            logger.error("Network error calling AI Service Mentor Chat endpoint: %s", e)
            raise AIClientError(f"AI Service unavailable: {type(e).__name__}")







