"""
Deterministic Skill Gap Engine.
Determines exact skill gaps, priority levels, evidence grounding, and actionable recommendations
for a student relative to a target role.
"""
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.role_requirements.roles import get_canonical_role_name, get_role_requirements
from app.schemas.skills import NormalizedSkill, StudentIntelligenceProfile, ProfileBuildRequest
from app.schemas.skill_gap import (
    RoleSkillRequirement,
    SkillGapAnalysis,
    SkillGapItem,
    SkillGapRequest,
)
from app.services.llm_service import LLMService
from app.utils.tech_taxonomy import normalize_skill_name
from app.engines.profile_engine import StudentProfileIntelligenceEngine


LEVEL_NUMERIC: Dict[str, int] = {
    "not detected": 0,
    "untested": 0,
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
    "expert": 4,
}


class LLMExplanationItem(BaseModel):
    skill: str
    explanation: str
    recommended_action: str


class LLMSynthesisOutput(BaseModel):
    summary: str
    item_explanations: List[LLMExplanationItem] = Field(default_factory=list)


class SkillGapEngine:
    """
    Deterministic Skill Gap Engine.
    Calculates level differences, gap severities, priority ratings, and evidence-grounded recommendations.
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
        self.profile_engine = StudentProfileIntelligenceEngine()

    def analyze_gaps(
        self,
        target_role: str,
        profile: Optional[Any] = None,
        profile_request: Optional[ProfileBuildRequest] = None,
    ) -> SkillGapAnalysis:
        """
        Calculates skill gaps between the student's profile and the target role requirements.
        """
        canonical_role = get_canonical_role_name(target_role)
        role_reqs = get_role_requirements(canonical_role)

        # Flexibly parse profile parameter (can be StudentIntelligenceProfile, dict, or None)
        parsed_profile: Optional[StudentIntelligenceProfile] = None
        if profile is not None:
            if isinstance(profile, StudentIntelligenceProfile):
                parsed_profile = profile
            elif isinstance(profile, dict) and profile:
                try:
                    parsed_profile = StudentIntelligenceProfile.model_validate(profile)
                except Exception:
                    parsed_profile = None

        if parsed_profile is None:
            req_to_use = profile_request if profile_request else ProfileBuildRequest()
            parsed_profile = self.profile_engine.build_profile(req_to_use)

        profile = parsed_profile

        # Build skill lookups from profile
        profile_skills_map: Dict[str, NormalizedSkill] = {
            s.skill.lower(): s for s in profile.skills
        }
        category_levels: Dict[str, str] = {
            "programming": profile.categories.programming.overall_level,
            "dsa": profile.categories.dsa.overall_level,
            "backend": profile.categories.backend.overall_level,
            "frontend": profile.categories.frontend.overall_level,
            "machine_learning": profile.categories.machine_learning.overall_level,
            "data_science": profile.categories.data_science.overall_level,
            "databases": profile.categories.databases.overall_level,
            "devops": profile.categories.devops.overall_level,
            "cloud": profile.categories.cloud.overall_level,
            "cs_fundamentals": profile.categories.cs_fundamentals.overall_level,
        }

        # Check prerequisite dependencies
        prereq_needed_set = set()
        for req in role_reqs:
            for prereq in req.prerequisites:
                prereq_needed_set.add(prereq.lower())

        gap_items: List[SkillGapItem] = []
        high_priority: List[str] = []
        medium_priority: List[str] = []
        low_priority: List[str] = []
        overall_evidence: List[str] = []

        for req in role_reqs:
            canonical_skill, _ = normalize_skill_name(req.skill)
            skill_key = canonical_skill.lower()

            # Find current level and evidence from profile
            matching_skill = profile_skills_map.get(skill_key) or profile_skills_map.get(req.skill.lower())
            
            if matching_skill:
                curr_level = matching_skill.current_level
                evidence = list(matching_skill.evidence)
            else:
                # Fallback to category level if available
                cat_key = req.category.lower().replace(" ", "_")
                cat_level = category_levels.get(cat_key, "Untested")
                if cat_level in ["Advanced", "Intermediate", "Beginner"]:
                    curr_level = cat_level
                    evidence = [f"Inferred {cat_level} standing from overall {req.category} category analysis."]
                else:
                    curr_level = "Untested"
                    evidence = [f"No verified evidence of {canonical_skill} detected in analyzed profiles."]

            # Check if there was a flagged conflict for this skill
            conflict_note = next(
                (c.conflict for c in profile.conflicts if c.skill_or_topic.lower() in [skill_key, req.skill.lower()]),
                None,
            )
            if conflict_note and f"Discrepancy: {conflict_note}" not in evidence:
                evidence.append(f"Discrepancy: {conflict_note}")

            # Calculate deterministic gap severity
            req_num = LEVEL_NUMERIC.get(req.required_level.lower(), 2)
            curr_num = LEVEL_NUMERIC.get(curr_level.lower(), 0)
            level_diff = req_num - curr_num

            if level_diff <= 0:
                gap = "None"
            elif level_diff == 1:
                gap = "Low"
            elif level_diff == 2:
                gap = "Medium"
            elif curr_num == 0 and req_num >= 3:
                gap = "Critical"
            else:
                gap = "High"

            # Calculate deterministic priority
            is_prereq_for_other = skill_key in prereq_needed_set
            priority = self._calculate_priority(
                importance=req.importance,
                gap=gap,
                is_prereq=is_prereq_for_other,
            )

            # Categorize into priority lists if there is a gap
            if gap != "None":
                if priority == "High":
                    high_priority.append(canonical_skill)
                elif priority == "Medium":
                    medium_priority.append(canonical_skill)
                else:
                    low_priority.append(canonical_skill)

            item = SkillGapItem(
                skill=canonical_skill,
                current_level=curr_level,
                required_level=req.required_level,
                gap=gap,
                priority=priority,
                importance=req.importance,
                category=req.category,
                evidence=evidence,
            )
            gap_items.append(item)

        # Synthesize natural-language explanations and recommendations via LLM / Fallback
        gap_items, summary = self._synthesize_explanations(
            target_role=canonical_role,
            profile=profile,
            gap_items=gap_items,
            high_priority=high_priority,
            medium_priority=medium_priority,
        )

        # Aggregate top evidence points
        for item in gap_items:
            if item.priority in ["High", "Medium"] and item.evidence:
                overall_evidence.extend(item.evidence[:2])
        overall_evidence = list(dict.fromkeys(overall_evidence))[:8]  # Deduplicate

        return SkillGapAnalysis(
            target_role=canonical_role,
            skills=gap_items,
            high_priority=high_priority,
            medium_priority=medium_priority,
            low_priority=low_priority,
            summary=summary,
            evidence=overall_evidence,
        )

    def _calculate_priority(
        self, importance: str, gap: str, is_prereq: bool
    ) -> str:
        """
        Deterministic priority logic based on importance, gap severity, and prerequisite dependency.
        """
        imp = importance.lower()
        
        if gap == "None":
            return "Low"

        # Critical / High importance with significant gap -> High priority
        if imp == "critical" and gap in ["Critical", "High", "Medium"]:
            return "High"
        if imp == "high" and gap in ["Critical", "High"]:
            return "High"
        if is_prereq and gap in ["Critical", "High", "Medium"]:
            return "High"

        # Moderate gaps or high importance low gap -> Medium priority
        if imp in ["critical", "high"] and gap in ["Medium", "Low"]:
            return "Medium"
        if imp == "medium" and gap in ["Critical", "High", "Medium"]:
            return "Medium"

        return "Low"

    def _synthesize_explanations(
        self,
        target_role: str,
        profile: StudentIntelligenceProfile,
        gap_items: List[SkillGapItem],
        high_priority: List[str],
        medium_priority: List[str],
    ) -> Tuple[List[SkillGapItem], str]:
        """
        Calls LLM Service to populate explanation, recommended_action, and executive summary.
        Falls back cleanly to deterministic template strings if LLM is unavailable.
        """
        gaps_to_explain = [item for item in gap_items if item.gap != "None"]
        
        # Prepare deterministic fallbacks first
        for item in gap_items:
            if item.gap == "None":
                item.explanation = f"Meets required '{item.required_level}' level for {target_role}."
                item.recommended_action = f"Maintain proficiency in {item.skill} through practice."
            else:
                item.explanation = f"{item.skill} is a {item.importance} requirement for {target_role}. Current level '{item.current_level}' is below required '{item.required_level}'."
                item.recommended_action = f"Practice {item.skill} to advance from {item.current_level} to {item.required_level}."

        fallback_summary = (
            f"Skill gap analysis for {target_role} identified {len(high_priority)} high-priority gap(s) "
            f"and {len(medium_priority)} medium-priority gap(s) based on verified profile evidence."
        )

        if not gaps_to_explain:
            return gap_items, f"Student meets or exceeds all core skill requirements for {target_role}."

        # Attempt LLM synthesis
        try:
            from app.prompts.skill_gap_prompts import SKILL_GAP_USER_PROMPT
            
            gaps_payload = [
                {
                    "skill": item.skill,
                    "current_level": item.current_level,
                    "required_level": item.required_level,
                    "gap": item.gap,
                    "priority": item.priority,
                    "importance": item.importance,
                    "evidence": item.evidence,
                }
                for item in gaps_to_explain
            ]

            prompt_text = SKILL_GAP_USER_PROMPT.format(
                target_role=target_role,
                readiness=profile.overall_readiness_level,
                high_priority_str=", ".join(high_priority) if high_priority else "None",
                medium_priority_str=", ".join(medium_priority) if medium_priority else "None",
                gaps_data_json=str(gaps_payload),
            )

            res = self.llm_service.generate_structured(
                prompt=prompt_text,
                response_model=LLMSynthesisOutput,
            )

            # Map generated explanations back to gap_items
            item_map = {e.skill.lower(): e for e in res.item_explanations}
            for item in gap_items:
                matched = item_map.get(item.skill.lower())
                if matched:
                    if matched.explanation:
                        item.explanation = matched.explanation
                    if matched.recommended_action:
                        item.recommended_action = matched.recommended_action

            summary = res.summary if res.summary else fallback_summary
            return gap_items, summary

        except Exception:
            # On LLM failure or offline mode, return deterministic fallback cleanly
            return gap_items, fallback_summary
