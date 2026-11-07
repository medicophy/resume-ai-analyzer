from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Priority = Literal["required", "preferred"]
MatchStatus = Literal["demonstrated", "listed", "related", "missing"]


class Evidence(BaseModel):
    section: str
    text: str


class SkillMatch(BaseModel):
    skill: str
    category: str
    priority: Priority
    status: MatchStatus = Field(
        description=(
            "demonstrated: used in experience/projects; listed: only in skills/summary; "
            "related: a related skill was found instead; missing: not found"
        )
    )
    related_to: str | None = None
    evidence: list[Evidence] = []


class ComponentScore(BaseModel):
    score: float
    weight: float = Field(description="Share of the overall score after excluding components that don't apply")


class ScoreBreakdown(BaseModel):
    skills: ComponentScore | None = None
    experience: ComponentScore | None = None
    education: ComponentScore | None = None


class YearsCheck(BaseModel):
    skill: str | None = Field(description="None for general professional experience")
    required_years: int
    resume_years: float
    priority: Priority
    met: bool


class ExperienceSummary(BaseModel):
    total_years: float
    roles_found: int
    checks: list[YearsCheck] = []


class EducationCheck(BaseModel):
    required_level: str
    resume_level: str | None
    priority: Priority
    equivalent_experience_ok: bool
    met: bool


class Suggestion(BaseModel):
    priority: Literal["high", "medium", "low"]
    message: str
    skill: str | None = None


class AtsCheck(BaseModel):
    id: str
    label: str
    status: Literal["pass", "warn", "fail"]
    severity: Literal["critical", "major", "minor"]
    message: str
    fix: str | None = None


class AtsReport(BaseModel):
    score: float = Field(description="0-100: how easily applicant tracking systems can read the resume")
    checks: list[AtsCheck]


class AiRewrite(BaseModel):
    original: str = Field(description="A line taken from the resume")
    suggested: str = Field(description="Draft rewrite; only use it if it is true")
    skills: list[str] = []
    reason: str


class AiRequirement(BaseModel):
    term: str
    priority: Priority
    found_in_resume: bool = Field(description="Checked by text search in the resume, not by the AI")


class AiReview(BaseModel):
    summary: str
    rewrites: list[AiRewrite]
    extra_requirements: list[AiRequirement] = Field(
        description="Requirements the AI found that the rule-based skill list doesn't cover"
    )
    model: str


class ExtractionInfo(BaseModel):
    file_type: Literal["pdf", "docx"]
    page_count: int
    char_count: int
    quality: Literal["good", "low", "empty"]


class AnalyzeResponse(BaseModel):
    filename: str
    overall_score: float | None = Field(description="0-100, or None when nothing in the job description could be scored")
    breakdown: ScoreBreakdown
    skills: list[SkillMatch]
    experience: ExperienceSummary
    education: EducationCheck | None
    suggestions: list[Suggestion]
    warnings: list[str]
    extraction: ExtractionInfo
    ats: AtsReport = Field(description="Resume readability for applicant tracking systems; separate from the job match score")

    # Kept for the existing frontend; prefer the fields above.
    match_score: float
    missing_keywords: list[str]
    char_count: int
