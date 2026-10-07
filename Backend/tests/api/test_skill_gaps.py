"""
Comprehensive Skill Gap Analysis Tests.

Tests cover:
- Authentication enforcement
- Full analyze -> retrieve flow
- Target_role validation (empty, whitespace, too long)
- Typo/alias normalization (Backend-Develpoer -> Backend Developer)
- All 15 canonical roles produce valid, role-specific results
- Target role never appears as a skill
- Cross-role skill set diversity
- Single-source-of-truth consistency (priority_gaps match skills)
- Dynamic ai_summary references correct role
- Custom unlisted role handling (no fallback to AI/ML Engineer)
"""
import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Auth / unauthenticated tests
# ---------------------------------------------------------------------------
def test_skill_gaps_unauthenticated_access(client: TestClient):
    """Ensure all skill gaps endpoints reject unauthenticated requests."""
    assert client.post("/api/v1/skill-gaps/analyze").status_code == 401
    assert client.get("/api/v1/skill-gaps").status_code == 401
    assert client.get("/api/v1/skill-gaps/summary").status_code == 401
    assert client.get("/api/v1/skill-gaps/history").status_code == 401
    assert client.get("/api/v1/skill-gaps/650c1f2e8f1b2c3d4e5f6a7b").status_code == 401


# ---------------------------------------------------------------------------
# Full integration flow
# ---------------------------------------------------------------------------
def test_skill_gaps_analyze_and_retrieve_flow(client: TestClient, auth_headers: dict):
    """Test full skill gaps flow: analyze -> get latest -> summary -> history -> get by ID."""
    res_analyze = client.post(
        "/api/v1/skill-gaps/analyze",
        json={"target_role": "Backend Developer"},
        headers=auth_headers
    )
    assert res_analyze.status_code == 200, res_analyze.text
    data_analyze = res_analyze.json()["data"]
    assert data_analyze["target_role"] == "Backend Developer"
    assert "overall_coverage" in data_analyze
    assert "summary" in data_analyze
    assert "skills" in data_analyze
    assert "priority_gaps" in data_analyze
    assert "category_coverage" in data_analyze
    assert "matrix2x2" in data_analyze
    assert "ai_summary" in data_analyze
    # ai_summary must reference the canonical role
    assert "Backend Developer" in (data_analyze["ai_summary"] or "")
    analysis_id = data_analyze["id"]

    res_latest = client.get("/api/v1/skill-gaps", headers=auth_headers)
    assert res_latest.status_code == 200
    data_latest = res_latest.json()["data"]
    assert data_latest["id"] == analysis_id
    assert data_latest["target_role"] == "Backend Developer"

    res_summary = client.get("/api/v1/skill-gaps/summary", headers=auth_headers)
    assert res_summary.status_code == 200
    data_summary = res_summary.json()["data"]
    assert data_summary["target_role"] == "Backend Developer"
    assert "overall_coverage" in data_summary
    assert "gaps_identified_count" in data_summary
    assert "top_priority_gaps" in data_summary

    res_history = client.get("/api/v1/skill-gaps/history", headers=auth_headers)
    assert res_history.status_code == 200
    data_history = res_history.json()["data"]
    assert data_history["total"] >= 1
    assert len(data_history["items"]) >= 1

    res_by_id = client.get(f"/api/v1/skill-gaps/{analysis_id}", headers=auth_headers)
    assert res_by_id.status_code == 200
    assert res_by_id.json()["data"]["id"] == analysis_id


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------
def test_skill_gaps_validation(client: TestClient, auth_headers: dict):
    """Test target_role Pydantic validation."""
    # Empty body
    res_empty = client.post("/api/v1/skill-gaps/analyze", json={}, headers=auth_headers)
    assert res_empty.status_code == 422

    # Empty string
    res_blank = client.post("/api/v1/skill-gaps/analyze", json={"target_role": "  "}, headers=auth_headers)
    assert res_blank.status_code == 422

    # Too long (> 100 chars)
    res_long = client.post(
        "/api/v1/skill-gaps/analyze",
        json={"target_role": "A" * 101},
        headers=auth_headers
    )
    assert res_long.status_code == 422


