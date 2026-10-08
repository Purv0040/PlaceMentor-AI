"""
Comprehensive 90-Day Role-Specific Curriculum Knowledge Base and Blueprint Generator.
Provides structured, progressive, and highly personalized curricula across technical domains:
- Cybersecurity Analyst & Engineer
- AI/ML Engineer
- Backend Developer
- Full Stack Developer
- Frontend Developer
- Data Scientist
- Data Analyst
- Data Engineer
- Cloud Engineer
- DevOps Engineer
- QA / Test Engineer
- Mobile App Developer
- Software Engineer / Custom Roles
"""
from typing import Any, Dict, List, Optional, Tuple


ROLE_DOMAIN_MAP: Dict[str, str] = {
    # Cybersecurity
    "cybersecurity analyst": "cybersecurity",
    "cybersecurity analyst & engineer": "cybersecurity",
    "cybersecurity engineer": "cybersecurity",
    "cyber security analyst": "cybersecurity",
    "cyber security engineer": "cybersecurity",
    "cyber security analyst & engineer": "cybersecurity",
    "security analyst": "cybersecurity",
    "security engineer": "cybersecurity",
    "information security analyst": "cybersecurity",
    "soc analyst": "cybersecurity",
    "penetration tester": "cybersecurity",
    
    # AI / ML
    "ai/ml engineer": "aiml",
    "ai engineer": "aiml",
    "ml engineer": "aiml",
    "machine learning engineer": "aiml",
    "deep learning engineer": "aiml",
    "nlp engineer": "aiml",
    "computer vision engineer": "aiml",
    
    # Backend
    "backend developer": "backend",
    "backend engineer": "backend",
    "python backend developer": "backend",
    "java backend developer": "backend",
    "node.js backend developer": "backend",
    "api developer": "backend",
    
    # Frontend
    "frontend developer": "frontend",
    "frontend engineer": "frontend",
    "react developer": "frontend",
    "ui engineer": "frontend",
    
    # Full Stack
    "full stack developer": "fullstack",
    "full stack engineer": "fullstack",
    "fullstack developer": "fullstack",
    "fullstack engineer": "fullstack",
    "mern developer": "fullstack",
    
    # Data Science & Analytics
    "data scientist": "data_science",
    "data analyst": "data_analyst",
    "business intelligence analyst": "data_analyst",
    "data engineer": "data_engineer",
    "big data engineer": "data_engineer",
    
    # Cloud & DevOps
    "cloud engineer": "cloud",
    "cloud architect": "cloud",
    "devops engineer": "devops",
    "site reliability engineer": "devops",
    "sre": "devops",
    
    # Mobile & QA & DB
    "mobile app developer": "mobile",
    "mobile developer": "mobile",
    "android developer": "mobile",
    "ios developer": "mobile",
    "qa / test engineer": "qa",
    "qa engineer": "qa",
    "test automation engineer": "qa",
    "sdet": "qa",
    "database engineer": "database",
    "database administrator": "database",
    
    # General SWE
    "software engineer": "software_engineer",
    "software developer": "software_engineer",
    "sde": "software_engineer",
    "swe": "software_engineer",
}


def resolve_role_domain(target_role: str) -> str:
    """Identifies the domain classification for a target role."""
    if not target_role:
        return "software_engineer"
    clean = target_role.strip().lower()
    
    if clean in ROLE_DOMAIN_MAP:
        return ROLE_DOMAIN_MAP[clean]
    
    # Keyword-based heuristics
    if any(k in clean for k in ["cyber", "security", "soc", "penetration", "threat", "siem", "vulnerability"]):
        return "cybersecurity"
    if any(k in clean for k in ["ai", "ml", "machine learning", "deep learning", "nlp", "vision"]):
        return "aiml"
    if any(k in clean for k in ["backend", "api", "microservice", "server", "fastapi", "spring", "django"]):
        return "backend"
    if any(k in clean for k in ["frontend", "react", "vue", "angular", "ui/ux", "web design"]):
        return "frontend"
    if any(k in clean for k in ["full stack", "fullstack", "mern", "mean"]):
        return "fullstack"
    if any(k in clean for k in ["data scientist", "ds"]):
        return "data_science"
    if any(k in clean for k in ["data analyst", "bi ", "business intelligence", "analytics"]):
        return "data_analyst"
    if any(k in clean for k in ["data engineer", "etl", "spark", "kafka", "pipeline"]):
        return "data_engineer"
    if any(k in clean for k in ["cloud", "aws", "azure", "gcp"]):
        return "cloud"
    if any(k in clean for k in ["devops", "sre", "reliability", "infrastructure", "kubernetes"]):
        return "devops"
    if any(k in clean for k in ["qa", "test", "quality", "sdet", "automation test"]):
        return "qa"
    if any(k in clean for k in ["mobile", "android", "ios", "flutter", "react native"]):
        return "mobile"
    if any(k in clean for k in ["database", "sql", "dba"]):
        return "database"
    
    return "software_engineer"


ROLE_RELEVANT_CATEGORIES_MAP: Dict[str, List[str]] = {
    "cybersecurity": ["Networking", "Security", "OS & Scripting", "CS Fundamentals", "Projects", "Resume", "GitHub", "Interview", "Communication"],
    "aiml": ["AI/ML", "Machine Learning", "Data Science", "Programming", "DevOps", "Projects", "Resume", "GitHub", "Interview", "DSA"],
    "backend": ["Backend", "Databases", "DevOps", "Programming", "DSA", "CS Fundamentals", "Projects", "Resume", "GitHub", "Interview"],
    "frontend": ["Frontend", "Programming", "Web Performance", "UI/UX", "Projects", "Resume", "GitHub", "Interview", "DSA"],
    "fullstack": ["Frontend", "Backend", "Databases", "DevOps", "Programming", "Projects", "Resume", "GitHub", "Interview", "DSA"],
    "data_science": ["Data Science", "AI/ML", "Databases", "Programming", "Projects", "Resume", "GitHub", "Interview"],
    "data_analyst": ["Data Science", "Databases", "Data Visualization", "Projects", "Resume", "GitHub", "Interview"],
    "data_engineer": ["Data Engineering", "Databases", "Backend", "DevOps", "Programming", "Projects", "Resume", "GitHub", "Interview"],
    "cloud": ["Cloud", "DevOps", "Networking", "Security", "Projects", "Resume", "GitHub", "Interview"],
    "devops": ["DevOps", "OS & Scripting", "Cloud", "Networking", "Projects", "Resume", "GitHub", "Interview"],
    "qa": ["Testing", "Programming", "Backend", "DevOps", "Projects", "Resume", "GitHub", "Interview"],
    "mobile": ["Mobile", "Frontend", "Backend", "Programming", "Projects", "Resume", "GitHub", "Interview"],
    "database": ["Databases", "Backend", "DevOps", "CS Fundamentals", "Projects", "Resume", "GitHub", "Interview"],
    "software_engineer": ["DSA", "CS Fundamentals", "Programming", "Backend", "Projects", "Resume", "GitHub", "Interview"],
}


def get_domain_categories(domain: str) -> List[str]:
    return ROLE_RELEVANT_CATEGORIES_MAP.get(domain, ROLE_RELEVANT_CATEGORIES_MAP["software_engineer"])


