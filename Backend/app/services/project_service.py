import logging
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.project_repository import ProjectRepository
from app.repositories.github_repository import GitHubRepository
from app.schemas.project import ProjectCreateRequest, ProjectUpdateRequest
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)

COMMON_TECH_MAP = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "react.js": "React",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "docker": "Docker",
    "mongodb": "MongoDB",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "redis": "Redis",
    "go": "Go",
    "golang": "Go",
    "c++": "C++",
    "c#": "C#",
    "java": "Java",
    "html": "HTML",
    "css": "CSS",
    "tailwindcss": "TailwindCSS",
    "graphql": "GraphQL",
    "grpc": "gRPC",
    "rabbitmq": "RabbitMQ",
    "kafka": "Apache Kafka",
    "kubernetes": "Kubernetes",
    "aws": "AWS"
}


class ProjectService:
    """Service layer for Project Intelligence CRUD and AI analysis."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        ai_client: Optional[AIClient] = None
    ) -> None:
        self.db = db
        self.repo = ProjectRepository(db)
        self.github_repo = GitHubRepository(db)
        self.ai_client = ai_client or AIClient()

    @staticmethod
    def normalize_technologies(tech_list: List[str]) -> List[str]:
        """Normalize and deduplicate technology names."""
        normalized: List[str] = []
        seen = set()

        for t in tech_list:
            clean = t.strip()
            if not clean:
                continue
            canonical = COMMON_TECH_MAP.get(clean.lower(), clean)
            if canonical.lower() not in seen:
                seen.add(canonical.lower())
                normalized.append(canonical)
        return normalized

    async def create_project(self, user_id: str, project_in: ProjectCreateRequest) -> Dict[str, Any]:
        """Create a new student project with technology normalization and initial STAR bullets."""
        clean_techs = self.normalize_technologies(project_in.technologies)
        clean_arch = [a.strip() for a in project_in.architectureTags if a.strip()]

        github_url = (project_in.githubUrl or (project_in.links.github if project_in.links else None) or "").strip()
        live_url = (project_in.liveUrl or (project_in.links.live if project_in.links else None) or "").strip()

        # Generate initial STAR bullet evidence if not provided
        tech_str = ", ".join(clean_techs[:3]) if clean_techs else "modern web frameworks"
        initial_bullets = [
            f"Engineered {project_in.title} utilizing {tech_str}, delivering modular code architecture and sub-200ms latency.",
            f"Integrated robust data validation and error handling across application components."
        ]

        # Check GitHub connection if GitHub URL is provided
        github_info = {"repository_id": None, "repository_url": github_url or None, "connected": False}
        if github_url and "github.com" in github_url:
            gh_profile = await self.github_repo.find_by_user_id(user_id)
            if gh_profile:
                github_info["connected"] = True

        project_dict = {
            "title": project_in.title.strip(),
            "description": project_in.description.strip(),
            "category": project_in.category or "Full Stack / AI",
            "role": project_in.role.strip() if project_in.role else None,
            "duration": project_in.duration.dict() if project_in.duration else {"start_date": None, "end_date": None},
            "technologies": clean_techs,
            "features": project_in.features,
            "achievements": project_in.achievements,
            "architectureTags": clean_arch or ["REST API", "Microservices"],
            "links": {
                "github": github_url or None,
                "live": live_url or None,
                "demo": project_in.links.demo if project_in.links else None
            },
            "githubUrl": github_url or None,
            "liveUrl": live_url or None,
            "github": github_info,
            "status": "active",
            "is_featured": project_in.is_featured,
            "score": min(95, 75 + len(clean_techs) * 3 + (5 if github_url else 0)),
            "scoreBadge": "Production Grade" if len(clean_techs) >= 4 else "System Architect",
            "complexityScore": min(95, 75 + len(clean_techs) * 3),
            "evidenceBullets": initial_bullets,
            "analysis": None,
            "analysis_status": "not_analyzed",
            "analysis_version": "1.0"
        }

        created = await self.repo.create_project(user_id, project_dict)
        logger.info("Created project '%s' (%s) for user %s", created["title"], created["id"], user_id)
        return created

    async def get_user_projects(self, user_id: str, include_archived: bool = False) -> List[Dict[str, Any]]:
        """List all active projects for the authenticated user."""
        return await self.repo.find_by_user_id(user_id, include_archived=include_archived)

    async def get_project_by_id(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Fetch project details enforcing strict user ownership."""
        project = await self.repo.find_by_id(project_id, user_id=user_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied."
            )
        return project

    async def update_project(self, project_id: str, user_id: str, project_in: ProjectUpdateRequest) -> Dict[str, Any]:
        """Update existing project fields and mark analysis stale if core content changes."""
        existing = await self.get_project_by_id(project_id, user_id)

        update_dict: Dict[str, Any] = {}
        if project_in.title is not None:
            update_dict["title"] = project_in.title.strip()
        if project_in.description is not None:
            update_dict["description"] = project_in.description.strip()
        if project_in.category is not None:
            update_dict["category"] = project_in.category
        if project_in.role is not None:
            update_dict["role"] = project_in.role.strip()
        if project_in.duration is not None:
            update_dict["duration"] = project_in.duration.dict()
        if project_in.technologies is not None:
            update_dict["technologies"] = self.normalize_technologies(project_in.technologies)
        if project_in.features is not None:
            update_dict["features"] = project_in.features
        if project_in.achievements is not None:
            update_dict["achievements"] = project_in.achievements
        if project_in.architectureTags is not None:
            update_dict["architectureTags"] = [a.strip() for a in project_in.architectureTags if a.strip()]

        if project_in.githubUrl is not None:
            update_dict["githubUrl"] = project_in.githubUrl.strip()
        if project_in.liveUrl is not None:
            update_dict["liveUrl"] = project_in.liveUrl.strip()
        if project_in.links is not None:
            update_dict["links"] = project_in.links.dict()
        if project_in.is_featured is not None:
            update_dict["is_featured"] = project_in.is_featured
        if project_in.status is not None:
            update_dict["status"] = project_in.status

        # Mark previous AI analysis as stale if core project attributes modified
        if existing.get("analysis_status") == "completed":
            if any(k in update_dict for k in ["title", "description", "technologies", "architectureTags"]):
                update_dict["analysis_status"] = "stale"

        updated = await self.repo.update_project(project_id, user_id, update_dict)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update project."
            )
        logger.info("Updated project %s for user %s", project_id, user_id)
        return updated

    async def delete_project(self, project_id: str, user_id: str, soft_delete: bool = True) -> bool:
        """Delete/archive project with ownership protection."""
        existing = await self.get_project_by_id(project_id, user_id)
        deleted = await self.repo.delete_project(project_id, user_id, soft_delete=soft_delete)
        logger.info("Deleted project %s for user %s", project_id, user_id)
        return deleted

    async def toggle_featured(self, project_id: str, user_id: str, is_featured: bool) -> Dict[str, Any]:
        """Toggle featured state for a project."""
        await self.get_project_by_id(project_id, user_id)
        updated = await self.repo.toggle_featured(project_id, user_id, is_featured)
        return updated or await self.get_project_by_id(project_id, user_id)

    async def analyze_project(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Trigger AI Project Intelligence analysis and save results."""
        project = await self.get_project_by_id(project_id, user_id)

        payload = {
            "title": project["title"],
            "description": project["description"],
            "category": project.get("category"),
            "role": project.get("role"),
            "technologies": project.get("technologies", []),
            "architectureTags": project.get("architectureTags", []),
            "github_url": project.get("githubUrl")
        }

        await self.repo.update_analysis_status(project_id, user_id, "analyzing")

        try:
            ai_result = await self.ai_client.analyze_project(payload)
        except AIClientError as e:
            logger.error("AI Project Analysis failed for project %s: %s", project_id, e)
            await self.repo.update_analysis_status(project_id, user_id, "failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI Project Analysis failed: {str(e)}"
            )

        saved = await self.repo.save_analysis(project_id, user_id, ai_result, version="1.0")
        if not saved:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save project analysis result."
            )

        logger.info("Successfully analyzed project %s for user %s", project_id, user_id)
        return await self.get_project_by_id(project_id, user_id)

    async def get_project_analysis(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Retrieve stored AI analysis payload for a project."""
        project = await self.get_project_by_id(project_id, user_id)
        analysis = project.get("analysis")
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project AI analysis has not been generated yet. Trigger analysis first."
            )
        return {
            "project_id": project_id,
            "user_id": user_id,
            "analysis_status": project.get("analysis_status", "completed"),
            "analysis_version": project.get("analysis_version", "1.0"),
            "analyzed_at": project.get("updated_at"),
            "analysis": analysis
        }
