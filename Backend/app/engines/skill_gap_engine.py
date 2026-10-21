import logging
from typing import Dict, List, Optional, Tuple, Any, Set

logger = logging.getLogger(__name__)

# Level numeric mappings
LEVEL_NUMERIC: Dict[str, int] = {
    "not detected": 0,
    "untested": 0,
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
    "expert": 4,
}

NUMERIC_TO_LEVEL: Dict[int, str] = {
    0: "Untested",
    1: "Beginner",
    2: "Intermediate",
    3: "Advanced",
    4: "Expert"
}

# Alias Lookup: maps lowercase alias -> canonical name
ALIAS_LOOKUP: Dict[str, str] = {
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "java": "Java",
    "cpp": "C++",
    "c++": "C++",
    "c": "C",
    "c#": "C#",
    "csharp": "C#",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "sql": "SQL",
    "dsa": "Data Structures & Algorithms",
    "data structures": "Data Structures & Algorithms",
    "algorithms": "Data Structures & Algorithms",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "next": "Next.js",
    "nextjs": "Next.js",
    "vue": "Vue.js",
    "html": "HTML/CSS",
    "css": "HTML/CSS",
    "html/css": "HTML/CSS",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "ci/cd": "CI/CD",
    "git": "Git",
    "github": "Git",
    "aws": "AWS",
    "system design": "System Design",
    "rest": "REST API",
    "rest api": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",
    "graphql": "GraphQL",
    "kafka": "Kafka",
    "rabbitmq": "RabbitMQ",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "deep learning": "Deep Learning",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "tableau": "Tableau",
    "powerbi": "Power BI",
    "statistics": "Statistics",
    "data visualization": "Data Visualization",
    "exploratory data analysis": "Exploratory Data Analysis",
    "eda": "Exploratory Data Analysis",
    "dbms": "DBMS",
    "operating systems": "Operating Systems",
    "computer networks": "Computer Networks",
    "oop": "Object-Oriented Programming",
    "oops": "Object-Oriented Programming",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "linux": "Linux",
    "terraform": "Terraform",
    "threat detection": "Threat Detection",
    "vulnerability assessment": "Vulnerability Assessment",
    "siem": "SIEM",
    "security fundamentals": "Security Fundamentals",
    "cryptography": "Cryptography",
    "security architecture": "Security Architecture",
    "selenium": "Selenium",
    "database tuning": "Database Tuning",
    "react native": "React Native",
    "figma": "Figma",
    "user research": "User Research",
    "design systems": "Design Systems",
    "wireframing": "Wireframing & Prototyping",
    "wireframing & prototyping": "Wireframing & Prototyping",
    "user experience design": "User Experience Design",
    "ux": "User Experience Design",
    "requirements gathering": "Requirements Gathering",
    "agile": "Agile Methodologies",
    "agile methodologies": "Agile Methodologies",
    "excel": "Excel Modeling",
    "excel modeling": "Excel Modeling",
    "mlops": "MLOps"
}

