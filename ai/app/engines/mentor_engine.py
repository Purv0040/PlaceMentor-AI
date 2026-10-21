"""
Personal AI Placement Mentor Engine.
Answers student questions using dynamically retrieved context from their placement profile.
"""
import json
import logging
import re
from typing import Any, Dict, List, Optional

from app.schemas.mentor import MentorChatRequest, MentorChatResponse, StudentContext
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ContextBuilder:
    """
    Dynamically selects relevant parts of the student context based on the user's message.
    Prevents token bloat, keeps the LLM focused on relevant evidence, and never restricts
    the model from answering arbitrary general knowledge or technical questions.
    """
    
    def __init__(self):
        # Specific intent routing rules for student placement data
        self.rules = {
            "greeting": {
                "keywords": ["hi", "hello", "hey", "greetings", "hola", "good morning", "good evening", "good afternoon"],
                "context_keys": ["student_name", "target_role"]
            },
            "resume": {
                "keywords": ["resume", "cv", "experience", "bullet", "ats", "resume score", "my resume"],
                "context_keys": ["resume_analysis", "profile", "target_role"]
            },
            "dsa_practice": {
                "keywords": ["which leetcode", "leetcode problems should i", "study on leetcode", "practice on leetcode", "my leetcode", "dsa topics should i", "topics should i practice"],
                "context_keys": ["leetcode_analysis", "leetcode_weak_topics", "roadmap", "progress", "skill_gaps"]
            },
            "today": {
                "keywords": ["today", "now", "focus", "work on", "next", "do today", "can i do", "should i do", "today's", "learn next", "what should i learn", "study next", "task 1", "first task", "first daily task"],
                "context_keys": ["today_tasks", "next_recommended_task", "roadmap", "all_pending_tasks", "skill_gaps", "progress", "profile"]
            },
            "yesterday": {
                "keywords": ["yesterday", "completed yesterday", "did yesterday", "done yesterday"],
                "context_keys": ["yesterday_completed_tasks", "today_tasks", "progress", "roadmap", "profile"]
            },
            "pending": {
                "keywords": ["pending", "incomplete", "unfinished", "left", "why 84", "why", "84", "overdue", "past due", "late", "tasks are incomplete", "how many tasks"],
                "context_keys": ["all_pending_tasks", "overdue_tasks", "today_tasks", "roadmap", "progress", "profile"]
            },
            "roadmap": {
                "keywords": ["roadmap", "plan", "future", "schedule", "month", "days", "remaining", "how many days", "days are remaining", "timeline"],
                "context_keys": ["roadmap", "today_tasks", "all_pending_tasks", "skill_gaps", "target_role", "profile"]
            },
            "progress": {
                "keywords": ["progress", "readiness", "ready", "improving", "assessment", "readiness score", "overall score"],
                "context_keys": ["readiness", "progress", "interview_results", "roadmap"]
            },
            "projects": {
                "keywords": ["github", "project", "repo", "commit", "my project", "my github", "portfolio"],
                "context_keys": ["github_analysis", "projects", "profile"]
            },
            "skills": {
                "keywords": ["skill gap", "skill gaps", "missing skill", "missing skills", "skills to learn", "what skills am i missing", "weakness"],
                "context_keys": ["skill_gaps", "profile", "target_role"]
            },
            "interview": {
                "keywords": ["interview questions", "ask me 5", "ask me questions", "mock interview", "behavioral interview", "hr interview", "quiz me"],
                "context_keys": ["profile", "target_role", "interview_results", "skill_gaps"]
            },
            "role": {
                "keywords": ["target role", "my role", "role am i", "my target", "target position", "what role", "what is my target role"],
                "context_keys": ["profile", "target_role", "roadmap", "skill_gaps"]
            },
            "self": {
                "keywords": ["tell me about myself", "tell me about me", "about myself", "my profile", "who am i"],
                "context_keys": ["profile", "skill_gaps", "progress", "today_tasks", "target_role"]
            }
        }

    def build_context(self, message: str, context: StudentContext, conversation_history: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        Extract relevant context based on intent and conversation history.
        Only includes placement roadmap and task details when relevant to the student's question.
        For general knowledge, coding, and technical questions, leaves the prompt lean and unconstrained.
        """
        message_lower = message.lower()
        if conversation_history:
            recent_texts = " ".join([getattr(m, "content", "") or (m.get("content", "") if isinstance(m, dict) else "") for m in conversation_history[-3:]])
            search_text = f"{recent_texts.lower()} {message_lower}"
        else:
            search_text = message_lower

        selected_keys = set(["target_role", "student_name"])

        # Check for specific intent match
        matched_any = False
        for category, rule in self.rules.items():
            if any(re.search(rf"\b{re.escape(kw)}\b", search_text) for kw in rule["keywords"]):
                selected_keys.update(rule["context_keys"])
                matched_any = True

        # Check for specific day queries like "Day 13"
        day_match = re.search(r"\bday\s*(\d+)\b", search_text)
        if day_match:
            selected_keys.update(["roadmap", "today_tasks", "all_pending_tasks", "tasks_by_day"])
            matched_any = True

        # Build the filtered context dictionary
        context_dict = context.model_dump(exclude_none=True)
        filtered_context = {}
        for k, v in context_dict.items():
            if k in selected_keys:
                if k == "tasks_by_day" and isinstance(v, dict):
                    # Only include the specific day queried to avoid token bloat
                    if day_match:
                        target_day_str = day_match.group(1)
                        filtered_context[k] = {target_day_str: v.get(target_day_str) or v.get(str(target_day_str)) or []}
                else:
                    filtered_context[k] = v
        
        return filtered_context


class PersonalMentorEngine:
    """
    Generates intelligent, dynamic, context-aware answers to student questions
    using Groq LLM across any technical, coding, architectural, general knowledge,
    or placement roadmap topic.
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
        self.context_builder = ContextBuilder()
        
    def chat(self, request: MentorChatRequest) -> MentorChatResponse:
        """
        Process a mentor chat request dynamically using Groq LLM.
        """
        # 1. Filter context dynamically considering conversation history for follow-ups
        filtered_context = self.context_builder.build_context(request.message, request.student_context, request.conversation_history)
        
        # 2. Prepare conversation history string if provided
        history_str = ""
        if request.conversation_history:
            history_lines = [f"{msg.role.upper()}: {msg.content}" for msg in request.conversation_history[-6:]]
            history_str = "\n".join(history_lines)
            
        # 3. Construct general-purpose system instructions
        system_instructions = (
            "You are a Personal AI Placement Mentor (PlaceMentor AI), an expert, encouraging, and elite technical mentor.\n"
            "You can answer ANY question asked by the student — across programming languages (Python, Java, C++, JavaScript, TypeScript, Go, Rust), "
            "data structures & algorithms, code debugging & bug fixes, software architecture & system design, cloud & DevOps (AWS, GCP, Azure, Docker, Kubernetes), "
            "databases (SQL, NoSQL), AI/ML & RAG, mathematics, science, general knowledge, interview preparation, and placement roadmap guidance.\n\n"
            "CRITICAL RULES & INSTRUCTIONS:\n"
            "1. DIRECT ANSWER FIRST: Answer the user's actual question directly, thoroughly, and immediately. Never evade the question or replace it with unrelated roadmap tasks.\n"
            "2. DYNAMIC SUBJECT & DEPTH: Dynamically adapt to the topic and provide the appropriate technical depth and clarity.\n"
            "3. CLEAR EXPLANATIONS: Explain concepts clearly and concisely with accessible language, intuitive analogies, and key principles.\n"
            "4. CODE & EXAMPLES: For coding questions, provide clean, idiomatic, production-grade, and syntactically valid code blocks. Explain critical lines, logic, edge cases, and Time/Space complexity ($O(N)$, $O(1)$) when relevant.\n"
            "5. DEBUGGING & ERRORS: When given an error or code snippet, identify the exact root cause, explain why it happens, and provide the corrected code. If essential code or traceback is missing, ask the student to provide the specific snippet and error.\n"
            "6. COMPARISONS: For comparisons (e.g. list vs tuple, EC2 vs S3 vs Lambda), explain core differences clearly across mutability, performance, use cases, and trade-offs. Use a markdown comparison table when helpful.\n"
            "7. MULTI-TURN & FOLLOW-UPS: For follow-up questions ('give me an example of that', 'can you simplify?', 'explain step 2'), resolve pronouns and references using the conversation history.\n"
            "8. GREETINGS: For greetings ('hi', 'hello', 'hey'), return a warm, natural, concise greeting (1-2 sentences), addressing the student by name if provided, and ask how you can help with their coding, interview prep, or placement preparation today. Do NOT force a single narrow role unless requested.\n"
            "9. STUDENT CONTEXT: Use student context (roadmap, today's tasks, readiness score, resume, skill gaps) ONLY when the user's question asks about their personal placement plan, tasks, progress, or profile. If personal data is requested but missing, state clearly that it is not yet recorded. Never hallucinate fake tasks, scores, or achievements. Never force every general question into placement roadmap advice.\n"
            "10. TONE: Elite, direct, empowering, and respectful. Avoid repetitive disclaimers, robotic preambles, or unneeded filler.\n"
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
            "Provide your response using the strictly required JSON structure matching MentorChatResponse:\n"
            "{\n"
            '  "answer": "Comprehensive, direct answer to the student question in clean Markdown",\n'
            '  "evidence": ["Factual evidence or topic highlights supporting the answer"],\n'
            '  "recommended_actions": ["Actionable next steps for the student"],\n'
            '  "related_skills": ["Key skills or concepts relevant to this question"],\n'
            '  "confidence": 0.95\n'
            "}"
        )
        
        # 4. Generate structured response with graceful text fallback
        try:
            return self.llm_service.generate_structured(
                prompt=prompt,
                response_model=MentorChatResponse
            )
        except Exception as e:
            logger.warning("generate_structured failed (%s), attempting text-mode fallback.", e)
            try:
                raw_text = self.llm_service.generate_text(prompt)
                if raw_text and raw_text.strip():
                    clean = raw_text.strip()
                    if clean.startswith("```json"):
                        clean = clean[7:]
                    elif clean.startswith("```"):
                        clean = clean[3:]
                    if clean.endswith("```"):
                        clean = clean[:-3]
                    clean = clean.strip()
                    try:
                        parsed = json.loads(clean)
                        if isinstance(parsed, dict) and "answer" in parsed:
                            return MentorChatResponse(
                                answer=parsed.get("answer", clean),
                                evidence=parsed.get("evidence") or [],
                                recommended_actions=parsed.get("recommended_actions") or [],
                                related_skills=parsed.get("related_skills") or [],
                                confidence=float(parsed.get("confidence", 0.9))
                            )
                    except Exception:
                        pass
                    return MentorChatResponse(
                        answer=raw_text.strip(),
                        evidence=[f"Topic: {request.message[:40]}"],
                        recommended_actions=["What can I do today?"],
                        related_skills=[],
                        confidence=0.85
                    )
            except Exception as e2:
                logger.error("Both generate_structured and generate_text failed: %s", e2)
                raise ValueError(f"Failed to generate mentor response: {str(e)}")