def get_role_phase_goals(target_role: str, domain: str, high_gaps: Optional[List[str]] = None) -> Tuple[str, str, str]:
    """Generates dynamic, highly specific phase goals for the target role."""
    gap_str = f" ({', '.join(high_gaps[:2])})" if high_gaps else ""
    
    if domain == "cybersecurity":
        p1 = f"Establish solid computer networking (TCP/IP, OSI), Linux security administration, cryptography fundamentals, SIEM log monitoring, and cybersecurity ATS profile setup for {target_role}."
        p2 = f"Master threat intelligence (MITRE ATT&CK), vulnerability management (Nessus/CVE), OWASP Top 10 web defenses, authentication protocols (OAuth/JWT), and build security portfolio projects{gap_str}."
        p3 = f"Master enterprise threat hunting, cloud security architecture (AWS/Azure IAM), incident response simulations, conduct mock SOC analyst technical interviews, and submit placement applications."
    elif domain == "aiml":
        p1 = f"Master Python for data engineering (NumPy, Pandas), linear algebra/statistics, classical machine learning foundations, and AI/ML ATS portfolio setup for {target_role}."
        p2 = f"Develop deep learning architectures (PyTorch/TensorFlow, CNNs, Transformers), model evaluation & validation metrics, MLOps tracking, and build an end-to-end predictive AI project{gap_str}."
        p3 = f"Master LLM/RAG pipelines, scalable ML system design, distributed model inference, conduct AI/ML technical mock interviews, and submit placement applications."
    elif domain == "backend":
        p1 = f"Master core language syntax & async programming, foundational DSA (Arrays, Hash Maps, Two Pointers), REST API architecture, and backend ATS resume setup for {target_role}."
        p2 = f"Develop robust web framework architectures (FastAPI/Express/Spring), database schema design & indexing (PostgreSQL), Redis caching, Docker containerization, and build a high-performance backend project{gap_str}."
        p3 = f"Master distributed System Design (scalability, microservices, message queues), high-concurrency benchmarks, live coding interviews, and submit backend placement applications."
    elif domain == "frontend":
        p1 = f"Master modern JavaScript/TypeScript, responsive CSS3 layout systems, core React component lifecycle & hooks, and frontend ATS portfolio setup for {target_role}."
        p2 = f"Develop advanced state management (Redux/Zustand), Next.js SSR architecture, web performance optimization (Core Web Vitals), and build a production-grade web application{gap_str}."
        p3 = f"Master frontend system design, accessibility (WCAG), live UI coding challenges, conduct frontend technical mock interviews, and submit job applications."
    elif domain == "fullstack":
        p1 = f"Master full stack core languages (JavaScript/TypeScript/Python), foundational DSA, RESTful API principles, responsive UI basics, and ATS portfolio setup for {target_role}."
        p2 = f"Develop end-to-end full stack architecture (React frontend + Node/FastAPI backend), PostgreSQL database modeling, Docker containerization, and build a production full stack portfolio project{gap_str}."
        p3 = f"Master full stack system design, authentication/authorization pipelines, cloud deployment (CI/CD), conduct full stack mock interviews, and submit placement applications."
    elif domain == "data_science":
        p1 = f"Master Python data manipulation (Pandas/NumPy), statistical hypothesis testing, exploratory data analysis (EDA), and data science ATS profile setup for {target_role}."
        p2 = f"Develop predictive modeling with Scikit-learn, feature engineering pipelines, advanced data visualization (Seaborn/Plotly), and build a metric-backed data science portfolio project{gap_str}."
        p3 = f"Master machine learning system design, business metrics translation, experimental design (A/B testing), conduct technical mock interviews, and submit placement applications."
    elif domain == "data_analyst":
        p1 = f"Master advanced SQL querying (Window functions, CTEs), data cleaning with Python/Pandas, exploratory analytics, and analytics ATS portfolio setup for {target_role}."
        p2 = f"Develop interactive business intelligence dashboards (Tableau/PowerBI), KPI metric modeling, statistical analysis, and build a comprehensive analytics portfolio project{gap_str}."
        p3 = f"Master business case studies, data storytelling, executive presentation defense, conduct analytical mock interviews, and submit placement applications."
    elif domain == "data_engineer":
        p1 = f"Master Python & advanced SQL data manipulation, foundational DSA, relational database modeling (PostgreSQL), and data engineering ATS profile setup for {target_role}."
        p2 = f"Develop scalable ETL/ELT pipelines, distributed processing with Apache Spark, event streaming with Kafka, Docker containerization, and build a data pipeline project{gap_str}."
        p3 = f"Master data warehouse architecture (Snowflake/BigQuery), data orchestration (Airflow), data system design, conduct technical mock interviews, and submit placement applications."
    elif domain == "cloud":
        p1 = f"Master Linux administration, networking fundamentals (VPC, CIDR, DNS), core cloud provider services (Compute, Storage, IAM), and cloud ATS resume setup for {target_role}."
        p2 = f"Develop Infrastructure as Code (Terraform), container orchestration (Docker/Kubernetes), cloud security monitoring, and build an automated cloud architecture project{gap_str}."
        p3 = f"Master high-availability cloud system design, disaster recovery architectures, cloud cost optimization, conduct cloud technical mock interviews, and submit placement applications."
    elif domain == "devops":
        p1 = f"Master Linux systems engineering, shell scripting, Git version control workflows, networking essentials, and DevOps ATS profile setup for {target_role}."
        p2 = f"Develop automated CI/CD pipelines (GitHub Actions/GitLab), Docker containerization, Kubernetes cluster management, Terraform IaC, and build a complete DevOps pipeline project{gap_str}."
        p3 = f"Master site reliability engineering (SRE) principles, monitoring & observability (Prometheus/Grafana), infrastructure design, conduct technical mock interviews, and submit placement applications."
    elif domain == "qa":
        p1 = f"Master software testing fundamentals, test case design methodologies, Python/JavaScript test scripting, and QA ATS profile setup for {target_role}."
        p2 = f"Develop end-to-end automation frameworks (Selenium/Playwright), API testing (Postman/Pytest), CI/CD test integration, and build a test automation portfolio project{gap_str}."
        p3 = f"Master performance & load testing (JMeter/k6), security testing basics, QA test strategy defense, conduct technical mock interviews, and submit placement applications."
    elif domain == "mobile":
        p1 = f"Master mobile programming fundamentals (TypeScript/React Native/Kotlin/Swift), mobile UI design principles, and mobile developer ATS profile setup for {target_role}."
        p2 = f"Develop state management, offline data persistence, device API integrations (Camera, Geolocation, Push Notifications), and build a complete mobile app project{gap_str}."
        p3 = f"Master mobile app performance optimization, app store deployment workflows, mobile architecture design, conduct technical mock interviews, and submit placement applications."
    elif domain == "database":
        p1 = f"Master advanced SQL querying, database normalization (1NF to BCNF), transaction isolation levels (ACID), and database engineer ATS profile setup for {target_role}."
        p2 = f"Develop query optimization (EXPLAIN ANALYZE, indexing strategies), high availability (replication, failover), NoSQL database modeling, and build a database architecture project{gap_str}."
        p3 = f"Master database sharding, distributed transactions, database reliability engineering, conduct technical mock interviews, and submit placement applications."
    else:
        p1 = f"Master core programming language fundamentals, data structures and algorithms, software engineering principles, and ATS profile setup for {target_role}."
        p2 = f"Develop domain-specific frameworks, databases, modular software architecture, and build a production portfolio project{gap_str}."
        p3 = f"Master System Design architectures, advanced problem-solving under timed conditions, conduct mock technical interviews, and submit placement applications."
        
    return p1, p2, p3


# ===========================================================================
# 90-Day Curriculum Blueprint Generators
# ===========================================================================

