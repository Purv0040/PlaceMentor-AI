import logging
import random
import uuid
from typing import Optional, Dict, Any, List
from app.role_requirements.roles import get_role_requirements, get_canonical_role_name
from app.schemas.interview import (
    AIInterviewQuestionRequest,
    AIInterviewQuestionResponse,
    AIInterviewAnswerEvaluateRequest,
    AIInterviewAnswerEvaluation,
    AIInterviewCompleteRequest,
    AIInterviewSummaryEvaluation,
)
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class AIInterviewEngine:
    def __init__(self, llm_service: Optional[LLMService] = None) -> None:
        self.llm_service = llm_service or LLMService()

    def generate_question(self, request: AIInterviewQuestionRequest) -> AIInterviewQuestionResponse:
        """Generate an interview question grounded in target role and student context."""
        canonical_role = get_canonical_role_name(request.target_role)
        role_reqs = get_role_requirements(canonical_role)
        role_skills = [r.skill for r in role_reqs]

        # Extract student background evidence
        ctx = request.student_context or {}
        projects = ctx.get("projects") or []
        resume_tech = ctx.get("resume", {}).get("skills", {}) if isinstance(ctx.get("resume"), dict) else {}
        github_repos = ctx.get("github", {}).get("top_repositories", []) if isinstance(ctx.get("github"), dict) else []
        skill_gaps = ctx.get("skill_gaps", {}).get("priority_gaps", []) if isinstance(ctx.get("skill_gaps"), dict) else []

        # Determine topic and question based on interview type & previous answers
        q_num = request.question_number
        itype = request.interview_type.lower()
        diff = request.difficulty.capitalize()

        # Check last Q&A performance for adaptive difficulty/topic selection
        last_eval = request.previous_qa[-1].get("evaluation", {}) if request.previous_qa else {}
        last_score = last_eval.get("score", 75) if isinstance(last_eval, dict) else 75
        
        adaptive_skill = None
        if last_score < 60 and request.previous_qa:
            # Clarifying / fundamental question on last topic
            adaptive_skill = request.previous_qa[-1].get("skill")
        elif last_score > 85 and skill_gaps:
            # Challenge on identified skill gap topic
            adaptive_skill = skill_gaps[0].get("skill") if isinstance(skill_gaps[0], dict) else None

        selected_skill = adaptive_skill or (role_skills[(q_num - 1) % len(role_skills)] if role_skills else "General")

        if itype == "project" and projects:
            p = projects[0]
            p_name = p.get("title") or p.get("name") or "Portfolio Project"
            p_tech = ", ".join(p.get("technologies", ["Python"]))
            question_text = f"In your project '{p_name}' using {p_tech}, describe the architectural trade-offs you faced when designing the data flow and how you handled high throughput or errors."
            category = "Project Architecture"
            expected_focus = "System design decisions, error handling, scale bottlenecks"
            hint = f"Focus on how {p_name} manages component separation and performance under load."

        elif itype == "hr" or itype == "behavioral":
            behavioral_questions = [
                (f"Tell me about a time when you faced a difficult technical challenge working with {selected_skill}. How did you resolve it?", "STAR Framework (Situation, Task, Action, Result)"),
                ("Describe a scenario where you had a conflict or disagreement over technical architecture in a team project.", "Conflict resolution & communication"),
                ("Give an example of a project deadline that was at risk. How did you prioritize tasks and deliver?", "Task management & accountability"),
            ]
            q_tuple = behavioral_questions[(q_num - 1) % len(behavioral_questions)]
            question_text = q_tuple[0]
            category = "Behavioral & STAR"
            expected_focus = q_tuple[1]
            hint = "Use the STAR method: Situation, Task, Action, and Quantified Result."

        elif itype == "dsa":
            dsa_questions = [
                ("How would you optimize the search for pair sums in an unsorted array from O(N^2) to O(N) time complexity? Walk through your approach and edge cases.", "Time & Space complexity, Hash Table lookup"),
                ("Explain how to detect a cycle in a Directed Acyclic Graph (DAG) or linked list, comparing BFS/DFS topological sort approach with Floyd's Algorithm.", "Cycle detection, BFS/DFS traversal"),
                ("Describe how Dynamic Programming memoization converts an exponential recursive tree into polynomial time for 2D grid pathfinding.", "Memoization, Tabulation, Subproblem overlap"),
            ]
            q_tuple = dsa_questions[(q_num - 1) % len(dsa_questions)]
            question_text = q_tuple[0]
            category = "Data Structures & Algorithms"
            expected_focus = q_tuple[1]
            hint = "State the brute force complexity first, then explain the optimal hash or 2-pointer strategy."

        elif itype == "system_design":
            sys_questions = [
                (f"Design a scalable RESTful API service for {canonical_role} handling 10,000 req/sec. How do you implement caching with Redis and database sharding?", "Scalability, Caching, DB Sharding"),
                ("How do you handle API rate-limiting and token bucket algorithm in a distributed microservices environment?", "Distributed rate limiting, Redis atomic ops"),
                ("Compare SQL relational transactional consistency (ACID) vs NoSQL document database eventual consistency for real-time applications.", "ACID vs BASE, CAP theorem trade-offs"),
            ]
            q_tuple = sys_questions[(q_num - 1) % len(sys_questions)]
            question_text = q_tuple[0]
            category = "System Design & Architecture"
            expected_focus = q_tuple[1]
            hint = "Diagram key components: Load Balancer -> API Gateway -> Service Instances -> Cache -> Database."

        else:  # Technical / Role-specific
            tech_questions = [
                (f"Explain how {selected_skill} works under the hood in {canonical_role} applications, highlighting memory management and concurrency.", "Core language runtime & execution model"),
                (f"What are the key security and performance considerations when building production REST APIs with {selected_skill}?", "Authentication, CORS, SQL injection, async I/O"),
                (f"How do you profile, debug, and eliminate performance bottlenecks in a {canonical_role} microservice?", "Profiling, monitoring metrics, query optimization"),
            ]
            q_tuple = tech_questions[(q_num - 1) % len(tech_questions)]
            question_text = q_tuple[0]
            category = "Technical Core"
            expected_focus = q_tuple[1]
            hint = f"Structure your answer with definition, implementation details, and concrete trade-offs."

        return AIInterviewQuestionResponse(
            question_id=f"q_{request.target_role.lower().replace(' ', '_')}_{q_num}_{uuid.uuid4().hex[:6]}",
            question_number=q_num,
            question=question_text,
            category=category,
            skill=selected_skill,
            difficulty=diff,
            expected_focus=expected_focus,
            hint=hint,
        )

    def evaluate_answer(self, request: AIInterviewAnswerEvaluateRequest) -> AIInterviewAnswerEvaluation:
        """Evaluate student submitted answer using rule-based metrics & structured analysis."""
        ans = request.answer.strip()
        word_count = len(ans.split()) if ans else 0

        if word_count < 10:
            return AIInterviewAnswerEvaluation(
                score=35,
                correctness=40,
                relevance=40,
                clarity=35,
                depth=20,
                technical_accuracy=30,
                communication_quality=40,
                strengths=["Submitted a response."],
                weaknesses=["Answer is extremely brief and lacks technical depth.", "No concrete code examples or architectural explanations provided."],
                improvement_suggestions=["Expand answer by covering: 1. Core concept, 2. Implementation details, 3. Trade-offs/metrics."],
                ai_feedback="Response is too concise for a technical interview. Elaborate on the underlying mechanics and trade-offs.",
                follow_up_needed=True,
                suggested_next_topic=request.skill,
            )

        # Evaluate quality based on key technical vocabulary & structure
        has_metrics = any(char.isdigit() for char in ans)
        has_structure = any(marker in ans.lower() for marker in ["first", "second", "specifically", "because", "however", "for example", "trade-off"])
        has_tech_kw = any(kw in ans.lower() for kw in [request.skill.lower(), "performance", "api", "database", "complexity", "o(n)", "cache", "scale", "system"])

        score_acc = min(95, max(60, 65 + (15 if has_tech_kw else 0) + (10 if has_metrics else 0)))
        score_depth = min(95, max(55, 60 + min(25, word_count // 5)))
        score_clarity = min(95, max(60, 70 + (15 if has_structure else 0)))
        score_comm = min(95, max(65, 75 + (10 if word_count >= 40 else 0)))

        overall = int((score_acc * 0.35) + (score_depth * 0.25) + (score_clarity * 0.20) + (score_comm * 0.20))

        strengths = [
            f"Demonstrated good conceptual awareness of {request.skill}.",
            "Used appropriate technical terms and structured reasoning.",
        ]
        if has_metrics:
            strengths.append("Included quantitative references and metrics.")

        weaknesses = []
        if not has_metrics:
            weaknesses.append("Could include concrete quantitative benchmark metrics (e.g. latency, throughput, memory impact).")
        if word_count < 35:
            weaknesses.append("Response depth could be expanded to cover edge cases and failover strategies.")

        suggestions = [
            f"When answering {request.category} questions, explicitly state time/space complexity or latency trade-offs.",
            "Use the STAR approach for behavioral/project questions (Situation, Task, Action, Result).",
        ]

        return AIInterviewAnswerEvaluation(
            score=overall,
            correctness=score_acc,
            relevance=min(95, score_acc + 5),
            clarity=score_clarity,
            depth=score_depth,
            technical_accuracy=score_acc,
            communication_quality=score_comm,
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_suggestions=suggestions,
            ai_feedback=f"Solid technical explanation scored at {overall}/100. Good coverage of {request.skill} principles.",
            follow_up_needed=overall < 70,
            suggested_next_topic=request.skill if overall < 70 else None,
        )

    def evaluate_complete_session(self, request: AIInterviewCompleteRequest) -> AIInterviewSummaryEvaluation:
        """Calculate overall interview evaluation from Q&A history."""
        qna = request.qna_history or []
        if not qna:
            return AIInterviewSummaryEvaluation(
                overall_score=70,
                category_scores={"Technical": 70, "Communication": 70},
                strengths=["Completed session setup."],
                weaknesses=["No answers recorded."],
                recommendations=["Attempt all questions in the mock interview drill."],
                technical_gaps=[],
                communication_feedback={"clarity": 70},
                overall_feedback="Session ended with no submitted answers.",
            )

        scores = []
        cat_scores: Dict[str, List[int]] = {}
        all_strengths = []
        all_weaknesses = []
        tech_gaps = []

        for item in qna:
            ev = item.get("evaluation") or {}
            sc = ev.get("score", 75)
            scores.append(sc)

            cat = item.get("category", "Technical")
            cat_scores.setdefault(cat, []).append(sc)

            if isinstance(ev.get("strengths"), list):
                all_strengths.extend(ev.get("strengths", []))
            if isinstance(ev.get("weaknesses"), list):
                all_weaknesses.extend(ev.get("weaknesses", []))
            if sc < 65 and item.get("skill"):
                tech_gaps.append(item.get("skill"))

        avg_score = int(sum(scores) / len(scores)) if scores else 75
        avg_cat = {cat: int(sum(sc_list) / len(sc_list)) for cat, sc_list in cat_scores.items()}

        unique_strengths = list(dict.fromkeys(all_strengths))[:4] or ["Good baseline technical knowledge."]
        unique_weaknesses = list(dict.fromkeys(all_weaknesses))[:4] or ["Can improve STAR structure compliance."]
        unique_gaps = list(dict.fromkeys(tech_gaps))

        recommendations = [
            f"Focus upcoming daily task practice on identified technical gaps: {', '.join(unique_gaps or ['Advanced System Design']).title()}.",
            "Practice structuring answers into clear 3-step points (Context -> Core Architecture -> Quantitative Outcome).",
            "Maintain optimal speaking cadence (140-150 WPM) during live verbal delivery.",
        ]

        return AIInterviewSummaryEvaluation(
            overall_score=avg_score,
            category_scores=avg_cat,
            strengths=unique_strengths,
            weaknesses=unique_weaknesses,
            recommendations=recommendations,
            technical_gaps=unique_gaps,
            communication_feedback={
                "clarity": int(avg_score * 0.95),
                "structure": int(avg_score * 0.92),
                "articulation": "Optimal interview cadence" if avg_score >= 75 else "Needs structural refinement",
            },
            overall_feedback=f"Performance rated at {avg_score}/100 across {len(qna)} question(s) for target role {request.target_role}.",
        )
