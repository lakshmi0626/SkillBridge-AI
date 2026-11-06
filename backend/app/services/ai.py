import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILL_CATALOG = {
 "Python": ["python"], "Java": ["java"], "JavaScript": ["javascript", "js"], "TypeScript": ["typescript"],
 "React": ["react", "react.js"], "FastAPI": ["fastapi"], "Flask": ["flask"], "Django": ["django"],
 "Node.js": ["node.js", "nodejs"], "Express": ["express.js", "express"], "HTML": ["html"], "CSS": ["css"],
 "SQL": ["sql"], "PostgreSQL": ["postgresql", "postgres"], "MySQL": ["mysql"], "MongoDB": ["mongodb"],
 "Redis": ["redis"], "Docker": ["docker"], "Kubernetes": ["kubernetes", "k8s"], "AWS": ["aws", "amazon web services"],
 "Azure": ["azure"], "Git": ["git"], "GitHub Actions": ["github actions"], "Linux": ["linux"],
 "Machine Learning": ["machine learning", "scikit-learn", "sklearn"], "Deep Learning": ["deep learning", "pytorch", "tensorflow"],
 "NLP": ["nlp", "natural language processing"], "Pandas": ["pandas"], "NumPy": ["numpy"], "Excel": ["excel"],
 "Power BI": ["power bi"], "Tableau": ["tableau"], "REST API": ["rest api", "restful"], "GraphQL": ["graphql"],
 "Testing": ["pytest", "unit testing", "testing"], "Agile": ["agile", "scrum"]
}
def extract_skills(text: str) -> list[str]:
    source = text.lower()
    found = []
    for canonical, aliases in SKILL_CATALOG.items():
        if any(re.search(r"(?<![a-z0-9+#])" + re.escape(a.lower()) + r"(?![a-z0-9+#])", source) for a in aliases): found.append(canonical)
    return sorted(found)
def analyze_job(description: str):
    skills = extract_skills(description)
    preferred = [s for s in skills if re.search(r"(preferred|nice.to.have|bonus|plus)[^\n.]{0,100}" + re.escape(s), description, re.I)]
    return [s for s in skills if s not in preferred], preferred
def similarity(a: str, b: str) -> float:
    if not a.strip() or not b.strip(): return 0.0
    try:
        matrix = TfidfVectorizer(stop_words="english", ngram_range=(1,2), max_features=5000).fit_transform([a, b])
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    except ValueError: return 0.0
def match_resume(resume_text: str, job_text: str, resume_skills: list[str], required: list[str], preferred: list[str]):
    present = set(resume_skills)
    matched = sorted(present.intersection(required + preferred))
    missing = sorted(set(required) - present)
    additional = sorted(present - set(required + preferred))
    required_coverage = len(set(required) & present) / max(1, len(set(required)))
    preferred_coverage = len(set(preferred) & present) / max(1, len(set(preferred))) if preferred else 1.0
    text_score = similarity(resume_text, job_text)
    score = round(100 * (0.65 * required_coverage + 0.10 * preferred_coverage + 0.25 * text_score), 1)
    return {"score": score, "skill_coverage": round(required_coverage * 100, 1), "matching_skills": matched, "missing_skills": missing, "additional_skills": additional,
            "explanation": f"Score = 65% required-skill coverage ({required_coverage:.0%}) + 10% preferred-skill coverage ({preferred_coverage:.0%}) + 25% TF-IDF text similarity ({text_score:.0%}). This is an explainable comparison aid, not an employer ATS score."}
def build_roadmap(missing: list[str]):
    priority_order = ["Python", "Java", "JavaScript", "HTML", "CSS", "SQL", "Git", "React", "Node.js", "FastAPI", "Django", "PostgreSQL", "Docker", "AWS", "Machine Learning", "NLP"]
    ordered = sorted(missing, key=lambda s: priority_order.index(s) if s in priority_order else len(priority_order))
    return [{"week": i + 1, "skill": skill, "milestone": f"Study {skill} fundamentals and complete one practical exercise", "project": f"Build a small portfolio feature demonstrating {skill}", "status": "Not Started"} for i, skill in enumerate(ordered)]
