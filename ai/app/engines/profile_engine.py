import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

from app.schemas.resume import LLMResumeExtraction, ResumeAnalysis, ScoreDetail
from app.schemas.github import GitHubAnalysis
from app.schemas.leetcode import LeetCodeAnalysis
from app.schemas.student import StudentProfile
from app.schemas.skills import (
    CategorySkillProfile,
    CommunicationProfileCategory,
    GitHubProfileCategory,
    NormalizedSkill,
    ProfileBuildRequest,
    ProfileCategories,
    ProfileConflict,
    ProfileSourceStatus,
    ProjectsProfileCategory,
    ResumeProfileCategory,
    SkillLevel,
    StudentIntelligenceProfile,
)
from app.utils.tech_taxonomy import TECH_TAXONOMY, normalize_skill_name


class ProfileEngine:
    """Engine for deterministic calculation of resume ATS and section scores."""

    @staticmethod
    def calculate_projects_score(extraction: LLMResumeExtraction) -> ScoreDetail:
        if not extraction.projects:
            return ScoreDetail(score=0, reason="No projects found on the resume.")
            
        total_projects = len(extraction.projects)
        metrics_projects = sum(1 for p in extraction.projects if p.has_metrics)
        tech_projects = sum(1 for p in extraction.projects if len(p.technologies) > 0)
        
        base_score = min(total_projects * 20, 60)
        metrics_bonus = min(metrics_projects * 15, 30)
        tech_bonus = min(tech_projects * 5, 10)
        
        final_score = base_score + metrics_bonus + tech_bonus
        
        if metrics_projects == 0:
            reason = f"Found {total_projects} projects, but none highlight quantifiable metrics. Add metrics to improve this score."
        elif metrics_projects < total_projects:
            reason = f"Found {total_projects} projects. {metrics_projects} have metrics, but others are lacking specific impact data."
        else:
            reason = f"Strong project section with {total_projects} projects, all showing quantifiable metrics and tech stacks."
            
        return ScoreDetail(score=final_score, reason=reason)

    @staticmethod
    def calculate_skills_score(extraction: LLMResumeExtraction) -> ScoreDetail:
        langs = len(extraction.skills.languages)
        fw = len(extraction.skills.frameworks)
        tools = len(extraction.skills.tools)
        
        total_skills = langs + fw + tools
        if total_skills == 0:
            return ScoreDetail(score=0, reason="No recognized skills found in the resume.")
            
        score = 0
        if langs > 0: score += 35
        if fw > 0: score += 35
        if tools > 0: score += 30
        
        if score == 100:
            reason = f"Well-rounded skills section covering {langs} languages, {fw} frameworks, and {tools} tools."
        else:
            missing = []
            if langs == 0: missing.append("programming languages")
            if fw == 0: missing.append("frameworks")
            if tools == 0: missing.append("tools")
            reason = f"Found some skills, but lacking explicitly categorized {', '.join(missing)}."
            
        return ScoreDetail(score=score, reason=reason)

    @staticmethod
    def calculate_experience_score(extraction: LLMResumeExtraction) -> ScoreDetail:
        if not extraction.experience:
            return ScoreDetail(score=0, reason="No work experience found on the resume.")
            
        score = min(len(extraction.experience) * 40, 100)
        reason = f"Found {len(extraction.experience)} role(s) listed under experience."
        return ScoreDetail(score=score, reason=reason)

    @staticmethod
    def calculate_impact_score(extraction: LLMResumeExtraction) -> ScoreDetail:
        total_bullets = sum(len(exp.bullets) for exp in extraction.experience) + \
                        sum(len(proj.bullets) for proj in extraction.projects)
                        
        if total_bullets == 0:
            return ScoreDetail(score=0, reason="No description bullets found to evaluate impact.")
            
        weak_count = len(extraction.weak_bullets)
        strong_ratio = max(0, (total_bullets - weak_count) / total_bullets)
        score = int(strong_ratio * 100)
        
        if weak_count == 0:
            reason = "All bullet points are strong, clear, and action-oriented."
        elif weak_count > total_bullets:
            reason = "Many bullet points lack metrics or are overly generic."
        else:
            reason = f"{weak_count} out of {total_bullets} bullet points are flagged as weak (e.g., missing metrics, generic phrasing)."
            
        return ScoreDetail(score=score, reason=reason)
        
    @staticmethod
    def calculate_formatting_score(extraction: LLMResumeExtraction) -> ScoreDetail:
        score = 100
        issues = []
        
        if extraction.missing_sections:
            score -= (len(extraction.missing_sections) * 15)
            issues.append(f"Missing sections: {', '.join(extraction.missing_sections)}")
            
        if extraction.repeated_words or extraction.generic_phrases:
            score -= 10
            issues.append("Contains cliches or highly repetitive phrasing")
            
        score = max(0, score)
        
        if score == 100:
            reason = "All standard sections present and phrasing is varied."
        else:
            reason = "; ".join(issues) + "."
            
        return ScoreDetail(score=score, reason=reason)

    @classmethod
    def calculate_overall_ats_score(cls, extraction: LLMResumeExtraction) -> int:
        p_score = cls.calculate_projects_score(extraction).score
        s_score = cls.calculate_skills_score(extraction).score
        e_score = cls.calculate_experience_score(extraction).score
        i_score = cls.calculate_impact_score(extraction).score
        f_score = cls.calculate_formatting_score(extraction).score
        
        if e_score == 0:
            weighted_score = (p_score * 0.40) + (s_score * 0.20) + (i_score * 0.20) + (f_score * 0.20)
        else:
            weighted_score = (e_score * 0.30) + (p_score * 0.20) + (s_score * 0.20) + (i_score * 0.20) + (f_score * 0.10)
            
        return int(weighted_score)


