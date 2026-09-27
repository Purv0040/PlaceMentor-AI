import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.interview_repository import InterviewRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.github_repository import GitHubRepository
from app.repositories.leetcode_repository import LeetCodeRepository
from app.repositories.skill_gap_repository import SkillGapRepository
from app.repositories.roadmap_repository import RoadmapRepository
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)


class InterviewService:
    def __init__(self, db: AsyncIOMotorDatabase, ai_client: Optional[AIClient] = None) -> None:
        self.interview_repo = InterviewRepository(db)
        self.profile_repo = ProfileRepository(db)
        self.resume_repo = ResumeRepository(db)
        self.project_repo = ProjectRepository(db)
        self.github_repo = GitHubRepository(db)
        self.leetcode_repo = LeetCodeRepository(db)
        self.skill_gap_repo = SkillGapRepository(db)
        self.roadmap_repo = RoadmapRepository(db)
        self.ai_client = ai_client or AIClient()

    async def _build_student_context(self, user_id: str) -> Dict[str, Any]:
        """Collect all student background intelligence for grounded AI questioning."""
        profile = await self.profile_repo.get_by_user_id(user_id) or {}
        resume = await self.resume_repo.find_active_by_user(user_id) or {}
        projects = await self.project_repo.find_by_user_id(user_id)
        github = await self.github_repo.find_by_user_id(user_id) or {}
        leetcode = await self.leetcode_repo.find_by_user_id(user_id) or {}
        skill_gaps = await self.skill_gap_repo.get_latest_by_user(user_id) or {}
        roadmap = await self.roadmap_repo.get_active_by_user_id(user_id) or {}

        return {
            "profile": profile,
            "resume": resume,
            "projects": projects,
            "github": github,
            "leetcode": leetcode,
            "skill_gaps": skill_gaps,
            "roadmap": roadmap,
        }

    async def start_mock_interview(
        self,
        user_id: str,
        interview_type: str = "technical",
        difficulty: str = "medium",
        question_count: int = 5,
        target_role_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Start a new mock interview session and generate the first adaptive question."""
        # 1. Load profile & student context
        profile = await self.profile_repo.get_by_user_id(user_id) or {}
        target_role = target_role_override or profile.get("target_role") or "Backend Developer"
        student_context = await self._build_student_context(user_id)

        interview_id = f"int_{user_id}_{int(datetime.now(timezone.utc).timestamp())}_{uuid.uuid4().hex[:4]}"

        # 2. Create interview session record
        session_data = {
            "interview_id": interview_id,
            "user_id": user_id,
            "target_role": target_role,
            "interview_type": interview_type,
            "difficulty": difficulty,
            "status": "active",
            "total_questions": question_count,
            "current_question": 1,
            "started_at": datetime.now(timezone.utc),
            "completed_at": None,
            "overall_score": None,
            "category_scores": {},
            "evaluation": None,
        }
        session = await self.interview_repo.create_session(session_data)

        # 3. Generate first question via AI service or local fallback
        q_payload = {
            "target_role": target_role,
            "interview_type": interview_type,
            "difficulty": difficulty,
            "question_number": 1,
            "total_questions": question_count,
            "previous_qa": [],
            "student_context": student_context,
        }

        try:
            q_res = await self.ai_client.generate_interview_question(q_payload)
        except AIClientError as e:
            logger.warning("AI Service unavailable for question generation (%s), using local fallback engine.", e)
            from app.engines.interview_engine import AIInterviewEngine
            q_res = AIInterviewEngine().generate_question(q_payload)

        # 4. Save question to MongoDB
        q_data = {
            "question_id": q_res.get("question_id") or f"q_{interview_id}_1",
            "interview_id": interview_id,
            "user_id": user_id,
            "question_number": 1,
            "question": q_res.get("question", "Describe your technical experience."),
            "category": q_res.get("category", "Technical"),
            "skill": q_res.get("skill", "Core"),
            "difficulty": q_res.get("difficulty", difficulty),
            "expected_focus": q_res.get("expected_focus", "Core concepts"),
            "hint": q_res.get("hint"),
            "answer": None,
            "evaluation": None,
        }
        created_q = await self.interview_repo.create_question(q_data)

        session["current_question_data"] = created_q
        return session

    async def get_current_question(self, interview_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch current question for active interview session."""
        session = await self.interview_repo.get_session_by_id(interview_id, user_id=user_id)
        if not session:
            return None

        questions = await self.interview_repo.get_questions_for_interview(interview_id, user_id=user_id)
        current_num = session.get("current_question", 1)
        
        current_q = next((q for q in questions if q.get("question_number") == current_num), None)
        if not current_q and questions:
            current_q = questions[-1]

        return {
            "session": session,
            "question": current_q,
        }

    async def submit_answer(self, interview_id: str, user_id: str, answer: str) -> Dict[str, Any]:
        """Submit answer for current question, evaluate it, and adaptively generate next question or complete."""
        session = await self.interview_repo.get_session_by_id(interview_id, user_id=user_id)
        if not session:
            raise ValueError("Interview session not found.")

        if session.get("status") == "completed":
            raise ValueError("Interview session is already completed.")

        questions = await self.interview_repo.get_questions_for_interview(interview_id, user_id=user_id)
        current_num = session.get("current_question", 1)
        current_q = next((q for q in questions if q.get("question_number") == current_num), None)
        
        if not current_q:
            raise ValueError(f"No active question found for question number {current_num}.")

        student_context = await self._build_student_context(user_id)

        # Build Q&A history
        previous_qa = []
        for q in questions:
            if q.get("answer"):
                previous_qa.append({
                    "question_number": q.get("question_number"),
                    "question": q.get("question"),
                    "category": q.get("category"),
                    "skill": q.get("skill"),
                    "answer": q.get("answer"),
                    "evaluation": q.get("evaluation"),
                })

        # Evaluate answer via AI Service or fallback
        eval_payload = {
            "question": current_q.get("question", ""),
            "category": current_q.get("category", "Technical"),
            "skill": current_q.get("skill", "Core"),
            "difficulty": current_q.get("difficulty", "medium"),
            "expected_focus": current_q.get("expected_focus", ""),
            "answer": answer,
            "previous_qa": previous_qa,
            "student_context": student_context,
            "question_number": current_num,
            "total_questions": session.get("total_questions", 5),
        }

        try:
            eval_res = await self.ai_client.evaluate_interview_answer(eval_payload)
        except AIClientError as e:
            logger.warning("AI Service unavailable for answer evaluation (%s), using local fallback engine.", e)
            from app.engines.interview_engine import AIInterviewEngine
            eval_res = AIInterviewEngine().evaluate_answer(eval_payload)

        # Update question in DB
        updated_q = await self.interview_repo.update_question_answer(
            question_id=current_q["question_id"],
            user_id=user_id,
            answer=answer,
            evaluation=eval_res,
        )

        total_q_count = session.get("total_questions", 5)

        if current_num < total_q_count:
            # Generate next question
            next_num = current_num + 1
            previous_qa.append({
                "question_number": current_num,
                "question": current_q.get("question"),
                "category": current_q.get("category"),
                "skill": current_q.get("skill"),
                "answer": answer,
                "evaluation": eval_res,
            })

            q_payload = {
                "target_role": session.get("target_role", "Backend Developer"),
                "interview_type": session.get("interview_type", "technical"),
                "difficulty": session.get("difficulty", "medium"),
                "question_number": next_num,
                "total_questions": total_q_count,
                "previous_qa": previous_qa,
                "student_context": student_context,
            }

            try:
                next_q_res = await self.ai_client.generate_interview_question(q_payload)
            except AIClientError as e:
                logger.warning("AI Service unavailable for next question generation (%s), using local fallback.", e)
                from app.engines.interview_engine import AIInterviewEngine
                next_q_res = AIInterviewEngine().generate_question(q_payload)

            next_q_data = {
                "question_id": next_q_res.get("question_id") or f"q_{interview_id}_{next_num}",
                "interview_id": interview_id,
                "user_id": user_id,
                "question_number": next_num,
                "question": next_q_res.get("question"),
                "category": next_q_res.get("category", "Technical"),
                "skill": next_q_res.get("skill", "Core"),
                "difficulty": next_q_res.get("difficulty", "medium"),
                "expected_focus": next_q_res.get("expected_focus", ""),
                "hint": next_q_res.get("hint"),
                "answer": None,
                "evaluation": None,
            }
            created_next_q = await self.interview_repo.create_question(next_q_data)

            # Update session status & current_question
            await self.interview_repo.update_session(interview_id, user_id, {"current_question": next_num})

            return {
                "status": "in_progress",
                "evaluation": eval_res,
                "completed_question": updated_q,
                "next_question": created_next_q,
                "is_last_question": False,
            }
        else:
            # Interview complete! Calculate summary
            completed_result = await self.complete_interview(interview_id, user_id)
            return {
                "status": "completed",
                "evaluation": eval_res,
                "completed_question": updated_q,
                "next_question": None,
                "is_last_question": True,
                "session_result": completed_result,
            }

    async def complete_interview(self, interview_id: str, user_id: str) -> Dict[str, Any]:
        """Finalize interview session, calculate overall score, and store final result."""
        session = await self.interview_repo.get_session_by_id(interview_id, user_id=user_id)
        if not session:
            raise ValueError("Interview session not found.")

        questions = await self.interview_repo.get_questions_for_interview(interview_id, user_id=user_id)
        student_context = await self._build_student_context(user_id)

        qna_history = []
        for q in questions:
            qna_history.append({
                "question_number": q.get("question_number"),
                "question": q.get("question"),
                "category": q.get("category"),
                "skill": q.get("skill"),
                "answer": q.get("answer"),
                "evaluation": q.get("evaluation"),
            })

        complete_payload = {
            "target_role": session.get("target_role", "Backend Developer"),
            "interview_type": session.get("interview_type", "technical"),
            "qna_history": qna_history,
            "student_context": student_context,
        }

        try:
            summary_res = await self.ai_client.complete_interview(complete_payload)
        except AIClientError as e:
            logger.warning("AI Service unavailable for interview completion (%s), using local fallback.", e)
            from app.engines.interview_engine import AIInterviewEngine
            summary_res = AIInterviewEngine().complete_interview(complete_payload)

        now = datetime.now(timezone.utc)
        update_data = {
            "status": "completed",
            "completed_at": now,
            "overall_score": summary_res.get("overall_score", 75),
            "category_scores": summary_res.get("category_scores", {}),
            "evaluation": summary_res,
        }
        updated_session = await self.interview_repo.update_session(interview_id, user_id, update_data)
        
        return {
            "interview_id": interview_id,
            "target_role": session.get("target_role"),
            "interview_type": session.get("interview_type"),
            "overall_score": summary_res.get("overall_score", 75),
            "category_scores": summary_res.get("category_scores", {}),
            "strengths": summary_res.get("strengths", []),
            "weaknesses": summary_res.get("weaknesses", []),
            "recommendations": summary_res.get("recommendations", []),
            "technical_gaps": summary_res.get("technical_gaps", []),
            "communication_feedback": summary_res.get("communication_feedback", {}),
            "completed_at": now,
        }

    async def get_session_by_id(self, interview_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.interview_repo.get_session_by_id(interview_id, user_id=user_id)

    async def get_interview_questions(self, interview_id: str, user_id: str) -> List[Dict[str, Any]]:
        return await self.interview_repo.get_questions_for_interview(interview_id, user_id=user_id)

    async def get_interview_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return await self.interview_repo.get_history_by_user_id(user_id, limit=limit)
