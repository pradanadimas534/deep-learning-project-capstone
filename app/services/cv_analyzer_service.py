"""
cv_analyzer_service.py
----------------------
Service untuk menganalisis teks CV dan menghasilkan:
  - Daftar skills yang terdeteksi
  - Rekomendasi role beserta match percentage
  - Gap skills (skill yang belum dimiliki tapi dibutuhkan)

Tidak memerlukan model ML tambahan — murni rule-based berdasarkan
kategori yang sudah diprediksi oleh CVPredictionService.
"""

from typing import Dict, List, Tuple
import re


# -----------------------------------------------------------------------
# Master data: skill ideal per kategori
# Tambahkan atau sesuaikan sesuai kebutuhan bisnis Anda
# -----------------------------------------------------------------------
SKILL_DATABASE: Dict[str, List[str]] = {
    "Data Science": [
        "Python", "R", "SQL", "Machine Learning", "Deep Learning",
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas",
        "NumPy", "Matplotlib", "Seaborn", "Tableau", "Power BI",
        "Statistics", "Data Visualization", "NLP", "Computer Vision",
        "Spark", "Hadoop", "Jupyter",
    ],
    "Software Engineer": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go",
        "Node.js", "React", "Vue", "Angular", "FastAPI", "Django", "Flask",
        "Spring Boot", "Docker", "Kubernetes", "Git", "REST API", "GraphQL",
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "AWS", "GCP", "Azure",
        "CI/CD", "Linux", "Microservices",
    ],
    "Frontend Developer": [
        "HTML", "CSS", "JavaScript", "TypeScript", "React", "Vue", "Angular",
        "Next.js", "Nuxt.js", "Tailwind CSS", "Bootstrap", "Figma",
        "Webpack", "Vite", "REST API", "GraphQL", "Git", "Responsive Design",
        "Jest", "Cypress",
    ],
    "Backend Developer": [
        "Python", "Java", "Node.js", "Go", "PHP", "C#", "FastAPI",
        "Django", "Flask", "Spring Boot", "Express.js", "Laravel",
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes",
        "REST API", "GraphQL", "Git", "AWS", "Linux", "CI/CD",
    ],
    "DevOps": [
        "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins",
        "GitHub Actions", "GitLab CI", "AWS", "GCP", "Azure", "Linux",
        "Bash", "Python", "Monitoring", "Prometheus", "Grafana",
        "Nginx", "CI/CD", "Git", "Helm",
    ],
    "Mobile Developer": [
        "Flutter", "Dart", "React Native", "Swift", "Kotlin", "Java",
        "Android", "iOS", "Firebase", "REST API", "Git",
        "App Store", "Play Store", "SQLite",
    ],
    "UI/UX Designer": [
        "Figma", "Adobe XD", "Sketch", "Prototyping", "Wireframing",
        "User Research", "Usability Testing", "Design System",
        "Illustrator", "Photoshop", "HTML", "CSS",
    ],
    "Data Analyst": [
        "SQL", "Excel", "Python", "R", "Tableau", "Power BI",
        "Google Analytics", "Statistics", "Data Visualization",
        "Pandas", "NumPy", "Looker",
    ],
    "Cybersecurity": [
        "Network Security", "Penetration Testing", "SIEM", "Firewall",
        "Linux", "Python", "Bash", "Cryptography", "OWASP",
        "Wireshark", "Metasploit", "Incident Response", "ISO 27001",
    ],
    "Project Manager": [
        "Agile", "Scrum", "Kanban", "JIRA", "Confluence", "Trello",
        "Risk Management", "Stakeholder Management", "Budgeting",
        "Communication", "Leadership", "MS Project",
    ],
}

