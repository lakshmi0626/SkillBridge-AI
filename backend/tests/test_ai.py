from app.services.ai import extract_skills, match_resume, build_roadmap

def test_extract_skills_uses_resume_text():
    assert set(extract_skills("Built APIs in Python with FastAPI and PostgreSQL")) == {"Python", "FastAPI", "PostgreSQL"}
def test_match_is_deterministic_and_explainable():
    args = ("Python SQL FastAPI", "Python SQL FastAPI Docker", ["Python", "SQL", "FastAPI"], ["Python", "SQL", "Docker"], [])
    first = match_resume(*args); second = match_resume(*args)
    assert first == second
    assert first["missing_skills"] == ["Docker"]
    assert "TF-IDF" in first["explanation"]
def test_roadmap_uses_missing_skills():
    result = build_roadmap(["Docker", "Python"])
    assert [x["skill"] for x in result] == ["Python", "Docker"]