def _generate_cybersecurity_curriculum(target_role: str, high_gaps: List[str]) -> List[Dict[str, Any]]:
    """Generates 90 progressive day blueprints for Cybersecurity roles."""
    days = []
    
    # --- Phase 1: Foundation (Days 1–30) ---
    p1_topics = [
        (1, "Networking", "Network Security", "Computer Networking Protocols: TCP/IP vs OSI 7-Layer Architecture", "Analyze packet encapsulation, protocol headers (IP, TCP, UDP), and port communication dynamics."),
        (2, "Networking", "Network Security", "Deep Packet Inspection & Network Traffic Analysis with Wireshark", "Capture live network packets, filter by protocols, and identify anomalous broadcast traffic or unencrypted payloads."),
        (3, "Networking", "Network Security", "Subnetting, CIDR Calculations & Stateful Firewall Rules", "Design IP subnet architectures, compute broadcast ranges, and configure stateful firewall filter rules."),
        (4, "Security", "Network Security", "Network Reconnaissance & Port Scanning Fundamentals with Nmap", "Perform SYN scans, service version detection, and OS fingerprinting using Nmap scan scripts."),
        (5, "Networking", "Network Security", "Core Application Protocols: DNS, DHCP, HTTP/S & TLS Handshake", "Trace DNS resolution hierarchies, DHCP leasing DORA process, and TLS 1.3 cryptographic negotiation."),
        (6, "OS & Scripting", "Linux Security", "Linux Security Essentials & Core System Administration", "Navigate Linux file hierarchies, inspect system processes (`ps`, `top`), and analyze `/etc/passwd` and `/etc/shadow` structures."),
        (7, "OS & Scripting", "Linux Security", "Linux Permissions, SUID/SGID Bits & Pluggable Authentication Modules (PAM)", "Audit file permissions, identify risky SUID executables, and configure PAM password policies."),
        (8, "OS & Scripting", "Linux Security", "Bash Scripting for Security Automation & Log Parsing", "Write shell scripts with regex to extract failed SSH attempts and automatically update iptables blacklists."),
        (9, "Programming", "Python", "Python for Security: Socket Programming & Banner Grabbing", "Develop a Python socket script to connect to remote ports, banner grab services, and parse server headers."),
        (10, "Resume", "Resume", "Cybersecurity ATS Resume Optimization & Profile Audit", f"Refactor resume bullets with quantified security metrics (e.g. vulnerability reductions, triage speed) for {target_role}."),
        (11, "Security", "Cryptography", "Cryptography Fundamentals: Symmetric & Asymmetric Encryption", "Implement AES-256 and RSA key pair generation. Compare computational overhead and cipher security guarantees."),
        (12, "Security", "Cryptography", "Cryptographic Hashing, Integrity Verification & HMACs", "Analyze SHA-256 collision resistance, salt generation for password storage, and HMAC token verification."),
        (13, "Security", "Cryptography", "Public Key Infrastructure (PKI), Digital Signatures & X.509 Certificates", "Create a self-signed Root CA, issue SSL/TLS certificates, and verify certificate revocation lists (CRLs)."),
        (14, "Security", "Security Operations", "Security Operations Center (SOC) Workflows & Incident Triage Hierarchy", "Map SOC Tier 1-3 analyst escalation tiers, SLA metrics (MTTD, MTTR), and alert triage priority matrices."),
        (15, "Security", "SIEM", "SIEM Architecture Fundamentals & Centralized Log Ingestion", "Understand SIEM log ingestion parsers, normalization into common schema, and correlation rule logic."),
        (16, "Security", "SIEM", "Elasticsearch, Logstash & Kibana (ELK) / Splunk Setup", "Deploy a SIEM log collector, configure index patterns, and build real-time security dashboard visualizations."),
        (17, "Security", "Log Analysis", "Windows Event Log Analysis & Sysmon Security Monitoring", "Analyze Windows Security Event IDs (4624, 4625, 4688, 7045) and detect suspicious PowerShell execution."),
        (18, "Security", "Log Analysis", "Linux Auditd & Auth Log Deep Dive for Intrusion Indicators", "Configure Linux `auditd` rules to monitor file modifications and detect unauthorized privilege escalation attempts."),
        (19, "Networking", "Security Monitoring", "Network Flow Monitoring with NetFlow, IPFIX & Zeek", "Inspect network flow metadata, calculate byte-transfer anomalies, and identify command-and-control beaconing."),
        (20, "GitHub", "GitHub", "GitHub Security Lab Setup & Open Source Security Tools Showcase", "Publish documented cybersecurity lab notes, defensive scripts, and attack mitigation writeups on GitHub."),
        (21, "Security", "Security Monitoring", "Intrusion Detection & Prevention (IDS/IPS) with Snort/Suricata", "Write custom Snort rule signatures to detect malicious payload patterns and TCP port scans."),
        (22, "Security", "Security Operations", "Host-Based Intrusion Detection (HIDS) with Wazuh / OSSEC", "Deploy Wazuh agents, monitor file integrity (FIM), and configure automated active responses."),
        (23, "Security", "OWASP", "Web Security Foundations & HTTP Security Headers", "Configure Content Security Policy (CSP), HSTS, X-Frame-Options, and analyze cookie security flags (Secure, HttpOnly, SameSite)."),
        (24, "Security", "Threat Intelligence", "OSINT & Passive Reconnaissance Methodologies", "Utilize WHOIS, DNS enumeration (Sublist3r), Certificate Transparency logs, and Shodan queries."),
        (25, "Security", "Vulnerability Assessment", "Active Network Scanning & Service Vulnerability Enumeration", "Perform automated vulnerability discovery and correlate open service versions against known CVE databases."),
        (26, "Security", "Security Operations", "Defense in Depth Principles & Network Segmentation", "Design segmented network DMZs, internal VLANs, and jump host bastion security controls."),
        (27, "Security", "Security Operations", "Endpoint Protection Platforms (EPP) & Antivirus Mechanics", "Analyze signature-based vs heuristic/behavioral endpoint malware detection engines."),
        (28, "Networking", "Network Security", "Wireless Security Architecture (WPA2/WPA3 Enterprise & 802.1X)", "Compare PSK vs 802.1X EAP authentication, 4-way handshakes, and rogue access point detection."),
        (29, "Security", "Security Fundamentals", "Data Loss Prevention (DLP) & Cryptographic Storage Principles", "Implement data-at-rest encryption policies, database column masking, and sensitive egress filtering."),
        (30, "Security", "Security Operations", "Phase 1 Security Milestone Review & Practical Skills Assessment", f"Complete comprehensive networking, Linux, cryptography, and log analysis benchmark for {target_role}."),
    ]
    for d, cat, skill, title, desc in p1_topics:
        days.append({"day": d, "phase": 1, "category": cat, "skill": skill, "title": f"Day {d}: {title}", "desc": desc, "diff": "Beginner"})
        
    # --- Phase 2: Skill Development & Threat Operations (Days 31–60) ---
    p2_topics = [
        (31, "Security", "Threat Intelligence", "Cyber Threat Intelligence Lifecycles & Cyber Kill Chain", "Map the 7 phases of Lockheed Martin Cyber Kill Chain to modern adversary attack patterns."),
        (32, "Security", "MITRE ATT&CK", "MITRE ATT&CK Framework: Enterprise Matrix & TTP Mapping", "Categorize attacker behaviors across Initial Access, Execution, Persistence, and Exfiltration tactics."),
        (33, "Security", "MITRE ATT&CK", "MITRE ATT&CK Navigator: Threat Actor Profiling & Heatmaps", "Build threat coverage matrices in ATT&CK Navigator to identify defensive telemetry blind spots."),
        (34, "Security", "Threat Intelligence", "Indicators of Compromise (IOCs) & STIX/TAXII Threat Feeds", "Ingest automated threat intelligence feeds into OpenCTI/MISP and correlate IOC hashes and IP addresses."),
        (35, "Security", "Vulnerability Assessment", "Vulnerability Management Lifecycle & Scanning with Nessus/OpenVAS", "Configure credentialed vulnerability scans, remediate false positives, and compile executive vulnerability summaries."),
        (36, "Security", "Vulnerability Assessment", "CVE Databases, NVD & CVSS v3.1/v4.0 Scoring Calculator", "Calculate base, temporal, and environmental CVSS vector scores to accurately prioritize patching deadlines."),
        (37, "Security", "Vulnerability Assessment", "Enterprise Patch Management & Vulnerability Remediation Workflows", "Design patch testing rollback plans, emergency zero-day patching playbooks, and configuration baselines."),
        (38, "Security", "OWASP", "OWASP Top 10: SQL Injection (SQLi) Mechanics & Parameterized Queries", "Identify Union, Error-based, and Blind SQL injection vulnerabilities and implement parameterized prepared statements."),
        (39, "Security", "OWASP", "OWASP Top 10: Cross-Site Scripting (XSS) & CSRF Defense", "Differentiate Stored, Reflected, and DOM XSS attacks; implement context-aware output encoding and anti-CSRF tokens."),
        (40, "Projects", "Vulnerability Assessment", "Security Project Sprint 1: Automated Vulnerability Scanner & Report Engine", "Build a Python-driven vulnerability assessment tool that scans target endpoints, queries CVE feeds, and generates HTML audit reports."),
        (41, "Security", "OWASP", "OWASP Top 10: Server-Side Request Forgery (SSRF) & Broken Access Control", "Analyze cloud metadata endpoint exploitation via SSRF and enforce strict object-level access control checks."),
        (42, "Security", "OWASP", "OWASP Top 10: Security Misconfiguration & Insecure Deserialization", "Audit default cloud configurations, debug insecure YAML/pickle deserialization, and enforce hardened baseline images."),
        (43, "Security", "Authentication and Authorization", "Enterprise Identity: Active Directory, Kerberos & LDAP Security", "Analyze Kerberos authentication tickets (TGT, TGS), SPNs, and mitigate Kerberoasting and AS-REP roasting attacks."),
        (44, "Security", "Authentication and Authorization", "Modern Authentication: OAuth 2.0, OpenID Connect & SAML 2.0", "Inspect OAuth2 authorization code flows with PKCE, JWT token structures, and prevent signature bypass vulnerabilities."),
        (45, "Security", "Authentication and Authorization", "Authorization Models: Role-Based (RBAC) & Attribute-Based (ABAC) Controls", "Implement fine-grained RBAC and ABAC access policies with JSON Web Tokens and policy enforcement points."),
        (46, "Security", "Authentication and Authorization", "Multi-Factor Authentication (MFA) & FIDO2/WebAuthn Protocols", "Deploy TOTP and hardware-backed WebAuthn authentication protocols to eliminate credential phishing risks."),
        (47, "Security", "Incident Response", "Incident Response Frameworks: NIST SP 800-61 & SANS 6-Step PICERL", "Master Preparation, Identification, Containment, Eradication, Recovery, and Lessons Learned incident response stages."),
        (48, "Security", "Incident Response", "Incident Triage, Scope Assessment & Forensic Containment Strategies", "Establish network isolation protocols, forensic volatile memory preservation, and system containment baselines."),
        (49, "Security", "Incident Response", "Digital Forensics & Chain of Custody Maintenance", "Generate forensic disk images using `dd`/FTK Imager and compute cryptographic hash chains of custody."),
        (50, "Projects", "SIEM", "Security Project Sprint 2: SIEM Threat Detection Rule Engine & Alert Pipeline", "Develop a custom detection rule pipeline that parses raw syslog JSON, triggers alert webhooks, and correlates multi-stage attacks."),
        (51, "Security", "Incident Response", "Memory Forensics with Volatility Framework", "Analyze memory dumps with Volatility: identify injected DLLs, extract process trees, and dump memory strings."),
        (52, "Security", "Threat Intelligence", "Malware Analysis Fundamentals: Static & Dynamic Analysis", "Perform PE header inspection, string extraction, and safe execution analysis in isolated Cuckoo sandbox environments."),
        (53, "Security", "Threat Intelligence", "YARA Rule Creation for Malware Detection & Threat Hunting", "Author custom YARA rules targeting specific malicious binary strings, regex patterns, and byte offsets."),
        (54, "Security", "SIEM", "Sigma Rules for Cross-Platform SIEM Detection Logic", "Write standardized Sigma detection rules and convert them into native Splunk SPL and Elasticsearch queries."),
        (55, "Security", "Security Operations", "Security Orchestration, Automation & Response (SOAR) Playbooks", "Automate threat containment playbooks (IP blocking, user account disabling, ticket creation) using Python APIs."),
        (56, "DevOps", "Security Operations", "Container Security: Dockerfile Hardening & Trivy Image Scanning", "Build rootless Docker images, scan container layers for vulnerabilities using Trivy, and minimize attack surfaces."),
        (57, "DevOps", "Security Operations", "Kubernetes Security: RBAC, Network Policies & Pod Security Standards", "Implement strict Kubernetes NetworkPolicies, service account token isolation, and Pod Security Admission controllers."),
        (58, "Security", "Security Operations", "Email Security Protocols: SPF, DKIM, DMARC & Phishing Defense", "Configure DNS SPF TXT records, DKIM cryptographic keys, and DMARC enforcement policies to prevent email spoofing."),
        (59, "Security", "OWASP", "API Security Testing & OWASP API Top 10 Vulnerabilities", "Audit REST APIs for Broken Object Level Authorization (BOLA), mass assignment, and improper rate limiting."),
        (60, "Projects", "Incident Response", "Security Project Sprint 3: SOC Incident Response Playbook & Threat Lab", "Document an end-to-end incident response simulation with malware containment, memory forensic report, and post-mortem review."),
    ]
    for d, cat, skill, title, desc in p2_topics:
        days.append({"day": d, "phase": 2, "category": cat, "skill": skill, "title": f"Day {d}: {title}", "desc": desc, "diff": "Intermediate"})
        
    # --- Phase 3: Advanced Architectures, Threat Hunting & Placement (Days 61–90) ---
    p3_topics = [
        (61, "Cloud", "Security Architecture", "Cloud Security Foundations: Shared Responsibility & Cloud Threat Vectors", "Analyze AWS/Azure security perimeters, misconfigurations, and cloud-native attack vectors."),
        (62, "Cloud", "Security Architecture", "Cloud IAM Deep Dive: Least Privilege & Role-Based Policies", "Audit AWS IAM trust policies, cross-account assume-role delegations, and eliminate permission creep."),
        (63, "Cloud", "Security Monitoring", "Cloud Network Security & Logging: VPC Flow Logs, CloudTrail & GuardDuty", "Analyze VPC traffic flows, correlate CloudTrail management event logs, and triage automated GuardDuty findings."),
        (64, "Security", "Security Architecture", "Zero Trust Architecture (ZTA): NIST 800-207 Principles", "Design perimeter-less security architectures incorporating continuous authentication, micro-segmentation, and device telemetry."),
        (65, "Security", "Threat Intelligence", "Proactive Threat Hunting: Hypothesis-Driven Threat Search", "Formulate threat hunting hypotheses based on MITRE ATT&CK techniques and query SIEM telemetry for living-off-the-land binaries (LOLBins)."),
        (66, "Security", "Security Monitoring", "Endpoint Detection & Response (EDR) Telemetry & Threat Hunting", "Analyze process injection, parent-child process anomalies, and scheduled task persistence using EDR queries."),
        (67, "Security", "Network Security", "Advanced Network Threat Hunting with Zeek & Suricata Alert Correlation", "Detect lateral movement, DNS tunneling, and encrypted SSL/TLS anomalies via network connection state logs."),
        (68, "Security", "Security Operations", "Purple Teaming: Adversary Emulation & Defensive Validation with Caldera", "Execute automated adversary emulation plans using Caldera and validate detection alerting coverage."),
        (69, "Security", "Vulnerability Assessment", "Penetration Testing Methodologies & Ethical Hacking Standards (PTES)", "Review penetration testing engagement lifecycles: scoping, reconnaissance, exploitation, privilege escalation, and cleanup."),
        (70, "CS Fundamentals", "Security Fundamentals", "Compliance Frameworks: SOC 2, ISO 27001, NIST CSF & HIPAA", "Map technical security controls to regulatory compliance standards, audit logs, and risk management frameworks."),
        (71, "Security", "Security Operations", "Timed SOC Alert Triage Simulation & Incident Priority Challenge", "Perform rapid alert triage under strict time constraints, determining severity, false positive rates, and containment actions."),
        (72, "Security", "Incident Response", "Real-World Incident Scenario: Ransomware Outbreak Response", "Walk through a full ransomware attack scenario: lateral movement isolation, shadow copy recovery, and ransom negotiation policies."),
        (73, "Security", "Incident Response", "Real-World Incident Scenario: Cloud Data Breach & Credential Compromise", "Investigate compromised cloud access keys, revoke sessions, audit exfiltrated S3 bucket objects, and issue disclosures."),
        (74, "Security", "Threat Intelligence", "Real-World Incident Scenario: Supply Chain Attack & Third-Party Risk", "Analyze software supply chain vulnerabilities, malicious package dependencies, and software bill of materials (SBOM)."),
        (75, "CS Fundamentals", "Security Architecture", "Security Architecture Design: Securing Enterprise Hybrid Cloud Infrastructure", "Architect a defense-in-depth security blueprint for a multi-region cloud environment with WAF, SIEM, and Zero Trust access."),
        (76, "Interview", "Cybersecurity Interview Preparation", "Technical Interview Prep: Computer Networking & Security Protocols Defense", "Practice answering deep-dive networking questions: TCP 3-way handshake teardown, DNS amplification, and TLS negotiation."),
        (77, "Interview", "Cybersecurity Interview Preparation", "Technical Interview Prep: Incident Response & SOC Scenario Questions", "Answer scenario-based interview questions: 'How would you handle an alert on PowerShell downloading an external executable?'"),
        (78, "Interview", "Cybersecurity Interview Preparation", "Technical Interview Prep: Threat Intelligence & MITRE ATT&CK Mapping", "Demonstrate fluency in explaining specific threat actor TTPs, C2 communication channels, and threat intelligence attribution."),
        (79, "Interview", "Cybersecurity Interview Preparation", "Technical Interview Prep: Cryptography & Identity Management Questions", "Defend PKI architectures, symmetric vs asymmetric tradeoffs, and explain JWT signature security controls to interviewers."),
        (80, "Interview", "Cybersecurity Interview Preparation", "Technical Interview Prep: OWASP Top 10 Web Application Defense", "Walk through live code remediation for SQL injection, XSS, SSRF, and broken access control in an interview setting."),
        (81, "Communication", "Communication", "Cybersecurity Behavioral Interview: STAR Method for Security Crises", "Formulate 5 STAR method responses detailing real security projects, crisis troubleshooting, and stakeholder communication."),
        (82, "Interview", "Cybersecurity Interview Preparation", "Mock Technical Interview: Live Incident Response & Forensic Defense", "Simulate a live 45-minute technical interview evaluating forensic artifacts and justifying containment decisions."),
        (83, "Interview", "Cybersecurity Interview Preparation", "Mock Technical Interview: Cloud Security Architecture & Threat Modeling", "Simulate a live 45-minute architecture whiteboard session defending a secure cloud deployment against advanced persistent threats."),
        (84, "Interview", "Cybersecurity Interview Preparation", "Mock Technical Interview: Vulnerability Triage & Risk Prioritization", "Defend risk remediation timelines and justify patch prioritization under competing business priorities."),
        (85, "Interview", "Cybersecurity Interview Preparation", "Full Cybersecurity Mock Placement Panel Simulation", "Complete a comprehensive 90-minute full mock placement interview covering technical, situational, and behavioral rounds."),
        (86, "GitHub", "GitHub", "Cybersecurity Portfolio Polish & Technical Lab Writeup Verification", "Verify all GitHub project repositories, include architectural diagrams, executive summaries, and clear replication instructions."),
        (87, "Resume", "Resume", "Final ATS Resume Calibration & Industry Security Certifications Roadmap", f"Finalize ATS-optimized cybersecurity resume and establish a roadmap for CompTIA Security+, CySA+, CEH, or BTL1."),
        (88, "Communication", "Communication", "LinkedIn Profile Optimization & Security Community Networking", "Optimize LinkedIn headline, summary, and connect with cybersecurity recruiters and hiring managers in target organizations."),
        (89, "Interview", "Cybersecurity Interview Preparation", "Targeted Security Job Application Sprint & Recruiter Outreach", f"Submit 15+ tailored job applications for {target_role} and track interview pipelines."),
        (90, "Interview", "Cybersecurity Interview Preparation", "Final Placement Readiness Audit & Career Launch Strategy", "Review overall readiness score, celebrate milestone achievements, and finalize ongoing placement interview schedule."),
    ]
    for d, cat, skill, title, desc in p3_topics:
        days.append({"day": d, "phase": 3, "category": cat, "skill": skill, "title": f"Day {d}: {title}", "desc": desc, "diff": "Advanced"})
        
    return days