# ---------------------------------------------------------------------------
# Typo / Alias normalization tests
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("typo_input,expected_canonical", [
    ("Backend-Develpoer",       "Backend Developer"),
    ("backend developer",       "Backend Developer"),
    ("BACKEND-DEVELOPER",       "Backend Developer"),
    ("backend dev",             "Backend Developer"),
    ("Backend Develper",        "Backend Developer"),
    ("backend engineer",        "Backend Developer"),
    ("Frontend-Developer",      "Frontend Developer"),
    ("frontend dev",            "Frontend Developer"),
    ("frontend engineer",       "Frontend Developer"),
    ("AI/ML Engineer",          "AI/ML Engineer"),
    ("ai ml engineer",          "AI/ML Engineer"),
    ("machine learning engineer","ML Engineer"),
    ("data scientist",          "Data Scientist"),
    ("Data Scientist",          "Data Scientist"),
    ("devops",                  "DevOps Engineer"),
    ("DevOps",                  "DevOps Engineer"),
    ("cybersecurity analyst",   "Cybersecurity Analyst"),
    ("Cybersecurity Analyst",   "Cybersecurity Analyst"),
    ("software engineer",       "Software Engineer"),
    ("sde",                     "Software Engineer"),
    ("data engineer",           "Data Engineer"),
    ("cloud engineer",          "Cloud Engineer"),
    ("qa engineer",             "QA / Test Engineer"),
    ("qa",                      "QA / Test Engineer"),
    ("quality assurance",       "QA / Test Engineer"),
    ("database engineer",       "Database Engineer"),
    ("business analyst",        "Business Analyst"),
    ("product manager",         "Product Manager"),
])
def test_role_typo_normalization(client: TestClient, auth_headers: dict, typo_input, expected_canonical):
    """All typos/aliases should resolve to canonical role names."""
    res = client.post(
        "/api/v1/skill-gaps/analyze",
        json={"target_role": typo_input},
        headers=auth_headers
    )
    assert res.status_code == 200, f"Role '{typo_input}' failed with {res.text}"
    data = res.json()["data"]
    assert data["target_role"] == expected_canonical, (
        f"Role '{typo_input}': expected canonical '{expected_canonical}', got '{data['target_role']}'"
    )


# ---------------------------------------------------------------------------
# Target role must NEVER appear as a skill
# ---------------------------------------------------------------------------
def _assert_role_not_in_skills(data: dict, role: str):
    """Assert the target role name is not present as a skill."""
    role_lower = role.lower().strip()
    for s in data["skills"]:
        skill_lower = s["skill"].lower().strip()
        assert skill_lower != role_lower, (
            f"Role '{role}' appeared as skill '{s['skill']}' — this is forbidden!"
        )
    for pg in data.get("priority_gaps", []):
        skill_lower = pg["skill"].lower().strip()
        assert skill_lower != role_lower, (
            f"Role '{role}' appeared as priority_gap skill '{pg['skill']}' — this is forbidden!"
        )


# ---------------------------------------------------------------------------
# All 15 canonical roles must pass comprehensively
# ---------------------------------------------------------------------------
ALL_15_ROLES = [
    "AI/ML Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "Data Scientist",
    "Data Engineer",
    "DevOps Engineer",
    "Cybersecurity Analyst",
    "Software Engineer",
    "Cloud Engineer",
    "Mobile App Developer",
    "QA / Test Engineer",
    "Database Engineer",
    "Business Analyst",
    "Product Manager",
]


