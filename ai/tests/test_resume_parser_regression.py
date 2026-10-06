import pytest
from app.services.dynamic_extractor import (
    parse_resume_dynamically,
    extract_projects,
    extract_education,
    extract_certifications,
    extract_skills_from_text,
    parse_resume_sections,
)
from app.analyzers.resume_analyzer import ResumeAnalyzer


def test_regression_one_project_five_bullets_tech_stack():
    """
    REGRESSION TEST:
    ONE project + FIVE bullet points + Tech Stack line.
    Must produce exactly 1 project with 5 bullet points and correctly parsed technologies.
    The Tech Stack line must NOT become another project or bullet point.
    """
    resume_text = """
    PROJECTS

    AI-Based Micro-Internship Task Matching Platform (Team Project)

    1. Developed a full-stack web application to connect students with short-term, skill-based micro-internship tasks.
    2. Implemented automated skill-matching logic to recommend tasks based on user profiles and availability.
    3. Designed role-based dashboards for students and companies to manage task posting, applications, and submissions.
    4. Built a performance tracking system using ratings and feedback to improve future task recommendations.
    5. Collaborated in a 2-member team with clear role division across frontend and backend development.
    6. Tech Stack: HTML, CSS, JavaScript, Node.js/Flask, MySQL/MongoDB
    """

    parsed = parse_resume_dynamically(resume_text)
    projects = parsed["projects"]

    assert len(projects) == 1, f"Expected 1 project, got {len(projects)}"
    proj = projects[0]

    assert "AI-Based Micro-Internship Task Matching Platform (Team Project)" in proj["name"]
    assert len(proj["bullets"]) == 5, f"Expected 5 bullets, got {len(proj['bullets'])}"

    expected_bullets = [
        "Developed a full-stack web application to connect students with short-term, skill-based micro-internship tasks.",
        "Implemented automated skill-matching logic to recommend tasks based on user profiles and availability.",
        "Designed role-based dashboards for students and companies to manage task posting, applications, and submissions.",
        "Built a performance tracking system using ratings and feedback to improve future task recommendations.",
        "Collaborated in a 2-member team with clear role division across frontend and backend development."
    ]
    assert proj["bullets"] == expected_bullets

    expected_techs = ["HTML", "CSS", "JavaScript", "Node.js", "Flask", "MySQL", "MongoDB"]
    for tech in expected_techs:
        assert tech in proj["technologies"], f"Expected {tech} in technologies, got {proj['technologies']}"

    # Ensure Tech Stack is not in bullets
    for b in proj["bullets"]:
        assert not b.startswith("Tech Stack:"), "Tech stack line was incorrectly appended to bullets"


def test_multiline_pdf_text_extraction():
    """
    Test reconstruction of multiline PDF wrapped sentences into a single bullet point.
    """
    resume_text = """
    PROJECTS

    Smart Healthcare System

    • Developed a real-time patient tracking web application to connect students with short-term
      micro-internship tasks and hospital updates.
    • Implemented automated skill-matching logic to recommend healthcare tasks based on user
      profiles and doctor availability.
    """

    parsed = parse_resume_dynamically(resume_text)
    projects = parsed["projects"]

    assert len(projects) == 1
    assert len(projects[0]["bullets"]) == 2
    assert "short-term micro-internship tasks" in projects[0]["bullets"][0]
    assert "user profiles and doctor availability." in projects[0]["bullets"][1]


def test_multiple_projects_parsing():
    """
    Test resume with multiple distinct projects.
    """
    resume_text = """
    PROJECTS

    AI Internship Platform (Team Project)
    • Developed full stack app using Python and React.
    • Tech Stack: Python, React, MongoDB

    Smart Waste Management System
    • Built an IoT garbage monitoring dashboard.
    • Tech Stack: C++, Node.js, Express.js
    """

    parsed = parse_resume_dynamically(resume_text)
    projects = parsed["projects"]

    assert len(projects) == 2
    assert projects[0]["name"] == "AI Internship Platform (Team Project)"
    assert len(projects[0]["bullets"]) == 1
    assert "Python" in projects[0]["technologies"]
    assert "React" in projects[0]["technologies"]

    assert projects[1]["name"] == "Smart Waste Management System"
    assert len(projects[1]["bullets"]) == 1
    assert "C++" in projects[1]["technologies"]
    assert "Node.js" in projects[1]["technologies"]