def _generate_aiml_curriculum(target_role: str, high_gaps: List[str]) -> List[Dict[str, Any]]:
    """Generates 90 progressive day blueprints for AI/ML Engineer roles."""
    days = []
    
    # --- Phase 1: Foundation (Days 1–30) ---
    p1_topics = [
        (1, "Programming", "Python", "Python for Machine Learning: Advanced OOP & Vectorization", "Review OOP class inheritance, generators, decorators, and vectorized computing paradigms."),
        (2, "Data Science", "NumPy", "NumPy Numerical Computing & Matrix Operations", "Perform high-performance tensor slicing, broadcasting rules, matrix multiplication, and linear algebra routines."),
        (3, "Data Science", "Pandas", "Pandas Data Wrangling & High-Performance Dataframes", "Clean missing data, execute multi-index grouping, aggregations, and merge heterogeneous tabular datasets."),
        (4, "Data Science", "Exploratory Data Analysis", "Exploratory Data Analysis (EDA) & Statistical Visualization", "Compute skewness, kurtosis, correlation matrices, and plot distributions using Seaborn and Matplotlib."),
        (5, "Data Science", "Statistics", "Linear Algebra Foundations for ML: Eigenvectors & SVD", "Calculate eigenvalues, eigenvectors, matrix rank, and Singular Value Decomposition (SVD) for dimensionality reduction."),
        (6, "Data Science", "Statistics", "Probability Distributions, Bayes Theorem & Hypothesis Testing", "Calculate normal, binomial, and Poisson distributions; conduct z-tests, t-tests, and p-value evaluations."),
        (7, "DSA", "DSA", "Data Structures for ML: Trees, Graphs & Priority Queues", "Implement binary search trees, graph adjacency matrices, and min-heaps for search optimization."),
        (8, "Machine Learning", "Scikit-learn", "Supervised Learning: Linear Regression & Regularization (Lasso/Ridge)", "Implement ordinary least squares, understand bias-variance tradeoff, and apply L1/L2 weight penalties."),
        (9, "Machine Learning", "Scikit-learn", "Classification Fundamentals: Logistic Regression & Decision Boundaries", "Derive sigmoid activation, log-loss cost function, and plot multi-class decision boundaries."),
        (10, "Resume", "Resume", "AI/ML ATS Resume Optimization & Kaggle Profile Audit", f"Structure AI/ML project bullet points with model metrics (F1, AUC, latency) tailored for {target_role}."),
        (11, "Machine Learning", "Scikit-learn", "Tree-Based Models: Decision Trees, Random Forests & Bagging", "Analyze Gini impurity, entropy, information gain, and ensemble averaging with Random Forests."),
        (12, "Machine Learning", "Scikit-learn", "Gradient Boosting Frameworks: XGBoost, LightGBM & CatBoost", "Tune learning rate, tree depth, and subsample ratios in gradient boosted decision trees."),
        (13, "Machine Learning", "Scikit-learn", "Support Vector Machines (SVM) & Kernel Methods", "Implement maximum margin hyperplanes, soft margin slack variables, and RBF kernel transformations."),
        (14, "Machine Learning", "Scikit-learn", "Unsupervised Learning: K-Means Clustering & Hierarchical Clustering", "Implement Elbow method for optimal K selection, silhouette scoring, and agglomerative clustering."),
        (15, "Machine Learning", "Scikit-learn", "Dimensionality Reduction: Principal Component Analysis (PCA) & t-SNE", "Project high-dimensional feature spaces onto principal components preserving maximum variance."),
        (16, "Data Science", "Feature Engineering", "Feature Engineering & Preprocessing Pipelines", "Construct automated pipelines with StandardScaler, OneHotEncoder, target encoding, and polynomial features."),
        (17, "Machine Learning", "Model Evaluation", "Model Evaluation Metrics: ROC-AUC, Precision, Recall & F1-Score", "Plot confusion matrices, ROC curves, precision-recall tradeoffs, and handle class imbalance with SMOTE."),
        (18, "Machine Learning", "Model Evaluation", "Cross-Validation Strategies & Hyperparameter Tuning with Optuna", "Implement stratified K-fold cross-validation and Bayesian hyperparameter search using Optuna."),
        (19, "DSA", "DSA", "Algorithm Optimization & Dynamic Programming for ML", "Solve 2 classic DP problems (Longest Common Subsequence, Knapsack) to sharpen algorithmic problem solving."),
        (20, "GitHub", "GitHub", "GitHub AI Portfolio Setup & Open-Source Benchmark Repositories", "Set up reproducible GitHub repositories with `environment.yml`, data download scripts, and README metrics."),
        (21, "Machine Learning", "Deep Learning", "Neural Network Foundations: Perceptrons & Backpropagation", "Derive forward propagation, computational graphs, chain rule gradients, and backpropagation step-by-step."),
        (22, "Machine Learning", "Deep Learning", "Activation Functions & Gradient Descent Optimizers", "Compare ReLU, LeakyReLU, GELU, and optimizers: SGD with Momentum, RMSprop, and Adam."),
        (23, "Machine Learning", "PyTorch", "PyTorch Tensor Operations, Autograd & Dataset Loaders", "Build custom `torch.utils.data.Dataset` and `DataLoader` pipelines with automatic gradient tracking."),
        (24, "Machine Learning", "PyTorch", "Building Multi-Layer Perceptrons (MLP) in PyTorch", "Define `nn.Module` classes with linear layers, batch normalization, dropout, and training loops."),
        (25, "Machine Learning", "TensorFlow", "TensorFlow & Keras Functional API Overview", "Build and train comparable neural network architectures using TensorFlow Keras functional APIs."),
        (26, "Machine Learning", "Deep Learning", "Overfitting Prevention: Dropout, Weight Decay & Early Stopping", "Implement early stopping callback checkpoints and evaluate validation loss trajectories."),
        (27, "Backend", "REST API", "REST API Basics for ML: Serving Model Predictions with FastAPI", "Build a lightweight FastAPI endpoint accepting JSON feature payloads and returning model inference predictions."),
        (28, "DevOps", "Docker", "Containerizing Machine Learning Environments with Docker", "Write a Dockerfile to package Python ML dependencies, model weights, and inference code into an isolated image."),
        (29, "CS Fundamentals", "CS Fundamentals", "Computer Architecture & GPU Acceleration (CUDA / Tensor Cores)", "Understand memory bandwidth bottlenecks, CPU vs GPU parallelism, and mixed-precision (FP16) training."),
        (30, "AI/ML", "AI/ML", "Phase 1 Machine Learning Milestone Review & Benchmark", f"Complete comprehensive ML theory, PyTorch, and classical algorithms benchmark for {target_role}."),
    ]
    for d, cat, skill, title, desc in p1_topics:
        days.append({"day": d, "phase": 1, "category": cat, "skill": skill, "title": f"Day {d}: {title}", "desc": desc, "diff": "Beginner"})
        
    # --- Phase 2: Skill Development & Deep Learning (Days 31–60) ---
    p2_topics = [
        (31, "Machine Learning", "Deep Learning", "Convolutional Neural Networks (CNNs): Convolutions & Pooling", "Implement 2D convolution filters, stride, padding, max pooling, and spatial feature extraction."),
        (32, "Machine Learning", "Deep Learning", "Modern Computer Vision Architectures: ResNet & Residual Connections", "Build residual blocks with skip connections in PyTorch to train deep networks without vanishing gradients."),
        (33, "Machine Learning", "Deep Learning", "Transfer Learning & Image Augmentation with Torchvision", "Fine-tune pretrained ResNet/EfficientNet weights on custom image classification datasets."),
        (34, "Machine Learning", "Deep Learning", "Object Detection & Segmentation Concepts (YOLO / U-Net)", "Analyze bounding box regression, Intersection over Union (IoU), and semantic segmentation masks."),
        (35, "Machine Learning", "Deep Learning", "Sequence Modeling: Recurrent Neural Networks (RNNs) & LSTMs", "Understand hidden state persistence, vanishing gradients through time, and LSTM gating mechanisms."),
        (36, "Machine Learning", "Deep Learning", "Natural Language Processing (NLP) Foundations: Tokenization & Word2Vec", "Implement BPE/WordPiece tokenization, Word2Vec embeddings, and cosine similarity semantic search."),
        (37, "Machine Learning", "Deep Learning", "Attention Mechanisms & Transformer Architecture (Vaswani et al.)", "Derive Scaled Dot-Product Attention, Multi-Head Attention, and positional encoding embeddings."),
        (38, "Machine Learning", "Deep Learning", "HuggingFace Transformers: BERT, RoBERTa & Fine-Tuning", "Fine-tune BERT for text classification and named entity recognition (NER) using HuggingFace Trainer."),
        (39, "Machine Learning", "Deep Learning", "Autoregressive LLM Architectures (GPT, LLaMA) & Decoder-Only Models", "Analyze causal self-attention masks, key-value (KV) caching, and text generation decoding strategies."),
        (40, "Projects", "AI/ML", "AI/ML Project Sprint 1: End-to-End Predictive Machine Learning Pipeline", "Build a production predictive modeling pipeline with automated feature engineering, XGBoost training, and artifact tracking."),
        (41, "Machine Learning", "Deep Learning", "Generative AI: Autoencoders & Variational Autoencoders (VAEs)", "Implement encoder-decoder networks, latent space sampling, and reconstruction loss optimization."),
        (42, "Machine Learning", "Deep Learning", "Diffusion Models & Generative Adversarial Networks (GANs)", "Understand forward/reverse diffusion processes, score matching, and generator-discriminator minimax games."),
        (43, "DevOps", "MLOps", "MLOps Essentials: Experiment Tracking with MLflow & Weights & Biases", "Log hyperparameters, training curves, confusion matrices, and model checkpoints to an MLflow tracking server."),
        (44, "DevOps", "MLOps", "Data Version Control (DVC) for Machine Learning Datasets", "Version large training datasets and pipelines using DVC integrated with remote S3/GCS cloud storage."),
        (45, "DevOps", "MLOps", "Model Packaging & Serialization: ONNX, TorchScript & TensorRT", "Export PyTorch models to ONNX and optimize inference graphs for latency reduction using TensorRT."),
        (46, "Backend", "REST API", "High-Throughput Model Serving API with FastAPI & Async Inference", "Build a production FastAPI serving layer supporting batch inference requests, request validation, and caching."),
        (47, "DevOps", "MLOps", "Container Orchestration for ML: Docker Compose & Triton Server", "Deploy NVIDIA Triton Inference Server or multi-container FastAPI + Redis prediction pipelines with Docker Compose."),
        (48, "Machine Learning", "Model Evaluation", "Model Monitoring: Data Drift & Concept Drift Detection with Evidently", "Implement drift detection algorithms (KS-test, PSI) to monitor live prediction distributions against baseline training data."),
        (49, "DSA", "DSA", "Advanced Data Structures & Algorithms: Graphs & Heuristics", "Implement Dijkstra's shortest path and A* heuristic search algorithms for spatial and network graph optimization."),
        (50, "Projects", "AI/ML", "AI/ML Project Sprint 2: Deep Learning Vision / NLP Transformer Model", "Train and evaluate a custom transformer/vision model on a real-world dataset with metric tracking in MLflow."),
        (51, "Machine Learning", "Deep Learning", "Parameter-Efficient Fine-Tuning (PEFT): LoRA & QLoRA", "Fine-tune open-source LLMs (LLaMA/Mistral) using Low-Rank Adaptation (LoRA) and 4-bit quantization."),
        (52, "AI/ML", "AI/ML", "Retrieval-Augmented Generation (RAG) Architecture & Vector Embeddings", "Design a RAG system: document chunking strategies, dense embedding generation, and semantic search."),
        (53, "Databases", "Databases", "Vector Databases: Pinecone, ChromaDB, Milvus & FAISS", "Index document vectors in ChromaDB/Pinecone, perform Approximate Nearest Neighbor (ANN) search, and tune top-k retrieval."),
        (54, "AI/ML", "AI/ML", "Advanced RAG: Re-ranking, HyDE & Agentic Workflows with LangChain", "Implement Cross-Encoder re-ranking, Hypothetical Document Embeddings (HyDE), and tool-calling agents."),
        (55, "DevOps", "MLOps", "Automated ML CI/CD Pipelines: Continuous Training with GitHub Actions", "Configure GitHub Actions workflows to trigger automated unit tests, model training, and artifact publishing on git commit."),
        (56, "Machine Learning", "Model Evaluation", "Fairness, Bias & Explainable AI (XAI): SHAP & LIME", "Generate SHAP waterfall plots and LIME explanations to interpret model predictions for stakeholders."),
        (57, "CS Fundamentals", "CS Fundamentals", "Distributed Training: Data Parallelism (DDP) & DeepSpeed", "Understand Distributed Data Parallel (DDP) gradient synchronization, ZeRO memory optimization, and pipeline parallelism."),
        (58, "Machine Learning", "PyTorch", "PyTorch Profiler & Memory Leak Debugging", "Profile GPU memory consumption, identify CUDA out-of-memory (OOM) bottlenecks, and optimize batch size throughput."),
        (59, "AI/ML", "AI/ML", "AI System Evaluation: Ragas Metrics for RAG Pipelines", "Evaluate RAG hallucination rates, faithfulness, answer relevancy, and context recall using Ragas."),
        (60, "Projects", "AI/ML", "AI/ML Project Sprint 3: Production Model Serving API & RAG Application", "Deploy a complete production AI application combining fine-tuned models/RAG, FastAPI backend, and interactive UI demo."),
    ]
    for d, cat, skill, title, desc in p2_topics:
        days.append({"day": d, "phase": 2, "category": cat, "skill": skill, "title": f"Day {d}: {title}", "desc": desc, "diff": "Intermediate"})
        
    # --- Phase 3: Advanced Architectures, System Design & Placement (Days 61–90) ---
    p3_topics = [
        (61, "CS Fundamentals", "AI/ML", "Machine Learning System Design: Recommendation Engines", "Design a multi-stage recommendation system: candidate generation, re-ranking, real-time feature store, and feedback loops."),
        (62, "CS Fundamentals", "AI/ML", "Machine Learning System Design: Real-Time Fraud Detection", "Architect a low-latency fraud detection system handling 100k QPS with streaming features (Flink/Kafka) and model inference."),
        (63, "CS Fundamentals", "AI/ML", "Machine Learning System Design: Visual Search & Multimodal Embeddings", "Design a multimodal image search engine using CLIP embeddings, vector indexing, and scalable distributed storage."),
        (64, "CS Fundamentals", "AI/ML", "Machine Learning System Design: Large Language Model Serving at Scale", "Design a scalable LLM gateway with continuous batching (vLLM), KV cache offloading, and rate limiting."),
        (65, "DSA", "DSA", "LeetCode Algorithmic Practice: Advanced Trees & Graph Traversals", "Solve LeetCode Hard problems on Graph BFS/DFS, Topological Sorting, and Trie prefix trees under timed constraints."),
        (66, "DSA", "DSA", "LeetCode Algorithmic Practice: Dynamic Programming & Sliding Window", "Solve classic LeetCode DP optimization and complex sliding window challenges."),
        (67, "Machine Learning", "Model Evaluation", "A/B Testing & Online Experimentation for Machine Learning Models", "Design online randomized control trials: sample size determination, statistical power, p-value tracking, and guardrail metrics."),
        (68, "DevOps", "MLOps", "Feature Stores: Feast & Hopsworks Architecture", "Implement offline training feature retrieval and low-latency online Redis feature serving using Feast."),
        (69, "CS Fundamentals", "CS Fundamentals", "Edge AI & Model Quantization: INT8 / GGML / GGUF Deployment", "Quantize deep learning models for CPU/edge deployment with minimal accuracy loss using ONNX Runtime."),
        (70, "CS Fundamentals", "CS Fundamentals", "AI Ethics, Governance, Safety & Guardrails (NeMo Guardrails)", "Implement input/output moderation rails to prevent jailbreaks, prompt injections, and PII leakage."),
        (71, "AI/ML", "AI/ML", "Timed ML Coding Benchmark: Implementing Algorithms from Scratch", "Implement Linear Regression, K-Means, and a simple Neural Network forward/backward pass using only NumPy from scratch in 60 minutes."),
        (72, "Interview", "AI/ML", "ML Theory Deep Dive: Bias-Variance, Regularization & Loss Formulations", "Practice articulating mathematical derivations for Cross-Entropy, KL Divergence, and regularization penalties."),
        (73, "Interview", "AI/ML", "Deep Learning Interview Prep: Transformer Architecture Defense", "Defend transformer design decisions: self-attention computational complexity $O(N^2)$, rotary position embeddings (RoPE), and flash attention."),
        (74, "Interview", "AI/ML", "MLOps & System Architecture Interview Questions", "Answer real-world scaling questions: 'How do you handle training dataset drift and automated zero-downtime model rollbacks?'"),
        (75, "Interview", "AI/ML", "Generative AI & LLM Engineering Interview Questions", "Explain fine-tuning vs RAG tradeoffs, hallucination mitigation techniques, and prompt caching strategies to interviewers."),
        (76, "Communication", "Communication", "AI/ML Behavioral Interview: STAR Method for Machine Learning Projects", "Craft 5 structured STAR method stories detailing project impact, model failures turned into successes, and cross-functional collaboration."),
        (77, "Interview", "AI/ML", "Mock Technical Interview: ML Coding & Algorithmic Problem Solving", "Simulate a live 45-minute technical coding interview solving data manipulation and ML implementation questions."),
        (78, "Interview", "AI/ML", "Mock Technical Interview: ML System Design Whiteboard Session", "Simulate a live 45-minute ML system design whiteboard session designing an end-to-end scalable ML product."),
        (79, "Interview", "AI/ML", "Mock Technical Interview: Deep Learning & Statistical Theory Drill", "Simulate a deep-dive interview probing mathematical foundations, loss functions, and optimization algorithms."),
        (80, "Interview", "AI/ML", "Full AI/ML Placement Mock Interview Panel Simulation", "Complete a comprehensive 90-minute full mock placement interview covering coding, system design, and behavioral questions."),
        (81, "GitHub", "GitHub", "AI/ML Portfolio Documentation, Demo Video & Live Links Polish", "Ensure all GitHub repos have live HuggingFace Spaces / Streamlit demos, reproducible notebooks, and clear architecture diagrams."),
        (82, "Resume", "Resume", "Final ATS Resume Calibration for AI/ML Engineer Roles", f"Finalize ATS-optimized resume highlighting tangible ML engineering achievements for {target_role}."),
        (83, "Communication", "Communication", "LinkedIn Profile Optimization & AI Community Networking", "Showcase project writeups on LinkedIn, engage with open-source ML communities, and reach out to hiring managers."),
        (84, "Interview", "AI/ML", "Targeted AI/ML Job Application Sprint", f"Submit 15+ tailored job applications for {target_role} across top technology companies and AI startups."),
        (85, "AI/ML", "AI/ML", "Reviewing Industry Whitepapers & Emerging Trends (DeepSeek, LLaMA-3)", "Analyze state-of-the-art architectures, mixture-of-experts (MoE), and distillation techniques to demonstrate cutting-edge knowledge."),
        (86, "Interview", "AI/ML", "Advanced ML Case Study: Cold-Start Problems in Recommender Systems", "Solve real-world business case studies addressing sparsity, exploration-exploitation (Multi-Armed Bandits), and matrix factorization."),
        (87, "Interview", "AI/ML", "Live Coding Refinement: Python Data Manipulation Speed Drills", "Execute rapid 15-minute Pandas/NumPy data manipulation challenges under tight timer pressure."),
        (88, "Interview", "AI/ML", "Follow-up Interview Communication & Offer Negotiation Strategies", "Master negotiation strategies for AI/ML roles, equity compensation structures, and post-interview thank you communications."),
        (89, "Interview", "AI/ML", "Final Application Follow-ups & Technical Assessment Submissions", "Complete pending take-home machine learning challenges and submit optimized code solutions."),
        (90, "Interview", "AI/ML", "Final Placement Readiness Evaluation & Career Launch Plan", "Review overall readiness score, celebrate milestone achievements, and finalize ongoing placement interview schedule."),
    ]
    for d, cat, skill, title, desc in p3_topics:
        days.append({"day": d, "phase": 3, "category": cat, "skill": skill, "title": f"Day {d}: {title}", "desc": desc, "diff": "Advanced"})
        
    return days


