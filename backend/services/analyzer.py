"""End-to-end analysis: extract, parse, match, score."""

from __future__ import annotations

from datetime import date

from models.schemas import AnalyzeResponse, ExtractionInfo
from services.ats import run_ats_checks
from services.extractor import extract_text
from services.jd_parser import parse_job_description
from services.matcher import match_skills, sections_recognized
from services.resume_parser import parse_resume
from services.scorer import (
    apply_relevance_cap,
    assess_education,
    assess_experience,
    build_suggestions,
    combine,
    required_skills_score,
    skills_score,
)


class AnalysisError(ValueError):
    """The inputs can't be analysed (unreadable resume, empty job description...)."""


def analyze(file_bytes: bytes, filename: str, job_description: str, today: date | None = None) -> AnalyzeResponse:
    if not job_description.strip():
        raise AnalysisError("Please paste a job description.")

    extraction = extract_text(file_bytes, filename)
    if extraction.quality == "empty":
        raise AnalysisError(extraction.warnings[0] if extraction.warnings else "No text could be read from the resume.")

    resume = parse_resume(extraction.text, today)
    jd = parse_job_description(job_description)
    warnings = list(extraction.warnings)

    matches = match_skills(resume, jd)
    experience, experience_score = assess_experience(resume, jd)
    education, education_score = assess_education(resume, jd, experience.total_years)

    if not jd.skills:
        warnings.append(
            "No recognisable skills were found in the job description, so the skills score was skipped. "
            "Check that you pasted the full posting, including its requirements."
        )
    if not sections_recognized(resume):
        warnings.append(
            "No standard section headings (Experience, Skills, Education) were found in the resume. "
            "Clear headings help applicant tracking systems read it."
        )
    if jd.years and not resume.date_ranges:
        warnings.append("No employment dates were found, so years of experience could not be counted.")

    overall, breakdown = combine({
        "skills": skills_score(matches),
        "experience": experience_score,
        "education": education_score,
    })
    overall, capped = apply_relevance_cap(overall, required_skills_score(matches))
    if capped:
        warnings.append(
            "Most of the required skills are missing, so the overall score is capped: "
            "experience and education only count fully when they are in the right field."
        )
    if overall is None:
        warnings.append("Nothing in the job description could be scored (no skills, experience or degree requirements found).")

    return AnalyzeResponse(
        filename=filename,
        overall_score=overall,
        breakdown=breakdown,
        skills=matches,
        experience=experience,
        education=education,
        suggestions=build_suggestions(matches, experience, education, resume),
        warnings=warnings,
        extraction=ExtractionInfo(
            file_type=extraction.file_type,
            page_count=extraction.page_count,
            char_count=extraction.char_count,
            quality=extraction.quality,
        ),
        ats=run_ats_checks(extraction, resume),
        match_score=overall or 0.0,
        missing_keywords=[m.skill for m in matches if m.status == "missing"],
        char_count=extraction.char_count,
    )
