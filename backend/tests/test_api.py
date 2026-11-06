import os, uuid, io
os.environ["DATABASE_URL"] = "sqlite:///./test_skillbridge.db"
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine
Base.metadata.create_all(bind=engine)
client = TestClient(app)

def test_register_login_and_protected_profile():
    email = f"qa-{uuid.uuid4().hex}@example.com"
    r = client.post("/api/auth/register", json={"name":"QA User", "email":email, "password":"StrongPass123"})
    assert r.status_code == 201
    token = r.json()["access_token"]
    assert client.get("/api/auth/me", headers={"Authorization":f"Bearer {token}"}).status_code == 200
    login = client.post("/api/auth/login", json={"email":email, "password":"StrongPass123"})
    assert login.status_code == 200
    assert client.get("/api/auth/me").status_code == 401


def test_resume_to_report_workflow():
    email = f"flow-{uuid.uuid4().hex}@example.com"
    registered = client.post("/api/auth/register", json={"name":"Flow User", "email":email, "password":"StrongPass123"})
    assert registered.status_code == 201
    headers = {"Authorization": f"Bearer {registered.json()['access_token']}"}
    import fitz
    pdf = fitz.open(); page = pdf.new_page(); page.insert_text((72, 72), "Python SQL Git FastAPI Docker. Built REST APIs and database projects.")
    pdf_bytes = pdf.tobytes(); pdf.close()
    uploaded = client.post("/api/resumes/upload", headers=headers, files={"file":("resume.pdf", pdf_bytes, "application/pdf")})
    assert uploaded.status_code == 201, uploaded.text
    resume_id = uploaded.json()["id"]
    rejected = client.post("/api/resumes/upload", headers=headers, files={"file":("bad.exe", b"not a resume", "application/octet-stream")})
    assert rejected.status_code == 415
    from docx import Document
    docx_buffer = io.BytesIO(); word_doc = Document(); word_doc.add_paragraph("Experience with JavaScript, React, and MongoDB")
    word_doc.save(docx_buffer)
    docx_upload = client.post("/api/resumes/upload", headers=headers, files={"file":("resume.docx", docx_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
    assert docx_upload.status_code == 201 and "React" in docx_upload.json()["skills"]
    outsider = client.post("/api/auth/register", json={"name":"Other User", "email":f"other-{uuid.uuid4().hex}@example.com", "password":"StrongPass123"})
    other_headers = {"Authorization": f"Bearer {outsider.json()['access_token']}"}
    private_read = client.get(f"/api/resumes/{resume_id}", headers=other_headers)
    assert private_read.status_code == 404
    job = client.post("/api/jobs/analyze", headers=headers, json={"title":"Python Engineer", "company":"Example Co", "description":"We need Python, SQL, FastAPI, Docker and Kubernetes skills to build APIs."})
    assert job.status_code == 201, job.text
    analysis = client.post(f"/api/matching/analyze?resume_id={resume_id}&job_id={job.json()['id']}", headers=headers)
    assert analysis.status_code == 201, analysis.text
    result = analysis.json()
    assert result["score"] >= 0 and result["score"] <= 100
    assert "Kubernetes" in result["missing_skills"]
    roadmap = client.post(f"/api/career/roadmaps?analysis_id={result['id']}", headers=headers)
    assert roadmap.status_code == 200 and any(m["skill"] == "Kubernetes" for m in roadmap.json()["milestones"])
    progress = client.patch("/api/skills/progress?skill=Kubernetes&status_value=Learning", headers=headers)
    assert progress.status_code == 200 and progress.json()["status"] == "Learning"
    report = client.get(f"/api/reports/{result['id']}/pdf", headers=headers)
    assert report.status_code == 200 and report.headers["content-type"] == "application/pdf"
    assert report.content.startswith(b"%PDF")
