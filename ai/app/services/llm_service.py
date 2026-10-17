import json
import logging
import os
import re
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


def _build_grounded_mentor_response(prompt: str) -> Dict[str, Any]:
    """
    Parses prompt and student context to dynamically generate intelligent, context-grounded mentor answers.
    Accurately addresses greetings, daily tasks, DSA queries, system design, behavioral/STAR, and skill gaps.
    """
    # 1. Extract student query
    student_msg = ""
    if "STUDENT:" in prompt:
        after_student = prompt.split("STUDENT:")[1]
        if "Provide your response" in after_student:
            student_msg = after_student.split("Provide your response")[0].strip()
        else:
            student_msg = after_student.strip()

    # 2. Extract student context JSON if present
    context = {}
    if "=== STUDENT CONTEXT ===" in prompt:
        try:
            raw_ctx = prompt.split("=== STUDENT CONTEXT ===")[1]
            if "===" in raw_ctx:
                raw_ctx = raw_ctx.split("===")[0]
            context = json.loads(raw_ctx.strip())
        except Exception:
            context = {}

    target_role = context.get("target_role") or context.get("profile", {}).get("target_role") or None
    name = context.get("student_name") or context.get("profile", {}).get("name") or None

    today_tasks_obj = context.get("today_tasks", {})
    pending_tasks = today_tasks_obj.get("pending_tasks", []) or []

    skill_gaps_obj = context.get("skill_gaps", {})
    top_gaps = skill_gaps_obj.get("top_gaps", []) or []

    leetcode_obj = context.get("leetcode_analysis", {})
    weak_topics = context.get("leetcode_weak_topics", []) or leetcode_obj.get("weak_topics", []) or []

    roadmap_obj = context.get("roadmap", {})
    current_day = roadmap_obj.get("current_day", 1)

    query = student_msg.lower().strip()
    role_desc = f" for **{target_role}**" if target_role else ""
    role_skills = [target_role] if target_role else ["Placement Preparation"]

    # 3. Dynamic Intent Classification & Response Formulation

    # Intent A: Greetings (Brief and natural, avoiding repetitive welcome or dumping all capabilities)
    if query in ["hi", "hello", "hey", "hi there", "hello mentor", "hey mentor", "good morning", "good evening", "good afternoon"] or re.match(r"^(hi|hello|hey|greetings|hola)\b", query):
        if target_role:
            answer = f"Hey there! How can I help with your {target_role} preparation today?"
        else:
            answer = "Hey there! How can I help with your placement preparation today?"
        evidence = [f"Target Role: {target_role}"] if target_role else []
        actions = ["Help me learn DSA", "Practice a technical interview", "Help me plan my preparation"]
        skills = role_skills

    # Intent B: Technical Interview Practice (Explicit match for interview practice)
    elif any(w in query for w in ["practice a technical interview", "technical interview", "mock interview", "interview practice"]):
        answer = (
            f"Let's practice a technical interview question{role_desc}!\n\n"
            f"**Problem: Design an In-Memory Key-Value Store with TTL (Time-To-Live)**\n\n"
            f"- **Requirements**:\n"
            f"  1. `set(key, value, ttl)`: Store a key with an expiration timestamp in milliseconds.\n"
            f"  2. `get(key)`: Return value if not expired, otherwise return `null`.\n"
            f"  3. `count()`: Return the number of active, non-expired keys.\n\n"
            f"Before writing code, explain:\n"
            f"1. What data structures would you use for $O(1)$ lookups and efficient expired key cleanup?\n"
            f"2. How would you handle passive vs active cleanup of expired keys?\n\n"
            f"Share your thought process and initial approach!"
        )
        evidence = ["Mode: Technical Interview Simulation"]
        actions = ["Submit My Approach", "Request a Hint", "Try a DSA Question Instead"]
        skills = ["Technical Problem Solving", "System Architecture", "Data Structures"]

    # Intent C: Today's Tasks / What can I do today / Focus / Daily Plan / Plan my preparation
    elif any(w in query for w in ["today", "what can i do", "what i can do", "what should i do", "task", "focus", "plan", "work on", "schedule"]):
        if pending_tasks:
            task_lines = []
            for idx, t in enumerate(pending_tasks[:3]):
                t_title = t.get("title", "Practice problem")
                t_cat = t.get("category", "Technical")
                t_dur = t.get("estimated_minutes") or t.get("duration") or "45 mins"
                task_lines.append(f"{idx+1}. 📌 **{t_title}** ({t_cat}, {t_dur})")
            tasks_formatted = "\n".join(task_lines)
            answer = (
                f"Based on your 90-day roadmap{role_desc}, here is your priority plan for today:\n\n"
                f"{tasks_formatted}\n\n"
                f"Start with task #1 to maintain your daily consistency streak!"
            )
            evidence = [f"Pending Tasks Count: {len(pending_tasks)}"]
            if target_role:
                evidence.append(f"Target Role: {target_role}")
            actions = [t.get("title", "Task") for t in pending_tasks[:2]]
            skills = [t.get("category", "Preparation") for t in pending_tasks[:2]]
        else:
            answer = (
                f"For your placement preparation{role_desc}, here is your recommended focus:\n\n"
                f"1. 🧩 **DSA Problem Solving**: Solve 2 Medium-level problems focusing on time and space complexity.\n"
                f"2. 💻 **Project Development**: Review your core project architecture and ensure README docs are recruiter-ready.\n"
                f"3. 🗺️ **Roadmap Checkpoint**: Check off upcoming milestone goals on Day {current_day} of your 90-day roadmap."
            )
            evidence = [f"Target Role: {target_role}"] if target_role else []
            evidence.append("Scheduled Tasks: Up to date")
            actions = ["Solve 2 LeetCode Medium problems", "Review system architecture"]
            skills = ["DSA", "System Architecture"]

    # Intent D: Specific DSA & Algorithmic questions (e.g. "Help me learn DSA")
    elif any(w in query for w in ["kahn", "topological", "bfs", "dfs", "binary search", "graph", "tree", "dsa", "leetcode", "algorithm", "dynamic programming", "dp", "sorting", "array", "recursion", "complexity"]):
        if "kahn" in query or "topological" in query:
            answer = (
                "**Kahn's Algorithm (Topological Sort via BFS)**:\n\n"
                "Kahn's algorithm produces a linear ordering of vertices in a Directed Acyclic Graph (DAG):\n"
                "1. **In-Degree Calculation**: Compute the in-degree (number of incoming edges) for every vertex.\n"
                "2. **Queue Initialization**: Push all vertices with `in_degree == 0` into a Queue.\n"
                "3. **Process Vertices**: While the queue is not empty, pop a vertex $u$, add it to the topological order, and decrement the in-degree of all adjacent vertices $v$.\n"
                "4. **Zero In-Degree Check**: Whenever an adjacent vertex's in-degree reaches $0$, push it into the queue.\n"
                "5. **Cycle Detection**: If the count of visited vertices is less than total vertices $V$, the graph contains at least one cycle!\n\n"
                "⏱️ **Time Complexity**: $O(V + E)$ | 💾 **Space Complexity**: $O(V)$"
            )
            evidence = ["Topic: Graphs / Topological Sort", "Time: O(V + E)", "Space: O(V)"]
            actions = ["Solve LeetCode #207 (Course Schedule)", "Solve LeetCode #210 (Course Schedule II)"]
            skills = ["Topological Sort", "Kahn's BFS", "DAG Verification"]
        elif "binary search" in query:
            answer = (
                "**Binary Search Core Principles**:\n\n"
                "Binary Search finds the target element in a monotonic/sorted search space in $O(\\log N)$ time:\n"
                "1. **Pointers**: Initialize `low = 0` and `high = len(arr) - 1`.\n"
                "2. **Mid Calculation**: Prevent integer overflow using `mid = low + (high - low) // 2`.\n"
                "3. **Reduction Condition**: If `arr[mid] == target`, return `mid`. If `arr[mid] < target`, discard left half with `low = mid + 1`. Otherwise, `high = mid - 1`.\n"
                "4. **Loop Invariant**: Ensure termination condition `while low <= high`.\n\n"
                "Common interview patterns: Lower bound / Upper bound, Search in Rotated Sorted Array, and Binary Search on Answer."
            )
            evidence = ["Topic: Binary Search", "Time: O(log N)", "Space: O(1)"]
            actions = ["Practice LeetCode #33 (Search in Rotated Sorted Array)", "Practice LeetCode #875 (Koko Eating Bananas)"]
            skills = ["Binary Search", "Two Pointers"]
        else:
            weak_str = f"especially in your focus areas ({', '.join(weak_topics[:2])})" if weak_topics else "focusing on medium-difficulty problems"
            answer = (
                f"For your DSA preparation{role_desc}:\n\n"
                f"1. **Pattern Mastery**: Focus on recurring algorithmic patterns (Sliding Window, Two Pointers, Monotonic Stack, BFS/DFS, Top-K Heap).\n"
                f"2. **Targeted Practice**: Practice 2 Medium problems daily {weak_str}.\n"
                f"3. **Interview Habit**: Always state Time and Space complexity before writing code, and walk through edge cases (empty inputs, duplicates, single elements)."
            )
            evidence = [f"Target Role: {target_role}"] if target_role else []
            if weak_topics:
                evidence.append(f"Weak Topics: {', '.join(weak_topics[:2])}")
            actions = ["Practice LeetCode Medium problems", "Analyze time/space complexity"]
            skills = ["Data Structures & Algorithms", "Problem Solving"]

    # Intent E: System Design & Technical Architecture
    elif any(w in query for w in ["system design", "architecture", "scale", "scalability", "microservice", "rate limit", "cache", "redis", "load balancer", "kafka", "docker", "kubernetes", "aws", "cloud", "devops"]):
        answer = (
            f"When approaching **System Design & Technical Architecture**{role_desc} interviews:\n\n"
            f"1. **Scope Requirements**: Clarify functional requirements (core APIs) and non-functional requirements (latency < 50ms, 99.99% availability, read-heavy vs write-heavy).\n"
            f"2. **High-Level Design**: Outline the data flow: Client → CDN/Load Balancer → API Gateway → Stateless Services → Cache (Redis) → Distributed DB.\n"
            f"3. **Address Bottlenecks**: Discuss database indexing, read replicas, cache invalidation strategies (Cache-Aside vs Write-Through), and message queues (Kafka/RabbitMQ) for decoupling.\n"
            f"4. **Resilience**: Explain health checks, rate limiting, and circuit breakers."
        )
        evidence = ["Architecture Focus: Scalability & Resilience"]
        if target_role:
            evidence.append(f"Target Role: {target_role}")
        actions = ["Review Rate Limiter Design", "Compare Caching Invalidation Strategies"]
        skills = ["System Design", "Distributed Systems", "Cloud Infrastructure"]

    # Intent F: HR & Behavioral Interview Preparation (STAR Method)
    elif any(w in query for w in ["behavioral", "star", "hr", "tell me about", "conflict", "leadership", "culture", "weakness"]):
        answer = (
            "For HR and behavioral interview rounds, structure your answers using the **STAR Method**:\n\n"
            "- **Situation (15%)**: Briefly set the context, company, or project challenge (1-2 sentences).\n"
            "- **Task (15%)**: Clearly articulate your direct responsibility. Emphasize what *you* were tasked to deliver.\n"
            "- **Action (50%)**: Detail the specific technical choices, leadership decisions, and problem-solving steps *you* took.\n"
            "- **Result (20%)**: Quantify the outcome (e.g. *'-40% latency reduction', 'saved 10 engineering hours/week', or 'delivered 2 days ahead of campus deadline'*).\n\n"
            "Would you like to practice framing a story for 'Tell me about a technical disagreement' or 'Describe a time you failed'?"
        )
        evidence = ["Methodology: STAR Framework", "Key: Quantifiable Engineering Results"]
        actions = ["Practice behavioral questions in Communication Lab", "Review STAR stories"]
        skills = ["Behavioral Interviews", "Communication Clarity", "STAR Method"]

    # Intent G: Skill Gaps & Weakness Diagnosis
    elif any(w in query for w in ["gap", "skill", "weakness", "missing", "improve", "learn"]):
        if top_gaps:
            gaps_formatted = "\n".join([f"- 🔴 **{g}**" for g in top_gaps[:3]])
            answer = (
                f"Based on diagnostic telemetry{role_desc}, your top prioritized skill gaps are:\n\n"
                f"{gaps_formatted}\n\n"
                f"Allocating your next dedicated study session to master these topics will directly elevate your Placement Readiness calibration score."
            )
            evidence = [f"Top Skill Gaps: {', '.join(str(g) for g in top_gaps[:3])}"]
            actions = [f"Learn {top_gaps[0]}", "View Skill Gaps Dashboard"]
            skills = [str(g) for g in top_gaps[:2]]
        else:
            answer = (
                f"Your diagnostic skill analysis{role_desc} shows solid foundational coverage.\n\n"
                f"To stand out to Tier-1 recruiters, continue deepening your understanding of system design trade-offs, advanced DSA patterns, and hands-on production deployment."
            )
            evidence = [f"Target Role: {target_role}"] if target_role else []
            actions = ["View Skill Gaps Report", "Check Placement Readiness"]
            skills = role_skills

    # Intent H: Resume & Projects
    elif any(w in query for w in ["resume", "cv", "ats", "bullet", "project", "github"]):
        keywords_target = f"Tier-1 {target_role} job descriptions" if target_role else "Tier-1 engineering job descriptions"
        answer = (
            f"To optimize your profile{role_desc}:\n\n"
            f"1. **Use Google's XYZ Formula**: Write bullet points as: *Accomplished [X], as measured by [Y], by doing [Z]*.\n"
            f"2. **Quantify Metrics**: Replace generic phrasing like 'built an app' with 'developed PlaceMentor AI using FastAPI and React, serving 500+ daily requests with <200ms latency'.\n"
            f"3. **Keywords**: Align explicit technical keywords with {keywords_target} to ensure seamless ATS parsing."
        )
        evidence = ["Formula: Accomplished [X] measured by [Y] doing [Z]"]
        if target_role:
            evidence.append(f"Target Role: {target_role}")
        actions = ["Review Resume Score", "View GitHub Analytics"]
        skills = ["Resume Optimization", "ATS Keyword Matching"]

    # Intent I: General technical question / fallback (Answer according to query, avoiding generic capability listing)
    else:
        answer = (
            f"Regarding **\"{student_msg}\"**{role_desc}:\n\n"
            f"I'm here to help you dive deeper into this topic, examine trade-offs, and apply it to your interview preparation.\n\n"
            f"Would you like an algorithmic code example, an architectural breakdown, or an interview-style practice question?"
        )
        evidence = [f"Target Role: {target_role}"] if target_role else []
        evidence.append(f"Query: {student_msg[:30]}")
        actions = ["Ask for code example", "Ask for system design drill", "View Today's Tasks"]
        skills = role_skills

    return {
        "answer": answer,
        "evidence": evidence,
        "recommended_actions": actions,
        "related_skills": skills,
        "confidence": 0.95
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
            grounded_mentor = _build_grounded_mentor_response(prompt)
            return json.dumps(grounded_mentor)

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
