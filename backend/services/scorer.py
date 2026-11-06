"""Score a resume against parsed job requirements and generate suggestions."""

from __future__ import annotations

from models.schemas import (
    ComponentScore,
    EducationCheck,
    ExperienceSummary,
    ScoreBreakdown,
    SkillMatch,
    Suggestion,
    YearsCheck,
)
from services.dates import total_years
from services.education import DEGREE_RANK
from services.jd_parser import JobRequirements
from services.matcher import STATUS_CREDIT
from services.resume_parser import ParsedResume
from services.skills import load_catalog

# Base weights. Components the job description says nothing about are dropped and the
# rest re-normalised, so a JD without a degree requirement isn't scored on education.
WEIGHTS = {"skills": 0.60, "experience": 0.25, "education": 0.15}
REQUIRED_SHARE = 0.75  # within the skills score: required vs preferred skills

LEVEL_LABEL = {"associate": "an associate degree", "bachelor": "a bachelor's degree",
               "master": "a master's degree", "doctorate": "a doctorate"}


# --- components -------------------------------------------------------------------------

def skills_score(matches: list[SkillMatch]) -> float | None:
    def avg(items: list[SkillMatch]) -> float | None:
        return sum(STATUS_CREDIT[m.status] for m in items) / len(items) * 100 if items else None

    required = avg([m for m in matches if m.priority == "required"])
    preferred = avg([m for m in matches if m.priority == "preferred"])
    if required is not None and preferred is not None:
        return REQUIRED_SHARE * required + (1 - REQUIRED_SHARE) * preferred
    return required if required is not None else preferred


def skill_years(resume: ParsedResume, skill: str) -> float:
    """Years across the roles whose text mentions the skill (overlaps counted once)."""
    catalog = load_catalog()
    ranges = [e.dates for e in resume.experience_entries if catalog.mentions(skill, e.text)]
    return total_years(ranges)


def assess_experience(resume: ParsedResume, jd: JobRequirements) -> tuple[ExperienceSummary, float | None]:
    total = total_years(resume.date_ranges)
    checks: list[YearsCheck] = []
    weighted: list[tuple[float, float]] = []  # (score, weight)

    seen: set[tuple[str | None, str]] = set()
    for req in sorted(jd.years, key=lambda r: -r.years):
        key = (req.skill, req.priority)
        if key in seen:  # keep the strictest requirement per skill
            continue
        seen.add(key)
        have = skill_years(resume, req.skill) if req.skill else total
        met = have >= req.years
        checks.append(YearsCheck(skill=req.skill, required_years=req.years, resume_years=have,
                                 priority=req.priority, met=met))
        score = 100.0 if met else 100.0 * have / req.years
        weight = (2.0 if req.skill is None else 1.0) * (1.0 if req.priority == "required" else 0.5)
        weighted.append((score, weight))

    summary = ExperienceSummary(total_years=total, roles_found=len(resume.experience_entries), checks=checks)
    if not weighted:
        return summary, None
    return summary, sum(s * w for s, w in weighted) / sum(w for _, w in weighted)


def assess_education(resume: ParsedResume, jd: JobRequirements, total_exp: float) -> tuple[EducationCheck | None, float | None]:
    req = jd.education
    if req is None:
        return None, None
    have_rank = DEGREE_RANK.get(resume.highest_degree or "", 0)
    need_rank = DEGREE_RANK[req.level]
    met = have_rank >= need_rank

    if met:
        score = 100.0
    elif req.equivalent_experience_ok and total_exp >= 4:
        score = 80.0
    elif have_rank:
        score = 60.0 if need_rank - have_rank == 1 else 30.0
    else:
        score = 30.0 if req.equivalent_experience_ok else 0.0
    if req.priority == "preferred" and not met:
        score = max(score, 60.0)

    check = EducationCheck(required_level=req.level, resume_level=resume.highest_degree, priority=req.priority,
                           equivalent_experience_ok=req.equivalent_experience_ok, met=met)
    return check, score


def required_skills_score(matches: list[SkillMatch]) -> float | None:
    return skills_score([m for m in matches if m.priority == "required"])


