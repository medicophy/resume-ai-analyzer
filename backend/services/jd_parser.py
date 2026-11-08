"""Extract skills, experience and education requirements from a job description."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

from services.bullets import is_bullet
from services.education import DEGREE_RANK, degrees_in
from services.skills import SkillCatalog, load_catalog

Priority = Literal["required", "preferred"]
Context = Literal["required", "preferred", "ignore"]

# Heading phrases (lower-case, punctuation stripped). Skills under "ignore" headings
# (company blurb, benefits, legal text) are not requirements.
_HEADINGS: dict[Context, tuple[str, ...]] = {
    "preferred": (
        "preferred qualifications", "preferred skills", "preferred experience", "preferred",
        "nice to have", "nice to haves", "good to have", "bonus", "bonus points", "pluses",
        "desirable", "desired skills", "desired qualifications", "extra credit", "it would be great if",
        "even better if", "ideally you have", "additional qualifications",
    ),
    "required": (
        "requirements", "qualifications", "minimum qualifications", "basic qualifications",
        "required qualifications", "required skills", "required experience", "must have", "must haves",
        "what you'll need", "what you need", "what we're looking for", "what we are looking for",
        "who you are", "you have", "you will have", "skills", "skills and experience",
        "requirements and qualifications", "key requirements", "about you", "your profile",
        "responsibilities", "key responsibilities", "what you'll do", "what you will do",
        "the role", "your role", "role", "duties", "day to day", "job description", "the job",
    ),
    "ignore": (
        "about us", "about the company", "who we are", "company overview", "our company", "benefits",
        "perks", "perks and benefits", "what we offer", "we offer", "compensation", "salary",
        "equal opportunity", "equal opportunity employer", "eeo statement", "diversity", "why join us",
        "why work with us", "our values", "how to apply", "application process", "location",
    ),
}
_HEADING_LOOKUP = {phrase: ctx for ctx, phrases in _HEADINGS.items() for phrase in phrases}

_PREFERRED_MARKERS = re.compile(
    r"\b(preferred|nice[\s-]to[\s-]have|a plus|is a plus|bonus|ideally|desirable|advantageous|"
    r"would be great|good to have|not required|familiarity with)\b",
    re.IGNORECASE,
)
_REQUIRED_MARKERS = re.compile(r"\b(required|must|mandatory|essential|minimum of|at least)\b", re.IGNORECASE)

_NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
                 "eight": 8, "nine": 9, "ten": 10, "twelve": 12, "fifteen": 15}
_NUM = r"(\d{1,2}|" + "|".join(_NUMBER_WORDS) + r")"
_YEARS = re.compile(
    rf"\b{_NUM}\s*\+?\s*(?:(?:-|–|to)\s*{_NUM}\s*\+?\s*)?(?:\(\s*\d+\s*\)\s*)?years?\b",
    re.IGNORECASE,
)
_EXPERIENCE_WORD = re.compile(r"\b(experience|experienced|background|working|professional)\b", re.IGNORECASE)


@dataclass
class YearsRequirement:
    years: int
    skill: str | None  # None = general professional experience
    priority: Priority
    text: str


@dataclass
class EducationRequirement:
    level: str  # key of DEGREE_RANK
    priority: Priority
    equivalent_experience_ok: bool
    text: str


@dataclass
class JobRequirements:
    skills: dict[str, Priority] = field(default_factory=dict)
    years: list[YearsRequirement] = field(default_factory=list)
    education: EducationRequirement | None = None
    has_structure: bool = False  # True when required/preferred headings were found

    @property
    def required_skills(self) -> list[str]:
        return [s for s, p in self.skills.items() if p == "required"]

    @property
    def preferred_skills(self) -> list[str]:
        return [s for s, p in self.skills.items() if p == "preferred"]

    @property
    def general_years(self) -> YearsRequirement | None:
        general = [y for y in self.years if y.skill is None and y.priority == "required"]
        return max(general, key=lambda y: y.years) if general else None


def _heading_context(line: str) -> Context | None:
    stripped = line.strip()
    if len(stripped) > 60 or is_bullet(stripped):
        return None
    # "Location: Remote" is a labelled value, not a heading.
    if ":" in stripped and stripped.split(":", 1)[1].strip():
        return None
    normalized = re.sub(r"[^a-z' ]", " ", stripped.lower().replace("’", "'"))
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if normalized in _HEADING_LOOKUP:
        return _HEADING_LOOKUP[normalized]
    # Slightly longer headings: "Preferred Qualifications (nice to have)", "Benefits & Perks"
    words = normalized.split()
    for phrase, ctx in sorted(_HEADING_LOOKUP.items(), key=lambda kv: -len(kv[0])):
        if normalized.startswith(phrase + " ") and len(words) <= len(phrase.split()) + 3:
            return ctx
    return None


def _line_priority(line: str, section: Context) -> Priority:
    if _PREFERRED_MARKERS.search(line):
        return "preferred"
    if _REQUIRED_MARKERS.search(line):
        return "required"
    return "preferred" if section == "preferred" else "required"


def _to_int(token: str) -> int:
    return int(token) if token.isdigit() else _NUMBER_WORDS[token.lower()]


def _years_in_line(line: str, priority: Priority, catalog: SkillCatalog) -> list[YearsRequirement]:
    results = []
    for m in _YEARS.finditer(line):
        years = _to_int(m.group(1))
        if not 0 < years <= 30:
            continue
        # Look for the skill right after "years" ("5 years of Python") before falling back
        # to anything else mentioned in the line.
        after = line[m.end(): m.end() + 60]
        skills_after = catalog.find_in(after)
        skills_line = catalog.find_in(line)
        if skills_after:
            skill = skills_after[0]
        elif skills_line and not _EXPERIENCE_WORD.search(after[:25]):
            skill = skills_line[0]
        elif _EXPERIENCE_WORD.search(line):
            skill = None
        else:
            continue  # "years" used in an unrelated sense ("founded 10 years ago")
        results.append(YearsRequirement(years=years, skill=skill, priority=priority, text=line.strip()))
    return results


def parse_job_description(text: str) -> JobRequirements:
    catalog = load_catalog()
    reqs = JobRequirements()
    section: Context = "required"
    education: list[EducationRequirement] = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        heading = _heading_context(line)
        if heading:
            section = heading
            if heading in ("required", "preferred"):
                reqs.has_structure = True
            continue
        if section == "ignore":
            continue

        priority = _line_priority(line, section)
        for skill in catalog.find_in(line):
            # A skill required anywhere stays required even if also mentioned as a plus.
            if reqs.skills.get(skill) != "required":
                reqs.skills[skill] = priority
        reqs.years.extend(_years_in_line(line, priority, catalog))

        levels = degrees_in(line)
        if levels:
            education.append(EducationRequirement(
                level=min(levels, key=DEGREE_RANK.__getitem__),  # "Bachelor's or Master's" -> bachelor
                priority=priority,
                equivalent_experience_ok=bool(re.search(r"equivalent|or relevant experience|or similar", line, re.I)),
                text=line,
            ))

    if education:
        required = [e for e in education if e.priority == "required"]
        pool = required or education
        reqs.education = min(pool, key=lambda e: DEGREE_RANK[e.level])
    return reqs