class StudentProfileIntelligenceEngine:
    """
    Student Profile Intelligence Engine.
    Combines ResumeAnalysis, GitHubAnalysis, LeetCodeAnalysis, and StudentProfile
    into a unified, evidence-grounded StudentIntelligenceProfile across 14 categories.
    """

    def build_profile(self, request: ProfileBuildRequest) -> StudentIntelligenceProfile:
        """Main entry point to build the normalized intelligence profile."""
        student = request.student_profile
        resume = request.resume_analysis
        github = request.github_analysis
        leetcode = request.leetcode_analysis

        # 1. Track provided data sources
        has_student = student is not None
        has_resume = resume is not None
        has_github = github is not None
        has_leetcode = leetcode is not None

        source_status = ProfileSourceStatus(
            student_profile=has_student,
            resume_analysis=has_resume,
            github_analysis=has_github,
            leetcode_analysis=has_leetcode,
            total_sources_provided=sum([has_student, has_resume, has_github, has_leetcode]),
        )

        # 2. Extract and accumulate raw skill signals from all sources
        skills_raw_map: Dict[str, Dict[str, Any]] = {}
        self._ingest_resume_skills(resume, skills_raw_map)
        self._ingest_github_skills(github, skills_raw_map)
        self._ingest_leetcode_skills(leetcode, skills_raw_map)
        self._ingest_student_skills(student, skills_raw_map)

        # 3. Detect conflicts across sources
        conflicts = self._detect_conflicts(student, resume, github, leetcode, skills_raw_map)

        # 4. Finalize normalized skills with evidence, confidence, and levels
        normalized_skills = self._normalize_skills(skills_raw_map, conflicts)

        # 5. Build the 14 category profiles
        categories = self._build_14_categories(
            normalized_skills=normalized_skills,
            student=student,
            resume=resume,
            github=github,
            leetcode=leetcode,
        )

        # 6. Extract executive summary, strengths, growth areas, and overall readiness
        strengths, growth_areas = self._derive_strengths_and_gaps(
            normalized_skills, categories, conflicts, source_status
        )
        readiness = self._calculate_overall_readiness(categories, normalized_skills, source_status)
        summary = self._generate_executive_summary(
            student=student,
            source_status=source_status,
            categories=categories,
            skills=normalized_skills,
            conflicts=conflicts,
            readiness=readiness,
        )

        student_metadata = None
        if student:
            student_metadata = {
                "name": student.name,
                "email": student.email,
                "degree": student.degree,
                "branch": student.branch,
                "institution": student.institution,
                "graduation_year": student.graduation_year,
                "cgpa": student.cgpa,
                "experience_level": student.experience_level,
                "target_companies": student.target_companies,
            }

        return StudentIntelligenceProfile(
            student_metadata=student_metadata,
            target_role=student.target_role if student else None,
            source_status=source_status,
            skills=normalized_skills,
            categories=categories,
            conflicts=conflicts,
            strengths=strengths,
            growth_areas=growth_areas,
            overall_readiness_level=readiness,
            executive_summary=summary,
        )

    # -----------------------------------------------------------------------
    # Ingestion helpers
    # -----------------------------------------------------------------------

    def _register_skill_signal(
        self,
        skills_raw_map: Dict[str, Dict[str, Any]],
        raw_name: str,
        source: str,
        evidence: str,
        suggested_level: str = "Intermediate",
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        canonical_name, category = normalize_skill_name(raw_name)
        if not canonical_name:
            return

        if canonical_name not in skills_raw_map:
            skills_raw_map[canonical_name] = {
                "skill": canonical_name,
                "category": category,
                "sources": set(),
                "evidence": [],
                "levels": [],
                "meta": {},
            }

        entry = skills_raw_map[canonical_name]
        entry["sources"].add(source)
        if evidence not in entry["evidence"]:
            entry["evidence"].append(evidence)
        entry["levels"].append(suggested_level)
        if meta:
            entry["meta"][source] = meta

    def _ingest_resume_skills(
        self, resume: Optional[ResumeAnalysis], skills_raw_map: Dict[str, Dict[str, Any]]
    ) -> None:
        if not resume:
            return

        for lang in resume.extracted_skills.languages:
            self._register_skill_signal(
                skills_raw_map,
                raw_name=lang,
                source="resume",
                evidence="Detected in resume programming languages section",
                suggested_level="Intermediate",
            )

        for fw in resume.extracted_skills.frameworks:
            self._register_skill_signal(
                skills_raw_map,
                raw_name=fw,
                source="resume",
                evidence="Detected in resume frameworks/libraries section",
                suggested_level="Intermediate",
            )

        for tool in resume.extracted_skills.tools:
            self._register_skill_signal(
                skills_raw_map,
                raw_name=tool,
                source="resume",
                evidence="Detected in resume tools/platforms section",
                suggested_level="Intermediate",
            )

        for other in resume.extracted_skills.other:
            self._register_skill_signal(
                skills_raw_map,
                raw_name=other,
                source="resume",
                evidence="Extracted from resume background details",
                suggested_level="Beginner",
            )

        # Projects on resume
        for proj in resume.projects:
            for tech in proj.technologies:
                metrics_note = " with quantifiable metrics" if proj.has_metrics else ""
                self._register_skill_signal(
                    skills_raw_map,
                    raw_name=tech,
                    source="resume",
                    evidence=f"Applied in resume project '{proj.name}'{metrics_note}",
                    suggested_level="Intermediate",
                )

    def _ingest_github_skills(
        self, github: Optional[GitHubAnalysis], skills_raw_map: Dict[str, Dict[str, Any]]
    ) -> None:
        if not github:
            return

        # Languages with repository counts
        for lang, count in github.languages.language_repo_counts.items():
            level = "Advanced" if count >= 3 or lang == github.languages.primary_language else ("Intermediate" if count >= 2 else "Beginner")
            self._register_skill_signal(
                skills_raw_map,
                raw_name=lang,
                source="github",
                evidence=f"Used in {count} analyzed GitHub repository{'ies' if count > 1 else ''}",
                suggested_level=level,
                meta={"repo_count": count, "is_primary": (lang == github.languages.primary_language)},
            )

        # Technical categories detected from repo topics/names/content
        for tech_cat in github.technical_categories:
            if tech_cat.detected:
                ev_str = f"Verified across GitHub repositories ({', '.join(tech_cat.evidence)})"
                self._register_skill_signal(
                    skills_raw_map,
                    raw_name=tech_cat.name,
                    source="github",
                    evidence=ev_str,
                    suggested_level="Intermediate",
                )

    def _ingest_leetcode_skills(
        self, leetcode: Optional[LeetCodeAnalysis], skills_raw_map: Dict[str, Dict[str, Any]]
    ) -> None:
        if not leetcode:
            return

        for topic in leetcode.topic_analysis:
            if topic.solved_count > 0:
                level_map = {
                    "strong": "Advanced",
                    "developing": "Intermediate",
                    "beginner": "Beginner",
                    "untested": "Untested",
                }
                level = level_map.get(topic.performance_level, "Intermediate")
                ev = f"Solved {topic.solved_count} LeetCode {topic.topic} problem(s) (performance: {topic.performance_level})"
                self._register_skill_signal(
                    skills_raw_map,
                    raw_name=topic.topic,
                    source="leetcode",
                    evidence=ev,
                    suggested_level=level,
                    meta={"solved_count": topic.solved_count, "performance_level": topic.performance_level},
                )

        # Add overall DSA if user solved problems
        if leetcode.problem_statistics.total_solved > 0:
            stats = leetcode.problem_statistics
            level = "Advanced" if stats.total_solved >= 100 or stats.hard_solved >= 5 else ("Intermediate" if stats.total_solved >= 25 else "Beginner")
            self._register_skill_signal(
                skills_raw_map,
                raw_name="Data Structures & Algorithms",
                source="leetcode",
                evidence=f"Solved {stats.total_solved} total problems on LeetCode ({stats.easy_solved} Easy, {stats.medium_solved} Medium, {stats.hard_solved} Hard)",
                suggested_level=level,
                meta={"total_solved": stats.total_solved},
            )

    def _ingest_student_skills(
        self, student: Optional[StudentProfile], skills_raw_map: Dict[str, Dict[str, Any]]
    ) -> None:
        if not student:
            return

        for s in student.self_reported_skills:
            self._register_skill_signal(
                skills_raw_map,
                raw_name=s.name,
                source="student_profile",
                evidence=f"Self-reported by student as '{s.level}'",
                suggested_level=s.level,
                meta={"self_reported_level": s.level},
            )

    # -----------------------------------------------------------------------
    # Conflict detection
    # -----------------------------------------------------------------------

    def _detect_conflicts(
        self,
        student: Optional[StudentProfile],
        resume: Optional[ResumeAnalysis],
        github: Optional[GitHubAnalysis],
        leetcode: Optional[LeetCodeAnalysis],
        skills_raw_map: Dict[str, Dict[str, Any]],
    ) -> List[ProfileConflict]:
        conflicts: List[ProfileConflict] = []

        # 1. Check self-reported skill level vs verified GitHub or LeetCode evidence
        if student and student.self_reported_skills:
            for s in student.self_reported_skills:
                canonical, category = normalize_skill_name(s.name)
                claimed = s.level.strip().capitalize()
                
                # If claimed Advanced/Expert
                if claimed in ["Advanced", "Expert"]:
                    # Check GitHub conflict
                    if github and github.activity.total_public_repos > 0:
                        repo_count = github.languages.language_repo_counts.get(canonical, 0)
                        is_tech_cat = any(
                            t.detected and normalize_skill_name(t.name)[0] == canonical
                            for t in github.technical_categories
                        )
                        # Claimed Advanced in a programming language, but 0 repos in GitHub
                        if category == "programming" and repo_count == 0:
                            conflicts.append(
                                ProfileConflict(
                                    id=f"conflict_self_github_{canonical.lower()}",
                                    category=category,
                                    skill_or_topic=canonical,
                                    conflict=f"Student claimed '{claimed}' level in {canonical}, but found 0 public GitHub repositories using {canonical}.",
                                    sources={
                                        "student_profile": f"Claimed '{claimed}' level",
                                        "github": "0 public repositories found with this language",
                                    },
                                    resolution_rule="Penalized confidence score; normalized level to Intermediate pending repository evidence.",
                                    severity="medium",
                                )
                            )
                        # Claimed Advanced in a framework/tool, but 0 detected in GitHub
                        elif category in ["backend", "frontend", "devops", "machine_learning"] and not is_tech_cat and repo_count == 0:
                            # Check if resume at least mentions it
                            has_resume_proj = False
                            if resume:
                                has_resume_proj = any(
                                    canonical.lower() in [normalize_skill_name(t)[0].lower() for t in p.technologies]
                                    for p in resume.projects
                                )
                            if not has_resume_proj:
                                conflicts.append(
                                    ProfileConflict(
                                        id=f"conflict_self_codebase_{canonical.lower()}",
                                        category=category,
                                        skill_or_topic=canonical,
                                        conflict=f"Student self-reported '{claimed}' proficiency in {canonical}, but codebase analysis (GitHub/Resume projects) shows no project implementation.",
                                        sources={
                                            "student_profile": f"Claimed '{claimed}'",
                                            "github": "Not detected in repositories",
                                            "resume": "Not evidenced in projects" if resume else "Resume not provided",
                                        },
                                        resolution_rule="Discounted unverified self-claim to Beginner/Intermediate with reduced confidence.",
                                        severity="medium",
                                    )
                                )

                    # Check LeetCode conflict for DSA topics
                    if leetcode and category == "dsa":
                        matching_topic = next(
                            (t for t in leetcode.topic_analysis if normalize_skill_name(t.topic)[0] == canonical),
                            None,
                        )
                        if matching_topic and matching_topic.solved_count < 3:
                            conflicts.append(
                                ProfileConflict(
                                    id=f"conflict_self_leetcode_{canonical.lower()}",
                                    category="dsa",
                                    skill_or_topic=canonical,
                                    conflict=f"Student claimed '{claimed}' in DSA topic '{canonical}', but LeetCode shows only {matching_topic.solved_count} solved ({matching_topic.performance_level}).",
                                    sources={
                                        "student_profile": f"Claimed '{claimed}'",
                                        "leetcode": f"Solved {matching_topic.solved_count} ({matching_topic.performance_level})",
                                    },
                                    resolution_rule="Prioritized verified LeetCode problem submission statistics over self-reported claim.",
                                    severity="high",
                                )
                            )

        # 2. Check Resume vs GitHub Language Discrepancy
        if resume and github and github.activity.total_public_repos >= 2:
            resume_langs = [normalize_skill_name(l)[0] for l in resume.extracted_skills.languages]
            primary_github = github.languages.primary_language
            
            if resume_langs and primary_github:
                primary_github_canonical = normalize_skill_name(primary_github)[0]
                # If resume highlights a language not in GitHub at all, or vice-versa
                if primary_github_canonical not in resume_langs and github.languages.language_repo_counts.get(primary_github, 0) >= 3:
                    conflicts.append(
                        ProfileConflict(
                            id="conflict_resume_github_primary_language",
                            category="programming",
                            skill_or_topic=f"{primary_github_canonical} vs {', '.join(resume_langs[:2])}",
                            conflict=f"GitHub shows '{primary_github_canonical}' as primary language across {github.languages.language_repo_counts.get(primary_github, 0)} repos, but it is omitted from the resume's core languages.",
                            sources={
                                "github": f"Primary language: {primary_github_canonical}",
                                "resume": f"Core languages: {', '.join(resume_langs)}",
                            },
                            resolution_rule="Aggregated both languages with respective source tags; flagged resume keyword update opportunity.",
                            severity="low",
                        )
                    )

        # 3. Check Resume vs LeetCode DSA claims
        if resume and leetcode:
            resume_text_mentions_dsa = any(
                "competitive" in str(a).lower() or "leetcode" in str(a).lower() or "dsa" in str(a).lower()
                for a in (resume.achievements + [p.name for p in resume.projects])
            )
            if resume_text_mentions_dsa and leetcode.problem_statistics.total_solved < 10:
                conflicts.append(
                    ProfileConflict(
                        id="conflict_resume_leetcode_dsa",
                        category="dsa",
                        skill_or_topic="DSA / Competitive Programming",
                        conflict="Resume mentions competitive programming/DSA achievements, but connected LeetCode profile shows fewer than 10 problems solved.",
                        sources={
                            "resume": "Mentions competitive programming/DSA in profile",
                            "leetcode": f"Total solved: {leetcode.problem_statistics.total_solved}",
                        },
                        resolution_rule="Assessed current DSA level using verified submission statistics.",
                        severity="medium",
                    )
                )

        return conflicts

    # -----------------------------------------------------------------------
    # Skill normalization & confidence scoring
    # -----------------------------------------------------------------------

    def _normalize_skills(
        self,
        skills_raw_map: Dict[str, Dict[str, Any]],
        conflicts: List[ProfileConflict],
    ) -> List[NormalizedSkill]:
        conflict_skill_names = {c.skill_or_topic.lower() for c in conflicts}
        normalized_list: List[NormalizedSkill] = []

        for skill_name, data in skills_raw_map.items():
            sources = sorted(list(data["sources"]))
            evidence = data["evidence"]
            source_count = len(sources)

            # Confidence formula:
            # Multi-source confirmation scales confidence cleanly
            if source_count == 1:
                if "student_profile" in sources:
                    base_confidence = 0.50
                elif "resume" in sources:
                    base_confidence = 0.70
                elif "github" in sources:
                    base_confidence = 0.75
                elif "leetcode" in sources:
                    base_confidence = 0.85
                else:
                    base_confidence = 0.65
            elif source_count == 2:
                base_confidence = 0.88
            elif source_count == 3:
                base_confidence = 0.94
            else:
                base_confidence = 0.98

            # Penalize confidence if there is a conflict on this skill
            has_conflict = skill_name.lower() in conflict_skill_names
            if has_conflict:
                base_confidence = max(0.40, round(base_confidence - 0.25, 2))

            # Determine assessed level
            levels = data["levels"]
            if "Advanced" in levels and (source_count >= 2 or "github" in sources or "leetcode" in sources):
                current_level = "Advanced" if not has_conflict else "Intermediate"
            elif "Advanced" in levels and source_count == 1 and "student_profile" in sources:
                current_level = "Intermediate" if not has_conflict else "Beginner"
            elif "Intermediate" in levels:
                current_level = "Intermediate"
            elif "Beginner" in levels:
                current_level = "Beginner"
            elif "Untested" in levels:
                current_level = "Untested"
            else:
                current_level = "Intermediate"

            normalized_list.append(
                NormalizedSkill(
                    skill=skill_name,
                    current_level=current_level,
                    evidence=evidence,
                    confidence=round(base_confidence, 2),
                    source=sources,
                )
            )

        # Sort alphabetically by skill name
        normalized_list.sort(key=lambda s: s.skill)
        return normalized_list

    # -----------------------------------------------------------------------
    # 14 Category construction
    # -----------------------------------------------------------------------

    def _build_14_categories(
        self,
        normalized_skills: List[NormalizedSkill],
        student: Optional[StudentProfile],
        resume: Optional[ResumeAnalysis],
        github: Optional[GitHubAnalysis],
        leetcode: Optional[LeetCodeAnalysis],
    ) -> ProfileCategories:
        # Categorize technical skills
        skills_by_category: Dict[str, List[NormalizedSkill]] = {
            "programming": [],
            "dsa": [],
            "backend": [],
            "frontend": [],
            "machine_learning": [],
            "data_science": [],
            "databases": [],
            "devops": [],
            "cloud": [],
            "cs_fundamentals": [],
        }

        for s in normalized_skills:
            _, cat = normalize_skill_name(s.skill)
            if cat in skills_by_category:
                skills_by_category[cat].append(s)

        # 1-10: Technical Categories
        prog_cat = self._build_tech_category("Programming", skills_by_category["programming"], "programming")
        dsa_cat = self._build_dsa_category(skills_by_category["dsa"], leetcode)
        backend_cat = self._build_tech_category("Backend", skills_by_category["backend"], "backend")
        frontend_cat = self._build_tech_category("Frontend", skills_by_category["frontend"], "frontend")
        ml_cat = self._build_tech_category("Machine Learning", skills_by_category["machine_learning"], "machine_learning")
        ds_cat = self._build_tech_category("Data Science", skills_by_category["data_science"], "data_science")
        db_cat = self._build_tech_category("Databases", skills_by_category["databases"], "databases")
        devops_cat = self._build_tech_category("DevOps", skills_by_category["devops"], "devops")
        cloud_cat = self._build_tech_category("Cloud", skills_by_category["cloud"], "cloud")
        cs_fund_cat = self._build_tech_category("CS Fundamentals", skills_by_category["cs_fundamentals"], "cs_fundamentals")

        # 11: Projects Category
        projects_cat = self._build_projects_category(resume, github)

        # 12: Resume Category
        resume_cat = self._build_resume_category(resume)

        # 13: GitHub Category
        github_cat = self._build_github_category(github)

        # 14: Communication Category
        comm_cat = self._build_communication_category(resume, github)

        return ProfileCategories(
            programming=prog_cat,
            dsa=dsa_cat,
            backend=backend_cat,
            frontend=frontend_cat,
            machine_learning=ml_cat,
            data_science=ds_cat,
            databases=db_cat,
            devops=devops_cat,
            cloud=cloud_cat,
            cs_fundamentals=cs_fund_cat,
            projects=projects_cat,
            resume=resume_cat,
            github=github_cat,
            communication=comm_cat,
        )

    def _build_tech_category(
        self, display_name: str, skills: List[NormalizedSkill], category_key: str
    ) -> CategorySkillProfile:
        if not skills:
            return CategorySkillProfile(
                category=display_name,
                overall_level="Not Detected",
                skills=[],
                evidence=[],
                summary=f"No {display_name} skills detected in the provided profile sources.",
            )

        # Aggregate evidence
        all_ev: List[str] = []
        for s in skills:
            all_ev.extend(s.evidence)

        # Determine level
        if any(s.current_level == "Advanced" for s in skills):
            overall_level = "Advanced"
        elif any(s.current_level == "Intermediate" for s in skills):
            overall_level = "Intermediate"
        elif any(s.current_level == "Beginner" for s in skills):
            overall_level = "Beginner"
        else:
            overall_level = "Untested"

        top_skills = [s.skill for s in skills[:3]]
        summary = f"Identified {len(skills)} skill(s) including {', '.join(top_skills)} with an overall assessed level of {overall_level}."

        return CategorySkillProfile(
            category=display_name,
            overall_level=overall_level,
            skills=skills,
            evidence=all_ev[:10],
            summary=summary,
        )

    def _build_dsa_category(
        self, dsa_skills: List[NormalizedSkill], leetcode: Optional[LeetCodeAnalysis]
    ) -> CategorySkillProfile:
        all_ev: List[str] = []
        for s in dsa_skills:
            all_ev.extend(s.evidence)

        if leetcode:
            stats = leetcode.problem_statistics
            if stats.total_solved >= 100:
                overall_level = "Advanced"
            elif stats.total_solved >= 25:
                overall_level = "Intermediate"
            elif stats.total_solved > 0:
                overall_level = "Beginner"
            else:
                overall_level = "Untested"

            ev_str = f"LeetCode: {stats.total_solved} solved ({stats.easy_solved} Easy, {stats.medium_solved} Medium, {stats.hard_solved} Hard)"
            if ev_str not in all_ev:
                all_ev.insert(0, ev_str)

            strong_str = f"Strong topics: {', '.join(leetcode.strong_topics)}" if leetcode.strong_topics else "No topics marked strong yet"
            summary = f"DSA profile verified with {stats.total_solved} LeetCode problems solved. {strong_str}."
        elif dsa_skills:
            overall_level = "Intermediate" if any(s.current_level in ["Intermediate", "Advanced"] for s in dsa_skills) else "Beginner"
            summary = f"DSA concepts noted in resume/profile ({len(dsa_skills)} detected), but no LeetCode profile was connected to verify problem-solving metrics."
        else:
            overall_level = "Untested"
            summary = "No DSA problem-solving statistics or algorithms data provided."

        return CategorySkillProfile(
            category="DSA",
            overall_level=overall_level,
            skills=dsa_skills,
            evidence=all_ev[:10],
            summary=summary,
        )

    def _build_projects_category(
        self, resume: Optional[ResumeAnalysis], github: Optional[GitHubAnalysis]
    ) -> ProjectsProfileCategory:
        resume_count = len(resume.projects) if resume else 0
        github_count = github.activity.non_fork_repos if github else 0
        total_projects = resume_count + github_count
        metrics_count = sum(1 for p in resume.projects if p.has_metrics) if resume else 0

        complexity_dist: Dict[str, int] = {}
        if github:
            for c in github.complexity_analyses:
                lvl = c.complexity_level.lower()
                complexity_dist[lvl] = complexity_dist.get(lvl, 0) + 1

        top_techs: List[str] = []
        if resume:
            for p in resume.projects:
                top_techs.extend(p.technologies)
        if github:
            top_techs.extend(github.languages.all_languages)
        # Deduplicate top techs preserving frequency
        top_techs_dedup = sorted(list(set(top_techs)), key=lambda t: top_techs.count(t), reverse=True)[:6]

        highlights: List[str] = []
        evidence: List[str] = []

        if resume:
            evidence.append(f"Resume lists {resume_count} project(s), with {metrics_count} containing quantifiable impact metrics.")
            for p in resume.projects[:3]:
                highlights.append(f"{p.name}: {p.description or ', '.join(p.technologies)}")
        if github:
            evidence.append(f"GitHub provides {github_count} original repository(ies) with {github.activity.total_stars} star(s).")

        if total_projects >= 4 and (metrics_count >= 1 or complexity_dist.get("advanced", 0) >= 1):
            level = "Advanced"
        elif total_projects >= 2:
            level = "Intermediate"
        elif total_projects >= 1:
            level = "Beginner"
        else:
            level = "Untested"

        if total_projects == 0:
            summary = "No verified projects found on resume or GitHub."
        else:
            summary = f"Portfolio contains {total_projects} total projects ({resume_count} in resume, {github_count} original repos). Key tech: {', '.join(top_techs_dedup[:4])}."

        return ProjectsProfileCategory(
            overall_level=level,
            total_projects_detected=total_projects,
            resume_projects_count=resume_count,
            github_repos_count=github_count,
            projects_with_metrics_count=metrics_count,
            complexity_breakdown=complexity_dist,
            top_technologies=top_techs_dedup,
            highlights=highlights,
            evidence=evidence,
            summary=summary,
        )

    def _build_resume_category(self, resume: Optional[ResumeAnalysis]) -> ResumeProfileCategory:
        if not resume:
            return ResumeProfileCategory(
                overall_level="Untested",
                summary="Resume analysis was not provided.",
                evidence=[],
            )

        score = resume.overall_score
        if score >= 80:
            level = "Strong"
        elif score >= 60:
            level = "Moderate"
        else:
            level = "Needs Work"

        sections_present = []
        if resume.extracted_skills.languages or resume.extracted_skills.frameworks:
            sections_present.append("Skills")
        if resume.education:
            sections_present.append("Education")
        if resume.experience:
            sections_present.append("Experience")
        if resume.projects:
            sections_present.append("Projects")
        if resume.certifications:
            sections_present.append("Certifications")

        ev = [
            f"Overall ATS score: {score}/100",
            f"Skills score: {resume.skills_score.score}/100, Projects score: {resume.projects_score.score}/100",
            f"Identified {len(resume.weak_bullets)} weak bullet point(s) needing impact rewrite",
        ]
        if resume.missing_sections:
            ev.append(f"Missing sections: {', '.join(resume.missing_sections)}")

        summary = f"Resume scored {score}/100 with {len(sections_present)} standard sections present. {len(resume.weak_bullets)} weak bullets flagged."

        return ResumeProfileCategory(
            overall_level=level,
            ats_score=resume.ats_score.score,
            overall_score=score,
            sections_present=sections_present,
            missing_sections=resume.missing_sections,
            weak_bullets_count=len(resume.weak_bullets),
            keyword_gaps=resume.keyword_gaps,
            evidence=ev,
            summary=summary,
        )

    def _build_github_category(self, github: Optional[GitHubAnalysis]) -> GitHubProfileCategory:
        if not github:
            return GitHubProfileCategory(
                overall_level="Untested",
                summary="GitHub analysis was not provided.",
                evidence=[],
            )

        total_repos = github.activity.total_public_repos
        non_fork = github.activity.non_fork_repos
        readme_pct = round(
            (github.activity.repos_with_readme / total_repos * 100) if total_repos > 0 else 0.0, 1
        )

        if total_repos >= 5 and github.activity.most_recent_push:
            level = "Active"
        elif total_repos >= 2:
            level = "Moderate"
        elif total_repos >= 1:
            level = "Low Activity"
        else:
            level = "Untested"

        ev = [
            f"Public profile with {total_repos} repositories ({non_fork} non-forked)",
            f"Primary language: {github.languages.primary_language or 'N/A'}",
            f"Total stars earned: {github.activity.total_stars}, forks: {github.activity.total_forks}",
            f"Documentation coverage: {readme_pct}% of repositories have a README",
        ]

        summary = f"GitHub user '{github.profile.username}' has {total_repos} repos with {github.languages.primary_language} as the primary language and {readme_pct}% README coverage."

        return GitHubProfileCategory(
            overall_level=level,
            username=github.profile.username,
            total_public_repos=total_repos,
            non_fork_repos=non_fork,
            total_stars=github.activity.total_stars,
            primary_language=github.languages.primary_language,
            languages_detected=github.languages.all_languages,
            readme_coverage_pct=readme_pct,
            activity_level=level,
            evidence=ev,
            summary=summary,
        )

    def _build_communication_category(
        self, resume: Optional[ResumeAnalysis], github: Optional[GitHubAnalysis]
    ) -> CommunicationProfileCategory:
        if not resume and not github:
            return CommunicationProfileCategory(
                overall_level="Untested",
                summary="No resume or GitHub data available to evaluate communication and documentation.",
                evidence=[],
            )

        bullet_score = resume.impact_score.score if resume else 60
        generic_count = len(resume.generic_phrases) if resume else 0

        readme_pct = 0.0
        if github and github.activity.total_public_repos > 0:
            readme_pct = round((github.activity.repos_with_readme / github.activity.total_public_repos) * 100, 1)

        # Documentation score combines readme ratio and bullet clarity
        doc_score = int((bullet_score * 0.5) + (readme_pct * 0.5)) if github else bullet_score

        ev = []
        if resume:
            ev.append(f"Resume bullet clarity/impact score: {bullet_score}/100 ({len(resume.weak_bullets)} weak bullets flagged)")
            if generic_count > 0:
                ev.append(f"Contains {generic_count} generic/cliche phrase(s)")
        if github:
            ev.append(f"GitHub repository README documentation coverage: {readme_pct}%")

        if doc_score >= 80:
            level = "Strong"
        elif doc_score >= 55:
            level = "Adequate"
        else:
            level = "Needs Improvement"

        summary = f"Documentation clarity assessed at {doc_score}/100 with {readme_pct}% repository README coverage and bullet impact score {bullet_score}/100."

        return CommunicationProfileCategory(
            overall_level=level,
            documentation_score=doc_score,
            bullet_clarity_score=bullet_score,
            readme_coverage_pct=readme_pct,
            generic_phrases_count=generic_count,
            evidence=ev,
            summary=summary,
        )

    # -----------------------------------------------------------------------
    # Strengths, Growth Areas & Synthesis
    # -----------------------------------------------------------------------

    def _derive_strengths_and_gaps(
        self,
        normalized_skills: List[NormalizedSkill],
        categories: ProfileCategories,
        conflicts: List[ProfileConflict],
        source_status: ProfileSourceStatus,
    ) -> Tuple[List[str], List[str]]:
        strengths: List[str] = []
        growth_areas: List[str] = []

        # Top verified skills (confidence >= 0.85 and level Advanced/Intermediate)
        verified_strong_skills = [
            s.skill for s in normalized_skills
            if s.confidence >= 0.85 and s.current_level in ["Advanced", "Intermediate"]
        ]
        if verified_strong_skills:
            strengths.append(f"Multi-source verified proficiency in {', '.join(verified_strong_skills[:4])}.")

        # DSA Strengths / Gaps
        if categories.dsa.overall_level == "Advanced":
            strengths.append("Demonstrated solid problem-solving foundation in Data Structures & Algorithms.")
        elif categories.dsa.overall_level in ["Beginner", "Untested"]:
            growth_areas.append("Strengthen DSA problem-solving and expand topic coverage on LeetCode.")

        # Projects Strengths / Gaps
        if categories.projects.overall_level in ["Advanced", "Intermediate"]:
            strengths.append(f"Solid project portfolio with {categories.projects.total_projects_detected} projects detected.")
        if categories.projects.projects_with_metrics_count == 0 and categories.projects.total_projects_detected > 0:
            growth_areas.append("Incorporate quantifiable metrics and measurable outcomes into project descriptions.")

        # Resume ATS
        if categories.resume.ats_score and categories.resume.ats_score >= 80:
            strengths.append(f"High resume ATS readiness score of {categories.resume.ats_score}/100.")
        elif categories.resume.weak_bullets_count > 0:
            growth_areas.append(f"Improve {categories.resume.weak_bullets_count} weak resume bullet points using action verbs and impact metrics.")

        # GitHub documentation
        if categories.github.overall_level == "Active":
            strengths.append(f"Active GitHub profile with {categories.github.total_public_repos} repositories.")
        if categories.github.readme_coverage_pct < 50.0 and categories.github.total_public_repos > 0:
            growth_areas.append("Add detailed README files and architecture documentation to public GitHub repositories.")

        # Flagged Conflicts
        for c in conflicts:
            if c.severity in ["medium", "high"]:
                growth_areas.append(f"Resolve discrepancy in {c.skill_or_topic}: {c.conflict}")

        # Missing sources
        if not source_status.github_analysis:
            growth_areas.append("Connect a GitHub profile to verify codebase depth and open-source contributions.")
        if not source_status.leetcode_analysis:
            growth_areas.append("Connect a LeetCode profile to benchmark DSA problem-solving readiness.")

        return strengths, growth_areas

    def _calculate_overall_readiness(
        self,
        categories: ProfileCategories,
        skills: List[NormalizedSkill],
        source_status: ProfileSourceStatus,
    ) -> str:
        if source_status.total_sources_provided == 0:
            return "Untested"

        advanced_count = sum(
            1 for cat in [
                categories.programming,
                categories.dsa,
                categories.backend,
                categories.frontend,
                categories.machine_learning,
                categories.devops,
                categories.cloud,
            ]
            if cat.overall_level == "Advanced"
        )
        intermediate_count = sum(
            1 for cat in [
                categories.programming,
                categories.dsa,
                categories.backend,
                categories.frontend,
                categories.machine_learning,
                categories.devops,
                categories.cloud,
            ]
            if cat.overall_level == "Intermediate"
        )

        if advanced_count >= 2 and categories.projects.overall_level in ["Advanced", "Intermediate"]:
            return "Placement Ready"
        elif intermediate_count >= 2 or advanced_count >= 1:
            return "Developing"
        else:
            return "Beginner"

    def _generate_executive_summary(
        self,
        student: Optional[StudentProfile],
        source_status: ProfileSourceStatus,
        categories: ProfileCategories,
        skills: List[NormalizedSkill],
        conflicts: List[ProfileConflict],
        readiness: str,
    ) -> str:
        parts: List[str] = []

        # Target role & student context
        name = student.name if student and student.name else "Student"
        role = student.target_role if student and student.target_role else "Software Engineering"
        parts.append(f"{name} is targeting {role} roles with an overall assessed readiness of '{readiness}'.")

        # Source coverage
        sources_used = []
        if source_status.resume_analysis: sources_used.append("Resume")
        if source_status.github_analysis: sources_used.append("GitHub")
        if source_status.leetcode_analysis: sources_used.append("LeetCode")
        if source_status.student_profile: sources_used.append("Student Profile")
        parts.append(f"Analysis synthesized {len(skills)} unique skills from {len(sources_used)} source(s) ({', '.join(sources_used) if sources_used else 'None'}).")

        # Tech highlights
        top_skills = [s.skill for s in skills if s.confidence >= 0.8][:4]
        if top_skills:
            parts.append(f"Primary verified skills include {', '.join(top_skills)}.")

        # Project and DSA highlights
        if categories.projects.total_projects_detected > 0:
            parts.append(f"Portfolio includes {categories.projects.total_projects_detected} verified project(s).")
        if categories.dsa.overall_level != "Untested":
            parts.append(f"DSA capability is rated {categories.dsa.overall_level}.")

        # Conflict notes
        if conflicts:
            parts.append(f"{len(conflicts)} data conflict(s) were flagged and normalized transparently.")

        return " ".join(parts)