def test_resume_without_experience():
    """
    Test resume with no work experience returns experience: [] and Education/Experience missing sections.
    """
    resume_text = """
    EDUCATION
    XYZ University
    B.Tech in Computer Engineering

    PROJECTS
    Test Project
    • Built a test project
    """

    parsed = parse_resume_dynamically(resume_text)
    assert parsed["experience"] == []
    assert "Experience" in parsed["missing_sections"]


def test_resume_with_experience():
    """
    Test resume with work experience extracts company, role, duration, bullets.
    """
    resume_text = """
    WORK EXPERIENCE

    Software Engineer Intern at TechCorp (Jun 2023 - Aug 2023)
    • Developed microservices API using Python FastAPI.
    • Reduced API response latency by 35%.
    """

    parsed = parse_resume_dynamically(resume_text)
    exp = parsed["experience"]
    assert len(exp) == 1
    assert exp[0]["role"] == "Software Engineer Intern"
    assert exp[0]["company"] == "TechCorp"
    assert exp[0]["duration"] == "Jun 2023 - Aug 2023"
    assert len(exp[0]["bullets"]) == 2


def test_education_parsing_merges_institution_and_degree():
    """
    Test education parsing does NOT split institution and degree into separate records.
    """
    resume_text = """
    EDUCATION

    Chandubhai S. Patel Institute of Technology (CSPIT), CHARUSAT
    B.Tech in Artificial Intelligence & Machine Learning
    2024-PRESENT
    CGPA: 7.16/10
    """

    sections = parse_resume_sections(resume_text)
    edu = extract_education(sections["education"], resume_text)

    assert len(edu) == 1, f"Expected 1 education entry, got {len(edu)}"
    assert edu[0]["institution"] == "Chandubhai S. Patel Institute of Technology (CSPIT), CHARUSAT"
    assert edu[0]["degree"] == "B.Tech in Artificial Intelligence & Machine Learning"
    assert edu[0]["graduation_date"] == "2024-PRESENT"
    assert "7.16" in edu[0]["gpa"]


def test_certification_parsing_filters_headers():
    """
    Test certification parsing ignores generic headings like 'PROFILE' or 'SUMMARY'.
    """
    resume_text = """
    PROFILE
    CERTIFICATIONS
    AWS Certified Cloud Practitioner
    Google Data Analytics Professional Certificate
    """

    sections = parse_resume_sections(resume_text)
    certs = extract_certifications(sections["certifications"])

    assert "PROFILE" not in certs
    assert "CERTIFICATIONS" not in certs
    assert "AWS Certified Cloud Practitioner" in certs
    assert "Google Data Analytics Professional Certificate" in certs


def test_skills_extraction_deduplication():
    """
    Test skills extraction normalizes aliases like Node, Node.js, NodeJS into single canonical skill.
    """
    text = "Proficient in Node, Node.js, NodeJS, React.js, React, Python, MySQL, and MongoDB."
    skills = extract_skills_from_text(text)

    assert skills["frameworks"].count("Node.js") == 1
    assert "Node" not in skills["frameworks"]
    assert "NodeJS" not in skills["frameworks"]
    assert skills["frameworks"].count("React") == 1
    assert "React.js" not in skills["frameworks"]


