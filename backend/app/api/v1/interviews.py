from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.interview import Interview
from app.schemas.interview import InterviewCreate, InterviewRead
from app.services.analysis import analyze_text, text_from_file

router = APIRouter(prefix="/interviews")


@router.post("", response_model=InterviewRead)
def create_interview(payload: InterviewCreate, db: Session = Depends(get_db)):
    analysis = analyze_text(payload.transcript)
    interview = Interview(title=payload.title, transcript=payload.transcript, analysis=analysis)
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


@router.post("/upload", response_model=InterviewRead)
def create_interview_from_files(
    files: List[UploadFile] = File(...),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    texts: List[str] = []
    for f in files:
        content = f.file.read()
        extracted = text_from_file(f.filename or "document", content)
        if extracted:
            header = f"===== {f.filename} =====\n" if f.filename else ""
            texts.append(header + extracted)
    if not texts:
        raise HTTPException(status_code=400, detail="Unable to extract text from uploaded files")

    combined_text = "\n\n".join(texts)
    final_title = title or (files[0].filename if files and files[0].filename else "Uploaded Interview")

    analysis = analyze_text(combined_text)
    interview = Interview(title=final_title, transcript=combined_text, analysis=analysis)
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


@router.get("", response_model=List[InterviewRead])
def list_interviews(db: Session = Depends(get_db)):
    return db.query(Interview).order_by(Interview.id.desc()).all()


@router.get("/{interview_id}", response_model=InterviewRead)
def get_interview(interview_id: int, db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview 