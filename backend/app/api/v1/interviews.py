from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.interview import Interview
from app.schemas.interview import InterviewCreate, InterviewRead
from app.services.analysis import analyze_text, text_from_file
from app.schemas.insight import AggregatedAnalysis
from app.services.insight_parser import parse_insights, format_insights_for_display


router = APIRouter(prefix="/interviews")


@router.post("", response_model=InterviewRead)

def create_interview(payload: InterviewCreate, db: Session = Depends(get_db)):
    analysis = analyze_text(payload.transcript, getattr(payload, "product_description", None))
    interview = Interview(title=payload.title, transcript=payload.transcript, analysis=analysis)
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


@router.post("/upload", response_model=InterviewRead)

def create_interview_from_files(
    files: List[UploadFile] = File(...),
    title: Optional[str] = Form(None),
    product_description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Build combined transcript with per-file headers for reference
    combined_texts: List[str] = []

    # Aggregate insights and track irrelevant files
    aggregated_insights = []
    irrelevant_files: List[str] = []

    for f in files:
        try:
            content = f.file.read()
        except Exception:
            content = b""
        extracted = text_from_file(f.filename or "document", content)

        filename_label = f.filename or "document"
        header = f"===== {filename_label} =====\n"
        if extracted:
            combined_texts.append(header + extracted)
            # Run LLM analysis per file
            raw_analysis = analyze_text(extracted, product_description)
            insights = parse_insights(raw_analysis)
            if insights:
                for ins in insights:
                    # Attach source filename for later display
                    try:
                        ins.source_filename = filename_label
                    except Exception:
                        pass
                aggregated_insights.extend(insights)
            else:
                irrelevant_files.append(filename_label)
        else:
            # No text extracted → mark as irrelevant
            irrelevant_files.append(filename_label)

    if not combined_texts:
        # No text could be extracted from any file
        raise HTTPException(status_code=400, detail="Unable to extract text from uploaded files")

    combined_text = "\n\n".join(combined_texts)
    final_title = title or (files[0].filename if files and files[0].filename else "Uploaded Interview")

    if not aggregated_insights:
        # All files produced no insights
        message = (
            "Analysis can't be conducted because all provided files are not transcripts of the interviews."
        )
        if irrelevant_files:
            message += "\n\nIrrelevant files: " + ", ".join(sorted(set(irrelevant_files)))
        analysis_for_storage = message
    else:
        aggregated = AggregatedAnalysis(insights=aggregated_insights, irrelevant_files=sorted(set(irrelevant_files)))
        analysis_for_storage = format_insights_for_display(aggregated)

    interview = Interview(title=final_title, transcript=combined_text, analysis=analysis_for_storage)
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