# -----------------------------------------------------------------------
# Rekomendasi role per kategori beserta bobot match dasar
# match % = bobot_dasar + bonus dari jumlah skill yang cocok
# -----------------------------------------------------------------------
REKOMENDASI_DATABASE: Dict[str, List[Dict]] = {
    "Data Science": [
        {"role": "Data Scientist",         "bobot": 80, "skill_bonus": ["Machine Learning", "Deep Learning", "Python"]},
        {"role": "Machine Learning Engineer", "bobot": 75, "skill_bonus": ["TensorFlow", "PyTorch", "Keras", "MLOps"]},
        {"role": "Data Analyst",           "bobot": 70, "skill_bonus": ["SQL", "Tableau", "Power BI"]},
        {"role": "AI Researcher",          "bobot": 65, "skill_bonus": ["NLP", "Computer Vision", "Deep Learning"]},
    ],
    "Software Engineer": [
        {"role": "Frontend Developer",     "bobot": 75, "skill_bonus": ["React", "Vue", "Angular", "JavaScript", "TypeScript"]},
        {"role": "Backend Developer",      "bobot": 75, "skill_bonus": ["Node.js", "FastAPI", "Django", "PostgreSQL", "Docker"]},
        {"role": "Fullstack Developer",    "bobot": 70, "skill_bonus": ["React", "Node.js", "PostgreSQL", "Docker"]},
        {"role": "Software Architect",     "bobot": 60, "skill_bonus": ["Microservices", "Kubernetes", "System Design"]},
    ],
    "Frontend Developer": [
        {"role": "Frontend Developer",     "bobot": 85, "skill_bonus": ["React", "Vue", "TypeScript", "Next.js"]},
        {"role": "UI Engineer",            "bobot": 75, "skill_bonus": ["Figma", "CSS", "Tailwind CSS", "Design System"]},
        {"role": "Fullstack Developer",    "bobot": 65, "skill_bonus": ["Node.js", "REST API", "PostgreSQL"]},
    ],
    "Backend Developer": [
        {"role": "Backend Developer",      "bobot": 85, "skill_bonus": ["Docker", "PostgreSQL", "REST API", "Redis"]},
        {"role": "API Engineer",           "bobot": 75, "skill_bonus": ["GraphQL", "REST API", "FastAPI", "Node.js"]},
        {"role": "DevOps Engineer",        "bobot": 60, "skill_bonus": ["Docker", "Kubernetes", "CI/CD", "AWS"]},
    ],
    "DevOps": [
        {"role": "DevOps Engineer",        "bobot": 85, "skill_bonus": ["Docker", "Kubernetes", "Terraform", "CI/CD"]},
        {"role": "Cloud Engineer",         "bobot": 75, "skill_bonus": ["AWS", "GCP", "Azure", "Terraform"]},
        {"role": "Site Reliability Engineer", "bobot": 70, "skill_bonus": ["Prometheus", "Grafana", "Linux", "Bash"]},
    ],
    "Mobile Developer": [
        {"role": "Android Developer",      "bobot": 80, "skill_bonus": ["Kotlin", "Java", "Android"]},
        {"role": "iOS Developer",          "bobot": 80, "skill_bonus": ["Swift", "iOS", "Xcode"]},
        {"role": "Flutter Developer",      "bobot": 80, "skill_bonus": ["Flutter", "Dart", "Firebase"]},
    ],
    "UI/UX Designer": [
        {"role": "UI Designer",            "bobot": 85, "skill_bonus": ["Figma", "Adobe XD", "Design System"]},
        {"role": "UX Researcher",          "bobot": 75, "skill_bonus": ["User Research", "Usability Testing", "Prototyping"]},
        {"role": "Product Designer",       "bobot": 70, "skill_bonus": ["Wireframing", "Prototyping", "Figma"]},
    ],
    "Data Analyst": [
        {"role": "Data Analyst",           "bobot": 85, "skill_bonus": ["SQL", "Tableau", "Excel", "Power BI"]},
        {"role": "Business Intelligence",  "bobot": 75, "skill_bonus": ["Power BI", "Tableau", "Looker"]},
        {"role": "Data Engineer",          "bobot": 60, "skill_bonus": ["Python", "Spark", "SQL", "Hadoop"]},
    ],
    "Cybersecurity": [
        {"role": "Security Analyst",       "bobot": 85, "skill_bonus": ["SIEM", "Firewall", "Incident Response"]},
        {"role": "Penetration Tester",     "bobot": 75, "skill_bonus": ["Penetration Testing", "Metasploit", "OWASP"]},
        {"role": "Cloud Security Engineer","bobot": 65, "skill_bonus": ["AWS", "ISO 27001", "Cryptography"]},
    ],
    "Project Manager": [
        {"role": "Project Manager",        "bobot": 85, "skill_bonus": ["Agile", "Scrum", "JIRA", "Risk Management"]},
        {"role": "Scrum Master",           "bobot": 75, "skill_bonus": ["Scrum", "Kanban", "Agile", "Confluence"]},
        {"role": "Product Owner",          "bobot": 70, "skill_bonus": ["Agile", "Stakeholder Management", "JIRA"]},
    ],
}

# Fallback jika kategori tidak ada di database
DEFAULT_REKOMENDASI = [
    {"role": "General IT Professional", "bobot": 60, "skill_bonus": []},
]
DEFAULT_SKILLS: List[str] = [
    "Communication", "Problem Solving", "Teamwork", "Git",
]


class CVAnalyzerService:
    """
    Menganalisis teks CV untuk mengekstrak skills,
    menghitung rekomendasi role, dan menentukan gap skills.
    """

    @staticmethod
    def ekstrak_skills(teks_cv: str, kategori: str) -> List[str]:
        """
        Mendeteksi skills dari teks CV berdasarkan master skill per kategori.
        Pencarian case-insensitive dengan word boundary.
        """
        semua_skill = SKILL_DATABASE.get(kategori, DEFAULT_SKILLS)

        # Gabungkan juga skill dari semua kategori lain agar tidak terlewat
        skill_global = set()
        for skills in SKILL_DATABASE.values():
            skill_global.update(skills)

        teks_lower = teks_cv.lower()
        ditemukan = []

        for skill in skill_global:
            # Escape karakter khusus regex (misal C++)
            pola = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pola, teks_lower):
                ditemukan.append(skill)

        # Urutkan: skill relevan dengan kategori muncul duluan
        skill_relevan = [s for s in ditemukan if s in semua_skill]
        skill_lainnya = [s for s in ditemukan if s not in semua_skill]

        return skill_relevan + skill_lainnya

    @staticmethod
    def hitung_rekomendasi(
        kategori: str, skills_dimiliki: List[str]
    ) -> List[Dict]:
        """
        Menghitung rekomendasi role beserta match percentage.
        match = bobot_dasar + bonus per skill_bonus yang dimiliki (max 100)
        """
        daftar_role = REKOMENDASI_DATABASE.get(kategori, DEFAULT_REKOMENDASI)
        skills_set = set(s.lower() for s in skills_dimiliki)

        hasil = []
        for item in daftar_role:
            bonus_per_skill = 5  # +5% per skill bonus yang dimiliki
            bonus = sum(
                bonus_per_skill
                for s in item["skill_bonus"]
                if s.lower() in skills_set
            )
            match = min(item["bobot"] + bonus, 100)
            hasil.append({"role": item["role"], "match": match})

        # Urutkan dari match tertinggi
        hasil.sort(key=lambda x: x["match"], reverse=True)
        return hasil

    @staticmethod
    def hitung_gap_skills(kategori: str, skills_dimiliki: List[str]) -> List[str]:
        """
        Menentukan gap skills: skill ideal untuk kategori yang belum dimiliki.
        Mengembalikan maksimal 8 skill gap teratas.
        """
        skill_ideal = SKILL_DATABASE.get(kategori, DEFAULT_SKILLS)
        skills_lower = set(s.lower() for s in skills_dimiliki)

        gap = [s for s in skill_ideal if s.lower() not in skills_lower]
        return gap[:8]  # batasi 8 gap skill agar tidak overwhelming

    @classmethod
    def analisis(
        cls, teks_cv: str, kategori: str
    ) -> Tuple[List[str], List[Dict], List[str]]:
        """
        Entry point utama. Menjalankan ketiga analisis sekaligus.

        Returns:
            Tuple(skills, rekomendasi, gap_skills)
        """
        skills = cls.ekstrak_skills(teks_cv, kategori)
        rekomendasi = cls.hitung_rekomendasi(kategori, skills)
        gap_skills = cls.hitung_gap_skills(kategori, skills)
        return skills, rekomendasi, gap_skills
