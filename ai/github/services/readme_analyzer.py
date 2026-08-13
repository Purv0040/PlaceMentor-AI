"""README and documentation quality analyzer for GitHub repositories."""

from typing import List, Optional, Dict, Any
from models.github import READMECheckDetails, RepositorySummary
from utils.constants import README_SECTION_KEYWORDS


class READMEAnalyzer:
    """Performs rule-based inspection of repository README content."""

    @staticmethod
    def analyze_readme_text(readme_content: Optional[str]) -> READMECheckDetails:
        """
        Analyzes raw README text content for essential section markers:
        Description, Installation, Usage, Features, Technologies, Screenshots, API docs, License.
        Returns a READMECheckDetails model with a sub-score (0 to 20).
        """
        if not readme_content or not readme_content.strip():
            return READMECheckDetails(has_readme=False, score=0.0)

        content_lower = readme_content.lower()

        def check_keywords(keywords: List[str]) -> bool:
            return any(kw in content_lower for kw in keywords)

        has_desc = check_keywords(README_SECTION_KEYWORDS["description"])
        has_inst = check_keywords(README_SECTION_KEYWORDS["installation"])
        has_usg = check_keywords(README_SECTION_KEYWORDS["usage"])
        has_feat = check_keywords(README_SECTION_KEYWORDS["features"])
        has_tech = check_keywords(README_SECTION_KEYWORDS["technologies"])
        has_shots = check_keywords(README_SECTION_KEYWORDS["screenshots"])
        has_api = check_keywords(README_SECTION_KEYWORDS["api_docs"])
        has_lic = check_keywords(README_SECTION_KEYWORDS["license"])

        # Score calculation out of 20 points
        score = 4.0  # Base score for having a non-empty README

        if has_desc:
            score += 2.5
        if has_inst:
            score += 2.5
        if has_usg:
            score += 2.5
        if has_feat:
            score += 2.0
        if has_tech:
            score += 2.0
        if has_shots:
            score += 2.0
        if has_api:
            score += 1.5
        if has_lic:
            score += 1.0

        final_score = min(20.0, round(score, 2))

        return READMECheckDetails(
            has_readme=True,
            has_description=has_desc,
            has_installation=has_inst,
            has_usage=has_usg,
            has_features=has_feat,
            has_technologies=has_tech,
            has_screenshots=has_shots,
            has_api_docs=has_api,
            has_license=has_lic,
            score=final_score
        )

    @classmethod
    def analyze_documentation(
        cls,
        repositories: List[RepositorySummary],
        readme_map: Dict[str, Optional[str]]
    ) -> float:
        """
        Aggregates documentation quality score across top non-fork repositories.
        Max score: 20.0
        """
        non_forks = [r for r in repositories if not r.is_fork]
        if not non_forks:
            return 0.0

        # Sort non-forks by pushed date / stars
        non_forks = non_forks[:5]

        total_doc_score = 0.0
        evaluated_count = 0

        for repo in non_forks:
            readme_text = readme_map.get(repo.name)
            check = cls.analyze_readme_text(readme_text)
            repo.has_readme = check.has_readme
            total_doc_score += check.score
            evaluated_count += 1

        if evaluated_count == 0:
            return 0.0

        avg_score = total_doc_score / evaluated_count
        return min(20.0, round(avg_score, 2))
