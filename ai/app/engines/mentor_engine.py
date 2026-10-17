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
                "keywords": ["dsa", "leetcode", "algorithm", "data structure", "problem", "kahn", "binary search", "bfs", "dfs", "tree", "graph", "dp"],
                "context_keys": ["leetcode_analysis", "leetcode_weak_topics", "roadmap", "progress", "skill_gaps"]
            },
            "today": {
                "keywords": ["today", "now", "focus", "work on", "next", "do today", "can i do", "should i do", "today's", "learn next", "what should i learn", "study next"],
                "context_keys": ["today_tasks", "next_recommended_task", "roadmap", "all_pending_tasks", "skill_gaps", "progress", "profile"]
            },
            "yesterday": {
                "keywords": ["yesterday", "completed yesterday", "did yesterday", "done yesterday"],
                "context_keys": ["yesterday_completed_tasks", "today_tasks", "progress", "roadmap", "profile"]
            },
            "pending": {
                "keywords": ["pending", "incomplete", "unfinished", "left", "why 84", "why", "84", "overdue", "past due", "late"],
                "context_keys": ["all_pending_tasks", "overdue_tasks", "today_tasks", "roadmap", "progress", "profile"]
            },
            "roadmap": {
                "keywords": ["roadmap", "plan", "future", "schedule", "month", "days", "day", "remaining", "how many days", "days are remaining"],
                "context_keys": ["roadmap", "today_tasks", "all_pending_tasks", "tasks_by_day", "skill_gaps", "target_role", "profile"]
            },
            "progress": {
                "keywords": ["progress", "score", "readiness", "ready", "improving"],
                "context_keys": ["readiness", "progress", "interview_results", "roadmap"]
            },
            "projects": {
                "keywords": ["github", "project", "repo", "commit", "code"],
                "context_keys": ["github_analysis", "projects", "profile"]
            },
            "skills": {
                "keywords": ["skill", "missing", "learn", "know", "tech", "gap"],
                "context_keys": ["skill_gaps", "profile", "target_role"]
            },
            "interview": {
                "keywords": ["interview", "mock", "ask me", "questions", "interview question", "behavioral", "hr", "quiz"],
                "context_keys": ["profile", "target_role", "interview_results", "skill_gaps"]
            },
            "role": {
                "keywords": ["target role", "my role", "role am i", "my target", "target position", "what role", "what is my target role"],
                "context_keys": ["profile", "target_role", "roadmap", "skill_gaps"]
            },
            "technical": {
                "keywords": ["python", "oop", "class", "encapsulation", "polymorphism", "inheritance", "abstraction", "error", "exception", "traceback", "typeerror", "indexerror", "keyerror", "fix", "code", "reverse", "algorithm", "system design", "microservice", "cache", "redis", "kafka", "api", "database", "sql", "numpy", "broadcasting", "pandas", "step by step"],
                "context_keys": ["profile", "target_role", "skill_gaps", "roadmap"]
            }
        }

    def build_context(self, message: str, context: StudentContext, conversation_history: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        Extract relevant context based on intent and conversation history. Always includes basic identifiers.
        """
        message_lower = message.lower()
        if conversation_history:
            recent_texts = " ".join([getattr(m, "content", "") or (m.get("content", "") if isinstance(m, dict) else "") for m in conversation_history[-3:]])
            search_text = f"{recent_texts.lower()} {message_lower}"
        else:
            search_text = message_lower

        selected_keys = set(["target_role", "student_name", "profile"]) # Always include profile identifiers
        
        # Check rules
        for category, rule in self.rules.items():
            if any(re.search(rf"\b{re.escape(kw)}\b", search_text) for kw in rule["keywords"]):
                selected_keys.update(rule["context_keys"])

        # Check for specific day queries like "Day 13"
        if re.search(r"\bday\s*\d+\b", search_text):
            selected_keys.update(["tasks_by_day", "roadmap", "today_tasks", "all_pending_tasks"])
                
        # If no specific intent matched or general query, provide rich balanced context
        if len(selected_keys) <= 3: 
            selected_keys.update(["roadmap", "today_tasks", "yesterday_completed_tasks", "all_pending_tasks", "tasks_by_day", "progress", "skill_gaps"])
            
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
        # 1. Filter context dynamically considering conversation history for follow-ups
        filtered_context = self.context_builder.build_context(request.message, request.student_context, request.conversation_history)
        
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
