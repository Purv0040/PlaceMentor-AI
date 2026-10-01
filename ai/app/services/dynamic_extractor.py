import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

KNOWN_LANGUAGES = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", "PHP", "SQL",
    "HTML", "CSS", "R", "Go", "Rust", "Kotlin", "Swift", "Ruby", "Dart", "Bash", "Shell"
]

KNOWN_FRAMEWORKS = [
    "React", "React.js", "Node", "Node.js", "NodeJS", "Express", "FastAPI", "Flask",
    "Django", "NumPy", "Pandas", "Matplotlib", "Seaborn", "Scikit-learn", "TensorFlow",
    "PyTorch", "Keras", "Spring Boot", "Bootstrap", "Tailwind", "RAG", "FAISS", "Pinecone",
    "LLM", "HuggingFace", "Transformers", "OpenCV", "Vue", "Angular", "Next.js", "MERN Stack"
]

KNOWN_TOOLS = [
    "Git", "GitHub", "GitLab", "Docker", "Kubernetes", "Excel", "Jupyter", "Jupyter Notebook",
    "PowerBI", "Postman", "VSCode", "Linux", "Unix", "AWS", "GCP", "Azure", "Vercel",
    "Netlify", "OCR", "Jira"
]

KNOWN_DATABASES = [
    "MySQL", "MongoDB", "PostgreSQL", "SQLite", "Redis", "Cassandra", "Oracle", "DynamoDB"
]

KNOWN_OTHER = [
    "Machine Learning", "Deep Learning", "Data Analysis", "Data Science", "Computer Vision",
    "Natural Language Processing", "NLP", "Data Structures", "Algorithms", "Web Scraping",
    "Artificial Intelligence", "Microservices", "REST API"
]


def extract_skills_from_text(text: str) -> Dict[str, List[str]]:
    """Dynamically scan text for known technologies and categorized skills."""
    text_lower = text.lower()
    
    extracted_languages = set()
    for lang in KNOWN_LANGUAGES:
        pattern = r'\b' + re.escape(lang.lower()) + r'\b'
        if re.search(pattern, text_lower):
            extracted_languages.add(lang)
            
    extracted_frameworks = set()
    for fw in KNOWN_FRAMEWORKS:
        pattern = r'\b' + re.escape(fw.lower()) + r'\b'
        if re.search(pattern, text_lower):
            extracted_frameworks.add(fw)
            
    extracted_tools = set()
    for tool in KNOWN_TOOLS:
        pattern = r'\b' + re.escape(tool.lower()) + r'\b'
        if re.search(pattern, text_lower):
            extracted_tools.add(tool)

    extracted_other = set()
    for db in KNOWN_DATABASES:
        pattern = r'\b' + re.escape(db.lower()) + r'\b'
        if re.search(pattern, text_lower):
            extracted_other.add(db)
            
    for oth in KNOWN_OTHER:
        pattern = r'\b' + re.escape(oth.lower()) + r'\b'
        if re.search(pattern, text_lower):
            extracted_other.add(oth)
            
    return {
        "languages": sorted(list(extracted_languages)),
        "frameworks": sorted(list(extracted_frameworks)),
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
        "other": []
    }
    
    current_section = "header"
    
    section_keywords = {
        "education": ["education", "academic background", "qualification"],
        "experience": ["work experience", "experience", "employment", "internships", "internship"],
        "projects": ["projects", "personal projects", "key projects", "academic projects"],
        "skills": ["skills", "technical skills", "skills & tools", "domain skills"],
        "certifications": ["certifications", "certificates", "courses"],
        "achievements": ["achievements", "awards", "honors", "accomplishments"]
    }
    
    for line in lines:
        line_clean = line.upper().strip(" :-_➢*•#")
        matched_section = None
        for sec_name, keywords in section_keywords.items():
            if any(line_clean == kw.upper() or line_clean.startswith(kw.upper() + " ") for kw in keywords):
                matched_section = sec_name
                break
                
        if matched_section:
            current_section = matched_section
            continue
            
        sections[current_section].append(line)
        
    return sections


def extract_education(edu_lines: List[str], full_text: str) -> List[Dict[str, Any]]:
    """Dynamically parse education items from resume lines."""
    results = []
    current_item = {}
    lines_to_search = edu_lines if edu_lines else full_text.split("\n")
    
    for line in lines_to_search:
        line_str = line.strip()
        if not line_str or line_str.upper().startswith("--- PAGE"):
            continue
            
        is_degree = any(deg in line_str.upper() for deg in ["B.TECH", "B.E.", "B.S.", "B.SC", "M.TECH", "M.S.", "HSC", "SSC", "DIPLOMA", "BACHELOR", "MASTER", "DEGREE"])
        is_gpa = any(g in line_str.upper() for g in ["CGPA", "GPA", "%", "PERCENT"])
        
        if is_degree or ("UNIVERSITY" in line_str.upper() or "COLLEGE" in line_str.upper() or "SCHOOL" in line_str.upper() or "INSTITUTE" in line_str.upper() or "SANKUL" in line_str.upper()):
            if current_item and ("degree" in current_item or "institution" in current_item):
                results.append(current_item)
                current_item = {}
                
            parts = [p.strip() for p in line_str.split(",") if p.strip()]
            if len(parts) >= 2:
                current_item["degree"] = parts[0]
                current_item["institution"] = ", ".join(parts[1:])
            else:
                current_item["degree"] = line_str
                current_item["institution"] = line_str
                
        elif is_gpa and current_item:
            current_item["gpa"] = line_str
        elif is_gpa and not current_item and results:
            results[-1]["gpa"] = line_str
            
    if current_item and ("degree" in current_item or "institution" in current_item):
        results.append(current_item)
        
    final_edu = []
    for item in results:
        final_edu.append({
            "institution": item.get("institution", item.get("degree", "University / School")),
            "degree": item.get("degree", "Degree / Certificate"),
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
            
        is_bullet = line_str.startswith("➢") or line_str.startswith("-") or line_str.startswith("*") or line_str.startswith("•")
        
        if not is_bullet and ("INTERN" in line_str.upper() or "DEVELOPER" in line_str.upper() or "ENGINEER" in line_str.upper() or "ANALYST" in line_str.upper() or "AT " in line_str.upper() or "MANAGER" in line_str.upper()):
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
            bullet_clean = line_str.lstrip("➢-*• ").strip()
            if bullet_clean:
                current_exp["bullets"].append(bullet_clean)
        elif current_exp and current_exp["bullets"] and not is_bullet:
            current_exp["bullets"][-1] += " " + line_str
                
    if current_exp:
        experiences.append(current_exp)
        
    return experiences


def extract_projects(proj_lines: List[str]) -> List[Dict[str, Any]]:
    """Dynamically parse project items."""
    if not proj_lines:
        return []
        
    projects = []
    current_proj = None
    
    for line in proj_lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        is_bullet = line_str.startswith("➢") or line_str.startswith("-") or line_str.startswith("*") or line_str.startswith("•")
        is_tech = line_str.upper().startswith("TECHNOLOGIES:") or line_str.upper().startswith("TECH STACK:") or line_str.upper().startswith("STACK:")
        
        if is_tech and current_proj:
            tech_str = line_str.split(":", 1)[-1].strip()
            current_proj["technologies"] = [t.strip() for t in tech_str.split(",") if t.strip()]
        elif is_bullet and current_proj:
            bullet_clean = line_str.lstrip("➢-*• ").strip()
            if bullet_clean:
                current_proj["bullets"].append(bullet_clean)
                if any(char.isdigit() for char in bullet_clean) or "%" in bullet_clean:
                    current_proj["has_metrics"] = True
        elif current_proj and current_proj["bullets"] and not is_tech and not is_bullet:
            current_proj["bullets"][-1] += " " + line_str
            if any(char.isdigit() for char in line_str) or "%" in line_str:
                current_proj["has_metrics"] = True
        elif not is_bullet and not is_tech:
            if current_proj:
                projects.append(current_proj)
                
            current_proj = {
                "name": line_str,
                "description": line_str,
                "technologies": [],
                "bullets": [],
                "has_metrics": False
            }
                    
    if current_proj:
        projects.append(current_proj)
        
    return projects


def extract_certifications(cert_lines: List[str]) -> List[str]:
    """Dynamically parse certification lines."""
    certs = []
    for line in cert_lines:
        clean = line.lstrip("➢-*• ").strip()
        if clean:
            certs.append(clean)
    return certs


def extract_achievements(achieve_lines: List[str]) -> List[str]:
    """Dynamically parse achievement lines."""
    achievements = []
    for line in achieve_lines:
        clean = line.lstrip("➢-*• ").strip()
        if clean:
            achievements.append(clean)
    return achievements


def parse_resume_dynamically(resume_text: str) -> Dict[str, Any]:
    """
    Main dynamic parser that parses raw resume text into structured findings matching LLMResumeExtraction schema.
    """
    if "Return ONLY valid JSON" in resume_text:
        resume_text = resume_text.split("Return ONLY valid JSON")[0]
        
    sections = parse_resume_sections(resume_text)
    
    skills = extract_skills_from_text(resume_text)
    education = extract_education(sections["education"], resume_text)
    experience = extract_experience(sections["experience"])
    projects = extract_projects(sections["projects"])
    certifications = extract_certifications(sections["certifications"])
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
        
    # Weak bullets analysis on extracted bullet points
    all_bullets = []
    for exp in experience:
        all_bullets.extend(exp.get("bullets", []))
    for proj in projects:
        all_bullets.extend(proj.get("bullets", []))
        
    weak_bullets = []
    for bullet in all_bullets:
        if len(bullet) < 30 or not any(char.isdigit() for char in bullet):
            weak_bullets.append({
                "original_bullet": bullet,
                "issues": ["missing quantifiable metrics or outcome indicators"],
                "suggestion": f"Quantify the impact of this achievement (e.g., 'improved performance by X%').",
                "evidence_used": [bullet[:50]]
            })
            
    # Generic phrases check
    generic_catalog = ["hard worker", "team player", "self motivated", "result oriented", "detail oriented", "fast learner"]
    generic_found = [phrase for phrase in generic_catalog if phrase in resume_text.lower()]
    
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
        "keyword_gaps": ["Docker", "Kubernetes", "CI/CD"] if "docker" not in resume_text.lower() else ["Unit Testing", "System Design"]
    }
