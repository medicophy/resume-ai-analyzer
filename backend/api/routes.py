from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TypeVar

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from config import settings
from models.schemas import AiReview, AnalyzeResponse
from services.ai_review import AiNotConfigured, AiUnavailable
from services.analyzer import AnalysisError, ai_review, analyze
from services.extractor import UnsupportedFileError

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_JOB_DESCRIPTION_CHARS = 30_000
T = TypeVar("T")


@router.get("/")
async def root() -> dict[str, object]:
    return {
        "status": "online",
        "message": "Resume AI Analyzer Backend Ready",
        "ai_enabled": settings.ai_enabled,
    }


async def _read_inputs(file: UploadFile, job_description: str) -> bytes:
    if len(job_description) > MAX_JOB_DESCRIPTION_CHARS:
        raise HTTPException(status_code=400, detail="The job description is too long (30,000 characters max).")
    # Read one byte past the limit so oversized uploads are rejected without loading them fully.
    file_bytes = await file.read(settings.max_upload_bytes + 1)
    if len(file_bytes) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail=f"The file is larger than {settings.max_upload_mb} MB.")
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    return file_bytes


async def _run(func: Callable[..., T], *args, filename: str | None) -> T:
    try:
        # Parsing and the AI call are blocking; keep them off the event loop.
        return await run_in_threadpool(func, *args)
    except (UnsupportedFileError, AnalysisError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AiNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AiUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Request failed for %s", filename)
        raise HTTPException(status_code=500, detail="Something went wrong while analysing the resume.") from exc


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(file: UploadFile = File(...), job_description: str = Form("")) -> AnalyzeResponse:
    file_bytes = await _read_inputs(file, job_description)
    return await _run(analyze, file_bytes, file.filename or "", job_description, filename=file.filename)


@router.post("/ai-review", response_model=AiReview)
async def ai_review_resume(file: UploadFile = File(...), job_description: str = Form("")) -> AiReview:
    if not settings.ai_enabled:
        raise HTTPException(status_code=503, detail="AI suggestions are not set up. Add GROQ_API_KEY to backend/.env.")
    file_bytes = await _read_inputs(file, job_description)
    return await _run(ai_review, file_bytes, file.filename or "", job_description, filename=file.filename)