def _generate_backend_curriculum(target_role: str, high_gaps: List[str], preferred_lang: Optional[str] = None) -> List[Dict[str, Any]]:
    """Generates 90 progressive day blueprints for Backend Developer roles."""
    lang = preferred_lang or "Python"
    framework = "FastAPI" if lang.lower() == "python" else ("Express.js" if "node" in lang.lower() or "javascript" in lang.lower() else "Spring Boot")
    days = []
    
    # --- Phase 1: Foundation (Days 1–30) ---
    p1_topics = [
        (1, "Programming", lang, f"{lang} Mastery: Advanced Syntax, Memory Model & Async I/O", f"Master core {lang} concurrency models, memory management, garbage collection, and async/await event loops."),
        (2, "Programming", lang, f"{lang} Object-Oriented Design & SOLID Principles", "Implement Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion patterns."),
        (3, "DSA", "Arrays", "DSA Foundation: Arrays, Strings & Two-Pointer Techniques", "Solve LeetCode Array & String problems applying two-pointer and sliding window algorithmic techniques."),
        (4, "DSA", "Hashing", "DSA Foundation: Hash Maps, Hash Sets & Collision Handling", "Analyze hash table load factors, hash functions, and solve LeetCode HashMap / Set problem sets."),
        (5, "DSA", "Linked Lists", "DSA Foundation: Singly & Doubly Linked Lists", "Implement linked list pointer manipulation, cycle detection (Floyd's algorithm), and list reversals."),
        (6, "DSA", "Stacks & Queues", "DSA Foundation: Stacks, Queues & Monotonic Stacks", "Implement stack and queue operations and solve monotonic stack problems (e.g. Next Greater Element)."),
        (7, "Backend", "REST API", "HTTP Protocol & RESTful API Architecture Design", "Master HTTP/1.1 vs HTTP/2 vs HTTP/3, idempotency, status codes, request-response lifecycle, and RESTful resource modeling."),
        (8, "Backend", framework, f"Web Framework Foundations with {framework}", f"Initialize a modular {framework} project structure with routing, dependency injection, and Pydantic validation."),
        (9, "Backend", framework, f"API Request Validation, Serialization & Error Handling in {framework}", "Build custom middleware, global exception handlers, and structured JSON error response schemas."),
        (10, "Resume", "Resume", "Backend ATS Resume Optimization & Profile Audit", f"Rewrite backend project bullets with quantifiable metrics (QPS, latency, DB indexing gains) for {target_role}."),
        (11, "Databases", "SQL", "Relational Databases: SQL Fundamentals & Normalization (1NF to 3NF)", "Write complex SELECT queries with multiple JOIN types, GROUP BY, HAVING, and design normalized database schemas."),
        (12, "Databases", "PostgreSQL", "PostgreSQL Advanced Queries: Window Functions & CTEs", "Master Common Table Expressions (WITH queries), ROW_NUMBER, RANK, and PARTITION BY window functions."),
        (13, "Databases", "PostgreSQL", "Database Indexing: B-Tree, Hash, GIN & EXPLAIN Query Planning", "Inspect query execution plans with `EXPLAIN ANALYZE` and optimize slow queries using composite B-Tree indexes."),
        (14, "Databases", "PostgreSQL", "Transactions, ACID Properties & Isolation Levels", "Analyze Read Committed, Repeatable Read, and Serializable isolation levels; understand dirty reads and phantom reads."),
        (15, "Backend", "Authentication", "Authentication Fundamentals: Session-Based vs Token-Based Auth", "Compare stateful server sessions vs stateless JWT authentication architectures and cookie security headers."),
        (16, "Backend", "Authentication", "JWT Authentication & Role-Based Access Control (RBAC)", "Implement secure JWT generation, refresh token rotation, and password hashing using bcrypt/Argon2."),
        (17, "DSA", "Recursion", "DSA Foundation: Recursion & Backtracking", "Solve classic backtracking problems: N-Queens, Subsets, and Permutations with time/space complexity analysis."),
        (18, "DSA", "Binary Search", "DSA Foundation: Binary Search on Values & Rotated Arrays", "Implement standard binary search and binary search on answer spaces in rotated sorted arrays."),
        (19, "CS Fundamentals", "Operating Systems", "Operating Systems: Processes, Threads & Concurrency", "Understand process address spaces, POSIX threads, race conditions, mutex locks, and deadlocks."),
        (20, "GitHub", "GitHub", "GitHub Backend Showcase & Clean Code Repository Setup", "Configure GitHub repository with automated linters (Ruff/ESLint), pre-commit hooks, and architecture documentation."),
        (21, "Backend", framework, f"ORM Integration: Database Modeling & Migrations in {framework}", "Configure SQLAlchemy / Prisma / Hibernate ORM models, relationships (1:N, M:N), and manage schema migrations with Alembic."),
        (22, "Databases", "Databases", "Preventing the N+1 Query Problem in ORMs", "Identify N+1 query bottlenecks and apply eager loading (`joinedload`, `selectinload`) to optimize query counts."),
        (23, "DevOps", "Docker", "Docker Essentials: Multi-Stage Dockerfile for Backend Services", "Write optimized, lightweight multi-stage Dockerfiles for backend APIs reducing image size and attack surface."),
        (24, "DevOps", "Docker", "Docker Compose: Multi-Service Environment (API + DB + Redis)", "Write `docker-compose.yml` to orchestrate backend API service, PostgreSQL database, and Redis cache containers."),
        (25, "Backend", "REST API", "API Documentation: OpenAPI / Swagger & Postman Collections", "Generate interactive OpenAPI documentation and publish automated Postman test collections with environment variables."),
        (26, "CS Fundamentals", "Networking", "Computer Networking for Backend: TCP, UDP, DNS & TLS", "Trace connection lifecycles, TCP handshake, socket buffers, and TLS termination in web servers."),
        (27, "Backend", "Testing", "Unit Testing & Integration Testing for Backend APIs", "Write comprehensive unit and integration test suites using Pytest / Jest / JUnit with mock database fixtures."),
        (28, "DevOps", "DevOps", "CI/CD Pipeline with GitHub Actions for Backend Testing", "Automate linting, unit test execution, and Docker container builds on every pull request using GitHub Actions."),
        (29, "Backend", "Backend", "API Rate Limiting, CORS & Security Best Practices", "Implement token bucket / sliding window rate limiting middleware and configure strict Cross-Origin Resource Sharing (CORS)."),
        (30, "Backend", "Backend", "Phase 1 Backend Milestone Review & Technical Benchmark", f"Complete comprehensive backend programming, database, and DSA benchmark for {target_role}."),
    ]
    for d, cat, skill, title, desc in p1_topics:
        days.append({"day": d, "phase": 1, "category": cat, "skill": skill, "title": f"Day {d}: {title}", "desc": desc, "diff": "Beginner"})
        
    # --- Phase 2: Skill Development, Caching & Architecture (Days 31–60) ---
    p2_topics = [
        (31, "Databases", "Redis", "In-Memory Caching with Redis: Cache-Aside & Write-Through Patterns", "Deploy Redis and implement Cache-Aside caching patterns with TTL expiration to reduce database read load."),
        (32, "Databases", "Redis", "Redis Data Structures: Hashes, Sorted Sets, Bitmaps & HyperLogLog", "Utilize Redis Sorted Sets for live leaderboards, Hashes for user sessions, and Bitmaps for daily active users."),
        (33, "Databases", "Redis", "Distributed Caching Challenges: Cache Stampede, Avalanche & Penetration", "Implement mutex locking, probabilistic early expiration (XFetch), and Bloom filters to mitigate caching anomalies."),
        (34, "DSA", "Trees", "Intermediate DSA: Binary Trees & Tree Traversals", "Solve LeetCode Binary Tree Medium problems (Inorder, Preorder, Postorder, Level-order BFS, and Tree Depth)."),
        (35, "DSA", "Trees", "Intermediate DSA: Binary Search Trees (BST) & Lowest Common Ancestor", "Implement BST validation, insertion, deletion, and lowest common ancestor search algorithms."),
        (36, "Backend", "Async Processing", "Asynchronous Background Tasks & Job Queues (Celery / BullMQ / RabbitMQ)", "Build background job workers to handle long-running operations (email sending, image processing) asynchronously."),
        (37, "Backend", "WebSockets", "Real-Time Communication: WebSockets & Server-Sent Events (SSE)", "Build bidirectional real-time WebSocket connection managers supporting user subscriptions and chat broadcasting."),
        (38, "Databases", "PostgreSQL", "Database Connection Pooling & Performance Tuning (PgBouncer)", "Configure connection pool limits, tune statement timeouts, and benchmark database throughput under high concurrent load."),
        (39, "Databases", "NoSQL", "NoSQL Databases: MongoDB Document Modeling & Aggregations", "Design flexible NoSQL document schemas, embed vs reference tradeoffs, and build aggregation pipelines ($match, $group, $lookup)."),
        (40, "Projects", "Backend", "Backend Project Sprint 1: Production REST API with JWT Auth & RBAC", "Build and deploy a scalable RESTful API with full CRUD endpoints, JWT auth, role permissions, and database migrations."),
        (41, "DSA", "Graphs", "Intermediate DSA: Graph Representations & BFS/DFS Traversals", "Implement graph adjacency lists, Breadth-First Search (shortest path in unweighted graphs), and Depth-First Search."),
        (42, "DSA", "Graphs", "Intermediate DSA: Topological Sort & Cycle Detection in Graphs", "Solve dependency resolution problems using Kahn's algorithm (Topological Sort) and cycle detection in directed graphs."),
        (43, "Backend", "Event-Driven", "Event-Driven Architecture & Message Brokers: Kafka / RabbitMQ", "Understand message broker semantics: publish-subscribe topics, consumer groups, offsets, and at-least-once delivery guarantees."),
        (44, "Backend", "Event-Driven", "Building Event Producers & Consumers with Apache Kafka", "Implement Kafka producers and consumer worker pools handling event deserialization and dead letter queues (DLQ)."),
        (45, "Backend", "Security", "Backend Security: SQL Injection, XSS, CSRF & Input Sanitization", "Audit backend endpoints for security vulnerabilities, implement strict input sanitization, and enforce parameterized SQL queries."),
        (46, "Backend", "Logging", "Structured Logging & Observability: OpenTelemetry & Prometheus Metrics", "Emit structured JSON logs with correlation IDs and expose Prometheus `/metrics` endpoints tracking request latency percentiles (p95, p99)."),
        (47, "Backend", "Logging", "Distributed Tracing with Jaeger & Zipkin", "Trace distributed requests across microservices using OpenTelemetry traces and span context propagation."),
        (48, "DSA", "Heaps", "Intermediate DSA: Heaps & Priority Queues (Top K Elements)", "Solve Top K Frequent Elements, Merge K Sorted Lists, and Find Median from Data Stream using min/max heaps."),
        (49, "DSA", "Dynamic Programming", "Intermediate DSA: 1D Dynamic Programming (Climbing Stairs, Coin Change)", "Solve classic 1D Dynamic Programming problems, derive state transition equations, and optimize space complexity from $O(N)$ to $O(1)$."),
        (50, "Projects", "Backend", "Backend Project Sprint 2: Asynchronous Task Queue & Event Pipeline", "Build a high-throughput event processing pipeline with Redis/Kafka message queues, worker pools, and automated retry mechanisms."),
        (51, "CS Fundamentals", "System Design", "System Design Principles: Vertical vs Horizontal Scaling & Load Balancing", "Compare vertical vs horizontal scaling and evaluate load balancing algorithms (Round Robin, Least Connections, Consistent Hashing)."),
        (52, "CS Fundamentals", "System Design", "System Design: Database Sharding, Replication & CAP Theorem", "Analyze master-slave database replication, partition keys, sharding strategies, and CAP theorem consistency tradeoffs."),
        (53, "CS Fundamentals", "System Design", "System Design: Content Delivery Networks (CDN) & Static Asset Caching", "Design globally distributed CDN caching layers with cache invalidation policies and edge compute rules."),
        (54, "Backend", "Microservices", "Microservice Architecture: API Gateways & Service Discovery", "Design API Gateway routing layers with reverse proxying, token verification, and health check service discovery."),
        (55, "Backend", "Microservices", "Inter-Service Communication: gRPC & Protocol Buffers", "Define `.proto` schema contracts and implement high-performance binary gRPC client-server communication."),
        (56, "Backend", "Transactions", "Distributed Transactions: Saga Pattern & Two-Phase Commit (2PC)", "Implement choreograph and orchestrator Saga patterns with compensating transactions for distributed database consistency."),
        (57, "Databases", "Search", "Full-Text Search Engines: Elasticsearch / Meilisearch", "Index complex entity records into Elasticsearch, configure fuzzy search tokenizers, and execute multi-match queries."),
        (58, "DevOps", "Cloud", "Deploying Backend Microservices to AWS (ECS / EKS / App Runner)", "Deploy containerized backend microservices to AWS cloud infrastructure with automated environment variable management."),
        (59, "DSA", "Dynamic Programming", "Intermediate DSA: 2D Dynamic Programming (Grid Paths, Edit Distance)", "Solve classic 2D Dynamic Programming matrix and string alignment problem sets under strict time limits."),
        (60, "Projects", "Backend", "Backend Project Sprint 3: Scalable Microservice Architecture Deployment", "Deploy a complete multi-tier microservice architecture with API Gateway, Redis caching, PostgreSQL DB, and Prometheus monitoring."),
    ]
    for d, cat, skill, title, desc in p2_topics:
        days.append({"day": d, "phase": 2, "category": cat, "skill": skill, "title": f"Day {d}: {title}", "desc": desc, "diff": "Intermediate"})
        
    # --- Phase 3: System Design, Advanced DSA & Placement (Days 61–90) ---
    p3_topics = [
        (61, "CS Fundamentals", "System Design", "System Design Architecture: Designing a URL Shortener (TinyURL)", "Design URL shortening service: base62 encoding vs MD5 hash collisions, database schema, Redis caching, and capacity estimations."),
        (62, "CS Fundamentals", "System Design", "System Design Architecture: Designing a Rate Limiter at Scale", "Design distributed rate limiter handling 500k QPS using Redis sliding window log and token bucket algorithms."),
        (63, "CS Fundamentals", "System Design", "System Design Architecture: Designing a Real-Time Chat System (WhatsApp/Slack)", "Design scalable real-time chat architecture: WebSocket servers, message persistence, presence servers, and Kafka message routing."),
        (64, "CS Fundamentals", "System Design", "System Design Architecture: Designing a Video Streaming Platform (YouTube/Netflix)", "Design video ingestion pipeline: chunking, transcoding into multiple bitrates (HLS/DASH), CDN distribution, and metadata storage."),
        (65, "DSA", "Graphs", "Advanced DSA: Shortest Path Algorithms (Dijkstra, Bellman-Ford)", "Implement Dijkstra's algorithm with priority queues and Bellman-Ford for negative weight edge detection."),
        (66, "DSA", "Dynamic Programming", "Advanced DSA: DP with Bitmasking & Knapsack Optimization", "Solve advanced dynamic programming problems utilizing bitmask states and knapsack variations."),
        (67, "CS Fundamentals", "System Design", "System Design Architecture: Designing a Distributed File Storage System (Google Drive)", "Design file storage service: block-level chunking, deduplication, metadata DB, S3 storage, and client synchronization protocols."),
        (68, "CS Fundamentals", "System Design", "System Design Architecture: Designing an E-Commerce Flash Sale System", "Architect high-concurrency inventory reservation with Redis atomic Lua scripts, optimistic locking, and message queue buffers."),
        (69, "DSA", "DSA", "Advanced LeetCode Problem Solving: Hard Graph & DP Challenges", "Solve 2 LeetCode Hard problems under a 45-minute strict timer simulating live technical screening conditions."),
        (70, "CS Fundamentals", "System Design", "System Design Architecture: Designing a Web Crawler at Scale", "Design distributed web crawler: URL frontier, politeness policies, HTML parsers, duplicate content detection, and storage layers."),
        (71, "Backend", "Backend", "High-Concurrency Performance Benchmarking & Load Testing with k6", "Write k6 load testing scripts, simulate 10,000 concurrent users, and diagnose CPU, memory, and database connection pool bottlenecks."),
        (72, "Interview", "Backend", "Backend Technical Interview Prep: Deep Dive on Database Internals", "Practice explaining database internals: B-Tree indexing mechanisms, WAL (Write-Ahead Logging), and transaction isolation anomalies."),
        (73, "Interview", "Backend", "Backend Technical Interview Prep: Concurrency, Multithreading & Race Conditions", "Practice defending thread synchronization, mutex vs semaphore tradeoffs, and lock-free atomic data structures."),
        (74, "Interview", "Backend", "Backend Technical Interview Prep: REST, gRPC & Distributed Protocols", "Articulate technical tradeoffs between REST, GraphQL, and gRPC for microservice backbones."),
        (75, "Interview", "System Design", "System Design Whiteboard Interview: 4-Step Framework Mastery", "Master the 4-step System Design interview method: (1) Scope & Requirements, (2) High-Level Architecture, (3) Deep-Dive Components, (4) Bottleneck Resolution."),
        (76, "Communication", "Communication", "Backend Behavioral Interview: STAR Method for Production Outages", "Prepare 5 STAR stories highlighting root cause analysis during production incidents, technical leadership, and engineering compromises."),
        (77, "Interview", "Interview", "Mock Technical Interview: Live Algorithmic Problem Solving (DSA)", "Simulate a live 45-minute technical coding interview solving complex data structures and algorithmic challenges."),
        (78, "Interview", "System Design", "Mock Technical Interview: System Design Whiteboard Session", "Simulate a live 45-minute System Design interview designing a scalable distributed service under interviewer probing."),
        (79, "Interview", "Backend", "Mock Technical Interview: Backend Framework & Database Architecture", "Simulate a technical deep dive probing ORM optimization, caching strategies, and API security controls."),
        (80, "Interview", "Interview", "Full Backend Placement Mock Interview Panel Simulation", "Complete a comprehensive 90-minute full mock placement interview covering live coding, System Design, and behavioral rounds."),
        (81, "GitHub", "GitHub", "Backend Portfolio Polish: Documentation, Architecture Diagrams & Live API Demos", "Ensure all GitHub backend repositories feature clear READMEs, OpenAPI specs, architecture diagrams, and live cloud deployment links."),
        (82, "Resume", "Resume", "Final ATS Resume Calibration for Backend Developer Roles", f"Finalize ATS-optimized backend resume with clear metric-backed achievements for {target_role}."),
        (83, "Communication", "Communication", "LinkedIn Profile Optimization & Engineering Networking", "Optimize LinkedIn profile, publish technical writeups on System Design, and connect with engineering leaders."),
        (84, "Interview", "Interview", "Targeted Backend Job Application Sprint", f"Submit 15+ tailored job applications for {target_role} across top product and enterprise engineering teams."),
        (85, "Backend", "Backend", "Code Review Simulation & Clean Architecture Practices", "Review real-world pull requests, enforce hexagonal architecture / clean architecture boundaries, and write constructive code reviews."),
        (86, "Interview", "System Design", "Advanced System Design Drill: Distributed Caching & Idempotency", "Defend distributed idempotency keys in payment processing and multi-datacenter replication strategies."),
        (87, "DSA", "DSA", "Speed Coding Benchmark: 3 Medium LeetCode Problems in 60 Minutes", "Execute rapid timed coding drills to build maximum speed and confidence under interview pressure."),
        (88, "Communication", "Communication", "Job Offer Negotiation & Compensation Strategies for Backend Engineers", "Understand backend engineering compensation packages (base salary, bonus, stock options/RSUs) and negotiation scripts."),
        (89, "Interview", "Interview", "Final Application Follow-ups & Take-Home Code Assessment Submissions", "Complete take-home backend code challenges with unit tests, Docker configs, and comprehensive documentation."),
        (90, "Interview", "Interview", "Final Placement Readiness Evaluation & Career Launch Plan", "Review overall readiness score, celebrate milestone achievements, and finalize ongoing placement interview schedule."),
    ]
    for d, cat, skill, title, desc in p3_topics:
        days.append({"day": d, "phase": 3, "category": cat, "skill": skill, "title": f"Day {d}: {title}", "desc": desc, "diff": "Advanced"})
        
    return days


def _generate_generic_role_curriculum(target_role: str, domain: str, high_gaps: List[str], medium_gaps: List[str]) -> List[Dict[str, Any]]:
    """Generates a dynamic 90-day progressive curriculum for other or custom roles."""
    categories = get_domain_categories(domain)
    primary_cat = categories[0]
    secondary_cat = categories[1] if len(categories) > 1 else categories[0]
    
    gaps = list(dict.fromkeys(high_gaps + medium_gaps))
    g1 = gaps[0] if gaps else f"{target_role} Core Fundamentals"
    g2 = gaps[1] if len(gaps) > 1 else f"{target_role} Advanced Architecture"
    g3 = gaps[2] if len(gaps) > 2 else "System Design & Optimization"
    
    days = []
    # Phase 1: Days 1-30 (Foundation)
    for day in range(1, 31):
        if day == 10:
            days.append({"day": day, "phase": 1, "category": "Resume", "skill": "Resume", "title": f"Day {day}: ATS Resume Optimization for {target_role}", "desc": f"Optimize resume bullet points, highlight technical achievements, and ensure ATS readability for {target_role}.", "diff": "Beginner"})
        elif day == 20:
            days.append({"day": day, "phase": 1, "category": "GitHub", "skill": "GitHub", "title": f"Day {day}: GitHub Portfolio Setup & Project Documentation", "desc": "Initialize clean public repositories, document architectural overviews, and configure environment setup files.", "diff": "Beginner"})
        elif day == 30:
            days.append({"day": day, "phase": 1, "category": primary_cat, "skill": g1, "title": f"Day {day}: Phase 1 Foundation Milestone Benchmark for {target_role}", "desc": f"Complete a comprehensive milestone assessment evaluating core foundations in {g1}.", "diff": "Beginner"})
        else:
            cat = primary_cat if day % 2 == 1 else secondary_cat
            skill = g1 if day % 2 == 1 else f"{target_role} Principles"
            days.append({"day": day, "phase": 1, "category": cat, "skill": skill, "title": f"Day {day}: {skill} — Foundation Module {day}", "desc": f"Master foundational concepts and solve core practice exercises in {skill} tailored for {target_role}.", "diff": "Beginner"})
            
    # Phase 2: Days 31-60 (Skill Development & Projects)
    for day in range(31, 61):
        if day in [40, 50, 60]:
            sprint_num = (day - 30) // 10
            days.append({"day": day, "phase": 2, "category": "Projects", "skill": g2, "title": f"Day {day}: {target_role} Portfolio Project Sprint {sprint_num} — {g2}", "desc": f"Build and test core production features for your portfolio project focusing on {g2} and end-to-end integration.", "diff": "Intermediate"})
        else:
            cat = secondary_cat if day % 2 == 1 else primary_cat
            skill = g2 if day % 2 == 1 else f"{target_role} Frameworks"
            days.append({"day": day, "phase": 2, "category": cat, "skill": skill, "title": f"Day {day}: {skill} — Advanced Implementation Part {day - 30}", "desc": f"Implement intermediate components, optimize modular code patterns, and debug real-world scenarios in {skill}.", "diff": "Intermediate"})
            
    # Phase 3: Days 61-90 (Placement Preparation)
    for day in range(61, 91):
        if day in [75, 80, 85]:
            days.append({"day": day, "phase": 3, "category": "Interview", "skill": f"{target_role} Interview Preparation", "title": f"Day {day}: Mock Technical & Scenario Interview for {target_role}", "desc": f"Conduct a timed mock technical interview simulating live domain problem solving and architecture defense for {target_role}.", "diff": "Advanced"})
        elif day == 81:
            days.append({"day": day, "phase": 3, "category": "Communication", "skill": "Communication", "title": f"Day {day}: Behavioral Interview & STAR Method Mastery", "desc": "Prepare structured STAR method stories highlighting project ownership, technical challenges, and team leadership.", "diff": "Intermediate"})
        elif day == 87:
            days.append({"day": day, "phase": 3, "category": "Resume", "skill": "Resume", "title": f"Day {day}: Final Placement Resume Calibration & Application Audit", "desc": f"Conduct final ATS audit on project bullets and prepare customized applications for {target_role}.", "diff": "Advanced"})
        elif day == 90:
            days.append({"day": day, "phase": 3, "category": "Interview", "skill": f"{target_role} Interview Preparation", "title": f"Day {day}: Final Placement Readiness Evaluation & Career Launch Plan", "desc": f"Complete final placement evaluation, review readiness score, and launch application submissions for {target_role}.", "diff": "Advanced"})
        else:
            cat = "CS Fundamentals" if day % 2 == 1 else "Interview"
            skill = g3 if day % 2 == 1 else f"{target_role} Placement Prep"
            days.append({"day": day, "phase": 3, "category": cat, "skill": skill, "title": f"Day {day}: {skill} — Advanced Architecture & Practice {day - 60}", "desc": f"Deep dive into high-level system design, edge-case optimization, and timed problem solving for {target_role}.", "diff": "Advanced"})
            
    return days


