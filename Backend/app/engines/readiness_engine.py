import logging
from typing import Dict, List, Optional, Any
from app.core.roles import get_role_competencies

logger = logging.getLogger(__name__)

DEFAULT_WEIGHTS = {
    "Resume": 0.15,
    "DSA": 0.20,
    "Projects": 0.20,
    "GitHub": 0.10,
    "CS Fundamentals": 0.15,
    "Communication": 0.10,
    "Interview": 0.10
}


class DeterministicReadinessEngine:
    """
    Deterministic readiness calculation engine enforcing data-driven category evaluation,
    role-aware skill alignment, normalized weights calculation, and data provenance.
    """

    def __init__(self, custom_weights: Optional[Dict[str, float]] = None) -> None:
        self.weights = custom_weights or DEFAULT_WEIGHTS.copy()

    @staticmethod
    def evaluate_resume(
        resume_data: Optional[Dict[str, Any]],
        required_role_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Evaluate Resume category deterministically from existing ATS analysis."""
        if not resume_data:
            return {
                "category": "Resume",
                "key": "resume",
                "score": None,
                "weight": 0.15,
                "weighted_score": 0.0,
                "confidence": 0.0,
                "status": "insufficient_data",
                "evidence": [],
                "missing_data": ["No uploaded resume document found."],
                "recommendations": ["Upload a professional PDF resume to analyze ATS compliance."]
            }

        analysis = resume_data.get("analysis") or resume_data
        ats_score = analysis.get("ats_score", {})
        score_val = ats_score.get("score") if isinstance(ats_score, dict) else analysis.get("overall_score")

        if score_val is None:
            score_val = 75

        score_int = min(100, max(0, int(score_val)))
        evidence = [f"ATS Quality Score: {score_int}/100"]

        skills = analysis.get("skills") or analysis.get("skills_extracted", [])
        if isinstance(skills, dict):
            total_skills = sum(len(v) for v in skills.values() if isinstance(v, list))
            evidence.append(f"Detected {total_skills} verified technical skills.")
        elif isinstance(skills, list):
            evidence.append(f"Detected {len(skills)} verified technical skills.")

        recs = []
        formatting_score = analysis.get("formatting_score", {})
        f_score = formatting_score.get("score") if isinstance(formatting_score, dict) else None
        if f_score and f_score < 80:
            recs.append("Improve resume STAR formatting: start bullets with strong action verbs and metrics.")
        else:
            recs.append("Quantify project impacts with concrete performance metrics on your resume.")

        return {
            "category": "Resume",
            "key": "resume",
            "score": score_int,
            "weight": 0.15,
            "weighted_score": 0.0,
            "confidence": 0.85,
            "status": "scored",
            "evidence": evidence,
            "missing_data": [],
            "recommendations": recs
        }

    @staticmethod
    def evaluate_leetcode(leetcode_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate DSA / LeetCode category deterministically."""
        if not leetcode_data:
            return {
                "category": "DSA",
                "key": "dsa",
                "score": None,
                "weight": 0.20,
                "weighted_score": 0.0,
                "confidence": 0.0,
                "status": "insufficient_data",
                "evidence": [],
                "missing_data": ["No connected LeetCode account."],
                "recommendations": ["Connect your LeetCode handle to analyze DSA problem-solving readiness."]
            }

        stats = leetcode_data.get("statistics", {})
        total_solved = stats.get("total_solved", 0)
        easy_solved = stats.get("easy_solved", 0)
        medium_solved = stats.get("medium_solved", 0)
        hard_solved = stats.get("hard_solved", 0)

        calculated_score = min(98, max(30, int(30 + (easy_solved * 0.15) + (medium_solved * 0.35) + (hard_solved * 0.6))))
        if total_solved == 0:
            calculated_score = 40

        evidence = [
            f"Total Solved: {total_solved} problems",
            f"Breakdown: Easy {easy_solved}, Medium {medium_solved}, Hard {hard_solved}"
        ]

        contest = leetcode_data.get("contest", {})
        if isinstance(contest, dict) and contest.get("rating"):
            evidence.append(f"Contest Rating: {round(contest['rating'])}")

        recs = []
        if hard_solved < 10:
            recs.append(f"Only {hard_solved} Hard problems solved. Complete at least 10 Hard problems in key topic areas.")
        else:
            recs.append("Target Medium & Hard Dynamic Programming and Graph problems.")

        topics = leetcode_data.get("topic_statistics", [])
        if isinstance(topics, list):
            weak_topics = [
                t.get("topic_name") for t in topics
                if isinstance(t, dict) and t.get("problems_solved", 0) < 3 and t.get("topic_name")
            ]
            if weak_topics:
                recs.append(f"Practice under-represented topics: {', '.join(weak_topics[:3])}.")

        return {
            "category": "DSA",
            "key": "dsa",
            "score": calculated_score,
            "weight": 0.20,
            "weighted_score": 0.0,
            "confidence": 0.90 if total_solved > 0 else 0.50,
            "status": "scored",
            "evidence": evidence,
            "missing_data": [],
            "recommendations": recs[:2]
        }

    @staticmethod
    def evaluate_projects(projects_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate Projects category deterministically from AST project intelligence."""
        if not projects_list or len(projects_list) == 0:
            return {
                "category": "Projects",
                "key": "projects",
                "score": None,
                "weight": 0.20,
                "weighted_score": 0.0,
                "confidence": 0.0,
                "status": "insufficient_data",
                "evidence": [],
                "missing_data": ["No portfolio projects recorded."],
                "recommendations": ["Add at least 2 engineering projects with GitHub URLs to build evidence."]
            }

        valid_projects = [p for p in projects_list if p.get("status") != "archived"]
        if not valid_projects:
            return {
                "category": "Projects",
                "key": "projects",
                "score": None,
                "weight": 0.20,
                "weighted_score": 0.0,
                "confidence": 0.0,
                "status": "insufficient_data",
                "evidence": [],
                "missing_data": ["No active portfolio projects found."],
                "recommendations": ["Add your engineering projects to generate AST code complexity metrics."]
            }

        count = len(valid_projects)
        avg_score = sum(p.get("score", 85) for p in valid_projects) / count
        github_linked = sum(1 for p in valid_projects if p.get("githubUrl") or (p.get("links") and p["links"].get("github")))
        live_linked = sum(1 for p in valid_projects if p.get("liveUrl") or (p.get("links") and p["links"].get("live")))

        calculated_score = min(98, max(40, int(avg_score + (github_linked * 3) + (live_linked * 4))))

        evidence = [
            f"{count} active portfolio projects audited.",
            f"Average AST complexity score: {int(avg_score)}/100",
            f"GitHub linkage: {github_linked}/{count} repositories connected",
            f"Live deployment: {live_linked}/{count} projects deployed"
        ]

        recs = []
        if github_linked < count:
            recs.append("Connect GitHub repository URLs for all portfolio projects.")
        if live_linked < count:
            recs.append("Add live deployment URLs and comprehensive README documentation.")
        if not recs:
            recs.append("Maintain clean project architecture and extend automated test suites.")

        return {
            "category": "Projects",
            "key": "projects",
            "score": calculated_score,
            "weight": 0.20,
            "weighted_score": 0.0,
            "confidence": 0.88,
            "status": "scored",
            "evidence": evidence,
            "missing_data": [],
            "recommendations": recs
        }

    @staticmethod
    def evaluate_github(github_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate GitHub category deterministically."""
        if not github_data:
            return {
                "category": "GitHub",
                "key": "github",
                "score": None,
                "weight": 0.10,
                "weighted_score": 0.0,
                "confidence": 0.0,
                "status": "insufficient_data",
                "evidence": [],
                "missing_data": ["No connected GitHub profile."],
                "recommendations": ["Connect your GitHub account to sync repositories and commit history."]
            }

        stats = github_data.get("statistics", {})
        repos = stats.get("total_repositories", 0)
        stars = stats.get("total_stars", 0)
        lang = stats.get("primary_language", "General")

        calculated_score = min(96, max(40, int(50 + min(repos * 3, 30) + min(stars * 2, 16))))

        evidence = [
            f"GitHub Handle: @{github_data.get('github_username', 'user')}",
            f"Repositories: {repos}, Total Stars: {stars}",
            f"Primary Language: {lang}"
        ]

        recs = []
        if stars == 0:
            recs.append("Enhance project READMEs to increase open-source repository engagement.")
        if repos < 3:
            recs.append("Create more public repositories demonstrating consistent commit activity.")
        if not recs:
            recs.append("Maintain a continuous commit streak and document public repository READMEs.")

        return {
            "category": "GitHub",
            "key": "github",
            "score": calculated_score,
            "weight": 0.10,
            "weighted_score": 0.0,
            "confidence": 0.85,
            "status": "scored",
            "evidence": evidence,
            "missing_data": [],
            "recommendations": recs
        }

    @staticmethod
    def evaluate_cs_fundamentals(
        profile_data: Optional[Dict[str, Any]],
        resume_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate CS Fundamentals (OS, DBMS, Networks, OOP) deterministically."""
        # 1. Check for explicit assessment evidence
        if profile_data and isinstance(profile_data, dict):
            assessments = profile_data.get("cs_assessments") or profile_data.get("assessments")
            if isinstance(assessments, dict) and assessments.get("score") is not None:
                score = min(100, max(0, int(assessments["score"])))
                return {
                    "category": "CS Fundamentals",
                    "key": "cs_fundamentals",
                    "score": score,
                    "weight": 0.15,
                    "weighted_score": 0.0,
                    "confidence": 0.85,
                    "status": "scored",
                    "evidence": [f"Verified CS Fundamentals assessment score: {score}/100 across DBMS, OS, Networks, OOP."],
                    "missing_data": [],
                    "recommendations": ["Review OS process scheduling, DBMS indexing, and TCP/IP networking."]
                }

        # 2. Proxy signal check from coursework/skills
        has_proxy_signal = False
        detected_topics: List[str] = []

        if profile_data:
            skills_info = profile_data.get("skills", {})
            if isinstance(skills_info, dict):
                sel_skills = [s.lower() for s in skills_info.get("selectedSkills", [])]
                for t, name in [("dbms", "DBMS"), ("sql", "SQL"), ("system design", "System Design"), ("oops", "OOP"), ("operating systems", "OS")]:
                    if any(t in s for s in sel_skills):
                        detected_topics.append(name)
                        has_proxy_signal = True

        if resume_data and not has_proxy_signal:
            analysis = resume_data.get("analysis") or resume_data
            extracted = [str(s).lower() for s in (analysis.get("skills_extracted") or [])]
            for t, name in [("dbms", "DBMS"), ("sql", "SQL"), ("system design", "System Design"), ("oops", "OOP"), ("operating systems", "OS")]:
                if any(t in s for s in extracted):
                    detected_topics.append(name)
                    has_proxy_signal = True

        if has_proxy_signal:
            return {
                "category": "CS Fundamentals",
                "key": "cs_fundamentals",
                "score": 75,
                "weight": 0.15,
                "weighted_score": 0.0,
                "confidence": 0.55,  # Reduced confidence for proxy signal per Requirement 8
                "status": "scored",
                "evidence": [f"Proxy signal: Coursework/skills detected in {', '.join(detected_topics[:4])}."],
                "missing_data": ["No formal CS Fundamentals technical assessment completed."],
                "recommendations": ["Brush up on SQL query optimization, ACID transactions, and OS concurrency."]
            }

        return {
            "category": "CS Fundamentals",
            "key": "cs_fundamentals",
            "score": None,
            "weight": 0.15,
            "weighted_score": 0.0,
            "confidence": 0.0,
            "status": "insufficient_data",
            "evidence": [],
            "missing_data": ["No CS Fundamentals assessment or coursework evidence detected."],
            "recommendations": ["Complete CS Fundamentals assessments in DBMS, Operating Systems, and Computer Networks."]
        }

    @staticmethod
    def evaluate_communication(
        resume_data: Optional[Dict[str, Any]],
        comm_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate Communication & Technical Explanation category deterministically."""
        if comm_data and isinstance(comm_data, dict):
            score_val = comm_data.get("overall_score") or comm_data.get("score") or 80
            score_int = min(100, max(0, int(score_val)))
            return {
                "category": "Communication",
                "key": "communication",
                "score": score_int,
                "weight": 0.10,
                "weighted_score": 0.0,
                "confidence": 0.85,
                "status": "scored",
                "evidence": [f"Communication assessment score: {score_int}/100 across structure and technical clarity."],
                "missing_data": [],
                "recommendations": ["Practice explaining complex system architecture trade-offs concisely."]
            }

        if resume_data and isinstance(resume_data, dict):
            analysis = resume_data.get("analysis") or resume_data
            formatting = analysis.get("formatting_score", {})
            f_score = formatting.get("score") if isinstance(formatting, dict) else 78
            score_int = min(100, max(40, int(f_score or 78)))
            return {
                "category": "Communication",
                "key": "communication",
                "score": score_int,
                "weight": 0.10,
                "weighted_score": 0.0,
                "confidence": 0.50,  # Reduced confidence for proxy signal per Requirement 9
                "status": "scored",
                "evidence": [f"Limited proxy signal: Resume STAR bullet point formatting compliance: {score_int}/100."],
                "missing_data": ["No full-length spoken communication or oral interview assessment available."],
                "recommendations": ["Practice explaining complex system architecture trade-offs out loud in STAR format."]
            }

        return {
            "category": "Communication",
            "key": "communication",
            "score": None,
            "weight": 0.10,
            "weighted_score": 0.0,
            "confidence": 0.0,
            "status": "insufficient_data",
            "evidence": [],
            "missing_data": ["No communication exercises or spoken assessment completed."],
            "recommendations": ["Complete a spoken technical explanation drill to assess communication skills."]
        }

    @staticmethod
    def evaluate_interview(interview_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate Mock Interview category deterministically."""
        if not interview_data or not isinstance(interview_data, dict):
            return {
                "category": "Interview",
                "key": "interview",
                "score": None,
                "weight": 0.10,
                "weighted_score": 0.0,
                "confidence": 0.0,
                "status": "insufficient_data",
                "evidence": [],
                "missing_data": ["No mock interview sessions completed."],
                "recommendations": ["Complete a simulated mock interview drill to assess live coding and communication performance."]
            }

        score_val = interview_data.get("overall_score") or interview_data.get("score") or 75
        score_int = min(100, max(0, int(score_val)))
        return {
            "category": "Interview",
            "key": "interview",
            "score": score_int,
            "weight": 0.10,
            "weighted_score": 0.0,
            "confidence": 0.85,
            "status": "scored",
            "evidence": [f"Mock interview performance score: {score_int}/100"],
            "missing_data": [],
            "recommendations": ["Practice live coding out loud under realistic time constraints."]
        }

    def compute(
        self,
        target_role: Optional[str],
        profile_data: Optional[Dict[str, Any]] = None,
        resume_data: Optional[Dict[str, Any]] = None,
        github_data: Optional[Dict[str, Any]] = None,
        leetcode_data: Optional[Dict[str, Any]] = None,
        projects_list: Optional[List[Dict[str, Any]]] = None,
        communication_data: Optional[Dict[str, Any]] = None,
        interview_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate evaluation across all 7 categories, dynamically align target role,
        and calculate normalized weighted overall score.
        """
        # 1. Target Role & Skill Alignment Resolution
        display_target_role = target_role if (target_role and str(target_role).strip()) else "Unspecified Role"
        required_role_skills = get_role_competencies(target_role) if target_role else []

        # Collect candidate's aggregated skills across telemetry
        candidate_skills: List[str] = []
        if profile_data and isinstance(profile_data, dict):
            candidate_skills.extend(profile_data.get("technical_skills", []))
            skills_info = profile_data.get("skills", {})
            if isinstance(skills_info, dict):
                candidate_skills.extend(skills_info.get("selectedSkills", []))

        if resume_data and isinstance(resume_data, dict):
            analysis = resume_data.get("analysis") or resume_data
            extracted = analysis.get("skills_extracted") or analysis.get("skills", [])
            if isinstance(extracted, list):
                candidate_skills.extend(extracted)
            elif isinstance(extracted, dict):
                for sk_list in extracted.values():
                    if isinstance(sk_list, list):
                        candidate_skills.extend(sk_list)

        if github_data and isinstance(github_data, dict):
            gh_analysis = github_data.get("analysis", {})
            if isinstance(gh_analysis, dict):
                candidate_skills.extend(gh_analysis.get("top_languages", []))
            stats = github_data.get("statistics", {})
            if isinstance(stats, dict) and stats.get("primary_language"):
                candidate_skills.append(stats["primary_language"])

        if projects_list:
            for p in projects_list:
                if isinstance(p, dict):
                    candidate_skills.extend(p.get("technologies", []))
                    candidate_skills.extend(p.get("architectureTags", []))

        # Normalize skill sets for comparison
        candidate_lower = {s.lower().strip() for s in candidate_skills if s and isinstance(s, str)}

        aligned_skills: List[str] = []
        missing_skills: List[str] = []

        if not required_role_skills:
            role_alignment = {
                "role": display_target_role,
                "aligned_skills": [],
                "missing_skills": [],
                "role_alignment_score": None,
                "status": "insufficient_data",
                "message": "Target role is not specified in student profile. Complete onboarding to select a target role."
            }
        else:
            for req in required_role_skills:
                if req.lower().strip() in candidate_lower or any(req.lower().strip() in c for c in candidate_lower):
                    aligned_skills.append(req)
                else:
                    missing_skills.append(req)

            alignment_score = round((len(aligned_skills) / max(1, len(required_role_skills))) * 100)
            role_alignment = {
                "role": display_target_role,
                "aligned_skills": aligned_skills,
                "missing_skills": missing_skills,
                "role_alignment_score": alignment_score,
                "status": "scored",
                "message": f"Evaluated alignment against {display_target_role} competencies ({alignment_score}% match)."
            }

        # 2. Evaluate 7 Diagnostic Categories
        c_resume = self.evaluate_resume(resume_data, required_role_skills)
        c_dsa = self.evaluate_leetcode(leetcode_data)
        c_projects = self.evaluate_projects(projects_list or [])
        c_github = self.evaluate_github(github_data)
        c_cs = self.evaluate_cs_fundamentals(profile_data, resume_data)
        c_comm = self.evaluate_communication(resume_data, communication_data)
        c_interview = self.evaluate_interview(interview_data)

        categories_dict = {
            "Resume": c_resume,
            "DSA": c_dsa,
            "Projects": c_projects,
            "GitHub": c_github,
            "CS Fundamentals": c_cs,
            "Communication": c_comm,
            "Interview": c_interview
        }

        # 3. Dynamic Weight Normalization Over Scored Categories
        scored_cats = [c for c in categories_dict.values() if c["status"] == "scored" and c["score"] is not None]
        insufficient_cats = [c for c in categories_dict.values() if c["status"] == "insufficient_data" or c["score"] is None]

        weights_used: Dict[str, float] = {name: 0.0 for name in categories_dict.keys()}

        if not scored_cats:
            overall_score = None
            overall_confidence = 0.0
            readiness_label = "Insufficient Evidence"
        else:
            sum_scored_weights = sum(self.weights.get(c["category"], 0.10) for c in scored_cats)
            if sum_scored_weights <= 0:
                sum_scored_weights = 1.0

            weighted_sum = 0.0
            weighted_conf_sum = 0.0

            for cat in scored_cats:
                cat_name = cat["category"]
                base_weight = self.weights.get(cat_name, 0.10)
                norm_w = round(base_weight / sum_scored_weights, 4)
                weights_used[cat_name] = norm_w

                cat["weighted_score"] = round(cat["score"] * norm_w, 2)
                weighted_sum += cat["score"] * norm_w
                weighted_conf_sum += cat["confidence"] * norm_w

            overall_score = int(round(weighted_sum))
            overall_confidence = round(weighted_conf_sum, 2)

            # Ensure sum of scored normalized weights equals ~1.0
            assert abs(sum(weights_used.values()) - 1.0) < 0.001

            if overall_score >= 80 and overall_confidence >= 0.75:
                readiness_label = "Placement Ready"
            elif overall_score >= 68:
                readiness_label = "Advanced"
            elif overall_score >= 50:
                readiness_label = "Developing"
            else:
                readiness_label = "Needs Work"

        # 4. Dynamic Strengths & Key Gaps Selection
        strengths: List[str] = []
        gaps: List[str] = []
        recs: List[str] = []

        for c in scored_cats:
            if c["score"] and c["score"] >= 80:
                strengths.append(f"{c['category']} is a strength ({c['score']}/100) with verified evidence.")
            elif c["score"] and c["score"] < 70:
                gaps.append(f"{c['category']} score is currently below target threshold ({c['score']}/100).")
            recs.extend(c.get("recommendations", []))

        for c in insufficient_cats:
            gaps.append(f"Missing evidence for {c['category']}.")
            recs.extend(c.get("recommendations", []))

        if missing_skills:
            gaps.append(f"Target role missing critical skills: {', '.join(missing_skills[:3])}.")

        # 5. Data Completeness & Provenance
        data_completeness = {
            "profile": profile_data is not None,
            "resume": resume_data is not None,
            "github": github_data is not None,
            "leetcode": leetcode_data is not None,
            "projects": bool(projects_list and len(projects_list) > 0),
            "communication": c_comm["status"] == "scored",
            "interviews": c_interview["status"] == "scored"
        }

        provenance = {
            "resume_analysis_id": str(resume_data["_id"]) if (resume_data and "_id" in resume_data) else None,
            "leetcode_analysis_id": str(leetcode_data["_id"]) if (leetcode_data and "_id" in leetcode_data) else None,
            "project_analysis_ids": [str(p["_id"]) for p in projects_list if "_id" in p] if projects_list else [],
            "github_analysis_id": str(github_data["_id"]) if (github_data and "_id" in github_data) else None,
            "communication_analysis_id": str(communication_data["_id"]) if (communication_data and "_id" in communication_data) else None,
            "interview_session_id": str(interview_data["_id"]) if (interview_data and "_id" in interview_data) else None,
        }

        return {
            "target_role": display_target_role,
            "overall_score": overall_score,
            "overall_confidence": overall_confidence,
            "readiness_label": readiness_label,
            "categories": categories_dict,
            "weights_used": weights_used,
            "scored_categories_count": len(scored_cats),
            "insufficient_categories_count": len(insufficient_cats),
            "strengths": strengths[:4],
            "key_gaps": gaps[:4],
            "recommendations": recs[:5],
            "role_alignment": role_alignment,
            "data_completeness": data_completeness,
            "stale_data": [],
            "provenance": provenance,
            "calculation_version": "1.0"
        }