# Years and degrees only matter if they're in the right field. When most required skills are
# missing, cap the overall score so unrelated experience can't make a poor fit look decent.
RELEVANCE_THRESHOLD = 50.0
RELEVANCE_MARGIN = 20.0


def apply_relevance_cap(overall: float | None, required_score: float | None) -> tuple[float | None, bool]:
    if overall is None or required_score is None or required_score >= RELEVANCE_THRESHOLD:
        return overall, False
    capped = min(overall, round(required_score + RELEVANCE_MARGIN, 1))
    return capped, capped < overall


def combine(components: dict[str, float | None]) -> tuple[float | None, ScoreBreakdown]:
    active = {k: v for k, v in components.items() if v is not None}
    if not active:
        return None, ScoreBreakdown()
    total_weight = sum(WEIGHTS[k] for k in active)
    breakdown = ScoreBreakdown(**{
        k: ComponentScore(score=round(v, 1), weight=round(WEIGHTS[k] / total_weight, 3))
        for k, v in active.items()
    })
    overall = sum(v * WEIGHTS[k] for k, v in active.items()) / total_weight
    return round(overall, 1), breakdown


# --- suggestions ------------------------------------------------------------------------

def _fmt_years(value: float) -> str:
    return f"{value:g}"


def build_suggestions(matches: list[SkillMatch], experience: ExperienceSummary,
                      education: EducationCheck | None, resume: ParsedResume) -> list[Suggestion]:
    out: list[Suggestion] = []
    required = [m for m in matches if m.priority == "required"]
    preferred = [m for m in matches if m.priority == "preferred"]

    for m in [m for m in required if m.status == "missing"][:5]:
        out.append(Suggestion(priority="high", skill=m.skill, message=(
            f"The job requires {m.skill}, but your resume doesn't mention it. If you have used it, "
            f"add an experience or project bullet that shows what you did with {m.skill}.")))

    for m in [m for m in required if m.status == "related"][:3]:
        out.append(Suggestion(priority="medium", skill=m.skill, message=(
            f"The job asks for {m.skill}; your resume shows {m.related_to}, which is related. "
            f"If you have used {m.skill} itself, name it explicitly.")))

    for m in [m for m in required if m.status == "listed"][:4]:
        out.append(Suggestion(priority="medium", skill=m.skill, message=(
            f"{m.skill} only appears in your skills list. Mention it in an experience or project "
            f"bullet with a concrete result so reviewers can see you've used it.")))

    for check in experience.checks:
        if check.met or check.priority != "required":
            continue
        if check.skill is None:
            hint = (" Make sure every role lists start and end dates."
                    if experience.roles_found == 0 else "")
            out.append(Suggestion(priority="high", message=(
                f"The job asks for {check.required_years}+ years of experience; the dates on your resume "
                f"add up to about {_fmt_years(check.resume_years)} years.{hint}")))
        else:
            out.append(Suggestion(priority="medium", skill=check.skill, message=(
                f"The job asks for {check.required_years}+ years of {check.skill}; it appears in roles "
                f"covering about {_fmt_years(check.resume_years)} years. If you used it longer, "
                f"mention it in each role where you did.")))

    if education and not education.met:
        need = LEVEL_LABEL[education.required_level]
        extra = " The posting accepts equivalent experience, so highlight relevant work." if education.equivalent_experience_ok else ""
        found = "no degree" if not education.resume_level else LEVEL_LABEL[education.resume_level]
        out.append(Suggestion(priority="high" if education.priority == "required" else "low", message=(
            f"The job asks for {need}; we found {found} on your resume.{extra}")))

    missing_pref = [m.skill for m in preferred if m.status == "missing"]
    if missing_pref:
        out.append(Suggestion(priority="low", message=(
            "Nice-to-have skills not found: " + ", ".join(missing_pref[:6])
            + ". Add any you genuinely have.")))

    if not resume.has_email:
        out.append(Suggestion(priority="medium", message="No email address was found. Put your contact details at the top of the resume."))

    order = {"high": 0, "medium": 1, "low": 2}
    out.sort(key=lambda s: order[s.priority])
    return out[:10]