# Mapping canonical skill -> category
TECH_TAXONOMY: Dict[str, str] = {
    "Python": "Programming",
    "Java": "Programming",
    "C++": "Programming",
    "C": "Programming",
    "C#": "Programming",
    "JavaScript": "Programming",
    "TypeScript": "Programming",
    "Go": "Programming",
    "Rust": "Programming",
    "SQL": "Databases",
    "HTML/CSS": "Frontend",
    "Data Structures & Algorithms": "DSA",
    "Arrays": "DSA",
    "Dynamic Programming": "DSA",
    "Trees": "DSA",
    "Graphs": "DSA",
    "FastAPI": "Backend",
    "Flask": "Backend",
    "Django": "Backend",
    "Spring Boot": "Backend",
    "Node.js": "Backend",
    "Express.js": "Backend",
    "REST API": "Backend",
    "Kafka": "Backend",
    "RabbitMQ": "Backend",
    "React": "Frontend",
    "Next.js": "Frontend",
    "Vue.js": "Frontend",
    "Tailwind CSS": "Frontend",
    "PostgreSQL": "Databases",
    "MySQL": "Databases",
    "MongoDB": "Databases",
    "Redis": "Databases",
    "Database Tuning": "Databases",
    "Docker": "DevOps",
    "Kubernetes": "DevOps",
    "CI/CD": "DevOps",
    "Git": "DevOps",
    "Terraform": "DevOps",
    "MLOps": "DevOps",
    "AWS": "Cloud",
    "Linux": "OS",
    "System Design": "CS Fundamentals",
    "DBMS": "CS Fundamentals",
    "Operating Systems": "CS Fundamentals",
    "Computer Networks": "CS Fundamentals",
    "Object-Oriented Programming": "CS Fundamentals",
    "PyTorch": "Machine Learning",
    "TensorFlow": "Machine Learning",
    "Scikit-learn": "Machine Learning",
    "Deep Learning": "Machine Learning",
    "Machine Learning": "Machine Learning",
    "Pandas": "Data Science",
    "NumPy": "Data Science",
    "Tableau": "Data Science",
    "Power BI": "Data Science",
    "Statistics": "Data Science",
    "Data Visualization": "Data Science",
    "Exploratory Data Analysis": "Data Science",
    "Security Fundamentals": "Security",
    "Threat Detection": "Security",
    "Vulnerability Assessment": "Security",
    "SIEM": "Security",
    "Cryptography": "Security",
    "Security Architecture": "Security",
    "Selenium": "Testing",
    "React Native": "Mobile",
    "Figma": "Design",
    "User Research": "Design",
    "Design Systems": "Design",
    "Wireframing & Prototyping": "Design",
    "User Experience Design": "Design",
    "Requirements Gathering": "Business",
    "Agile Methodologies": "Business",
    "Excel Modeling": "Business",
}

from app.services.role_requirement_service import (
    RoleRequirementService,
    RoleNormalizationService,
    ROLE_REQUIREMENTS_REGISTRY,
    ROLE_ALIASES,
)

# Export for backward compatibility with existing tests/services
ROLE_REQUIREMENTS = ROLE_REQUIREMENTS_REGISTRY


def normalize_skill_name(raw_name: str) -> Tuple[str, str]:
    """Normalize raw skill name to canonical title and engineering category."""
    if not raw_name:
        return "", "Programming"
    clean = raw_name.strip()
    lookup = clean.lower().replace("_", " ").replace("-", " ")
    canonical = ALIAS_LOOKUP.get(clean.lower()) or ALIAS_LOOKUP.get(lookup)
    if not canonical:
        if clean in TECH_TAXONOMY:
            canonical = clean
        else:
            canonical = clean.title() if len(clean) > 3 else clean.upper()
    category = TECH_TAXONOMY.get(canonical, "Programming")
    return canonical, category


def get_canonical_role(target_role: Optional[str]) -> str:
    """Resolve target role name to canonical registry key using centralized RoleNormalizationService."""
    if not target_role:
        return "Software Engineer"
    return RoleNormalizationService.normalize(target_role)


def _is_role_name(skill: str, canonical_role: str) -> bool:
    """
    Return True if the skill string matches the target role name (or a known alias).
    Used to prevent the target role itself from appearing as a required skill.
    """
    s_norm = RoleNormalizationService._normalize_for_lookup(skill)
    r_norm = RoleNormalizationService._normalize_for_lookup(canonical_role)
    if s_norm == r_norm:
        return True
    # Also check against all aliases
    from app.services.role_requirement_service import ROLE_ALIASES
    for alias, canon in ROLE_ALIASES.items():
        if s_norm == alias and canon == canonical_role:
            return True
    return False