@pytest.mark.parametrize("role", ALL_15_ROLES)
def test_all_15_canonical_roles(client: TestClient, auth_headers: dict, role: str):
    """
    Comprehensively test each of the 15 required roles.
    Verifies: canonical role, skill list, role-not-a-skill, consistency, dynamic coverage.
    """
    res = client.post(
        "/api/v1/skill-gaps/analyze",
        json={"target_role": role},
        headers=auth_headers
    )
    assert res.status_code == 200, f"Role '{role}' failed with: {res.text}"
    data = res.json()["data"]

    # 1. Correct canonical target_role
    assert data["target_role"] == role, f"Expected '{role}', got '{data['target_role']}'"

    # 2. Non-empty skill list (at least 4 skills)
    skills = data["skills"]
    assert len(skills) >= 4, f"Role '{role}' returned too few skills: {[s['skill'] for s in skills]}"

    # 3. Target role is NOT a skill
    _assert_role_not_in_skills(data, role)

    # 4. Required levels are internally consistent (from role requirements, not random)
    for s in skills:
        assert s["required_level_num"] >= 1, f"required_level_num must be >= 1 for skill {s['skill']}"
        assert s["current_level_num"] >= 0, f"current_level_num must be >= 0 for skill {s['skill']}"

    # 5. gap_type is mathematically consistent with levels
    for s in skills:
        cur = s["current_level_num"]
        req = s["required_level_num"]
        gt = s["gap_type"]
        if cur >= req:
            assert gt == "aligned", f"Skill '{s['skill']}': cur={cur} >= req={req} but gap_type='{gt}'"
        elif cur == 0:
            assert gt == "missing", f"Skill '{s['skill']}': cur=0 should be 'missing' but got '{gt}'"
        else:
            assert gt == "developing", f"Skill '{s['skill']}': cur={cur} < req={req} (non-zero) should be 'developing' but got '{gt}'"

    # 6. Reason is internally consistent (no untested contradiction)
    for s in skills:
        if s["current_level"] != "Untested":
            assert "untested" not in s["reason"].lower(), (
                f"Skill '{s['skill']}': current_level={s['current_level']} but reason says 'untested'"
            )

    # 7. priority_gaps exist only for actual gaps and match skills
    skill_map = {s["skill"]: s for s in skills}
    for pg in data["priority_gaps"]:
        sk = skill_map.get(pg["skill"])
        assert sk is not None, f"priority_gap '{pg['skill']}' has no matching entry in skills"
        assert pg["current_level"] == sk["current_level"], (
            f"priority_gap.current_level '{pg['current_level']}' != skills.current_level '{sk['current_level']}' for '{pg['skill']}'"
        )
        assert pg["required_level"] == sk["required_level"], (
            f"priority_gap.required_level mismatch for '{pg['skill']}'"
        )
        assert pg["reason"] == sk["reason"], f"priority_gap.reason mismatch for '{pg['skill']}'"
        assert pg["suggested_action"] == sk["recommended_action"], (
            f"priority_gap.suggested_action mismatch for '{pg['skill']}'"
        )
        # Gaps cannot be for aligned skills
        assert sk["gap_type"] != "aligned", f"Aligned skill '{pg['skill']}' found in priority_gaps"

    # 8. Recommendations must reference actual skills, not the role name as a skill
    for rec in data.get("recommendations", []):
        title = rec.get("title", "")
        desc = rec.get("description", "")
        role_lower = role.lower()
        # Recommendations CAN reference the role name (e.g., "for Backend Developer")
        # but should NOT say "Bridge Priority Gap: Backend Developer for Backend Developer"
        # i.e. the skill part should not equal the role name
        if "Bridge Priority Gap:" in title:
            skill_part = title.replace("Bridge Priority Gap:", "").split(" for ")[0].strip()
            assert skill_part.lower() != role_lower, (
                f"Bad recommendation title for role '{role}': skill_part='{skill_part}'"
            )

    # 9. ai_summary references the correct role
    ai_summary = data.get("ai_summary", "") or ""
    assert role in ai_summary, (
        f"ai_summary for role '{role}' does not mention the role: '{ai_summary}'"
    )

    # 10. overall_coverage is between 0 and 100
    cov = data["overall_coverage"]
    assert 0 <= cov <= 100, f"overall_coverage={cov} out of range for role '{role}'"

    # 11. category_coverage is dynamic and matches skills categories
    skill_categories = {s["category"] for s in skills}
    cat_cov_names = {c["category"] for c in data.get("category_coverage", [])}
    # Every skill category should appear in category_coverage
    for cat in skill_categories:
        assert cat in cat_cov_names, (
            f"Category '{cat}' from skills not found in category_coverage for role '{role}'"
        )