def test_end_to_end_user_exact_resume():
    """
    End-to-End test on the user's exact uploaded resume text verifying all 8 bug fixes.
    """
    resume_text = """
PROFILE

EDUCATION
Chandubhai S. Patel Institute of Technology (CSPIT), CHARUSAT
B.Tech in Artificial Intelligence & Machine Learning
2024–PRESENT
CGPA-7.16/10

SKILLS
Python, C, C++
Git, GitHub, Jupyter Notebook, VS Code
NumPy, Pandas, Matplotlib, Seaborn
Data Structures & Algorithms, Basic OOP
Regression, Classification, Model Evaluation
MongoDB, MySQL

PROJECTS

AI-Based Micro-Internship Task Matching Platform (Team Project)

• Developed a full-stack web application to connect students with short-term, skill-based micro-internship tasks.

• Implemented automated skill-matching logic to recommend tasks based on user profiles and availability.

• Designed role-based dashboards for students and companies to manage task posting, applications, and submissions.

• Built a performance tracking system using ratings and feedback to improve future task recommendations.

• Collaborated in a 2-member team with clear role division across frontend and backend development.

Technology stack:
HTML, CSS, JavaScript, Node.js, Flask, MySQL, MongoDB

CERTIFICATIONS

Python for Data Science-NPTEL
Demystifying Networking- NPTEL
"""

    analyzer = ResumeAnalyzer()
    analysis = analyzer.analyze_text(resume_text)

    # BUG 1 & BUG 7: Projects count must be 1
    assert len(analysis.projects) == 1
    proj = analysis.projects[0]
    assert proj.name == "AI-Based Micro-Internship Task Matching Platform (Team Project)"
    assert len(proj.bullets) == 5
    assert "HTML" in proj.technologies
    assert "Node.js" in proj.technologies

    # BUG 3: Name must never be bullet marker
    for p in analysis.projects:
        assert p.name not in ["•", "-", "*", "●", "▪"]

    # BUG 4: Certifications extracted and NOT in missing_sections
    assert len(analysis.certifications) == 2
    assert "Python for Data Science-NPTEL" in analysis.certifications
    assert "Demystifying Networking- NPTEL" in analysis.certifications
    assert "Certifications" not in analysis.missing_sections
    assert "Experience" in analysis.missing_sections

    # BUG 5: Global skills extracted from SKILLS section, project techs separated
    assert "Python" in analysis.extracted_skills.languages
    assert "C++" in analysis.extracted_skills.languages
    assert "HTML" not in analysis.extracted_skills.languages

    # BUG 6: Impact score evaluated on existing 5 project bullets
    assert analysis.impact_score.score > 0
    assert "No description bullets found" not in analysis.impact_score.reason


def test_library_classification_and_cpp_language():
    """
    Test NumPy, Pandas, Matplotlib, Seaborn are classified as libraries, C++ as language.
    """
    text = "SKILLS\nPython, C++, Java\nNumPy, Pandas, Matplotlib, Seaborn\nFlask, React"
    parsed = parse_resume_dynamically(text)
    skills = parsed["skills"]

    assert "C++" in skills["languages"]
    assert "Python" in skills["languages"]

    for lib in ["NumPy", "Pandas", "Matplotlib", "Seaborn"]:
        assert lib in skills["libraries"], f"Expected {lib} in libraries, got {skills['libraries']}"
        assert lib not in skills["frameworks"], f"Did not expect {lib} in frameworks"


def test_skill_normalization():
    """
    Test Jupyter + Jupyter Notebook -> Jupyter Notebook, Git + GIT -> Git, Github + GitHub -> GitHub
    """
    text = "SKILLS\nJupyter, Jupyter Notebook, Git, GIT, Github, GitHub"
    parsed = parse_resume_dynamically(text)
    skills = parsed["skills"]

    all_skills = skills["languages"] + skills["frameworks"] + skills["libraries"] + skills["tools"] + skills["other"]

    assert all_skills.count("Jupyter Notebook") == 1
    assert "Jupyter" not in all_skills
    assert all_skills.count("Git") == 1
    assert "GIT" not in all_skills
    assert all_skills.count("GitHub") == 1
    assert "Github" not in all_skills


def test_project_description_extraction():
    """
    Test project description is populated from bullet 1 summary when bullets exist.
    """
    text = """
    PROJECTS
    Task Matching System
    • Developed a full-stack task matching application.
    • Built using React and Node.js.
    """
    parsed = parse_resume_dynamically(text)
    proj = parsed["projects"][0]

    assert proj["description"] is not None
    assert proj["description"] == "Developed a full-stack task matching application."


def test_role_and_jd_keyword_gaps():
    """
    Test keyword gaps depend on target role or job description.
    """
    text = "SKILLS\nPython, SQL, HTML, CSS"
    
    # 1. No role and No JD -> empty keyword gaps (do not fabricate Docker/Kubernetes)
    parsed_none = parse_resume_dynamically(text)
    assert parsed_none["keyword_gaps"] == []

    # 2. Target role AI Engineer -> expects PyTorch, TensorFlow, Transformers, LLMs, RAG, MLOps
    parsed_ai = parse_resume_dynamically(text, target_role="AI Engineer")
    assert "PyTorch" in parsed_ai["keyword_gaps"]
    assert "Transformers" in parsed_ai["keyword_gaps"]

    # 3. Job Description provided -> missing JD skills
    jd = "Looking for candidate skilled in Python, FastAPI, Docker, and PostgreSQL"
    parsed_jd = parse_resume_dynamically(text, job_description=jd)
    assert "FastAPI" in parsed_jd["keyword_gaps"]
    assert "Docker" in parsed_jd["keyword_gaps"]
    assert "Python" not in parsed_jd["keyword_gaps"]


