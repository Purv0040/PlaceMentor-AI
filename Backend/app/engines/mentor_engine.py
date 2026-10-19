import logging
import re
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class AIMentorEngine:
    """Local fallback mentor engine when standalone AI service is unavailable."""

    def __init__(self, llm_service: Optional[Any] = None) -> None:
        self.llm_service = llm_service
        self.rules = {
            "resume": ["resume", "cv", "ats", "formatting", "experience", "bullet"],
            "github": ["github", "git", "commit", "repo", "repository", "open source"],
            "leetcode": ["leetcode", "dsa", "algorithm", "problem", "solve", "tree", "graph", "dp", "dynamic programming"],
            "projects": ["project", "architecture", "microservice", "portfolio", "build", "system design project"],
            "readiness": ["readiness", "score", "ready", "assessment", "tier", "placement readiness"],
            "skill_gap": ["skill", "gap", "missing", "weakness", "weak topic", "learn", "study"],
            "daily_plan": ["today", "now", "task", "schedule", "work on", "do today"],
            "roadmap": ["roadmap", "phase", "week", "month", "plan", "milestone"],
            "interview": ["interview", "mock", "technical interview", "behavioral", "hr"],
            "communication": ["communication", "clarity", "speech", "english", "filler", "wpm", "speaking"],
            "progress": ["progress", "streak", "improving", "level", "completion"],
            "career": ["career", "company", "tier", "salary", "role", "job", "offer"],
        }

    def detect_intent(self, message: str, history: Optional[List[Dict[str, Any]]] = None) -> str:
        msg_lower = message.lower().strip()
        last_asst = ""
        if history:
            for turn in reversed(history):
                role = turn.get("role") or ("user" if turn.get("sender") == "user" else "assistant")
                content = turn.get("content") or turn.get("text", "")
                if role == "assistant" and not last_asst:
                    last_asst = content.lower()
                    break

        if any(phrase in msg_lower for phrase in ["not working properly", "not working", "working properly", "you are broken", "you don't work", "stop repeating", "wrong answer", "you are bad", "you're broken"]):
            return "feedback"
        if msg_lower in ["hi", "hello", "hey", "hi there", "hello mentor", "hey mentor", "good morning", "good evening", "good afternoon", "greetings", "hola"] or re.match(r"^(hi|hello|hey|greetings|hola)\b", msg_lower):
            return "greeting"

        # Follow-ups via conversation history
        if last_asst and "which leetcode problem" in last_asst and any(w in msg_lower for w in ["two sum", "reverse", "valid parentheses", "lru", "1", "206", "20", "146"]):
            return "leetcode"
        if last_asst and any(w in last_asst for w in ["share your python code", "error message or traceback"]) and any(w in msg_lower for w in ["typeerror", "indexerror", "keyerror", "nonetype", "out of range", "subscriptable", "def ", "line "]):
            return "python_error"
        # Technical topics with code examples or comparisons
        if any(w in msg_lower for w in ["decorator", "decorators"]):
            return "decorators"
        if ("list" in msg_lower and "tuple" in msg_lower) or any(phrase in msg_lower for phrase in ["list versus tuple", "list vs tuple"]):
            return "list_tuple"
        if any(w in msg_lower for w in ["aws", "cloud engineer", "lambda", "s3", "ec2", "dynamodb"]) and any(w in msg_lower for w in ["interview", "prepare", "preparation", "advice", "service"]):
            return "aws_interview"

        if any(phrase in msg_lower for phrase in ["code example", "show me code", "give code", "show code", "give me code", "example in python", "code snippet", "show an example"]):
            return "followup_code"
        if any(phrase in msg_lower for phrase in ["first task", "task 1", "task 2", "task #1", "explain the first task", "explain task 1", "how do i do task 1"]):
            return "task_detail"

        # Target role & profile query
        if any(phrase in msg_lower for phrase in ["what is my target role", "what is my role", "which role am i targeting", "what role am i targeting", "my target role", "what role is saved", "what is my saved role"]):
            return "target_role"

        # What should I learn next
        if any(phrase in msg_lower for phrase in ["what should i learn next", "what to learn next", "what should i study next", "what do i learn next", "learn next", "study next", "what is next", "what do i do next", "recommend next"]):
            return "learn_next"

        # Overdue tasks
        if any(phrase in msg_lower for phrase in ["which tasks are overdue", "what tasks are overdue", "are any tasks overdue", "overdue tasks", "overdue task", "tasks are overdue", "past due", "overdue"]):
            return "overdue_tasks"

        # NumPy & Vectorized computing
        if any(phrase in msg_lower for phrase in ["numpy", "broadcasting", "broadcast"]):
            return "numpy"

        # Python error debugging
        if any(w in msg_lower for w in ["typeerror", "indexerror", "keyerror", "valueerror", "syntaxerror", "attributeerror", "zerodivisionerror", "indentationerror", "nameerror", "traceback", "exception", "python error", "error in python", "fix this error", "fix my code", "code error", "code is giving an error", "throwing an error", "getting an error", "error in my code", "debug my code", "why is my code failing", "code is failing"]) or ("error" in msg_lower and any(w in msg_lower for w in ["python", "code", "script", "function", "line"])):
            has_error_details = any(w in msg_lower for w in ["typeerror", "indexerror", "keyerror", "attributeerror", "valueerror", "syntaxerror", "zerodivisionerror", "nameerror", "nonetype", "subscriptable", "out of range", "has no attribute", "division by zero", "invalid syntax"]) or ("def " in msg_lower or "print(" in msg_lower or "return " in msg_lower or "```" in msg_lower or "line " in msg_lower)
            return "python_error" if has_error_details else "python_error_missing"

        # OOP for technical interviews
        if any(phrase in msg_lower for phrase in ["oop concepts for interview", "oop concepts for interviews", "oop for interview", "oop for interviews", "oop interview", "explain oop concepts for interviews"]):
            return "oop_interview"

        # OOP Explanations
        if any(w in msg_lower for w in ["oop", "object-oriented", "object oriented", "four pillars", "encapsulation", "polymorphism", "inheritance", "abstraction", "method overriding", "method overloading"]):
            return "oop"

        # Interview questions generation
        if any(phrase in msg_lower for phrase in ["interview questions", "interview question", "ask me", "quiz me"]) or ("interview" in msg_lower and any(w in msg_lower for w in ["questions", "question", "ask", "5", "3", "python", "dsa", "react"])):
            return "interview_questions"

        # LeetCode topic recommendation / DSA questions
        if any(phrase in msg_lower for phrase in ["topics", "topic", "weak", "what should i practice", "which topics", "dsa topics", "study on leetcode", "practice on leetcode"]) or ("dsa" in msg_lower and "leetcode" in msg_lower):
            return "leetcode"

        # LeetCode Problems
        if "leetcode" in msg_lower or any(w in msg_lower for w in ["two sum", "reverse linked list", "valid parentheses", "lru cache", "course schedule", "trapping rain water", "3sum"]):
            has_specific_prob = any(w in msg_lower for w in ["two sum", "reverse", "valid parentheses", "lru", "schedule", "rain water", "3sum", "1", "206", "20", "146", "207", "binary search", "anagram", "koko", "tree", "graph", "stock"])
            return "leetcode" if has_specific_prob else "leetcode_missing"

        # Coding & Algorithms
        if "binary search" in msg_lower and any(phrase in msg_lower for phrase in ["step by step", "step-by-step", "how it works", "walkthrough", "trace"]):
            return "binary_search_step"
        if any(w in msg_lower for w in ["reverse a linked list", "binary search", "two pointers", "sliding window", "kahn", "topological", "bfs", "dfs", "cycle", "merge sort", "quick sort"]):
            return "coding"

        # Roadmap & Tasks
        if "yesterday" in msg_lower:
            return "yesterday"
        if re.search(r"\bday\s*\d+\b", msg_lower):
            return "day_specific"
        if any(phrase in msg_lower for phrase in ["how many days are remaining", "how many days remaining", "days are remaining", "days remaining", "remaining days", "how many days left", "days left"]):
            return "remaining_days"
        if re.search(r"why\s*(?:are\s*)?(\d+)", msg_lower) or ("why" in msg_lower and any(w in msg_lower for w in ["pending", "incomplete", "tasks", "84"])):
            return "why_pending"
        if any(phrase in msg_lower for phrase in ["do today", "can i do today", "should i do today", "what can i do", "what should i do", "today's task", "today tasks", "task today"]) or (msg_lower == "today"):
            return "today_tasks"
        if any(phrase in msg_lower for phrase in ["pending tasks", "pending task", "incomplete tasks", "incomplete task", "tasks are pending", "tasks pending", "tasks incomplete", "tasks are incomplete", "how many tasks are incomplete", "how many tasks are pending"]):
            return "pending_tasks"
        if any(w in msg_lower for w in ["practice a technical interview", "technical interview", "mock interview", "interview practice", "interview question"]):
            return "interview_practice"
        if any(w in msg_lower for w in ["readiness", "score", "ready for placement", "placement ready"]):
            return "readiness"
        if any(w in msg_lower for w in ["system design", "architecture", "microservice", "rate limit", "cache", "redis", "load balancer", "kafka"]):
            return "system_design"
        if any(w in msg_lower for w in ["salary", "negotiate", "career", "placement tips", "how to prepare", "maang", "tier-1"]):
            return "career"

        for intent, kws in self.rules.items():
            if any(re.search(rf"\b{kw}\b", msg_lower) for kw in kws):
                return intent
        return "general_placement"

    def chat(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        message = request_payload.get("message", "")
        context = request_payload.get("student_context") or {}
        client_history = request_payload.get("conversation_history") or []
        intent = self.detect_intent(message, client_history)
        query = message.lower().strip()

        last_asst = ""
        if client_history:
            for turn in reversed(client_history):
                role = turn.get("role") or ("user" if turn.get("sender") == "user" else "assistant")
                content = turn.get("content") or turn.get("text", "")
                if role == "assistant" and not last_asst:
                    last_asst = content.lower()
                    break

        profile = context.get("profile") or {}
        target_role = context.get("target_role") or profile.get("target_role")
        name = context.get("student_name") or profile.get("name") or "Student"
        role_desc = f" for **{target_role}**" if target_role else ""

        readiness = context.get("readiness") or {}
        score = readiness.get("overall_score")
        readiness_label = readiness.get("readiness_label")

        skill_gaps_obj = context.get("skill_gaps") or {}
        gaps = skill_gaps_obj.get("top_gaps") or []

        leetcode_analysis = context.get("leetcode_analysis") or {}
        leetcode_weak = context.get("leetcode_weak_topics") or []

        roadmap = context.get("roadmap") or {}
        if not isinstance(roadmap, dict):
            roadmap = {}
        current_day = roadmap.get("current_day") or 1
        total_days = roadmap.get("total_days") or 90
        remaining_days = roadmap.get("remaining_days", max(0, total_days - current_day))

        today_tasks_obj = context.get("today_tasks") or {}
        if isinstance(today_tasks_obj, dict):
            today_pending_tasks = today_tasks_obj.get("pending_tasks") or []
            today_completed_tasks = today_tasks_obj.get("completed_tasks") or []
        elif isinstance(today_tasks_obj, list):
            today_pending_tasks = today_tasks_obj
            today_completed_tasks = []
        else:
            today_pending_tasks = []
            today_completed_tasks = []

        yesterday_obj = context.get("yesterday_completed_tasks") or {}
        if isinstance(yesterday_obj, dict):
            yesterday_tasks = yesterday_obj.get("tasks") or []
        elif isinstance(yesterday_obj, list):
            yesterday_tasks = yesterday_obj
        else:
            yesterday_tasks = []

        all_pending_obj = context.get("all_pending_tasks") or {}
        if isinstance(all_pending_obj, dict):
            all_pending_tasks_list = all_pending_obj.get("tasks") or []
            raw_total_pending = all_pending_obj.get("total_pending")
            if isinstance(raw_total_pending, int):
                total_pending_count = raw_total_pending
            elif isinstance(raw_total_pending, list):
                total_pending_count = len(raw_total_pending)
            elif raw_total_pending is not None:
                try:
                    total_pending_count = int(raw_total_pending)
                except (ValueError, TypeError):
                    total_pending_count = len(all_pending_tasks_list)
            else:
                total_pending_count = len(all_pending_tasks_list)
        elif isinstance(all_pending_obj, list):
            all_pending_tasks_list = all_pending_obj
            total_pending_count = len(all_pending_obj)
        elif isinstance(all_pending_obj, int):
            all_pending_tasks_list = []
            total_pending_count = all_pending_obj
        else:
            all_pending_tasks_list = []
            total_pending_count = 0

        progress = context.get("progress") or {}
        if isinstance(progress, dict):
            raw_completed = progress.get("completed_tasks", 0)
            if isinstance(raw_completed, int):
                completed_tasks_count = raw_completed
            elif isinstance(raw_completed, list):
                completed_tasks_count = len(raw_completed)
            elif raw_completed is not None:
                try:
                    completed_tasks_count = int(raw_completed)
                except (ValueError, TypeError):
                    completed_tasks_count = 0
            else:
                completed_tasks_count = 0
        elif isinstance(progress, list):
            completed_tasks_count = len(progress)
        elif isinstance(progress, int):
            completed_tasks_count = progress
        else:
            completed_tasks_count = 0

        raw_total_tasks = roadmap.get("total_tasks_count")
        if isinstance(raw_total_tasks, int) and raw_total_tasks > 0:
            total_tasks_count = raw_total_tasks
        else:
            total_tasks_count = total_pending_count + completed_tasks_count

        tasks_by_day = context.get("tasks_by_day") or {}
        if not isinstance(tasks_by_day, dict):
            tasks_by_day = {}

        start_date = roadmap.get("start_date")
        overdue_obj = context.get("overdue_tasks") or {}
        if isinstance(overdue_obj, dict):
            overdue_tasks_list = overdue_obj.get("tasks") or []
            raw_overdue_count = overdue_obj.get("total_overdue")
            if isinstance(raw_overdue_count, int):
                overdue_count = raw_overdue_count
            elif isinstance(raw_overdue_count, list):
                overdue_count = len(raw_overdue_count)
            else:
                overdue_count = len(overdue_tasks_list)
        elif isinstance(overdue_obj, list):
            overdue_tasks_list = overdue_obj
            overdue_count = len(overdue_obj)
        else:
            overdue_tasks_list = []
            overdue_count = 0
        next_task_obj = context.get("next_recommended_task")

        sources: List[str] = ["profile"]
        evidence: List[str] = []
        if target_role:
            evidence.append(f"Target Role: {target_role}")

        # Intent handling matching the specification
        if intent == "greeting":
            answer = f"Hey {name}! How can I help with your coding, technical concepts, or placement preparation today?"
            actions = [
                {"label": "What can I do today?", "route": "/tasks"},
                {"label": "How many days are remaining?", "route": "/roadmap"},
                {"label": "Practice a technical interview", "route": "/interview"},
            ]

        elif intent == "feedback":
            answer = (
                "I apologize for the misunderstanding! I'm here to give you direct, accurate information from your placement profile and roadmap.\n\n"
                "You can ask me directly about:\n"
                "1. 📅 **Today's Tasks**: *\"What can I do today?\"*\n"
                "2. ✅ **Yesterday's Progress**: *\"What did I complete yesterday?\"*\n"
                "3. 📋 **Pending Tasks**: *\"What are my pending tasks?\"*\n"
                "4. ⏳ **Roadmap Schedule**: *\"How many days are remaining?\"* or *\"What about Day 13?\"*\n"
                "5. 💡 **DSA & Interviews**: *\"Help me learn DSA\"* or *\"Practice a technical interview\"*\n\n"
                "What would you like to check right now?"
            )
            evidence.append("Mode: User Assistance & Clarification")
            actions = [
                {"label": "What can I do today?", "route": "/tasks"},
                {"label": "How many days are remaining?", "route": "/roadmap"},
                {"label": "What are my pending tasks?", "route": "/tasks"},
            ]

        elif intent == "target_role":
            if target_role:
                prof_skills = context.get("profile", {}).get("skills", [])
                skills_str = ", ".join(prof_skills) if prof_skills else ""
                tier = context.get("profile", {}).get("target_company_tier")
                tier_str = f"- **Target Company Tier**: {tier}\n" if tier else ""
                skills_str_fmt = f"- **Saved Profile Skills**: {skills_str}\n" if skills_str else ""
                start_str = f" (Started: {start_date})" if start_date else ""
                answer = (
                    f"Your saved target role is **{target_role}**.\n\n"
                    f"- **Roadmap Timeline**: Day {current_day} of your {total_days}-day roadmap{start_str}\n"
                    f"{tier_str}"
                    f"{skills_str_fmt}\n"
                    f"Your curriculum, daily tasks, and mock interview questions are tailored specifically for **{target_role}** placement preparation."
                )
                evidence.append(f"Target Role: {target_role}")
            else:
                answer = (
                    "You currently do not have a target role saved in your placement profile.\n\n"
                    "You can select your target role (e.g. *Backend Developer*, *Full Stack Engineer*, *Cloud / DevOps Engineer*, or *Data Scientist*) in your Profile settings to get a personalized roadmap and daily task plan."
                )
                evidence.append("Target Role: Not Set")
            actions = [
                {"label": "What can I do today?", "route": "/tasks"},
                {"label": "What should I learn next?", "route": "/tasks"},
                {"label": "How many days are remaining?", "route": "/roadmap"},
            ]

        elif intent == "learn_next":
            sources.append("roadmap")
            if next_task_obj and (next_task_obj.get("title") or next_task_obj.get("task_id")):
                nt_title = next_task_obj.get("title", "Roadmap Task")
                nt_cat = next_task_obj.get("category", "Technical")
                nt_day = next_task_obj.get("day") or current_day
                nt_dur = next_task_obj.get("estimated_minutes", 60)
                nt_diff = next_task_obj.get("difficulty", "Intermediate")
                answer = (
                    f"Based on your {total_days}-day roadmap{role_desc}, the next recommended task for you to learn is:\n\n"
                    f"📌 **{nt_title}**\n"
                    f"- **Roadmap Day**: Day {nt_day}\n"
                    f"- **Category**: {nt_cat}\n"
                    f"- **Difficulty**: {nt_diff}\n"
                    f"- **Estimated Time**: ~{nt_dur} mins\n\n"
                    f"Start with this topic to maintain your consistency streak and keep advancing toward your placement goals!"
                )
                evidence.append(f"Next Task: {nt_title}")
                evidence.append(f"Scheduled Day: {nt_day}")
            elif today_pending_tasks:
                t = today_pending_tasks[0]
                t_title = t.get("title", "Daily Task")
                t_cat = t.get("category", "Preparation")
                t_dur = t.get("estimated_minutes", 60)
                answer = (
                    f"For your next learning step today (Day {current_day} of {total_days}{role_desc}), focus on:\n\n"
                    f"📌 **{t_title}** ({t_cat}, ~{t_dur} mins)\n\n"
                    f"Completing this today keeps you right on schedule for your target placement timeline!"
                )
                evidence.append(f"Next Task: {t_title}")
            elif all_pending_tasks_list:
                t = all_pending_tasks_list[0]
                t_title = t.get("title", "Upcoming Task")
                t_day = t.get("day") or t.get("day_number") or current_day
                t_cat = t.get("category", "Preparation")
                t_dur = t.get("estimated_minutes", 60)
                answer = (
                    f"All tasks for Day {current_day} are complete! The next upcoming task on your roadmap{role_desc} is:\n\n"
                    f"📌 **{t_title}** (Day {t_day}, {t_cat}, ~{t_dur} mins)\n\n"
                    f"You can jump ahead to Day {t_day} or spend time practicing DSA problems and mock interviews."
                )
                evidence.append(f"Next Task: {t_title}")
            else:
                answer = (
                    f"You have completed all scheduled tasks in your {total_days}-day roadmap! 🎉\n\n"
                    f"At this stage, your best next learning focus is comprehensive mock interviews, system design drills, and high-difficulty DSA problem solving."
                )
                evidence.append("Roadmap Status: All Tasks Completed")
            actions = [
                {"label": "What can I do today?", "route": "/tasks"},
                {"label": "How many days are remaining?", "route": "/roadmap"},
            ]

        elif intent == "overdue_tasks":
            sources.append("tasks")
            computed_overdue = list(overdue_tasks_list)
            if not computed_overdue and all_pending_tasks_list:
                for t in all_pending_tasks_list:
                    t_day = t.get("day") or t.get("day_number")
                    try:
                        if int(t_day) < current_day:
                            computed_overdue.append(t)
                    except (ValueError, TypeError):
                        pass
            count = len(computed_overdue)
            if count > 0:
                lines = []
                for idx, t in enumerate(computed_overdue[:5]):
                    t_title = t.get("title", "Task")
                    t_day = t.get("day") or t.get("day_number") or 1
                    t_cat = t.get("category", "Technical")
                    t_mins = t.get("estimated_minutes", 60)
                    lines.append(f"{idx+1}. ⚠️ **{t_title}** (Scheduled Day: Day {t_day}, {t_cat}, ~{t_mins} mins)")
                tasks_str = "\n".join(lines)
                more_str = f"\n*...and {count - len(computed_overdue[:5])} more overdue task(s).*" if count > 5 else ""
                answer = (
                    f"You have **{count}** overdue task(s) scheduled prior to Day {current_day}{role_desc}:\n\n"
                    f"{tasks_str}{more_str}\n\n"
                    f"I recommend prioritizing these backlogs alongside today's Day {current_day} tasks to get back on track!"
                )
                evidence.append(f"Total Overdue Tasks: {count}")
                evidence.append(f"Current Day: {current_day}")
            else:
                answer = (
                    f"You have **0** overdue tasks! 🎉\n\n"
                    f"All tasks from previous days have been completed, and you are fully up to date with Day {current_day} of your {total_days}-day roadmap."
                )
                evidence.append("Total Overdue Tasks: 0")
                evidence.append(f"Current Day: {current_day}")
            actions = [
                {"label": "What can I do today?", "route": "/tasks"},
                {"label": "What are my pending tasks?", "route": "/tasks"},
            ]

        elif intent == "numpy":
            sources.append("python")
            answer = (
                "**NumPy Broadcasting Explained**:\n\n"
                "**Broadcasting** is NumPy's mechanism that allows arithmetic operations between arrays of different shapes without copying data in memory.\n\n"
                "### 📏 The 2 Broadcasting Rules\n"
                "NumPy compares shapes element-wise starting with the **trailing (rightmost) dimensions**:\n"
                "1. **Prepend 1s**: If the two arrays have a different number of dimensions, prepend dimensions of size `1` to the smaller shape.\n"
                "2. **Dimension Compatibility**: Two dimensions are compatible if:\n"
                "   - They are equal, OR\n"
                "   - One of them is `1` (which gets virtually stretched to match the other dimension).\n\n"
                "### 💻 Python Code Demonstration\n"
                "```python\n"
                "import numpy as np\n\n"
                "# Example 1: 2D Matrix (2, 3) + 1D Array (3,)\n"
                "# Shape (3,) is prepended to (1, 3), then stretched across 2 rows -> (2, 3)\n"
                "matrix = np.array([[1, 2, 3], [4, 5, 6]])  # shape (2, 3)\n"
                "vector = np.array([10, 20, 30])             # shape (3,)\n\n"
                "result = matrix + vector\n"
                "print(\"Matrix + Vector:\\n\", result)\n"
                "# Output:\n"
                "# [[11, 22, 33],\n"
                "#  [14, 25, 36]]\n\n"
                "# Example 2: Column Vector (3, 1) + Row Vector (1, 3) -> (3, 3)\n"
                "col = np.array([[1], [2], [3]])  # shape (3, 1)\n"
                "row = np.array([[10, 20, 30]])   # shape (1, 3)\n"
                "grid = col + row\n"
                "print(\"Outer Sum (3, 3):\\n\", grid)\n"
                "# Output:\n"
                "# [[11, 21, 31],\n"
                "#  [12, 22, 32],\n"
                "#  [13, 23, 33]]\n"
                "```\n\n"
                "⏱️ **Performance Advantage**: Broadcasting runs in compiled C and consumes $O(1)$ extra memory because it never creates physical duplicate copies of array elements."
            )
            evidence.append("Topic: NumPy Broadcasting")
            actions = [
                {"label": "Explain OOP concepts for interviews", "route": "/mentor"},
                {"label": "What can I do today?", "route": "/tasks"},
            ]

        elif intent == "oop_interview":
            sources.append("oop")
            answer = (
                "**OOP Concepts for Technical Interviews**:\n\n"
                "### 🏛️ The 4 Core Pillars\n"
                "1. 🔒 **Encapsulation**: Bundling state and methods within a class while restricting direct external access (`_protected` or `__private` attributes) to enforce integrity and prevent invalid states.\n"
                "2. 🎭 **Abstraction**: Exposing only essential public interfaces while hiding complex internal implementations (e.g. using `abc.ABC` and `@abstractmethod`).\n"
                "3. 🧬 **Inheritance**: Creating hierarchical relationships where child classes inherit and extend behaviors from parent classes (promoting code reuse).\n"
                "4. 🔄 **Polymorphism**: Allowing different classes to implement methods with the same name, enabling clients to interact with varying objects via a uniform interface (runtime method overriding vs compile-time overloading).\n\n"
                "### 🎯 Top 3 Interview Discussion Questions\n"
                "1. **Composition vs. Inheritance**: Interviewers look for: *\"Favor composition over inheritance\"* (has-a vs is-a) to avoid tightly coupled class hierarchies.\n"
                "2. **Abstract Classes vs. Interfaces**: Abstract classes can have state and concrete methods; pure interfaces only declare method signatures.\n"
                "3. **Method Overriding vs Overloading**: Python achieves overloading via default arguments (`*args, **kwargs`) and overriding by redefining a parent method in a subclass.\n\n"
                "### 💻 Python Demonstration\n"
                "```python\n"
                "from abc import ABC, abstractmethod\n\n"
                "class PaymentGateway(ABC):  # Abstraction\n"
                "    def __init__(self, currency: str):\n"
                "        self._currency = currency  # Encapsulation\n\n"
                "    @abstractmethod\n"
                "    def charge(self, amount: float) -> bool:\n"
                "        pass\n\n"
                "class StripePayment(PaymentGateway):  # Inheritance\n"
                "    def charge(self, amount: float) -> bool:  # Polymorphism\n"
                "        print(f\"Charging {amount} {self._currency} via Stripe API\")\n"
                "        return True\n"
                "```"
            )
            evidence.append("Topic: OOP for Technical Interviews")
            actions = [
                {"label": "Explain Polymorphism in Python", "route": "/mentor"},
                {"label": "What can I do today?", "route": "/tasks"},
            ]

        elif intent == "binary_search_step":
            sources.append("coding")
            answer = (
                "**Binary Search: Step-by-Step Walkthrough & Implementation**:\n\n"
                "### 📋 Precondition\n"
                "The input array **must be sorted** in ascending order.\n\n"
                "### 🔍 Step-by-Step Algorithm\n"
                "1. **Initialize Pointers**: Set `low = 0` (start) and `high = len(arr) - 1` (end).\n"
                "2. **Calculate Midpoint**: Compute `mid = low + (high - low) // 2`. Using `(high - low) // 2` avoids integer overflow.\n"
                "3. **Evaluate Comparison**:\n"
                "   - If `arr[mid] == target`: Match found! Return index `mid` immediately.\n"
                "   - If `arr[mid] < target`: Target lies in the right half. Discard the left half: `low = mid + 1`.\n"
                "   - If `arr[mid] > target`: Target lies in the left half. Discard the right half: `high = mid - 1`.\n"
                "4. **Loop Condition**: Repeat while `low <= high`. If `low > high`, target is not present (return `-1`).\n\n"
                "### 📊 Concrete Trace Walkthrough\n"
                "Searching for `target = 23` in `arr = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]` ($N=10$):\n"
                "- **Pass 1**: `low=0`, `high=9` → `mid=4` (`arr[4]=16`). Since $16 < 23$, search right: `low = 5`.\n"
                "- **Pass 2**: `low=5`, `high=9` → `mid=7` (`arr[7]=56`). Since $56 > 23$, search left: `high = 6`.\n"
                "- **Pass 3**: `low=5`, `high=6` → `mid=5` (`arr[5]=23`). Match found! Returns index `5`.\n\n"
                "### 💻 Python Implementation\n"
                "```python\n"
                "def binary_search(arr: list[int], target: int) -> int:\n"
                "    low, high = 0, len(arr) - 1\n"
                "    while low <= high:\n"
                "        mid = low + (high - low) // 2\n"
                "        if arr[mid] == target:\n"
                "            return mid\n"
                "        elif arr[mid] < target:\n"
                "            low = mid + 1\n"
                "        else:\n"
                "            high = mid - 1\n"
                "    return -1  # Target not found\n\n"
                "# Verification:\n"
                "numbers = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]\n"
                "print(binary_search(numbers, 23))  # 5\n"
                "```\n\n"
                "⏱️ **Time Complexity**: $O(\\log N)$ | 💾 **Space Complexity**: $O(1)$"
            )
            evidence.append("Topic: Binary Search (Step-by-Step)")
            evidence.append("Time: O(log N)")
            actions = [
                {"label": "Practice on LeetCode", "route": "/leetcode"},
                {"label": "What can I do today?", "route": "/tasks"},
            ]

        elif intent == "decorators":
            answer = (
                "**Python Decorators Explanation & Code Example**:\n\n"
                "A **decorator** in Python is a callable that takes another function as an argument, extends its behavior without modifying it, and returns the modified wrapper function.\n\n"
                "**Simple Code Example**:\n"
                "```python\n"
                "import functools\n\n"
                "def my_logger(func):\n"
                "    @functools.wraps(func)\n"
                "    def wrapper(*args, **kwargs):\n"
                "        print(f\"Calling {func.__name__} with args: {args}\")\n"
                "        result = func(*args, **kwargs)\n"
                "        print(f\"{func.__name__} returned {result}\")\n"
                "        return result\n"
                "    return wrapper\n\n"
                "@my_logger\n"
                "def add(a: int, b: int) -> int:\n"
                "    return a + b\n\n"
                "# Usage:\n"
                "print(add(3, 4))  # Logs call and returns 7\n"
                "```\n\n"
                "**Three Important Facts**:\n"
                "1. **First-Class Functions**: Decorators work because Python treats functions as first-class objects (they can be passed as arguments, assigned, and returned).\n"
                "2. **Syntactic Sugar**: The `@my_decorator` syntax is shorthand for `func = my_decorator(func)`.\n"
                "3. **Metadata Preservation**: Always use `@functools.wraps(func)` inside the wrapper so the decorated function retains its original `__name__` and `__doc__`."
            )
            evidence.append("Topic: Python Decorators & Metaprogramming")
            actions = [
                {"label": "Practice Decorator Problems", "route": "/tasks"},
                {"label": "What can I do today?", "route": "/tasks"}
            ]

        elif intent == "list_tuple":
            answer = (
                "**Difference Between a Python List and a Tuple**:\n\n"
                "1. **Mutability**:\n"
                "   - **List** (`[1, 2, 3]`): Mutable. Elements can be added, removed, or modified in-place.\n"
                "   - **Tuple** (`(1, 2, 3)`): Immutable. Once created, elements cannot be altered.\n\n"
                "2. **Performance & Memory**:\n"
                "   - Tuples have a smaller memory footprint and faster iteration speed because their size and elements are fixed at allocation.\n"
                "   - Lists allocate extra buffer space to allow efficient $O(1)$ amortized appending.\n\n"
                "3. **Dictionary Keys & Hashability**:\n"
                "   - Tuples (containing only hashable elements) are **hashable** and can be used as dictionary keys or set elements.\n"
                "   - Lists are unhashable and will raise `TypeError: unhashable type: 'list'` if used as dict keys.\n\n"
                "4. **Syntax & Use Cases**:\n"
                "   - Use **lists** for collections of items that change during runtime (e.g. data pipelines, queues, sorting).\n"
                "   - Use **tuples** for fixed data records or constants (e.g. `(x, y)` coordinates, database rows)."
            )
            evidence.append("Topic: Python Data Structures: List vs Tuple")
            actions = [
                {"label": "Practice Data Structures", "route": "/leetcode"},
                {"label": "What can I do today?", "route": "/tasks"}
            ]

        elif intent == "aws_interview":
            answer = (
                "**How to Prepare for an AWS Technical Interview**:\n\n"
                "1. **Master Core AWS Services**:\n"
                "   - **Compute**: EC2 (instance types, security groups), ECS/EKS (Docker containers), Lambda (serverless triggers & cold starts).\n"
                "   - **Storage & Databases**: S3 (storage classes, lifecycle policies), RDS (multi-AZ replication, read replicas), DynamoDB (partition keys, sort keys, GSI/LSI).\n"
                "   - **Networking & Security**: VPC, subnets (public/private), NAT Gateways, IAM (least privilege, roles vs users), Route 53, CloudFront.\n\n"
                "2. **AWS Well-Architected Framework Pillars**:\n"
                "   - Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability.\n\n"
                "3. **System Design on AWS**:\n"
                "   - Be prepared to design high-availability 3-tier web applications: Route 53 -> CloudFront -> ALB -> Auto-Scaling EC2 -> Multi-AZ RDS / ElastiCache.\n\n"
                "4. **Hands-On & Behavioral**:\n"
                "   - Have 2-3 real architecture examples from your projects explaining trade-offs, disaster recovery (RTO/RPO), and cost optimization."
            )
            evidence.append("Topic: AWS Cloud Architecture & Technical Interview Preparation")
            actions = [
                {"label": "Practice System Design", "route": "/interview"},
                {"label": "What can I do today?", "route": "/tasks"}
            ]

        elif intent == "followup_code":
            if "encapsulation" in query or (last_asst and "encapsulation" in last_asst):
                answer = (
                    "Here is a clean Python code example demonstrating **Encapsulation**:\n\n"
                    "```python\n"
                    "class BankAccount:\n"
                    "    def __init__(self, owner: str, initial_balance: float = 0.0):\n"
                    "        self.owner = owner\n"
                    "        self.__balance = max(0.0, initial_balance)  # Private attribute\n\n"
                    "    def deposit(self, amount: float) -> bool:\n"
                    "        if amount > 0:\n"
                    "            self.__balance += amount\n"
                    "            return True\n"
                    "        return False\n\n"
                    "    def get_balance(self) -> float:\n"
                    "        return self.__balance\n\n"
                    "# Usage:\n"
                    "account = BankAccount(\"Alice\", 500.0)\n"
                    "account.deposit(150.0)\n"
                    "print(f\"Balance: ${account.get_balance():.2f}\")  # $650.00\n"
                    "```\n\n"
                    "Notice how `__balance` cannot be directly altered from outside the class, enforcing validation rules through methods."
                )
            else:
                answer = (
                    f"**Code Demonstration for: {message}**:\n\n"
                    "```python\n"
                    "def solve_problem(data: list) -> list:\n"
                    "    # Process elements efficiently with defensive validation\n"
                    "    return [x for x in data if x is not None]\n\n"
                    "# Verification:\n"
                    "print(solve_problem([1, 2, None, 4]))  # [1, 2, 4]\n"
                    "```"
                )
            evidence.append("Topic: Python Code Example Demonstration")
            actions = [
                {"label": "What about Polymorphism?", "route": "/mentor"},
                {"label": "What can I do today?", "route": "/tasks"},
            ]

        elif intent == "task_detail":
            if today_pending_tasks:
                t = today_pending_tasks[0]
                t_title = t.get("title", "Daily Task")
                t_cat = t.get("category", "Preparation")
                t_dur = t.get("estimated_minutes", 60)
                answer = (
                    f"**How to complete Task #1: {t_title}** ({t_cat}, ~{t_dur} mins):\n\n"
                    f"1. **Core Objective**: Master the fundamentals and problem-solving patterns in {t_cat}.\n"
                    f"2. **Step-by-Step Approach**:\n"
                    f"   - Step A: Review concept documentation or core definitions.\n"
                    f"   - Step B: Implement clean code solution from scratch without hints.\n"
                    f"   - Step C: Analyze Time and Space complexity ($O(N)$, $O(1)$) and verify edge cases.\n"
                    f"3. **Milestone**: Mark the task completed in your dashboard once finished!"
                )
                evidence.append(f"Task: {t_title}")
            else:
                answer = (
                    f"You have completed all tasks scheduled for today (Day {current_day})! 🎉\n\n"
                    f"You can practice Medium DSA problems or review upcoming Day {current_day + 1} topics."
                )
            actions = [{"label": "View Today's Tasks", "route": "/tasks"}]

        elif intent == "python_error_missing":
            answer = (
                "Could you please share your Python code snippet and the exact error message or traceback you are receiving?\n\n"
                "Once you paste them, I'll identify the root cause, explain why the error occurs, and provide the corrected code with best practices!"
            )
            evidence.append("Mode: Python Debugging (Awaiting Code & Traceback)")
            actions = [
                {"label": "Paste code snippet", "route": "/mentor"},
                {"label": "What can I do today?", "route": "/tasks"},
            ]

        elif intent == "python_error":
            sources.append("python_debugging")
            if "typeerror" in query or "nonetype" in query or "subscriptable" in query:
                answer = (
                    "**Fixing `TypeError: 'NoneType' object is not subscriptable`**:\n\n"
                    "**Root Cause**: You are attempting to index or slice an object (`obj[key]` or `obj[index]`) that evaluates to `None` instead of a list, dict, or string.\n\n"
                    "**Common Causes**:\n"
                    "1. A function missing a `return` statement returns `None` by default.\n"
                    "2. Methods like `list.sort()`, `list.append()`, or `dict.update()` modify in-place and return `None`.\n"
                    "3. Accessing a missing dictionary key with `.get()` returns `None`.\n\n"
                    "**Corrected Code**:\n"
                    "```python\n"
                    "# Problematic:\n"
                    "data = get_api_data()  # returns None\n"
                    "print(data[\"status\"])   # Raises TypeError!\n\n"
                    "# Corrected:\n"
                    "data = get_api_data()\n"
                    "if data is not None and isinstance(data, dict):\n"
                    "    print(data.get(\"status\", \"unknown\"))\n"
                    "else:\n"
                    "    print(\"Data is None or invalid\")\n"
                    "```"
                )
                evidence.append("Error: TypeError (NoneType Subscriptable)")
            elif "indexerror" in query or "out of range" in query:
                answer = (
                    "**Fixing `IndexError: list index out of range`**:\n\n"
                    "**Root Cause**: Attempting to access an index outside list bounds (`index < 0` or `index >= len(list)`).\n\n"
                    "**Corrected Code**:\n"
                    "```python\n"
                    "my_list = [10, 20, 30]\n"
                    "index = 5\n\n"
                    "if 0 <= index < len(my_list):\n"
                    "    print(my_list[index])\n"
                    "else:\n"
                    "    print(f\"Index {index} is out of bounds for list of size {len(my_list)}\")\n"
                    "```"
                )
                evidence.append("Error: IndexError")
            elif "keyerror" in query:
                answer = (
                    "**Fixing `KeyError` in Python**:\n\n"
                    "**Root Cause**: Trying to access a dictionary key with `d[key]` where `key` does not exist.\n\n"
                    "**Fix**: Use `dict.get(key, default_value)` or `if key in dict:`."
                )
                evidence.append("Error: KeyError")
            else:
                answer = (
                    "**Python Error Analysis & Fix**:\n\n"
                    "1. Check the traceback for the exact line number and exception name.\n"
                    "2. Verify variable types (`type(var)`) and values before the failing line.\n"
                    "3. Add explicit `None` checks or defensive bounds checks."
                )
            actions = [
                {"label": "Explain OOP concepts", "route": "/mentor"},
                {"label": "What can I do today?", "route": "/tasks"},
            ]

        elif intent == "oop":
            sources.append("oop_concepts")
            if "encapsulation" in query and not ("4" in query or "four" in query or "pillars" in query):
                answer = (
                    "**Encapsulation in Object-Oriented Programming**:\n\n"
                    "**Definition**: Encapsulation is the practice of bundling data (attributes) and methods that operate on that data into a single class, while restricting direct modification of internal state (data hiding).\n\n"
                    "**Python Example**:\n"
                    "```python\n"
                    "class BankAccount:\n"
                    "    def __init__(self, owner: str, balance: float):\n"
                    "        self.owner = owner\n"
                    "        self.__balance = max(0.0, balance)  # Private attribute\n\n"
                    "    def get_balance(self) -> float:\n"
                    "        return self.__balance\n\n"
                    "    def deposit(self, amount: float):\n"
                    "        if amount > 0:\n"
                    "            self.__balance += amount\n"
                    "```"
                )
                evidence.append("Pillar: Encapsulation")
            elif "polymorphism" in query and not ("4" in query or "four" in query or "pillars" in query):
                answer = (
                    "**Polymorphism in Object-Oriented Programming**:\n\n"
                    "**Definition**: Polymorphism (\"many forms\") allows different classes to implement methods with the same interface name, enabling uniform handling of diverse objects.\n\n"
                    "**Python Example**:\n"
                    "```python\n"
                    "class Shape:\n"
                    "    def area(self) -> float: raise NotImplementedError\n\n"
                    "class Rectangle(Shape):\n"
                    "    def __init__(self, w, h): self.w, self.h = w, h\n"
                    "    def area(self): return self.w * self.h\n\n"
                    "class Circle(Shape):\n"
                    "    def __init__(self, r): self.r = r\n"
                    "    def area(self): return 3.14159 * self.r * self.r\n\n"
                    "for s in [Rectangle(4, 5), Circle(3)]:\n"
                    "    print(f\"Area: {s.area():.2f}\")\n"
                    "```"
                )
                evidence.append("Pillar: Polymorphism")
            else:
                answer = (
                    "**The 4 Pillars of Object-Oriented Programming (OOP)**:\n\n"
                    "1. 🔒 **Encapsulation**: Bundles data and methods together inside classes and restricts direct access to internal state (`__private` variables) to prevent accidental mutation.\n"
                    "2. 🎭 **Abstraction**: Hides complex internal logic and exposes only essential interfaces to callers (`abc.ABC` and `@abstractmethod`).\n"
                    "3. 🧬 **Inheritance**: Allows a child class to inherit fields and methods from a parent class, maximizing code reusability and hierarchical design.\n"
                    "4. 🔄 **Polymorphism**: Enables different classes to implement methods with the same name, allowing clients to treat varying objects through a single uniform interface.\n\n"
                    "**Unified Python Demonstration**:\n"
                    "```python\n"
                    "from abc import ABC, abstractmethod\n\n"
                    "class Animal(ABC):  # Abstraction\n"
                    "    def __init__(self, name: str):\n"
                    "        self._name = name  # Encapsulation (protected)\n\n"
                    "    @abstractmethod\n"
                    "    def make_sound(self) -> str:\n"
                    "        pass\n\n"
                    "class Dog(Animal):  # Inheritance\n"
                    "    def make_sound(self) -> str:  # Polymorphism\n"
                    "        return f\"{self._name} says Woof!\"\n\n"
                    "dog = Dog(\"Buddy\")\n"
                    "print(dog.make_sound())  # Buddy says Woof!\n"
                    "```"
                )
                evidence.append("Topic: OOP 4 Pillars")
            actions = [
                {"label": "Explain Encapsulation in detail", "route": "/mentor"},
                {"label": "Explain Polymorphism in detail", "route": "/mentor"},
                {"label": "What can I do today?", "route": "/tasks"},
            ]

        elif intent == "leetcode_missing":
            answer = (
                "Which LeetCode problem are you working on? Please share the problem number, title, or the problem statement, and I'll walk you through the optimal approach, time/space complexity, and clean code implementation!"
            )
            evidence.append("Mode: LeetCode Coaching (Awaiting Problem Details)")
            actions = [
                {"label": "Two Sum (LeetCode #1)", "route": "/mentor"},
                {"label": "Reverse Linked List (LeetCode #206)", "route": "/mentor"},
                {"label": "Valid Parentheses (LeetCode #20)", "route": "/mentor"},
            ]

        elif intent == "coding":
            sources.append("coding")
            if "binary search" in query:
                answer = (
                    "**Binary Search Implementation**:\n\n"
                    "Operates on a sorted search space in $O(\\log N)$ time:\n\n"
                    "⏱️ **Time**: $O(\\log N)$ | 💾 **Space**: $O(1)$\n\n"
                    "```python\n"
                    "def binary_search(arr: list[int], target: int) -> int:\n"
                    "    low, high = 0, len(arr) - 1\n"
                    "    while low <= high:\n"
                    "        mid = low + (high - low) // 2\n"
                    "        if arr[mid] == target: return mid\n"
                    "        elif arr[mid] < target: low = mid + 1\n"
                    "        else: high = mid - 1\n"
                    "    return -1\n"
                    "```"
                )
            else:
                answer = (
                    "**Algorithmic Problem Solving**:\n\n"
                    "1. Define Time and Space complexity constraints.\n"
                    "2. Select appropriate data structures (Hash Map, Heap, Stack).\n"
                    "3. Implement clean, modular code with boundary verification."
                )
            actions = [
                {"label": "Practice LeetCode", "route": "/leetcode"},
                {"label": "What can I do today?", "route": "/tasks"},
            ]

        elif intent == "yesterday":
            sources.append("yesterday_completed_tasks")
            if yesterday_tasks:
                lines = [f"{idx+1}. ✅ **{t.get('title', 'Task')}** ({t.get('category', 'Preparation')})" for idx, t in enumerate(yesterday_tasks)]
                answer = (
                    f"Yesterday, you completed the following {len(yesterday_tasks)} task(s):\n\n"
                    f"{chr(10).join(lines)}\n\n"
                    f"Great job maintaining your preparation momentum!"
                )
                evidence.append(f"Yesterday Completed Tasks: {len(yesterday_tasks)}")
            else:
                answer = (
                    "According to your records, you did not complete any tasks yesterday.\n\n"
                    f"You can dive into today's tasks (Day {current_day} of {total_days}) to build your consistency streak!"
                )
                evidence.append("Yesterday Completed Tasks: 0")
            actions = [
                {"label": "What can I do today?", "route": "/tasks"},
                {"label": "View Today's Tasks", "route": "/tasks"},
            ]

        elif intent == "day_specific":
            sources.append("tasks_by_day")
            day_match = re.search(r"\bday\s*(\d+)\b", query)
            target_day = int(day_match.group(1)) if day_match else current_day
            day_tasks = tasks_by_day.get(str(target_day)) or tasks_by_day.get(target_day) or []
            if day_tasks:
                lines = []
                for idx, t in enumerate(day_tasks):
                    status_icon = "✅" if t.get("status") == "completed" else "📌"
                    lines.append(f"{idx+1}. {status_icon} **{t.get('title')}** ({t.get('category', 'General')}, ~{t.get('estimated_minutes', 60)} mins) — Status: *{t.get('status', 'pending')}*")
                answer = (
                    f"Here are the tasks scheduled for **Day {target_day}** of your {total_days}-day roadmap{role_desc}:\n\n"
                    f"{chr(10).join(lines)}\n\n"
                    f"You are currently on **Day {current_day}**. Keep moving forward to reach this milestone!"
                )
                evidence.append(f"Queried Day: {target_day}")
                evidence.append(f"Tasks on Day {target_day}: {len(day_tasks)}")
            else:
                answer = (
                    f"**Day {target_day}** is part of your {total_days}-day roadmap{role_desc}.\n\n"
                    f"You are currently on **Day {current_day}** with {remaining_days} days remaining."
                )
                evidence.append(f"Queried Day: {target_day}")
            actions = [
                {"label": "What can I do today?", "route": "/tasks"},
                {"label": "Open Roadmap", "route": "/roadmap"},
            ]

        elif intent == "remaining_days":
            sources.append("roadmap")
            answer = (
                f"You are currently on **Day {current_day}** of your **{total_days}-day** roadmap{role_desc}.\n\n"
                f"There are **{remaining_days} days remaining** in your placement schedule.\n\n"
                f"*(Note: You have {total_pending_count} total pending tasks remaining across the rest of the roadmap, with {len(today_pending_tasks)} due today on Day {current_day}).*"
            )
            evidence.append(f"Current Day: {current_day}")
            evidence.append(f"Total Days: {total_days}")
            evidence.append(f"Remaining Days: {remaining_days}")
            actions = [
                {"label": "What can I do today?", "route": "/tasks"},
                {"label": "What are my pending tasks?", "route": "/tasks"},
                {"label": "Open Roadmap", "route": "/roadmap"},
            ]

        elif intent == "why_pending":
            sources.extend(["roadmap", "all_pending_tasks"])
            m_num = re.search(r"\b(\d+)\b", query)
            num_str = m_num.group(1) if m_num else str(total_pending_count)
            answer = (
                f"The **{num_str}** pending tasks represent all the incomplete tasks distributed across the remaining **{remaining_days}** days of your **{total_days}-day** roadmap (out of {total_tasks_count} total tasks in your curriculum).\n\n"
                f"- **Total Roadmap Tasks**: {total_tasks_count}\n"
                f"- **Completed Tasks**: {completed_tasks_count}\n"
                f"- **Total Pending Across Roadmap**: {total_pending_count}\n"
                f"- **Remaining Roadmap Days**: {remaining_days} days\n"
                f"- **Due Today (Day {current_day})**: {len(today_pending_tasks)} task(s)\n\n"
                f"You do not need to do all {num_str} tasks at once! You only need to complete today's {len(today_pending_tasks)} task(s) to stay on track."
            )
            evidence.append(f"Reported Pending: {num_str}")
            evidence.append(f"Remaining Days: {remaining_days}")
            actions = [
                {"label": "What can I do today?", "route": "/tasks"},
                {"label": "Open Roadmap", "route": "/roadmap"},
            ]

        elif intent == "today_tasks":
            sources.append("today_tasks")
            if today_pending_tasks:
                lines = [f"{idx+1}. 📌 **{t.get('title', 'Task')}** ({t.get('category', 'Technical')}, ~{t.get('estimated_minutes', 60)} mins)" for idx, t in enumerate(today_pending_tasks)]
                answer = (
                    f"Here are your incomplete tasks scheduled for today (Day {current_day} of {total_days}{role_desc}):\n\n"
                    f"{chr(10).join(lines)}\n\n"
                    f"Start with task #1 to maintain your daily consistency streak!"
                )
                evidence.append(f"Today Incomplete Tasks: {len(today_pending_tasks)}")
            else:
                answer = (
                    f"You have no pending tasks scheduled for today (Day {current_day} of {total_days}{role_desc})! 🎉\n\n"
                    f"All tasks for today are completed. You can practice DSA problems, review upcoming roadmap topics, or explore system design concepts."
                )
                evidence.append("Today Incomplete Tasks: 0")
            actions = [
                {"label": "View Today's Tasks", "route": "/tasks"},
                {"label": "How many days are remaining?", "route": "/roadmap"},
            ]

        elif intent == "pending_tasks":
            sources.append("all_pending_tasks")
            today_cnt = len(today_pending_tasks)
            if all_pending_tasks_list or total_pending_count > 0:
                top_lines = []
                for idx, t in enumerate(all_pending_tasks_list[:5]):
                    t_day = t.get("day") or t.get("day_number") or current_day
                    top_lines.append(f"{idx+1}. 📌 **{t.get('title', 'Task')}** (Day {t_day}, {t.get('category', 'General')})")
                more_note = f"\n*...and {total_pending_count - len(all_pending_tasks_list[:5])} more tasks scheduled across remaining days.*" if total_pending_count > 5 else ""
                answer = (
                    f"You have **{total_pending_count}** pending task(s) in total across your {total_days}-day roadmap ({today_cnt} due today on Day {current_day}):\n\n"
                    f"{chr(10).join(top_lines)}{more_note}\n\n"
                    f"Focus on today's tasks first to maintain steady daily progress!"
                )
                evidence.append(f"Total Pending Tasks: {total_pending_count}")
                evidence.append(f"Today Pending Tasks: {today_cnt}")
            else:
                answer = (
                    f"You have **0** pending tasks across your roadmap! All tasks have been completed. Fantastic work!"
                )
                evidence.append("Total Pending Tasks: 0")
            actions = [
                {"label": "What can I do today?", "route": "/tasks"},
                {"label": "How many days are remaining?", "route": "/roadmap"},
            ]

        elif intent in ["interview_questions", "interview_practice"]:
            sources.append("interview")
            m_count = re.search(r"\b(\d+)\b", query)
            q_count = int(m_count.group(1)) if m_count else (5 if any(k in query for k in ["questions", "ask me", "quiz me"]) else 1)
            q_count = max(1, min(q_count, 10))

            if "python" in query:
                topic_title = "Python"
                question_bank = [
                    ("Mutability & Memory Management", "What is the difference between mutable (lists, dicts, sets) and immutable (tuples, strings, ints) types in Python? How does `id()` reflect object mutation versus reassignment?"),
                    ("The Global Interpreter Lock (GIL)", "What is the CPython GIL, and why was it implemented? How does it affect CPU-bound multithreading, and what architectures (e.g. multiprocessing or asyncio) should you use to bypass it?"),
                    ("Generators & Memory Efficiency", "Explain how the `yield` keyword turns a regular function into a generator. What is the space complexity advantage of a generator expression `(x for x in data)` over a list comprehension `[x for x in data]`?"),
                    ("Decorators & Closures", "How do decorators work in Python? Write a clean decorator that measures and prints the execution time of any function using `functools.wraps`."),
                    ("OOP & Python Data Model", "Explain the difference between `__init__` and `__new__`. How do `__repr__` and `__str__` differ, and how does implementing `__eq__` and `__hash__` allow custom objects to be used as dictionary keys?"),
                    ("Dictionary Internals & Hash Collisions", "How does Python's dictionary implement $O(1)$ amortized lookups? How are hash collisions resolved in CPython's compact dictionary implementation?"),
                    ("Variable Scope (LEGB Rule)", "Explain the LEGB rule for variable resolution (Local, Enclosing, Global, Built-in). What are the differences between the `global` and `nonlocal` keywords?"),
                    ("Context Managers & the `with` Statement", "How do context managers work under the hood? Explain the contract between `__enter__` and `__exit__`, including how exceptions are propagated or suppressed."),
                    ("Shallow Copy vs Deep Copy", "What is the difference between `copy.copy()` and `copy.deepcopy()`? When can mutating a shallow copy lead to unexpected side effects in nested structures?"),
                    ("List Comprehension vs Map/Filter", "Compare list comprehensions with `map()` and `filter()`. When is a generator expression preferred over both?"),
                ]
            elif any(w in query for w in ["dsa", "algorithm", "data structure", "leetcode"]):
                topic_title = "Data Structures & Algorithms"
                question_bank = [
                    ("Time & Space Complexity", "Explain the Master Theorem for divide-and-conquer recurrences. What is the time complexity of Merge Sort versus Quick Sort in the worst case?"),
                    ("Hash Map Collisions", "How do separate chaining and open addressing handle collisions in a hash table? What causes worst-case $O(N)$ lookup degradation?"),
                    ("Cycle Detection", "Explain Floyd's Cycle Detection Algorithm (Tortoise and Hare) for linked lists. What is its time and space complexity?"),
                    ("Monotonic Stacks", "When should you use a monotonic stack instead of a standard stack? Walk through solving the Next Greater Element problem."),
                    ("Graph Traversals", "Compare BFS and DFS for finding shortest paths in unweighted graphs. Why does BFS guarantee the shortest path while DFS does not?"),
                ]
            elif any(w in query for w in ["react", "frontend", "javascript"]):
                topic_title = "Frontend & React"
                question_bank = [
                    ("Virtual DOM & Reconciliation", "How does React's Virtual DOM diffing algorithm work, and why are unique `key` props essential when rendering lists?"),
                    ("Hooks Rules & Closures", "Why can't React hooks be called inside conditional statements or loops? Explain stale closures in `useEffect`."),
                    ("State Management", "When would you choose React Context API versus external state managers like Redux Toolkit or Zustand?"),
                    ("Performance Optimization", "Explain the difference between `useMemo`, `useCallback`, and `React.memo`. When does memoization cause more overhead than benefit?"),
                    ("Event Loop in JS", "How does the JavaScript Event Loop handle microtasks (Promises) versus macrotasks (`setTimeout`)?"),
                ]
            elif any(w in query for w in ["sql", "database", "postgres", "rdbms"]):
                topic_title = "Databases & SQL"
                question_bank = [
                    ("ACID Transactions", "Explain Atomicity, Consistency, Isolation, and Durability (ACID). How do database engines implement Isolation levels (Read Committed vs Serializable)?"),
                    ("Indexing Strategies", "What is the internal data structure of a B-Tree index, and why is it preferred over a binary search tree or hash index for range queries?"),
                    ("SQL Joins vs Subqueries", "Compare the query execution plan of an INNER JOIN versus an `IN (...)` or `EXISTS (...)` subquery. How does the query optimizer choose hash join vs nested loop?"),
                    ("Database Normalization", "Explain 1NF, 2NF, 3NF, and BCNF. When is intentional denormalization appropriate in read-heavy applications?"),
                    ("Optimistic vs Pessimistic Locking", "When should you use `SELECT ... FOR UPDATE` versus a version timestamp column for concurrency control?"),
                ]
            elif any(w in query for w in ["system design", "architecture"]):
                topic_title = "System Design & Architecture"
                question_bank = [
                    ("Consistent Hashing", "Explain how Consistent Hashing minimizes cache misses and key remapping when nodes are added or removed in distributed caches."),
                    ("Caching Topologies", "Compare Cache-Aside, Write-Through, Write-Around, and Write-Back caching strategies. How do you resolve stale data under high concurrency?"),
                    ("Database Sharding", "How does horizontal database sharding work? What are the trade-offs of range-based vs hash-based sharding keys?"),
                    ("Rate Limiting Algorithms", "Explain Token Bucket vs Leaky Bucket vs Sliding Window Counter algorithms for API Gateway rate limiting."),
                    ("Event-Driven Architecture", "Explain the difference between message queues (RabbitMQ) and distributed commit logs (Apache Kafka). When do you use each?"),
                ]
            else:
                topic_title = target_role or "Technical Placement"
                question_bank = [
                    ("Core Architecture", f"What are the foundational design principles essential for a modern {target_role or 'software engineer'} role?"),
                    ("Data Structures", "Explain how you choose between an in-memory hash map, a B-Tree, and a binary heap for different workload patterns."),
                    ("Concurrency & Race Conditions", "How do you handle race conditions in multi-threaded backend services or distributed workers?"),
                    ("Database Performance", "Explain composite indexing and the left-to-right prefix matching rule in relational databases."),
                    ("API Reliability", "How do you guarantee idempotency in payment and order processing REST/gRPC APIs?"),
                ]

            if any(w in query for w in ["questions", "ask me", "quiz me"]) or q_count > 1:
                selected_q = question_bank[:q_count]
                q_lines = [f"**{i+1}. {item[0]}**:\n   {item[1]}" for i, item in enumerate(selected_q)]
                questions_formatted = "\n\n".join(q_lines)
                answer = (
                    f"Here are **{len(selected_q)} {topic_title}** interview questions tailored for technical rounds:\n\n"
                    f"{questions_formatted}\n\n"
                    f"💡 **Interactive Practice**: Which question would you like to answer first? Type your response or code, and I'll evaluate your explanation with actionable feedback!"
                )
                evidence.append(f"Topic: {topic_title} Interview Questions")
                evidence.append(f"Questions Count: {len(selected_q)}")
                actions = [
                    {"label": "Answer Question 1", "route": "/interview"},
                    {"label": "What can I do today?", "route": "/tasks"},
                ]
            else:
                q_title, q_desc = question_bank[0]
                answer = (
                    f"Let's practice an interactive **{topic_title}** interview question{role_desc}!\n\n"
                    f"**Problem: {q_title}**\n\n"
                    f"{q_desc}\n\n"
                    f"Share your thought process, approach, and code. I'll evaluate your answer on clarity, time/space complexity, and edge cases!"
                )
                evidence.append("Mode: Technical Interview Simulation")
                evidence.append(f"Topic: {topic_title}")
                actions = [
                    {"label": "Submit Approach", "route": "/interview"},
                    {"label": "What can I do today?", "route": "/tasks"},
                ]

        elif intent == "readiness":
            sources.append("readiness")
            if score is not None:
                evidence.append(f"Readiness Score: {score}/100" + (f" ({readiness_label})" if readiness_label else ""))
                answer = (
                    f"Your overall Placement Readiness score is currently **{score}/100**{role_desc}.\n\n"
                    f"Keep practicing regularly with tasks and mock interviews to maintain top readiness."
                )
            else:
                answer = f"Your Placement Readiness score for **{role_desc}** is being calculated as you complete tasks."
            actions = [
                {"label": "Analyze Placement Readiness", "route": "/readiness"},
                {"label": "Review Skill Gaps", "route": "/skill-gaps"},
            ]

        elif intent in ["leetcode", "dsa"]:
            sources.append("leetcode")
            if leetcode_weak:
                evidence.append(f"LeetCode Weak Topic: {', '.join(str(w) for w in leetcode_weak[:2])}")
            if "two sum" in query or "1" in query:
                answer = (
                    "**LeetCode #1: Two Sum**\n\n"
                    "**Optimal Approach (Single-Pass Hash Map)**:\n"
                    "Iterate through `nums` while computing the complement (`target - num`). If the complement already exists in the hash map, return both indices. Otherwise, insert current number and its index.\n\n"
                    "⏱️ **Time Complexity**: $O(N)$ — Single pass through the array.\n"
                    "💾 **Space Complexity**: $O(N)$ — In the worst case, stores $N$ elements in the dictionary.\n\n"
                    "```python\n"
                    "def twoSum(nums: list[int], target: int) -> list[int]:\n"
                    "    seen = {}\n"
                    "    for i, num in enumerate(nums):\n"
                    "        complement = target - num\n"
                    "        if complement in seen:\n"
                    "            return [seen[complement], i]\n"
                    "        seen[num] = i\n"
                    "    return []\n"
                    "```"
                )
                evidence.append("Problem: LeetCode #1 (Two Sum)")
            elif "reverse" in query or "206" in query:
                answer = (
                    "**LeetCode #206: Reverse Linked List**\n\n"
                    "**Optimal Approach (Iterative 3-Pointers)**:\n"
                    "Maintain `prev`, `curr`, and `next_node`. At each node, reverse `curr.next` to point to `prev`, then advance both pointers.\n\n"
                    "⏱️ **Time Complexity**: $O(N)$ | 💾 **Space Complexity**: $O(1)$\n\n"
                    "```python\n"
                    "class ListNode:\n"
                    "    def __init__(self, val=0, next=None):\n"
                    "        self.val = val\n"
                    "        self.next = next\n\n"
                    "def reverseList(head: ListNode) -> ListNode:\n"
                    "    prev = None\n"
                    "    curr = head\n"
                    "    while curr:\n"
                    "        next_node = curr.next\n"
                    "        curr.next = prev\n"
                    "        prev = curr\n"
                    "        curr = next_node\n"
                    "    return prev\n"
                    "```"
                )
                evidence.append("Problem: LeetCode #206 (Reverse Linked List)")
            elif "valid parentheses" in query or "20" in query:
                answer = (
                    "**LeetCode #20: Valid Parentheses**\n\n"
                    "**Optimal Approach (Stack)**:\n"
                    "Push opening brackets onto a stack. When a closing bracket is encountered, verify it matches the popped element from the top of the stack.\n\n"
                    "⏱️ **Time Complexity**: $O(N)$ | 💾 **Space Complexity**: $O(N)$"
                )
                evidence.append("Problem: LeetCode #20 (Valid Parentheses)")
            elif "kahn" in query or "topological" in query:
                answer = (
                    "**Kahn's Algorithm (Topological Sort via BFS)**:\n\n"
                    "1. Compute in-degree for all vertices.\n"
                    "2. Enqueue all vertices with `in_degree == 0`.\n"
                    "3. While queue is not empty, dequeue $u$, append to ordering, decrement in-degree of neighbors $v$.\n"
                    "4. If neighbor's in-degree becomes 0, enqueue it.\n"
                    "5. If processed vertices < $V$, graph has a cycle!\n\n"
                    "Time: $O(V + E)$ | Space: $O(V)$"
                )
            elif leetcode_weak:
                weak_topic = leetcode_weak[0]
                answer = (
                    f"For your **{target_role or 'placement'}** DSA preparation, your analysis highlights **{weak_topic}** as an area for improvement.\n\n"
                    f"Focus on practicing 2-3 medium difficulty problems specifically in **{weak_topic}** on LeetCode today."
                )
            else:
                answer = (
                    f"For your DSA preparation{role_desc}:\n\n"
                    f"1. **Pattern Mastery**: Focus on Two Pointers, Sliding Window, Monotonic Stack, BFS/DFS, Top-K Heap.\n"
                    f"2. **Daily Habit**: Practice 2 Medium problems daily.\n"
                    f"3. Always analyze Time and Space complexity before writing code."
                )
            actions = [
                {"label": "Solve LeetCode Problems", "route": "/leetcode"},
                {"label": "View Today's Tasks", "route": "/tasks"},
            ]

        else:
            answer = (
                f"Regarding **\"{message}\"**:\n\n"
                f"1. **Overview**: In engineering interviews and placement preparation, mastering the core principles, syntax, and performance characteristics of this topic is critical.\n"
                f"2. **Next Steps**: Review the relevant concept fundamentals, practice problem implementations, or ask for a targeted code example or architectural breakdown.\n\n"
                f"Would you like an illustrative code example, architectural breakdown, or interview-style practice on this topic?"
            )
            actions = [
                {"label": "Explain with code example", "route": "/mentor"},
                {"label": "What can I do today?", "route": "/tasks"},
                {"label": "Practice a technical interview", "route": "/interview"},
            ]

        confidence = 0.95
        return {
            "answer": answer,
            "intent": intent,
            "context_sources": sources,
            "evidence": evidence,
            "suggested_actions": actions,
            "confidence": confidence,
        }
