import os, uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.core.database import get_db
from app.core.security import current_user, hash_password, verify_password, create_token, admin_user
from app.core.config import settings
from app.models.models import User, Resume, JobDescription, Analysis, SkillProgress
from app.schemas.schemas import RegisterIn, LoginIn, JobIn, UserOut
from app.services.ai import extract_skills, analyze_job, match_resume, build_roadmap

router = APIRouter(prefix="/api")
@router.post("/auth/register", status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(func.lower(User.email) == payload.email.lower()).first(): raise HTTPException(409, "Email is already registered")
    user = User(name=payload.name.strip(), email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"user": UserOut.model_validate(user), "access_token": create_token(user.id), "token_type": "bearer"}
@router.post("/auth/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash): raise HTTPException(401, "Incorrect email or password")
    return {"user": UserOut.model_validate(user), "access_token": create_token(user.id), "token_type": "bearer"}
@router.post("/auth/logout")
def logout(user: User = Depends(current_user)): return {"message": "Signed out. Remove the access token from this client."}
@router.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(current_user)): return user

@router.post("/resumes/upload", status_code=201)
async def upload_resume(file: UploadFile = File(...), user: User = Depends(current_user), db: Session = Depends(get_db)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".docx"}: raise HTTPException(415, "Only PDF and DOCX files are supported")
    data = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if not data or len(data) > settings.max_upload_mb * 1024 * 1024: raise HTTPException(413, f"File must be between 1 byte and {settings.max_upload_mb} MB")
    expected_mimes = {".pdf": {"application/pdf", "application/octet-stream"}, ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/octet-stream"}}
    if file.content_type and file.content_type not in expected_mimes[suffix]: raise HTTPException(415, "File MIME type does not match the selected document format")
    if suffix == ".pdf" and not data.startswith(b"%PDF-"): raise HTTPException(415, "The uploaded file is not a valid PDF document")
    if suffix == ".docx":
        import io, zipfile
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                if "word/document.xml" not in archive.namelist(): raise HTTPException(415, "The uploaded DOCX file is invalid")
        except zipfile.BadZipFile: raise HTTPException(415, "The uploaded DOCX file is invalid")
    os.makedirs(settings.upload_dir, exist_ok=True)
    stored = f"{uuid.uuid4().hex}{suffix}"; path = Path(settings.upload_dir) / stored
    try:
        if suffix == ".pdf":
            import fitz
            doc = fitz.open(stream=data, filetype="pdf"); extracted = "\n".join(page.get_text() for page in doc)
        else:
            from docx import Document
            import io
            doc = Document(io.BytesIO(data)); extracted = "\n".join(p.text for p in doc.paragraphs)
        if not extracted.strip(): raise ValueError("No selectable text found; scanned PDFs require OCR and are not supported yet")
        path.write_bytes(data)
    except Exception as exc: raise HTTPException(422, f"Could not extract resume text: {str(exc)[:180]}")
    resume = Resume(user_id=user.id, filename=Path(file.filename or "resume").name, stored_path=str(path), extracted_text=extracted[:100000], skills=extract_skills(extracted))
    db.add(resume); db.commit(); db.refresh(resume)
    return {"id": resume.id, "filename": resume.filename, "skills": resume.skills, "text_characters": len(extracted), "created_at": resume.created_at}
@router.get("/resumes")
def list_resumes(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{"id": r.id, "filename": r.filename, "skills": r.skills, "created_at": r.created_at} for r in db.query(Resume).filter_by(user_id=user.id).order_by(desc(Resume.created_at)).all()]
@router.get("/resumes/{resume_id}")
def get_resume(resume_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    r = db.query(Resume).filter_by(id=resume_id, user_id=user.id).first()
    if not r: raise HTTPException(404, "Resume not found")
    return {"id": r.id, "filename": r.filename, "skills": r.skills, "text": r.extracted_text}
@router.delete("/resumes/{resume_id}")
def delete_resume(resume_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    r = db.query(Resume).filter_by(id=resume_id, user_id=user.id).first()
    if not r: raise HTTPException(404, "Resume not found")
    try: Path(r.stored_path).unlink(missing_ok=True)
    except OSError: pass
    db.delete(r); db.commit(); return {"message": "Resume deleted"}

@router.post("/jobs/analyze", status_code=201)
def create_job(payload: JobIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    required, preferred = analyze_job(payload.description)
    job = JobDescription(user_id=user.id, title=payload.title, company=payload.company, description=payload.description, required_skills=required, preferred_skills=preferred)
    db.add(job); db.commit(); db.refresh(job)
    return {"id": job.id, "title": job.title, "company": job.company, "required_skills": required, "preferred_skills": preferred}
@router.get("/jobs")
def list_jobs(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{"id": j.id, "title": j.title, "company": j.company, "required_skills": j.required_skills, "preferred_skills": j.preferred_skills, "created_at": j.created_at} for j in db.query(JobDescription).filter_by(user_id=user.id).order_by(desc(JobDescription.created_at)).all()]
@router.get("/jobs/{job_id}")
def get_job(job_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    j = db.query(JobDescription).filter_by(id=job_id, user_id=user.id).first()
    if not j: raise HTTPException(404, "Job description not found")
    return {"id": j.id, "title": j.title, "company": j.company, "description": j.description, "required_skills": j.required_skills, "preferred_skills": j.preferred_skills}

@router.post("/matching/analyze", status_code=201)
def matching(resume_id: int, job_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter_by(id=resume_id, user_id=user.id).first(); job = db.query(JobDescription).filter_by(id=job_id, user_id=user.id).first()
    if not resume or not job: raise HTTPException(404, "Resume or job description not found")
    result = match_resume(resume.extracted_text, job.description, resume.skills, job.required_skills, job.preferred_skills)
    row = Analysis(user_id=user.id, resume_id=resume.id, job_id=job.id, **result)
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "job_title": job.title, **result, "created_at": row.created_at}
@router.get("/matching/history")
def history(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Analysis).filter_by(user_id=user.id).order_by(desc(Analysis.created_at)).limit(50).all()
    return [{"id": a.id, "score": a.score, "matching_skills": a.matching_skills, "missing_skills": a.missing_skills, "created_at": a.created_at, "job_title": db.get(JobDescription, a.job_id).title} for a in rows]
@router.get("/matching/{analysis_id}")
def get_analysis(analysis_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.query(Analysis).filter_by(id=analysis_id, user_id=user.id).first()
    if not a: raise HTTPException(404, "Analysis not found")
    return {"id": a.id, "score": a.score, "skill_coverage": a.skill_coverage, "matching_skills": a.matching_skills, "missing_skills": a.missing_skills, "additional_skills": a.additional_skills, "explanation": a.explanation}
@router.get("/skills")
def skills(user: User = Depends(current_user), db: Session = Depends(get_db)):
    resumes = db.query(Resume).filter_by(user_id=user.id).all(); return {"skills": sorted({s for r in resumes for s in r.skills})}
@router.get("/skills/gaps")
def gaps(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Analysis).filter_by(user_id=user.id).order_by(desc(Analysis.created_at)).all()
    return {"missing_skills": sorted({s for a in rows for s in a.missing_skills})}
@router.patch("/skills/progress")
def update_progress(skill: str, status_value: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if status_value not in {"Not Started", "Learning", "Practicing", "Completed"}: raise HTTPException(422, "Invalid progress status")
    row = db.query(SkillProgress).filter_by(user_id=user.id, skill=skill).first()
    if not row: row = SkillProgress(user_id=user.id, skill=skill); db.add(row)
    row.status = status_value; db.commit(); return {"skill": skill, "status": row.status}
@router.get("/career/recommendations")
def recommendations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    skills_set = {s for r in db.query(Resume).filter_by(user_id=user.id).all() for s in r.skills}
    roles = {"Python Developer": {"Python", "SQL", "Git", "FastAPI", "Docker"}, "Frontend Developer": {"JavaScript", "HTML", "CSS", "React", "Git"}, "Full Stack Developer": {"JavaScript", "React", "Node.js", "SQL", "Docker"}, "Data Analyst": {"Python", "SQL", "Pandas", "Excel", "Power BI"}, "AI Engineer": {"Python", "Machine Learning", "Deep Learning", "NLP", "Docker"}}
    return sorted([{"role": name, "score": round(100*len(skills_set & needed)/len(needed), 1), "matching_skills": sorted(skills_set & needed), "missing_skills": sorted(needed-skills_set)} for name, needed in roles.items()], key=lambda x: x["score"], reverse=True)
@router.post("/career/roadmaps")
def create_roadmap(analysis_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.query(Analysis).filter_by(id=analysis_id, user_id=user.id).first()
    if not a: raise HTTPException(404, "Analysis not found")
    return {"analysis_id": a.id, "milestones": build_roadmap(a.missing_skills)}
@router.get("/career/roadmaps")
def roadmaps(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Analysis).filter_by(user_id=user.id).order_by(desc(Analysis.created_at)).all()
    return [{"analysis_id": a.id, "milestones": build_roadmap(a.missing_skills)} for a in rows]
@router.patch("/career/roadmaps/{analysis_id}/progress")
def roadmap_progress(analysis_id: int, skill: str, status_value: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.query(Analysis).filter_by(id=analysis_id, user_id=user.id).first()
    if not a or skill not in a.missing_skills: raise HTTPException(404, "Roadmap skill not found")
    return update_progress(skill, status_value, user, db)
@router.get("/dashboard/summary")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    resumes = db.query(Resume).filter_by(user_id=user.id).count(); analyses = db.query(Analysis).filter_by(user_id=user.id).all(); progress = db.query(SkillProgress).filter_by(user_id=user.id).all()
    return {"resume_count": resumes, "analysis_count": len(analyses), "average_score": round(sum(a.score for a in analyses)/len(analyses), 1) if analyses else 0, "skills_identified": len({s for r in db.query(Resume).filter_by(user_id=user.id).all() for s in r.skills}), "missing_skills": len({s for a in analyses for s in a.missing_skills}), "learning_progress": round(100*sum(p.status == "Completed" for p in progress)/len(progress), 1) if progress else 0, "recent_analyses": [{"id": a.id, "score": a.score, "created_at": a.created_at, "job_title": db.get(JobDescription, a.job_id).title} for a in analyses[:5]]}
@router.get("/dashboard/analytics")
def analytics(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"matching_history": [{"date": a.created_at.date().isoformat(), "score": a.score} for a in db.query(Analysis).filter_by(user_id=user.id).order_by(Analysis.created_at).all()], "skill_distribution": {s: sum(s in r.skills for r in db.query(Resume).filter_by(user_id=user.id).all()) for s in sorted({s for r in db.query(Resume).filter_by(user_id=user.id).all() for s in r.skills})}}
@router.get("/reports/{analysis_id}/pdf")
def report(analysis_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    from fastapi.responses import StreamingResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
    from reportlab.lib.styles import getSampleStyleSheet
    from io import BytesIO
    from xml.sax.saxutils import escape
    a = db.query(Analysis).filter_by(id=analysis_id, user_id=user.id).first()
    if not a: raise HTTPException(404, "Analysis not found")
    job = db.get(JobDescription, a.job_id); buf = BytesIO(); doc = SimpleDocTemplate(buf, pagesize=A4); styles = getSampleStyleSheet()
    story = [Paragraph("SkillBridge AI — Career Match Report", styles["Title"]), Spacer(1, 14), Paragraph(f"Candidate: {escape(user.name)}", styles["Normal"]), Paragraph(f"Role: {escape(job.title)}", styles["Normal"]), Paragraph(f"Compatibility score: {a.score}%", styles["Heading2"]), Paragraph(f"Required skill coverage: {a.skill_coverage}%", styles["Normal"]), Spacer(1, 12), Paragraph("Matching skills", styles["Heading2"]), Paragraph(escape(", ".join(a.matching_skills)) or "None identified", styles["BodyText"]), Paragraph("Missing skills", styles["Heading2"]), Paragraph(escape(", ".join(a.missing_skills)) or "None identified", styles["BodyText"]), Paragraph("Scoring explanation", styles["Heading2"]), Paragraph(escape(a.explanation), styles["BodyText"]), Paragraph("Suggested learning sequence", styles["Heading2"])]
    story += [Paragraph(f"Week {m['week']}: {m['skill']} — {m['milestone']}", styles["BodyText"]) for m in build_roadmap(a.missing_skills)]
    doc.build(story); buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=skillbridge-analysis-{a.id}.pdf"})
@router.get("/admin/users")
def admin_users(user: User = Depends(admin_user), db: Session = Depends(get_db)):
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role, "is_active": u.is_active} for u in db.query(User).order_by(User.id).limit(200).all()]
@router.get("/admin/analytics")
def admin_analytics(user: User = Depends(admin_user), db: Session = Depends(get_db)):
    return {"users": db.query(User).count(), "resumes": db.query(Resume).count(), "analyses": db.query(Analysis).count()}
@router.get("/skills/progress")
def skill_progress(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{"skill": p.skill, "status": p.status, "updated_at": p.updated_at} for p in db.query(SkillProgress).filter_by(user_id=user.id).order_by(SkillProgress.skill).all()]
