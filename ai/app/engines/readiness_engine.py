"""
Deterministic Placement Readiness Engine.
Calculates readiness scores across 7 categories with configurable weighting,
transparent confidence scoring, explicit status tracking, and historical snapshot support.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.engines.profile_engine import StudentProfileIntelligenceEngine
from app.schemas.skills import StudentIntelligenceProfile, ProfileBuildRequest
from app.schemas.resume import ResumeAnalysis
from app.schemas.github import GitHubAnalysis
from app.schemas.leetcode import LeetCodeAnalysis
from app.schemas.student import StudentProfile
from app.schemas.readiness import (
    CategoryReadinessScore,
    PlacementReadinessAnalysis,
    ReadinessCalculateRequest,
    ReadinessScoreSnapshot,
    ReadinessWeights,
)
from app.utils.tech_taxonomy import normalize_skill_name


class PlacementReadinessEngine:
    """
    Deterministic Placement Readiness Engine.
    Combines evidence across 7 categories: Resume, DSA, GitHub, Projects, CS Fundamentals, Communication, Interview.
    """

    def __init__(self):
        self.profile_engine = StudentProfileIntelligenceEngine()

    def calculate_readiness(
        self, request: ReadinessCalculateRequest
    ) -> PlacementReadinessAnalysis:
        """
        Calculates placement readiness across all 7 categories and computes normalized overall score.
        """
        weights_config = request.weights or ReadinessWeights()
        target_role = request.target_role or "Backend Developer"

        # 1. Resolve or build StudentIntelligenceProfile if needed for fallback skill resolution
        profile: Optional[StudentIntelligenceProfile] = None
        if request.profile is not None:
            if isinstance(request.profile, StudentIntelligenceProfile):
                profile = request.profile
            elif isinstance(request.profile, dict) and request.profile:
                try:
                    profile = StudentIntelligenceProfile.model_validate(request.profile)
                except Exception:
                    profile = None

        if profile is None:
            # Build profile from individual analysis objects if available
            profile_req = ProfileBuildRequest(
                student_profile=request.student_profile,
                resume_analysis=request.resume_analysis,
                github_analysis=request.github_analysis,
                leetcode_analysis=request.leetcode_analysis,
            )
            profile = self.profile_engine.build_profile(profile_req)

        # 2. Evaluate each of the 7 categories deterministically
        cat_resume = self._evaluate_resume(request.resume_analysis, profile)
        cat_dsa = self._evaluate_dsa(request.leetcode_analysis, profile)
        cat_github = self._evaluate_github(request.github_analysis, profile)
        cat_projects = self._evaluate_projects(request.resume_analysis, request.github_analysis, profile)
        cat_cs_fund = self._evaluate_cs_fundamentals(profile)
        cat_comm = self._evaluate_communication(request.resume_analysis, request.github_analysis, profile)
        cat_interview = self._evaluate_interview(request.interview_data)

        categories: Dict[str, CategoryReadinessScore] = {
            "Resume": cat_resume,
            "DSA": cat_dsa,
            "GitHub": cat_github,
            "Projects": cat_projects,
            "CS Fundamentals": cat_cs_fund,
            "Communication": cat_comm,
            "Interview": cat_interview,
        }

        # 3. Calculate normalized weighted overall score & confidence
        raw_weights_map = weights_config.get_raw_weights_map()
        scored_cats = [cat for cat in categories.values() if cat.status == "scored" and cat.score is not None]
        insufficient_cats = [cat for cat in categories.values() if cat.status == "insufficient_data"]

        weights_used: Dict[str, float] = {}

        if not scored_cats:
            overall_score = None
            overall_confidence = 0.0
            readiness_label = "Insufficient Evidence"
            formula_explanation = "No category had sufficient evidence to calculate a readiness score."
        else:
            sum_weights_scored = sum(raw_weights_map[cat.category] for cat in scored_cats)
            if sum_weights_scored <= 0:
                sum_weights_scored = 1.0

            # Re-normalize weights over scored categories
            for cat in scored_cats:
                weights_used[cat.category] = round(raw_weights_map[cat.category] / sum_weights_scored, 4)

            weighted_score_sum = sum(cat.score * weights_used[cat.category] for cat in scored_cats)
            overall_score = int(round(weighted_score_sum))

            weighted_conf_sum = sum(cat.confidence * weights_used[cat.category] for cat in scored_cats)
            overall_confidence = round(weighted_conf_sum, 2)

            # Assign readiness label
            if overall_score >= 80 and overall_confidence >= 0.75:
                readiness_label = "Placement Ready"
            elif overall_score >= 68 and overall_confidence >= 0.60:
                readiness_label = "Advanced"
            elif overall_score >= 50:
                readiness_label = "Developing"
            else:
                readiness_label = "Needs Work"

            scored_cat_names = [f"{cat.category} ({int(weights_used[cat.category]*100)}%)" for cat in scored_cats]
            formula_explanation = (
                f"Overall score is calculated using normalized weighted sum over {len(scored_cats)} scored categories: "
                f"{', '.join(scored_cat_names)}. Formula: sum(category_score * normalized_weight)."
            )

        # 4. Extract strengths & key gaps
        strengths: List[str] = []
        key_gaps: List[str] = []

        for cat in scored_cats:
            if cat.score >= 75:
                strengths.append(f"Strong standing in {cat.category} ({cat.score}/100)")
            elif cat.score < 60:
                key_gaps.append(f"{cat.category} score of {cat.score}/100 needs improvement")

        for cat in insufficient_cats:
            key_gaps.append(f"Missing data for {cat.category} category")

        # 5. Build historical snapshot payload
        now_iso = datetime.now(timezone.utc).isoformat()
        snapshot = ReadinessScoreSnapshot(
            timestamp=now_iso,
            overall_score=overall_score,
            overall_confidence=overall_confidence,
            readiness_label=readiness_label,
            category_scores=categories,
        )

        return PlacementReadinessAnalysis(
            target_role=target_role,
            overall_score=overall_score,
            overall_confidence=overall_confidence,
            readiness_label=readiness_label,
            categories=categories,
            weights_used=weights_used,
            scored_categories_count=len(scored_cats),
            insufficient_categories_count=len(insufficient_cats),
            strengths=strengths,
            key_gaps=key_gaps,
            historical_snapshot=snapshot,
            scoring_formula_explanation=formula_explanation,
        )

    # -----------------------------------------------------------------------
    # Individual Category Evaluators
    # -----------------------------------------------------------------------

    def _evaluate_resume(
        self,
        resume: Optional[ResumeAnalysis],
        profile: StudentIntelligenceProfile,
    ) -> CategoryReadinessScore:
        if resume:
            score = resume.overall_score
            ev = [
                f"Resume ATS overall score: {score}/100",
                f"Skills score: {resume.skills_score.score}/100, Projects score: {resume.projects_score.score}/100",
                f"Identified {len(resume.weak_bullets)} weak bullet point(s)",
            ]
            return CategoryReadinessScore(
                category="Resume",
                score=score,
                confidence=0.90,
                status="scored",
                evidence=ev,
            )
        elif profile.source_status.resume_analysis and profile.categories.resume.overall_score:
            score = profile.categories.resume.overall_score
            return CategoryReadinessScore(
                category="Resume",
                score=score,
                confidence=0.85,
                status="scored",
                evidence=profile.categories.resume.evidence,
            )

        return CategoryReadinessScore(
            category="Resume",
            score=None,
            confidence=0.0,
            status="insufficient_data",
            evidence=["No resume analysis provided."],
        )

    def _evaluate_dsa(
        self,
        leetcode: Optional[LeetCodeAnalysis],
        profile: StudentIntelligenceProfile,
    ) -> CategoryReadinessScore:
        if leetcode and leetcode.data_source_status.problems_available and leetcode.problem_statistics.total_solved > 0:
            stats = leetcode.problem_statistics
            
            solved_pts = min(40.0, (stats.total_solved / 150.0) * 40.0)
            medium_pts = min(40.0, (stats.medium_solved / 75.0) * 40.0)
            hard_pts = min(20.0, (stats.hard_solved / 15.0) * 20.0)
            
            calculated_score = int(round(solved_pts + medium_pts + hard_pts))
            final_score = min(100, max(15, calculated_score))

            ev = [
                f"Solved {stats.total_solved} problems on LeetCode ({stats.easy_solved} Easy, {stats.medium_solved} Medium, {stats.hard_solved} Hard)",
                f"Strong topics: {', '.join(leetcode.strong_topics)}" if leetcode.strong_topics else "No strong topics flagged yet",
            ]
            return CategoryReadinessScore(
                category="DSA",
                score=final_score,
                confidence=0.95,
                status="scored",
                evidence=ev,
            )
        elif profile.categories.dsa.overall_level in ["Advanced", "Intermediate", "Beginner"]:
            # Baseline from resume or self-reported DSA
            level = profile.categories.dsa.overall_level
            level_score_map = {"Advanced": 75, "Intermediate": 55, "Beginner": 35}
            score = level_score_map.get(level, 40)
            ev = [
                f"DSA concepts detected in profile ({level} standing), but no LeetCode profile connected to verify submission metrics."
            ]
            return CategoryReadinessScore(
                category="DSA",
                score=score,
                confidence=0.40,  # Low confidence because unverified by contest/problem metrics
                status="scored",
                evidence=ev,
            )

        return CategoryReadinessScore(
            category="DSA",
            score=None,
            confidence=0.0,
            status="insufficient_data",
            evidence=["No LeetCode profile or DSA problem-solving statistics provided."],
        )

    def _evaluate_github(
        self,
        github: Optional[GitHubAnalysis],
        profile: StudentIntelligenceProfile,
    ) -> CategoryReadinessScore:
        if github and github.activity.total_public_repos > 0:
            act = github.activity
            repos = act.non_fork_repos or act.total_public_repos
            readme_pct = (act.repos_with_readme / act.total_public_repos * 100) if act.total_public_repos > 0 else 0.0
            
            repo_pts = min(35.0, (repos / 5.0) * 35.0)
            star_pts = min(20.0, (act.total_stars / 20.0) * 20.0)
            readme_pts = min(25.0, (readme_pct / 100.0) * 25.0)
            
            has_advanced = any(c.complexity_level == "advanced" for c in github.complexity_analyses)
            has_inter = any(c.complexity_level == "intermediate" for c in github.complexity_analyses)
            complexity_pts = 20.0 if has_advanced else (10.0 if has_inter else 5.0)

            score = min(100, int(round(repo_pts + star_pts + readme_pts + complexity_pts)))

            ev = [
                f"Public GitHub profile with {act.total_public_repos} repos ({repos} original)",
                f"{readme_pct:.1f}% README documentation coverage across repositories",
                f"Primary language: {github.languages.primary_language or 'N/A'}, total stars: {act.total_stars}",
            ]
            return CategoryReadinessScore(
                category="GitHub",
                score=score,
                confidence=0.90,
                status="scored",
                evidence=ev,
            )

        return CategoryReadinessScore(
            category="GitHub",
            score=None,
            confidence=0.0,
            status="insufficient_data",
            evidence=["No public GitHub profile analysis provided."],
        )

    def _evaluate_projects(
        self,
        resume: Optional[ResumeAnalysis],
        github: Optional[GitHubAnalysis],
        profile: StudentIntelligenceProfile,
    ) -> CategoryReadinessScore:
        resume_count = len(resume.projects) if resume else 0
        github_count = github.activity.non_fork_repos if github else 0
        total_projects = resume_count + github_count
        metrics_count = sum(1 for p in resume.projects if p.has_metrics) if resume else 0

        if total_projects > 0:
            count_pts = min(40.0, (total_projects / 4.0) * 40.0)
            metrics_pts = min(30.0, (metrics_count / 2.0) * 30.0) if resume else 15.0
            
            has_adv = False
            if github:
                has_adv = any(c.complexity_level == "advanced" for c in github.complexity_analyses)
            complexity_pts = 30.0 if (has_adv or metrics_count >= 2) else 15.0

            score = min(100, int(round(count_pts + metrics_pts + complexity_pts)))
            confidence = 0.85 if (resume and github) else 0.65

            ev = [
                f"Evaluated {total_projects} total project(s) across resume ({resume_count}) and GitHub ({github_count})",
                f"{metrics_count} project(s) highlight quantifiable metrics",
            ]
            return CategoryReadinessScore(
                category="Projects",
                score=score,
                confidence=confidence,
                status="scored",
                evidence=ev,
            )

        return CategoryReadinessScore(
            category="Projects",
            score=None,
            confidence=0.0,
            status="insufficient_data",
            evidence=["No verified projects found on resume or GitHub."],
        )

    def _evaluate_cs_fundamentals(
        self,
        profile: StudentIntelligenceProfile,
    ) -> CategoryReadinessScore:
        # Check CS Fundamental category skills or profile skills
        cs_cat = profile.categories.cs_fundamentals
        cs_skills = cs_cat.skills if cs_cat else []

        detected_areas = set()
        for s in cs_skills:
            detected_areas.add(s.skill)

        # Also check all normalized skills for OS, DBMS, Networks, OOP, System Design
        for s in profile.skills:
            skill_lower = s.skill.lower()
            if any(term in skill_lower for term in ["operating system", "os", "dbms", "database management", "computer network", "networking", "oop", "system design", "lld", "hld"]):
                detected_areas.add(s.skill)

        if detected_areas:
            count = len(detected_areas)
            score = min(100, count * 25)
            confidence = 0.75 if count >= 2 else 0.50

            ev = [
                f"Identified {count} CS Fundamental area(s) in profile: {', '.join(sorted(list(detected_areas)))}"
            ]
            return CategoryReadinessScore(
                category="CS Fundamentals",
                score=score,
                confidence=confidence,
                status="scored",
                evidence=ev,
            )

        return CategoryReadinessScore(
            category="CS Fundamentals",
            score=None,
            confidence=0.0,
            status="insufficient_data",
            evidence=["No CS Fundamentals skills or coursework detected in profile."],
        )

    def _evaluate_communication(
        self,
        resume: Optional[ResumeAnalysis],
        github: Optional[GitHubAnalysis],
        profile: StudentIntelligenceProfile,
    ) -> CategoryReadinessScore:
        bullet_score = resume.impact_score.score if resume else None
        
        readme_pct = None
        if github and github.activity.total_public_repos > 0:
            readme_pct = (github.activity.repos_with_readme / github.activity.total_public_repos * 100)

        if bullet_score is not None and readme_pct is not None:
            score = int(round(0.5 * bullet_score + 0.5 * readme_pct))
            confidence = 0.85
            ev = [
                f"Resume bullet clarity & impact score: {bullet_score}/100",
                f"GitHub repository README coverage: {readme_pct:.1f}%",
            ]
            return CategoryReadinessScore(
                category="Communication",
                score=score,
                confidence=confidence,
                status="scored",
                evidence=ev,
            )
        elif bullet_score is not None:
            return CategoryReadinessScore(
                category="Communication",
                score=bullet_score,
                confidence=0.70,
                status="scored",
                evidence=[f"Resume bullet clarity & impact score: {bullet_score}/100"],
            )
        elif readme_pct is not None:
            return CategoryReadinessScore(
                category="Communication",
                score=int(round(readme_pct)),
                confidence=0.65,
                status="scored",
                evidence=[f"GitHub repository README coverage: {readme_pct:.1f}%"],
            )

        return CategoryReadinessScore(
            category="Communication",
            score=None,
            confidence=0.0,
            status="insufficient_data",
            evidence=["No resume bullet points or GitHub README documentation available to evaluate communication."],
        )

    def _evaluate_interview(
        self,
        interview_data: Optional[Dict[str, Any]],
    ) -> CategoryReadinessScore:
        if interview_data and isinstance(interview_data, dict):
            raw_score = (
                interview_data.get("score")
                or interview_data.get("average_rating")
                or interview_data.get("rating")
                or interview_data.get("overall_score")
            )
            if raw_score is not None:
                score = min(100, max(0, int(raw_score)))
                sessions = interview_data.get("sessions_count") or interview_data.get("mock_interviews_completed") or 1
                ev = [
                    f"Mock interview performance rating: {score}/100 across {sessions} session(s)"
                ]
                return CategoryReadinessScore(
                    category="Interview",
                    score=score,
                    confidence=0.85,
                    status="scored",
                    evidence=ev,
                )

        return CategoryReadinessScore(
            category="Interview",
            score=None,
            confidence=0.0,
            status="insufficient_data",
            evidence=["No mock interview or live interview assessment data available."],
        )