# ---------------------------------------------------------------------------
# Cross-role skill set diversity
# ---------------------------------------------------------------------------
def test_cross_role_skill_diversity(client: TestClient, auth_headers: dict):
    """Run the same student against 6 distinct roles and verify different skill sets."""
    roles_to_compare = [
        "Backend Developer",
        "Cybersecurity Analyst",
        "Data Scientist",
        "DevOps Engineer",
        "Frontend Developer",
        "AI/ML Engineer",
    ]

    role_skill_sets = {}
    for role in roles_to_compare:
        res = client.post(
            "/api/v1/skill-gaps/analyze",
            json={"target_role": role},
            headers=auth_headers
        )
        assert res.status_code == 200, f"Role '{role}' failed"
        data = res.json()["data"]
        role_skill_sets[role] = frozenset(s["skill"] for s in data["skills"])

    # Each pair of distinct roles should NOT have identical skill sets
    role_list = list(role_skill_sets.keys())
    for i in range(len(role_list)):
        for j in range(i + 1, len(role_list)):
            r1, r2 = role_list[i], role_list[j]
            s1, s2 = role_skill_sets[r1], role_skill_sets[r2]
            assert s1 != s2, (
                f"Roles '{r1}' and '{r2}' produced identical skill sets: {sorted(s1)}"
            )


# ---------------------------------------------------------------------------
# Typo BACKENDDEVELPOER specifically (the main reported bug)
# ---------------------------------------------------------------------------
def test_typo_backend_develpoer_not_a_skill(client: TestClient, auth_headers: dict):
    """
    'Backend-Develpoer' must:
    1. Normalize to 'Backend Developer' (canonical role)
    2. Never appear as a skill in the result
    """
    res = client.post(
        "/api/v1/skill-gaps/analyze",
        json={"target_role": "Backend-Develpoer"},
        headers=auth_headers
    )
    assert res.status_code == 200, res.text
    data = res.json()["data"]

    assert data["target_role"] == "Backend Developer", (
        f"Expected 'Backend Developer' canonical, got '{data['target_role']}'"
    )
    _assert_role_not_in_skills(data, "Backend-Develpoer")
    _assert_role_not_in_skills(data, "Backend Developer")


# ---------------------------------------------------------------------------
# Custom unlisted role handling
# ---------------------------------------------------------------------------
def test_custom_unlisted_role_handling(client: TestClient, auth_headers: dict):
    """
    Custom unlisted roles should:
    1. Return 200 OK
    2. Never produce the role name itself as a skill
    3. Never silently fall back to AI/ML Engineer requirements
    4. Have at least 4 skills
    """
    res = client.post(
        "/api/v1/skill-gaps/analyze",
        json={"target_role": "Robotics Engineer"},
        headers=auth_headers
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["target_role"] == "Robotics Engineer"

    skills = [s["skill"] for s in data["skills"]]
    assert len(skills) >= 4, f"Too few skills for custom role: {skills}"

    # NEVER use role name as skill
    _assert_role_not_in_skills(data, "Robotics Engineer")

    # NEVER return same skill set as AI/ML Engineer (no silent fallback)
    aiml_skills = {req["skill"] for req in [
        {"skill": "PyTorch"}, {"skill": "Machine Learning"},
        {"skill": "Deep Learning"}, {"skill": "TensorFlow"},
    ]}
    custom_skills = set(skills)
    # Should not be identical to the AI/ML Engineer skill set
    assert custom_skills != {"Python", "PyTorch", "Scikit-learn", "Data Structures & Algorithms",
                              "Deep Learning", "Statistics", "Docker", "REST API", "TensorFlow"}, (
        "Custom role silently fell back to AI/ML Engineer requirements!"
    )


# ---------------------------------------------------------------------------
# No AI/ML Engineer hardcoded fallback for specific roles
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("role,forbidden_skill", [
    ("Cybersecurity Analyst", "PyTorch"),
    ("Frontend Developer",     "PyTorch"),
    ("DevOps Engineer",        "PyTorch"),
    ("Database Engineer",      "Deep Learning"),
    ("Business Analyst",       "Machine Learning"),
    ("Product Manager",        "PyTorch"),
])
def test_no_aiml_leakage_in_role(client: TestClient, auth_headers: dict, role: str, forbidden_skill: str):
    """Non-ML roles should not have ML-specific required skills leaking from AI/ML fallback."""
    res = client.post(
        "/api/v1/skill-gaps/analyze",
        json={"target_role": role},
        headers=auth_headers
    )
    assert res.status_code == 200, f"Role '{role}' failed"
    data = res.json()["data"]
    skills = [s["skill"] for s in data["skills"]]
    assert forbidden_skill not in skills, (
        f"Role '{role}' has AI/ML-leaked skill '{forbidden_skill}': {skills}"
    )
