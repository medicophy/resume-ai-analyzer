from __future__ import annotations

import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from config import settings
from models.schemas import AnalyzeResponse
from services.analyzer import AnalysisError, analyze
from services.extractor import UnsupportedFileError

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_JOB_DESCRIPTION_CHARS = 30_000


@router.get("/")
async def root() -> dict[str, str]:
    return {"status": "online", "message": "Resume AI Analyzer Backend Ready"}


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(""),
) -> AnalyzeResponse:
    if len(job_description) > MAX_JOB_DESCRIPTION_CHARS:
        raise HTTPException(status_code=400, detail="The job description is too long (30,000 characters max).")

    # Read one byte past the limit so oversized uploads are rejected without loading them fully.
    file_bytes = await file.read(settings.max_upload_bytes + 1)
    if len(file_bytes) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail=f"The file is larger than {settings.max_upload_mb} MB.")
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        # Parsing is CPU-bound; keep it off the event loop.
        return await run_in_threadpool(analyze, file_bytes, file.filename or "", job_description)
    except (UnsupportedFileError, AnalysisError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Analysis failed for %s", file.filename)
        raise HTTPException(status_code=500, detail="Something went wrong while analysing the resume.") from exc
