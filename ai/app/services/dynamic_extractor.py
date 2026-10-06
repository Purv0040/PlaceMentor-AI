import re
import logging
from typing import Dict, Any, List, Optional, Tuple

from app.utils.tech_taxonomy import normalize_skill_name, TECH_TAXONOMY, ALIAS_LOOKUP

logger = logging.getLogger(__name__)

KNOWN_LANGUAGES = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", "PHP", "SQL",
    "R", "Go", "Rust", "Kotlin", "Swift", "Ruby", "Dart", "Bash", "Shell"
]

KNOWN_FRAMEWORKS = [
    "React", "React.js", "Node", "Node.js", "NodeJS", "Express", "FastAPI", "Flask",
    "Django", "Spring Boot", "Bootstrap", "Tailwind", "Vue", "Angular", "Next.js", "MERN Stack",
    "HTML", "CSS", "HTML/CSS"
]

KNOWN_LIBRARIES = [
    "NumPy", "Pandas", "Matplotlib", "Seaborn", "Scikit-learn", "TensorFlow",
    "PyTorch", "Keras", "OpenCV", "Transformers", "Hugging Face", "LangChain", "SciPy", "RAG", "FAISS", "Pinecone", "Chart.js"
]

KNOWN_TOOLS = [
    "Git", "GitHub", "GitLab", "Docker", "Kubernetes", "Excel", "Jupyter", "Jupyter Notebook",
    "PowerBI", "Postman", "VSCode", "VS Code", "Linux", "Unix", "AWS", "GCP", "Azure", "Vercel",
    "Netlify", "OCR", "Jira"
]

KNOWN_DATABASES = [
    "MySQL", "MongoDB", "PostgreSQL", "SQLite", "Redis", "Cassandra", "Oracle", "DynamoDB"
]

KNOWN_OTHER = [
    "Machine Learning", "Deep Learning", "ML", "Basic DL", "Data Analysis", "Data Science", "Computer Vision",
    "Natural Language Processing", "NLP", "Data Structures & Algorithms", "Data Structures", "Algorithms",
    "Web Scraping", "Artificial Intelligence", "Microservices", "REST API", "Basic OOP", "OOP",
    "Regression", "Classification", "Model Evaluation"
]


BULLET_MARKER_CHARS = {"•", "●", "○", "▪", "◦", "-", "*", "→", "➢", "▪️", "▶", "✦", "❖", "–", "—"}

BULLET_MARKER_REGEX = re.compile(
    r'^\s*(?:[•●○▪◦\-\*→➢▪️▶✦❖–—]|(?:\(?\d+[\.\)]|\d+\]|[a-zA-Z][\.\)]))\s+'
)

TECH_HEADER_REGEX = re.compile(
    r'^\s*(?:[•●○▪◦\-\*→➢▪️▶✦❖–—]|(?:\(?\d+[\.\)]|\d+\]|[a-zA-Z][\.\)]))?\s*(?:TECH\s*STACK|TECHNOLOGY\s*STACK|TECHNOLOGIES\s*USED|TECHNOLOGIES|TOOLS\s*USED|TOOLS|STACK|KEY\s*TECHNOLOGIES|TECH\s*USED)\s*[:\-]\s*(.*)',
    re.IGNORECASE
)

ACTION_VERBS = {
    "developed", "implemented", "stored", "used", "built", "added", "created",
    "designed", "integrated", "engineered", "spearheaded", "collaborated",
    "architected", "managed", "lead", "optimized", "crafted", "deployed",
    "configured", "tested", "utilizing", "utilized", "constructed", "formulated",
    "leveraged", "maintained", "automated", "orchestrated", "retrieved"
}

NOISE_PROJECT_HEADERS = {
    "BULLETS:", "BULLETS", "KEY FEATURES:", "KEY FEATURES", "RESPONSIBILITIES:",
    "KEY RESPONSIBILITIES:", "OVERVIEW:", "DESCRIPTION:", "PROJECT 1:", "PROJECT 2:",
    "PROJECT 3:", "PROJECT 4:", "PROJECT 5:"
}


def parse_tech_stack_string(tech_str: str) -> List[str]:
    """Parse raw tech stack text into normalized technology tokens."""
    if not tech_str or not tech_str.strip():
        return []
    
    raw_tokens = re.split(r'[,;\|&]+', tech_str)
    tokens = []
    
    for token in raw_tokens:
        token = token.strip()
        if not token:
            continue
        
        # Handle slash-separated techs e.g., "Node.js/Flask" or "MySQL/MongoDB"
        if "/" in token and token.upper() not in ["CI/CD", "HTML/CSS", "C/C++", "PL/SQL"]:
            sub_parts = [p.strip() for p in token.split("/") if p.strip()]
            for sub in sub_parts:
                canonical, _ = normalize_skill_name(sub)
                if canonical and canonical not in tokens:
                    tokens.append(canonical)
        else:
            canonical, _ = normalize_skill_name(token)
            if canonical and canonical not in tokens:
                tokens.append(canonical)
                
    return tokens


def extract_skills_from_text(text: str) -> Dict[str, List[str]]:
    """Dynamically scan text for known technologies and return normalized categorized skills."""
    if not text:
        return {"languages": [], "frameworks": [], "libraries": [], "tools": [], "other": []}

    text_lower = text.lower()
    
    extracted_languages = set()
    for lang in KNOWN_LANGUAGES:
        pattern = r'\b' + re.escape(lang.lower()) + (r'\b' if lang[-1].isalnum() else r'(?!\w)')
        if re.search(pattern, text_lower):
            canonical, _ = normalize_skill_name(lang)
            extracted_languages.add(canonical)
            
    extracted_frameworks = set()
    for fw in KNOWN_FRAMEWORKS:
        pattern = r'\b' + re.escape(fw.lower()) + (r'\b' if fw[-1].isalnum() else r'(?!\w)')
        if re.search(pattern, text_lower):
            canonical, _ = normalize_skill_name(fw)
            extracted_frameworks.add(canonical)

    extracted_libraries = set()
    for lib in KNOWN_LIBRARIES:
        pattern = r'\b' + re.escape(lib.lower()) + (r'\b' if lib[-1].isalnum() else r'(?!\w)')
        if re.search(pattern, text_lower):
            canonical, _ = normalize_skill_name(lib)
            extracted_libraries.add(canonical)
            
    extracted_tools = set()
    for tool in KNOWN_TOOLS:
        pattern = r'\b' + re.escape(tool.lower()) + (r'\b' if tool[-1].isalnum() else r'(?!\w)')
        if re.search(pattern, text_lower):
            canonical, _ = normalize_skill_name(tool)
            extracted_tools.add(canonical)

    extracted_other = set()
    for db in KNOWN_DATABASES:
        pattern = r'\b' + re.escape(db.lower()) + (r'\b' if db[-1].isalnum() else r'(?!\w)')
        if re.search(pattern, text_lower):
            canonical, _ = normalize_skill_name(db)
            extracted_other.add(canonical)
            
    for oth in KNOWN_OTHER:
        pattern = r'\b' + re.escape(oth.lower()) + (r'\b' if oth[-1].isalnum() else r'(?!\w)')
        if re.search(pattern, text_lower):
            canonical, _ = normalize_skill_name(oth)
            extracted_other.add(canonical)
            
    return {
        "languages": sorted(list(extracted_languages)),
        "frameworks": sorted(list(extracted_frameworks)),
        "libraries": sorted(list(extracted_libraries)),
        "tools": sorted(list(extracted_tools)),
        "other": sorted(list(extracted_other)),
    }