class DeterministicSkillGapEngine:
    """Pure, deterministic engine that evaluates candidate skill evidence against target role benchmarks."""

    def __init__(self, role_service: Optional[RoleRequirementService] = None) -> None:
        self.role_service = role_service or RoleRequirementService()

    def normalize_skills(self, raw_skills: List[str]) -> List[str]:
        """Normalize a list of raw skill strings."""
        result: List[str] = []
        for s in raw_skills:
            can, _ = normalize_skill_name(s)
            if can and can not in result:
                result.append(can)
        return result

    def get_role_requirements(self, target_role: str) -> List[Dict[str, Any]]:
        """Retrieve requirement list for a given role dynamically from RoleRequirementService."""
        return self.role_service.get_requirements(target_role)



    def build_skill_inventory(
        self,
        profile_data: Optional[Dict[str, Any]] = None,
        resume_data: Optional[Dict[str, Any]] = None,
        github_data: Optional[Dict[str, Any]] = None,
        leetcode_data: Optional[Dict[str, Any]] = None,
        projects_list: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate verified factual telemetry from all 5 modules into a comprehensive skill evidence map.
        """
        inventory: Dict[str, Dict[str, Any]] = {}

        def _add_evidence(skill_name: str, source: str, detail: str, weight: int = 1):
            canonical, category = normalize_skill_name(skill_name)
            if not canonical:
                return
            key = canonical.lower()
            if key not in inventory:
                inventory[key] = {
                    "skill": canonical,
                    "category": category,
                    "evidence_items": [],
                    "evidence_sources": set(),
                    "evidence_weight": 0,
                }
            inventory[key]["evidence_items"].append({"source": source, "detail": detail})
            inventory[key]["evidence_sources"].add(source)
            inventory[key]["evidence_weight"] += weight

        # 1. Student Profile Data
        if profile_data:
            technical_skills = profile_data.get("technical_skills", [])
            for s in technical_skills:
                _add_evidence(s, "profile", f"Declared '{s}' in technical profile.", weight=1)
            
            # Categories in profile
            profile_categories = profile_data.get("categories", {})
            if isinstance(profile_categories, dict):
                for cat_name, cat_obj in profile_categories.items():
                    if isinstance(cat_obj, dict) and cat_obj.get("skills"):
                        for sk in cat_obj["skills"]:
                            _add_evidence(sk, "profile", f"Listed in {cat_name} category.", weight=1)

        # 2. Resume Data
        if resume_data:
            resume_analysis = resume_data.get("analysis", {})
            if isinstance(resume_analysis, dict):
                extracted_skills = resume_analysis.get("skills_extracted", [])
                for s in extracted_skills:
                    _add_evidence(s, "resume", f"Extracted from resume technical audit.", weight=2)
                
                # Check experience or projects in resume
                for exp in resume_analysis.get("experience", []):
                    if isinstance(exp, dict) and exp.get("technologies"):
                        for t in exp["technologies"]:
                            _add_evidence(t, "resume", f"Applied in work experience: {exp.get('role', 'Role')}", weight=2)

        # 3. GitHub Data
        if github_data:
            # Languages in GitHub profile
            stats = github_data.get("statistics", {})
            languages = stats.get("languages", {}) if isinstance(stats, dict) else {}
            if isinstance(languages, dict):
                for lang, bytes_count in languages.items():
                    _add_evidence(lang, "github", f"Verified {bytes_count} bytes in public GitHub repositories.", weight=3)

            # GitHub AI analysis top languages/topics
            gh_analysis = github_data.get("analysis", {})
            if isinstance(gh_analysis, dict):
                for lang in gh_analysis.get("top_languages", []):
                    _add_evidence(lang, "github", f"Demonstrated in active GitHub repositories.", weight=2)

        # 4. LeetCode Data
        if leetcode_data:
            # Topic statistics
            topics = leetcode_data.get("topic_statistics", [])
            if isinstance(topics, list):
                for top in topics:
                    if isinstance(top, dict) and top.get("topic_name"):
                        solved = top.get("problems_solved", 0)
                        if solved > 0:
                            _add_evidence(
                                top["topic_name"],
                                "leetcode",
                                f"Solved {solved} problems on LeetCode.",
                                weight=min(5, max(1, solved // 5))
                            )
            
            # DSA General
            stats = leetcode_data.get("statistics", {})
            if isinstance(stats, dict) and stats.get("total_solved", 0) > 0:
                _add_evidence(
                    "Data Structures & Algorithms",
                    "leetcode",
                    f"Solved {stats.get('total_solved')} total LeetCode problems (Rating: {leetcode_data.get('contest', {}).get('rating', 'N/A')}).",
                    weight=4
                )

        # 5. Projects Data
        if projects_list:
            for proj in projects_list:
                if not isinstance(proj, dict):
                    continue
                p_title = proj.get("title", "Portfolio Project")
                p_techs = proj.get("technologies", [])
                p_score = proj.get("score", 80)
                for t in p_techs:
                    _add_evidence(t, "projects", f"Implemented in '{p_title}' (Audit Score: {p_score}/100).", weight=3)
                
                # Architecture tags
                for arch in proj.get("architectureTags", []):
                    _add_evidence(arch, "projects", f"Architected in '{p_title}'.", weight=2)

        # Calculate assessed level and evidence level for each inventory item
        for key, item in inventory.items():
            sources = item["evidence_sources"]
            weight = item["evidence_weight"]
            evidence_count = len(item["evidence_items"])

            # Evidence level
            if len(sources) >= 2 or weight >= 5:
                item["evidence_level"] = "strong_evidence"
            elif "projects" in sources or "github" in sources or "leetcode" in sources:
                item["evidence_level"] = "demonstrated"
            elif "resume" in sources or "profile" in sources:
                item["evidence_level"] = "mentioned"
            else:
                item["evidence_level"] = "none"

            # Assessed Level calculation (0-4)
            if weight >= 6 or (len(sources) >= 3):
                item["current_level_num"] = 3  # Advanced
                item["current_level"] = "Advanced"
            elif weight >= 3 or ("projects" in sources and "resume" in sources):
                item["current_level_num"] = 2  # Intermediate
                item["current_level"] = "Intermediate"
            elif weight >= 1:
                item["current_level_num"] = 1  # Beginner
                item["current_level"] = "Beginner"
            else:
                item["current_level_num"] = 0  # Untested
                item["current_level"] = "Untested"

        return inventory

    def analyze(
        self,
        target_role: str,
        profile_data: Optional[Dict[str, Any]] = None,
        resume_data: Optional[Dict[str, Any]] = None,
        github_data: Optional[Dict[str, Any]] = None,
        leetcode_data: Optional[Dict[str, Any]] = None,
        projects_list: Optional[List[Dict[str, Any]]] = None,
        role_requirements: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Execute deterministic Skill Gap analysis comparing candidate inventory against target role requirements.
        """
        canonical_role = get_canonical_role(target_role)
        role_reqs = role_requirements or self.get_role_requirements(canonical_role)

        # --- GUARD: Remove any requirement whose skill name matches the target role ---
        role_reqs = [
            req for req in role_reqs
            if not _is_role_name(req.get("skill", ""), canonical_role)
        ]

        inventory = self.build_skill_inventory(
            profile_data=profile_data,
            resume_data=resume_data,
            github_data=github_data,
            leetcode_data=leetcode_data,
            projects_list=projects_list
        )

        evaluated_skills: List[Dict[str, Any]] = []
        priority_gaps: List[Dict[str, Any]] = []
        strengths: List[str] = []
        covered_required_count = 0
        total_required_skills = len(role_reqs)
        aligned_count = 0
        developing_count = 0
        weak_count = 0
        missing_count = 0

        # Evaluate each required role skill
        for req in role_reqs:
            req_skill = req["skill"]
            can_skill, category = normalize_skill_name(req_skill)
            req_level = req.get("required_level", "Intermediate")
            req_level_num = LEVEL_NUMERIC.get(req_level.lower(), 2)
            importance = req.get("importance", "medium")

            key = can_skill.lower()
            inv_item = inventory.get(key)

            if inv_item:
                curr_level = inv_item["current_level"]
                curr_level_num = inv_item["current_level_num"]
                evidence_level = inv_item["evidence_level"]
                evidence_list = [e["detail"] for e in inv_item["evidence_items"]][:3]
            else:
                curr_level = "Untested"
                curr_level_num = 0
                evidence_level = "none"
                evidence_list = [f"No verified evidence of {can_skill} detected in analyzed student data."]

            diff = req_level_num - curr_level_num
            # Always use canonical role for display — prevents raw typos in output
            target_role_display = canonical_role

            # Determine gap type, severity, priority, reason, recommended action using SINGLE SOURCE OF TRUTH
            if curr_level_num >= req_level_num:
                gap_type = "aligned"
                gap_severity = "None"
                priority = "Low"
                aligned_count += 1
                reason = f"Current {curr_level} proficiency meets or exceeds the required {req_level} level for {target_role_display}."
                action = f"Maintain and deepen {can_skill} proficiency through advanced projects and production use."
                action_label = "Proficiency Aligned"
                action_route = "/dashboard"
            elif curr_level_num == 0:
                gap_type = "missing"
                gap_severity = "Critical" if importance == "critical" else "High"
                priority = "High" if importance in ["critical", "high"] else "Medium"
                missing_count += 1
                reason = f"No verified evidence of {can_skill} was found, so current proficiency is Untested for {target_role_display}."
                action = f"Build practical {can_skill} projects to establish verified {req_level} proficiency."
                action_label = "Add to Roadmap"
                action_route = "/roadmap"
            else:
                gap_type = "developing"
                gap_severity = "High" if diff >= 2 else "Medium"
                priority = "High" if (importance in ["critical", "high"] and diff >= 2) else ("Medium" if importance in ["critical", "high"] else "Low")
                developing_count += 1
                reason = f"Current {curr_level} proficiency is below the required {req_level} level for {target_role_display}."
                action = f"Advance {can_skill} proficiency from {curr_level} to {req_level} through production-style projects and practice."
                action_label = "Add to Roadmap"
                action_route = "/roadmap"

            eval_item = {
                "skill": can_skill,
                "category": category,
                "required": True,
                "importance": importance,
                "required_level": req_level,
                "required_level_num": req_level_num,
                "current_level": curr_level,
                "current_level_num": curr_level_num,
                "gap_type": gap_type,
                "gap_severity": gap_severity,
                "priority": priority,
                "evidence_level": evidence_level,
                "evidence": evidence_list,
                "reason": reason,
                "recommended_action": action,
                "action_label": action_label,
                "action_route": action_route
            }
            evaluated_skills.append(eval_item)

            # Add to priority gaps list if there is a gap
            if gap_type != "aligned":
                p_gap = {
                    "id": f"gap-{len(priority_gaps) + 1}",
                    "skill": can_skill,
                    "category": category,
                    "gap_type": gap_type,
                    "priority": priority,
                    "importance": importance,
                    "current_level": curr_level,
                    "current_level_text": f"{curr_level} (Level {curr_level_num}/4)",
                    "required_level": req_level,
                    "required_level_text": f"{req_level} (Level {req_level_num}/4)",
                    "reason": reason,
                    "suggested_action": action,
                    "action_label": action_label,
                    "action_route": action_route
                }
                priority_gaps.append(p_gap)

        # Sort priority gaps: Critical/High first, then Medium, then Low
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        priority_gaps.sort(key=lambda g: priority_order.get(g["priority"], 2))

        # Overall coverage calculation (weighted by importance and level requirements)
        total_weight = sum(req.get("weight", 0.8) * req.get("required_level_num", 2) for req in role_reqs)
        achieved_weight = sum(
            req.get("weight", 0.8) * min(req.get("required_level_num", 2), s["current_level_num"])
            for req, s in zip(role_reqs, evaluated_skills)
        )
        overall_coverage = round((achieved_weight / max(0.1, total_weight)) * 100) if total_weight > 0 else 0
        overall_coverage = min(100, max(0, overall_coverage))

        # Category coverage breakdown (dynamic from actual role categories)
        category_groups: Dict[str, Dict[str, float]] = {}
        for req, item in zip(role_reqs, evaluated_skills):
            cat = item["category"]
            w = req.get("weight", 0.8)
            req_l = req.get("required_level_num", 2)
            cur_l = item["current_level_num"]
            if cat not in category_groups:
                category_groups[cat] = {"total": 0.0, "achieved": 0.0}
            category_groups[cat]["total"] += w * req_l
            category_groups[cat]["achieved"] += w * min(req_l, cur_l)

        color_palette = ["#4edea3", "#8083ff", "#ddb7ff", "#ffb4ab", "#fcd34d", "#60a5fa", "#f472b6", "#38bdf8"]
        category_coverage = []
        for idx, (c_name, c_data) in enumerate(category_groups.items()):
            cov = round((c_data["achieved"] / max(0.1, c_data["total"])) * 100) if c_data["total"] > 0 else 0
            category_coverage.append({
                "category": c_name,
                "coverage": min(100, max(0, cov)),
                "color": color_palette[idx % len(color_palette)]
            })

        # Strengths dynamically derived from actual aligned or highest-scoring skills
        strengths = [
            f"Demonstrated {s['current_level']} competency in {s['skill']} ({s['category']})."
            for s in evaluated_skills if s["gap_type"] == "aligned"
        ][:4]
        if not strengths:
            top_assessed = sorted([s for s in evaluated_skills if s["current_level_num"] > 0], key=lambda x: x["current_level_num"], reverse=True)
            if top_assessed:
                strengths = [f"Demonstrated {s['current_level']} competency in {s['skill']} ({s['category']})." for s in top_assessed[:3]]
            else:
                strengths = [f"Foundational skills required for {target_role_display} are in early development."]

        # 2x2 Impact vs Effort Matrix
        quick_wins = []
        major_projects = []
        fill_ins = []
        hard_long_term = []

        for item in evaluated_skills:
            sk_name = item["skill"]
            sk_cat = item["category"]
            sk_imp = item["importance"]
            sk_gap = item["gap_type"]

            if sk_imp in ["critical", "high"]:
                if sk_gap in ["missing", "weak"]:
                    major_projects.append({"skill": sk_name, "category": sk_cat})
                elif sk_gap == "developing":
                    quick_wins.append({"skill": sk_name, "category": sk_cat})
            else:
                if sk_gap in ["missing", "weak"]:
                    hard_long_term.append({"skill": sk_name, "category": sk_cat})
                elif sk_gap == "developing":
                    fill_ins.append({"skill": sk_name, "category": sk_cat})

        # Ensure matrix has default examples if empty
        if not quick_wins:
            quick_wins = [{"skill": "STAR Resume Bullets Quantification", "category": "Resume"}]
        if not major_projects and priority_gaps:
            major_projects = [{"skill": priority_gaps[0]["skill"], "category": priority_gaps[0]["category"]}]

        # Dynamic Recommendations based on top priority gaps and target role
        recommendations = []
        if priority_gaps:
            top_gap = priority_gaps[0]
            recommendations.append({
                "title": f"Bridge Priority Gap: {top_gap['skill']} for {target_role_display}",
                "description": f"Focus on advancing {top_gap['skill']} from {top_gap['current_level']} to {top_gap['required_level']} to align with {target_role_display} standards.",
                "action_label": "View 90-Day Roadmap",
                "action_route": "/roadmap"
            })
        if len(priority_gaps) > 1:
            second_gap = priority_gaps[1]
            recommendations.append({
                "title": f"Strengthen {second_gap['category']} Proficiency",
                "description": f"Target practical milestones in {second_gap['skill']} ({second_gap['required_level']} level required).",
                "action_label": "View Today's Tasks",
                "action_route": "/tasks"
            })
        else:
            recommendations.append({
                "title": f"Maintain Role Alignment for {target_role_display}",
                "description": "Engage in advanced system design and production-style projects.",
                "action_label": "View Today's Tasks",
                "action_route": "/tasks"
            })

        # Evidence-grounded confidence index
        active_sources = set()
        for item in inventory.values():
            active_sources.update(item["evidence_sources"])

        source_weight = 0
        if "profile" in active_sources: source_weight += 7
        if "resume" in active_sources: source_weight += 10
        if "github" in active_sources: source_weight += 11
        if "leetcode" in active_sources: source_weight += 11
        if "projects" in active_sources: source_weight += 11

        volume_bonus = min(8, len(inventory) // 2)
        confidence_val = min(98.0, max(50.0, 50.0 + source_weight + volume_bonus))
        confidence_index = confidence_val  # float, e.g. 98.0

        return {
            # Always return the canonical role — not the raw typo-riddled input
            "target_role": canonical_role,
            "overall_coverage": overall_coverage,
            "confidence_index": confidence_index,
            "total_audited": len(inventory) + total_required_skills,
            "summary": {
                "total_required_skills": total_required_skills,
                "skills_aligned": aligned_count,
                "skills_developing": developing_count,
                "skills_weak": weak_count,
                "skills_missing": missing_count,
            },
            "category_coverage": category_coverage,
            "skills": evaluated_skills,
            "priority_gaps": priority_gaps,
            "strengths": strengths[:4],
            "recommendations": recommendations,
            "matrix2x2": {
                "quick_wins": quick_wins[:4],
                "major_projects": major_projects[:4],
                "fill_ins": fill_ins[:4],
                "hard_long_term": hard_long_term[:4],
            },
            "data_quality": {
                "profile": bool(profile_data and (profile_data.get("technical_skills") or profile_data.get("categories"))),
                "resume": bool(resume_data and (resume_data.get("analysis", {}).get("skills_extracted") or resume_data.get("skills_extracted"))),
                "github": bool(github_data and (github_data.get("statistics", {}).get("languages") or github_data.get("analysis", {}).get("top_languages"))),
                "leetcode": bool(leetcode_data and (leetcode_data.get("topic_statistics") or leetcode_data.get("statistics", {}).get("total_solved", 0) > 0)),
                "projects": bool(projects_list and len(projects_list) > 0),
            }
        }


