"""
Personal AI Placement Mentor Engine.
Answers student questions using dynamically retrieved context from their placement profile.
"""
import re
from typing import Any, Dict, List, Optional
import json

from app.schemas.mentor import MentorChatRequest, MentorChatResponse, StudentContext
from app.services.llm_service import LLMService


class ContextBuilder:
    """
    Dynamically selects relevant parts of the student context based on the user's message.
    Prevents token bloat and keeps the LLM focused on relevant evidence.
    """
    
    def __init__(self):
        # Keyword-based intent routing rules
        self.rules = {
            "resume": {
                "keywords": ["resume", "cv", "experience", "bullet", "ats"],
                "context_keys": ["resume_analysis", "profile"]
            },
            "dsa": {
                "keywords": ["dsa", "leetcode", "algorithm", "data structure", "problem"],
                "context_keys": ["leetcode_analysis", "roadmap", "progress", "skill_gaps"]
            },
            "today": {
                "keywords": ["today", "now", "focus", "work on", "next"],
                "context_keys": ["today_tasks", "roadmap", "skill_gaps", "progress"]
            },
            "roadmap": {
                "keywords": ["roadmap", "plan", "future", "schedule", "month", "days"],
                "context_keys": ["roadmap", "skill_gaps", "target_role"]
            },
            "progress": {
                "keywords": ["progress", "score", "readiness", "ready", "improving"],
                "context_keys": ["readiness", "progress", "interview_results"]
            },
            "projects": {
                "keywords": ["github", "project", "repo", "commit", "code"],
                "context_keys": ["github_analysis", "projects", "profile"]
            },
            "skills": {
                "keywords": ["skill", "missing", "learn", "know", "tech"],
                "context_keys": ["skill_gaps", "profile", "target_role"]
            }
        }

    def build_context(self, message: str, context: StudentContext) -> Dict[str, Any]:
        """
        Extract relevant context based on intent. Always includes basic identifiers.
        """
        message_lower = message.lower()
        selected_keys = set(["target_role"]) # Always include target role
        
        # Check rules
        for category, rule in self.rules.items():
            if any(re.search(rf"\b{kw}\b", message_lower) for kw in rule["keywords"]):
                selected_keys.update(rule["context_keys"])
                
        # If no specific intent matched, provide a balanced general context
        if len(selected_keys) == 1: 
            selected_keys.update(["profile", "skill_gaps", "progress", "today_tasks"])
            
        # Build the filtered context dictionary
        context_dict = context.model_dump(exclude_none=True)
        filtered_context = {k: v for k, v in context_dict.items() if k in selected_keys}
        
        return filtered_context


class PersonalMentorEngine:
    """
    Generates evidence-backed responses to student queries using strict context boundaries.
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
        self.context_builder = ContextBuilder()
        
    def chat(self, request: MentorChatRequest) -> MentorChatResponse:
        """
        Process a mentor chat request.
        """
        # 1. Filter context dynamically
        filtered_context = self.context_builder.build_context(request.message, request.student_context)
        
        # 2. Prepare conversation history string if provided
        history_str = ""
        if request.conversation_history:
            history_lines = [f"{msg.role.upper()}: {msg.content}" for msg in request.conversation_history[-5:]]
            history_str = "\n".join(history_lines)
            
        # 3. Construct the prompt
        system_instructions = (
            "You are a Personal AI Placement Mentor for a student preparing for technical placements. "
            "You must answer their questions using ONLY the provided student context data.\n"
            "CRITICAL RULES:\n"
            "1. Do NOT behave like a generic chatbot. Your advice must be highly specific to the student's actual metrics, gaps, and roadmap.\n"
            "2. Distinguish known facts (evidence) from recommendations.\n"
            "3. NEVER invent or hallucinate student achievements, scores, or skills.\n"
            "4. If the required information to answer the question is unavailable in the context, explicitly state that the information is unavailable.\n"
            "5. Maintain an encouraging but realistic and professional tone."
        )
        
        context_str = json.dumps(filtered_context, indent=2)
        
        prompt = (
            f"{system_instructions}\n\n"
            "=== STUDENT CONTEXT ===\n"
            f"{context_str}\n\n"
        )
        
        if history_str:
            prompt += (
                "=== CONVERSATION HISTORY ===\n"
                f"{history_str}\n\n"
            )
            
        prompt += (
            "=== CURRENT QUESTION ===\n"
            f"STUDENT: {request.message}\n\n"
            "Provide your response using the strictly required JSON structure."
        )
        
        # 4. Generate structured response
        try:
            response = self.llm_service.generate_structured(
                prompt=prompt,
                response_model=MentorChatResponse
            )
            return response
        except Exception as e:
            raise ValueError(f"Failed to generate mentor response: {str(e)}")