def parse_resume_sections(text: str) -> Dict[str, List[str]]:
    """Split resume text into sections based on standard section headings."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    sections: Dict[str, List[str]] = {
        "header": [],
        "education": [],
        "experience": [],
        "projects": [],
        "skills": [],
        "certifications": [],
        "achievements": [],
        "summary": [],
        "other": []
    }
    
    current_section = "header"
    
    section_keywords = {
        "education": ["education", "academic background", "academic qualifications", "qualification", "qualifications", "academics"],
        "experience": ["work experience", "experience", "employment", "employment history", "internships", "internship", "work history", "professional experience"],
        "projects": ["projects", "project", "personal projects", "key projects", "academic projects", "featured projects", "technical projects"],
        "skills": ["skills", "technical skills", "skills & tools", "domain skills", "technical proficiency", "core competencies", "technologies", "skills and expertise"],
        "certifications": ["certifications", "certification", "certificates", "courses", "licenses & certifications", "certifications & training"],
        "achievements": ["achievements", "awards", "honors", "accomplishments", "awards & achievements", "honors & awards"],
        "summary": ["profile", "summary", "executive summary", "career objective", "objective", "about me", "professional summary"],
        "other": ["publications", "research", "extra-curricular", "extracurricular", "activities", "volunteer", "leadership", "positions of responsibility"]
    }
    
    for line in lines:
        if line.upper().startswith("--- PAGE"):
            continue
            
        line_clean = line.upper().strip(" :-_➢*•#")
        matched_section = None
        
        # Match heading if short line (heading length <= 45) or exact keyword
        if len(line_clean) <= 45:
            for sec_name, keywords in section_keywords.items():
                if any(line_clean == kw.upper() or line_clean.startswith(kw.upper() + " ") or line_clean.startswith(kw.upper() + ":") for kw in keywords):
                    matched_section = sec_name
                    break
                
        if matched_section:
            current_section = matched_section
            continue
            
        sections[current_section].append(line)
        
    return sections


def extract_education(edu_lines: List[str], full_text: str) -> List[Dict[str, Any]]:
    """Dynamically parse education items from resume lines, merging institution and degree into single items."""
    lines_to_search = [l.strip() for l in (edu_lines if edu_lines else full_text.split("\n")) if l.strip() and not l.strip().upper().startswith("--- PAGE")]
    
    if not lines_to_search:
        return []

    degree_keywords = [
        "B.TECH", "B.E.", "B.S.", "B.SC", "BACHELOR", "M.TECH", "M.S.", "M.SC", "MASTER",
        "DIPLOMA", "HSC", "SSC", "DEGREE", "PH.D", "DOCTORATE", "HIGH SCHOOL", "SECONDARY",
        "12TH", "10TH", "BCA", "MCA"
    ]
    inst_keywords = [
        "UNIVERSITY", "COLLEGE", "INSTITUTE", "SCHOOL", "ACADEMY", "SANKUL", "CHARUSAT", "CSPIT", "IIT", "NIT", "BITS"
    ]

    items = []
    current_item: Dict[str, Any] = {}

    def flush_item():
        nonlocal current_item
        if current_item and ("degree" in current_item or "institution" in current_item):
            deg = current_item.get("degree", "")
            inst = current_item.get("institution", "")
            if not inst and "(" in deg and ")" in deg:
                paren_match = re.search(r'\((.*?)\)', deg)
                if paren_match:
                    possible_inst = paren_match.group(1).strip()
                    if any(k in possible_inst.upper() for k in inst_keywords) or len(possible_inst) <= 15:
                        current_item["institution"] = possible_inst
                        current_item["degree"] = deg.replace(f"({possible_inst})", "").strip(" :-_")
            
            if current_item.get("gpa") and "degree" in current_item:
                gpa_str = current_item["gpa"]
                current_item["degree"] = re.sub(r'[\s\|]*' + re.escape(gpa_str), '', current_item["degree"]).strip(" |:-_")
                
            items.append(current_item)
            current_item = {}

    for line in lines_to_search:
        upper = line.upper()
        
        gpa_match = re.search(r'\b(?:CGPA|GPA|SPI|CPI)\s*[:\-]?\s*([0-9\.\/\s]+)', line, re.IGNORECASE)
        if not gpa_match:
            gpa_match = re.search(r'\b(?:[0-9]\.[0-9]{1,2}\s*/\s*10(?:\.00)?|[0-9]{2,3}(?:\.[0-9]{1,2})?\s*%)', line)
            
        gpa_val = gpa_match.group(0).strip() if gpa_match else None

        date_match = re.search(r'\b(20\d{2}\s*[\-\–\—\to]+\s*(20\d{2}|PRESENT|CURRENT)|(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[a-z]*\s+20\d{2})\b', line, re.IGNORECASE)
        date_val = date_match.group(0).strip() if date_match else None

        parts = [p.strip() for p in re.split(r'[\|\–\—]', line) if p.strip()]
        has_deg_part = any(any(k in p.upper() for k in degree_keywords) for p in parts)
        has_inst_part = any(any(k in p.upper() for k in inst_keywords) for p in parts)

        if len(parts) >= 2 and (has_deg_part and has_inst_part):
            flush_item()
            inst_val = None
            deg_val = None
            for p in parts:
                p_upper = p.upper()
                if any(k in p_upper for k in inst_keywords) and not inst_val:
                    inst_val = p
                elif any(k in p_upper for k in degree_keywords) and not deg_val:
                    deg_val = p
                elif not deg_val and ("GSEB" in p_upper or "CBSE" in p_upper or "BOARD" in p_upper):
                    deg_val = p
            
            if inst_val or deg_val:
                current_item = {
                    "institution": inst_val or parts[0],
                    "degree": deg_val or (parts[1] if len(parts) > 1 else parts[0]),
                }
                if gpa_val:
                    current_item["gpa"] = gpa_val
                if date_val:
                    current_item["graduation_date"] = date_val
                continue

        is_inst = any(k in upper for k in inst_keywords)
        is_deg = any(k in upper for k in degree_keywords)

        if is_deg:
            if "degree" in current_item:
                flush_item()
            if gpa_val:
                current_item["degree"] = re.sub(r'[\s\|]*' + re.escape(gpa_val), '', line).strip(" |:-_")
                current_item["gpa"] = gpa_val
            else:
                current_item["degree"] = line
            if date_val:
                current_item["graduation_date"] = date_val
        elif is_inst:
            if ("institution" in current_item and "degree" in current_item) or ("degree" in current_item and ("gpa" in current_item or "(" in current_item.get("degree", ""))):
                flush_item()
            current_item["institution"] = line
            if gpa_val:
                current_item["gpa"] = gpa_val
            if date_val:
                current_item["graduation_date"] = date_val
        elif (gpa_val or date_val) and current_item:
            if gpa_val:
                current_item["gpa"] = gpa_val
            if date_val:
                current_item["graduation_date"] = date_val

    flush_item()

    final_edu = []
    for item in items:
        inst = item.get("institution")
        deg = item.get("degree")
        if not inst and deg:
            inst = deg
        elif not deg and inst:
            deg = inst
            
        final_edu.append({
            "institution": inst or "University / School",
            "degree": deg or "Degree / Certificate",
            "graduation_date": item.get("graduation_date"),
            "gpa": item.get("gpa")
        })

    return final_edu


def extract_experience(exp_lines: List[str]) -> List[Dict[str, Any]]:
    """Dynamically parse work experience items."""
    if not exp_lines:
        return []
        
    experiences = []
    current_exp = None
    
    for line in exp_lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        is_bullet = bool(BULLET_MARKER_REGEX.match(line_str))
        
        if not is_bullet and ("INTERN" in line_str.upper() or "DEVELOPER" in line_str.upper() or "ENGINEER" in line_str.upper() or "ANALYST" in line_str.upper() or " AT " in line_str.upper() or "MANAGER" in line_str.upper() or "LEAD" in line_str.upper()):
            if current_exp:
                experiences.append(current_exp)
                
            role = line_str
            company = line_str
            duration = None
            
            if "(" in line_str and ")" in line_str:
                dur_match = re.search(r'\((.*?)\)', line_str)
                if dur_match:
                    duration = dur_match.group(1)
                    line_str = line_str.replace(f"({duration})", "").strip()
                    
            if " AT " in line_str.upper():
                parts = re.split(r'\s+at\s+', line_str, flags=re.IGNORECASE)
                role = parts[0].strip()
                company = parts[1].strip() if len(parts) > 1 else role
                
            current_exp = {
                "company": company,
                "role": role,
                "duration": duration,
                "bullets": []
            }
        elif current_exp and is_bullet:
            bullet_clean = BULLET_MARKER_REGEX.sub('', line_str).strip()
            if bullet_clean:
                current_exp["bullets"].append(bullet_clean)
        elif current_exp and current_exp["bullets"] and not is_bullet:
            current_exp["bullets"][-1] += " " + line_str
                
    if current_exp:
        experiences.append(current_exp)
        
    return experiences


def check_has_metrics(text: str) -> bool:
    """Detect if text contains quantifiable metrics (percentages, counts, currency, throughput, time, etc.)."""
    if not text:
        return False
    metric_regex = re.compile(
        r'\b(?:\d+%\b|\d+\s*(?:users|members|records|seconds|ms|fps|x|times|k|mb|gb|tb|rows|customers|clients|requests|throughput)\b|\$\d+|\₹\d+|\d+x\b|\d+\+\s*(?:users|records|members|tasks)\b)',
        re.IGNORECASE
    )
    return bool(metric_regex.search(text))


def extract_projects(proj_lines: List[str]) -> List[Dict[str, Any]]:
    """Dynamically parse project items using section boundaries, bullet markers, and tech stack detection."""
    if not proj_lines:
        return []
        
    projects = []
    current_proj: Optional[Dict[str, Any]] = None
    expecting_tech_list = False
    
    def finalize_project(proj: Optional[Dict[str, Any]]) -> None:
        if not proj:
            return
        clean_name = re.sub(r'^PROJECT\s*\d+\s*[:\-]?\s*', '', proj["name"], flags=re.IGNORECASE).strip()
        if clean_name:
            proj["name"] = clean_name
        if proj["bullets"] and not proj["description"]:
            proj["description"] = proj["bullets"][0]
            
        if not proj["technologies"]:
            extracted = set()
            for b in proj["bullets"]:
                sk = extract_skills_from_text(b)
                for cat in ["languages", "frameworks", "libraries", "tools", "other"]:
                    for item in sk.get(cat, []):
                        extracted.add(item)
            proj["technologies"] = sorted(list(extracted))

        all_bullets_text = " ".join(proj["bullets"])
        proj["has_metrics"] = check_has_metrics(all_bullets_text)
        
        if proj["name"] and proj["name"] not in BULLET_MARKER_CHARS and proj["name"].upper() not in NOISE_PROJECT_HEADERS and proj["name"].upper().rstrip(":") not in NOISE_PROJECT_HEADERS:
            projects.append(proj)

    for line in proj_lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        if line_str in BULLET_MARKER_CHARS or line_str.strip(" :-_➢*•#●○▪◦→") == "":
            continue

        upper_line = line_str.upper()
        if upper_line in NOISE_PROJECT_HEADERS or upper_line.rstrip(":") in NOISE_PROJECT_HEADERS:
            continue

        if line_str.startswith("(") and line_str.endswith(")"):
            if current_proj is not None:
                if current_proj["description"]:
                    current_proj["description"] += " " + line_str
                else:
                    current_proj["description"] = line_str
            continue

        tech_match = TECH_HEADER_REGEX.match(line_str)
        if tech_match or expecting_tech_list:
            if tech_match:
                tech_content = tech_match.group(1).strip()
                if tech_content:
                    extracted_techs = parse_tech_stack_string(tech_content)
                    if current_proj is not None:
                        for t in extracted_techs:
                            if t not in current_proj["technologies"]:
                                current_proj["technologies"].append(t)
                    expecting_tech_list = False
                else:
                    expecting_tech_list = True
                continue
            elif expecting_tech_list:
                extracted_techs = parse_tech_stack_string(line_str)
                if current_proj is not None:
                    for t in extracted_techs:
                        if t not in current_proj["technologies"]:
                            current_proj["technologies"].append(t)
                expecting_tech_list = False
                continue

        is_bullet = bool(BULLET_MARKER_REGEX.match(line_str))
        bullet_clean = BULLET_MARKER_REGEX.sub('', line_str).strip()
        first_word = bullet_clean.split()[0].lower() if bullet_clean else ""

        if is_bullet or (first_word in ACTION_VERBS and current_proj is not None):
            expecting_tech_list = False
            if bullet_clean and bullet_clean not in BULLET_MARKER_CHARS:
                if current_proj is None:
                    current_proj = {
                        "name": "Project",
                        "description": None,
                        "technologies": [],
                        "bullets": [],
                        "has_metrics": False
                    }
                current_proj["bullets"].append(bullet_clean)
                bullet_techs = extract_skills_from_text(bullet_clean)
                for cat in ["languages", "frameworks", "libraries", "tools", "other"]:
                    for t in bullet_techs.get(cat, []):
                        if t not in current_proj["technologies"]:
                            current_proj["technologies"].append(t)
            continue

        expecting_tech_list = False
        if current_proj is None:
            current_proj = {
                "name": line_str,
                "description": None,
                "technologies": [],
                "bullets": [],
                "has_metrics": False
            }
        else:
            is_continuation = False
            if line_str[0].islower() or line_str.startswith(("tasks.", "application.", "system.", "and", "or", "to", "with", "for", "in", "by", "from", "logic.", "dashboards.", "recommendations.")):
                is_continuation = True
                
            if current_proj["bullets"] and (is_continuation or not current_proj["bullets"][-1].endswith(('.', '!', '?')) or len(line_str) > 120 or line_str[0].islower()):
                current_proj["bullets"][-1] += " " + line_str
            else:
                finalize_project(current_proj)
                current_proj = {
                    "name": line_str,
                    "description": None,
                    "technologies": [],
                    "bullets": [],
                    "has_metrics": False
                }
                
    if current_proj:
        finalize_project(current_proj)
        
    return projects


def extract_certifications(cert_lines: List[str], full_text: Optional[str] = None) -> List[str]:
    """Dynamically parse certification lines, filtering out section headers."""
    lines_to_search = cert_lines[:]
    
    # Fallback search if cert_lines empty
    if not lines_to_search and full_text:
        in_cert = False
        for l in full_text.split("\n"):
            l_str = l.strip()
            l_clean = l_str.upper().strip(" :-_➢*•#")
            if "CERTIFICATION" in l_clean or "CERTIFICATE" in l_clean:
                in_cert = True
                continue
            elif in_cert and len(l_clean) <= 35 and any(h in l_clean for h in ["PROJECT", "SKILL", "EDUCATION", "EXPERIENCE", "PROFILE", "ACHIEVEMENT", "PUBLICATIONS"]):
                break
            elif in_cert and l_str:
                lines_to_search.append(l_str)

    certs = []
    ignored_headers = {
        "PROFILE", "SUMMARY", "OBJECTIVE", "EDUCATION", "EXPERIENCE", "WORK EXPERIENCE",
        "INTERNSHIP", "SKILLS", "PROJECTS", "CERTIFICATIONS", "ACHIEVEMENTS", "PUBLICATIONS",
        "EXTRA-CURRICULAR", "LEADERSHIP", "HEADER", "OTHER"
    }
    for line in lines_to_search:
        clean = BULLET_MARKER_REGEX.sub('', line).strip()
        if not clean or clean.upper().startswith("--- PAGE"):
            continue
        clean_header = clean.upper().strip(" :-_➢*•#")
        if clean_header in ignored_headers or clean_header.rstrip(":") in ignored_headers:
            continue
        if clean not in certs:
            certs.append(clean)
    return certs


def extract_achievements(achieve_lines: List[str]) -> List[str]:
    """Dynamically parse achievement lines."""
    achievements = []
    for line in achieve_lines:
        clean = BULLET_MARKER_REGEX.sub('', line).strip()
        if clean:
            achievements.append(clean)
    return achievements


def parse_resume_dynamically(
    resume_text: str,
    target_role: Optional[str] = None,
    job_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main dynamic parser that parses raw resume text into structured findings matching LLMResumeExtraction schema.
    """
    if "Return ONLY valid JSON" in resume_text:
        resume_text = resume_text.split("Return ONLY valid JSON")[0]
        
    sections = parse_resume_sections(resume_text)
    
    # Global skills primarily from actual SKILLS section if present
    if sections.get("skills"):
        skills_source_text = "\n".join(sections["skills"])
        skills = extract_skills_from_text(skills_source_text)
    else:
        skills = extract_skills_from_text(resume_text)
        
    education = extract_education(sections["education"], resume_text)
    experience = extract_experience(sections["experience"])
    projects = extract_projects(sections["projects"])
    certifications = extract_certifications(sections["certifications"], full_text=resume_text)
    achievements = extract_achievements(sections["achievements"])
    
    missing_sections = []
    if not education:
        missing_sections.append("Education")
    if not experience:
        missing_sections.append("Experience")
    if not projects:
        missing_sections.append("Projects")
    if not certifications:
        missing_sections.append("Certifications")
        
    all_bullets = []
    for exp in experience:
        all_bullets.extend(exp.get("bullets", []))
    for proj in projects:
        all_bullets.extend(proj.get("bullets", []))
        
    weak_bullets = []
    for bullet in all_bullets:
        if len(bullet) < 30 or not check_has_metrics(bullet):
            weak_bullets.append({
                "original_bullet": bullet,
                "issues": ["missing quantifiable metrics or outcome indicators"],
                "suggestion": f"Quantify the impact of this achievement (e.g., 'improved performance by X%').",
                "evidence_used": [bullet[:50]]
            })
            
    generic_catalog = ["hard worker", "team player", "self motivated", "result oriented", "detail oriented", "fast learner"]
    generic_found = [phrase for phrase in generic_catalog if phrase in resume_text.lower()]

    # Role/JD aware keyword gaps calculation
    all_extracted_skills = set(skills.get("languages", []) + skills.get("frameworks", []) + skills.get("libraries", []) + skills.get("tools", []) + skills.get("other", []))
    keyword_gaps = []
    if job_description:
        jd_skills = extract_skills_from_text(job_description)
        all_jd = set(jd_skills.get("languages", []) + jd_skills.get("frameworks", []) + jd_skills.get("libraries", []) + jd_skills.get("tools", []) + jd_skills.get("other", []))
        keyword_gaps = [s for s in sorted(list(all_jd)) if s not in all_extracted_skills]
    elif target_role:
        role_map = {
            "AI Engineer": ["PyTorch", "TensorFlow", "Transformers", "LLMs", "RAG", "MLOps"],
            "ML Engineer": ["PyTorch", "TensorFlow", "Transformers", "MLOps", "Scikit-learn"],
            "Data Scientist": ["Pandas", "NumPy", "Scikit-learn", "Statistics", "SQL"],
            "Backend Developer": ["FastAPI", "REST API", "Docker", "Redis", "PostgreSQL"],
            "Frontend Developer": ["React", "Next.js", "TypeScript", "Tailwind CSS"],
            "Software Engineer": ["Data Structures & Algorithms", "System Design", "Git", "Unit Testing"]
        }
        expected = role_map.get(target_role, ["Unit Testing", "System Design"])
        keyword_gaps = [s for s in expected if s not in all_extracted_skills]
    
    return {
        "skills": skills,
        "education": education,
        "experience": experience,
        "projects": projects,
        "certifications": certifications,
        "achievements": achievements,
        "missing_sections": missing_sections,
        "weak_bullets": weak_bullets[:3],
        "repeated_words": [],
        "generic_phrases": generic_found,
        "keyword_gaps": keyword_gaps
    }