def generate_90_day_curriculum(
    target_role: str,
    daily_minutes: int,
    high_gaps: Optional[List[str]] = None,
    medium_gaps: Optional[List[str]] = None,
    preferred_language: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Main curriculum generator.
    Produces 90 daily tasks with split estimated_minutes strictly summing to daily_minutes.
    """
    high_gaps = high_gaps or []
    medium_gaps = medium_gaps or []
    daily_minutes = max(30, min(int(daily_minutes), 480))
    domain = resolve_role_domain(target_role)
    
    # 1. Fetch progressive 90-day blueprints
    if domain == "cybersecurity":
        blueprints = _generate_cybersecurity_curriculum(target_role, high_gaps)
    elif domain == "aiml":
        blueprints = _generate_aiml_curriculum(target_role, high_gaps)
    elif domain == "backend":
        blueprints = _generate_backend_curriculum(target_role, high_gaps, preferred_language)
    else:
        blueprints = _generate_generic_role_curriculum(target_role, domain, high_gaps, medium_gaps)
        
    all_tasks = []
    
    for bp in blueprints:
        day = bp["day"]
        phase_num = bp["phase"]
        cat = bp["category"]
        skill = bp["skill"]
        title = bp["title"]
        desc = bp["desc"]
        diff = bp["diff"]
        
        # Determine task splits for the day based on available daily minutes
        if daily_minutes <= 45:
            splits = [daily_minutes]
        else:
            m1 = daily_minutes // 2
            m2 = daily_minutes - m1
            splits = [m1, m2]
            
        # Primary task from blueprint
        t1 = {
            "id": f"task_d{day}_1",
            "day": day,
            "category": cat,
            "title": title,
            "description": desc,
            "estimated_minutes": splits[0],
            "difficulty": diff,
            "priority": "High" if day % 2 == 1 or day in [10, 20, 30, 40, 50, 60, 75, 80, 85, 90] else "Medium",
            "skill": skill,
            "status": "pending",
            "phase_number": phase_num,
        }
        all_tasks.append(t1)
        
        # Complementary secondary task if time permits
        if len(splits) > 1:
            if phase_num == 1:
                sec_cat = "DSA" if domain in ["backend", "aiml", "software_engineer", "fullstack"] else ("Networking" if domain == "cybersecurity" else "Programming")
                sec_skill = "Problem Solving" if domain in ["backend", "aiml", "software_engineer"] else ("Network Protocols" if domain == "cybersecurity" else "Core Syntax")
                sec_title = f"Day {day}: Hands-On Practice & Core Drills in {sec_skill}"
                sec_desc = f"Complete interactive practice modules and hands-on drills focusing on {sec_skill} for {target_role}."
                sec_diff = "Beginner"
            elif phase_num == 2:
                sec_cat = "Databases" if domain in ["backend", "fullstack", "data_science"] else ("Threat Intelligence" if domain == "cybersecurity" else "Machine Learning")
                sec_skill = "Database Architecture" if domain in ["backend", "fullstack"] else ("Threat Detection" if domain == "cybersecurity" else "Model Architecture")
                sec_title = f"Day {day}: Applied Implementation Lab — {sec_skill}"
                sec_desc = f"Implement modular lab exercises and component integration testing focusing on {sec_skill} for {target_role}."
                sec_diff = "Intermediate"
            else:
                sec_cat = "Interview" if day % 2 == 1 else "Communication"
                sec_skill = f"{target_role} Interview Prep" if day % 2 == 1 else "STAR Method"
                sec_title = f"Day {day}: Placement Interview Scenario Practice"
                sec_desc = f"Conduct timed practice explaining technical decisions, trade-offs, and domain challenges for {target_role}."
                sec_diff = "Advanced"
                
            t2 = {
                "id": f"task_d{day}_2",
                "day": day,
                "category": sec_cat,
                "title": sec_title,
                "description": sec_desc,
                "estimated_minutes": splits[1],
                "difficulty": sec_diff,
                "priority": "High" if day % 3 == 0 else "Medium",
                "skill": sec_skill,
                "status": "pending",
                "phase_number": phase_num,
            }
            all_tasks.append(t2)
            
    return all_tasks
