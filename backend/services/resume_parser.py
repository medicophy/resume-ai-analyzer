"""Split resume text into sections and dated experience entries."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

from services.bullets import is_bullet, normalize_bullets
from services.dates import DATE_RANGE, DateRange, find_date_ranges
from services.education import highest_degree

# Heading text (lower-case, punctuation stripped) -> canonical section name.
SECTION_HEADINGS: dict[str, tuple[str, ...]] = {
    "summary": ("summary", "professional summary", "profile", "professional profile", "objective",
                "career objective", "about me", "about", "overview", "career summary"),
    "experience": ("experience", "work experience", "professional experience", "employment",
                   "employment history", "work history", "career history", "relevant experience",
                   "professional background", "internships", "internship experience"),
    "projects": ("projects", "personal projects", "key projects", "selected projects", "academic projects"),
    "skills": ("skills", "technical skills", "core skills", "key skills", "core competencies",
               "competencies", "technologies", "tools", "tools and technologies", "skills and tools",
               "areas of expertise", "expertise"),
    "education": ("education", "academic background", "education and training", "qualifications",
                  "academic qualifications"),
    "certifications": ("certifications", "certificates", "licenses", "licenses and certifications",
                       "certifications and licenses", "courses", "training"),
    "other": ("awards", "honors", "achievements", "publications", "languages", "interests",
              "volunteer", "volunteering", "volunteer experience", "references", "activities"),
}
_HEADING_LOOKUP = {alias: name for name, aliases in SECTION_HEADINGS.items() for alias in aliases}
# Sections that show skills being used rather than merely listed.
APPLIED_SECTIONS = ("experience", "projects")



@dataclass
class ExperienceEntry:
    """One dated block in the experience section: the date line plus the lines that follow it."""

    dates: DateRange
    lines: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


@dataclass
class ParsedResume:
    text: str
    sections: dict[str, list[str]]
    experience_entries: list[ExperienceEntry]
    date_ranges: list[DateRange]  # ranges that count as work experience
    highest_degree: str | None
    has_email: bool
    has_phone: bool

    def section_text(self, name: str) -> str:
        return "\n".join(self.sections.get(name, []))

    def bullets(self, section: str = "experience") -> list[str]:
        return [ln for ln in self.sections.get(section, []) if is_bullet(ln)]


def _heading_name(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or len(stripped) > 45:
        return None
    normalized = re.sub(r"[^a-z& ]", " ", stripped.lower()).replace("&", " and ")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return _HEADING_LOOKUP.get(normalized)


def split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"header": []}
    current = "header"
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        name = _heading_name(line)
        if name:
            current = name
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


def _experience_entries(lines: list[str], today: date | None) -> list[ExperienceEntry]:
    """A line containing a date range starts a new entry. A short title line directly above
    the date line (e.g. "Senior Engineer, Acme") belongs to the new entry, not the previous one."""
    entries: list[ExperienceEntry] = []
    for i, line in enumerate(lines):
        found = find_date_ranges(line, today)
        if found:
            entry = ExperienceEntry(dates=found[0], lines=[line])
            prev = lines[i - 1] if i > 0 else None
            if prev and not is_bullet(prev) and not DATE_RANGE.search(prev) and len(prev) <= 80:
                if entries and entries[-1].lines and entries[-1].lines[-1] == prev:
                    entries[-1].lines.pop()
                entry.lines.insert(0, prev)
            entries.append(entry)
        elif entries:
            entries[-1].lines.append(line)
    return entries


def parse_resume(text: str, today: date | None = None) -> ParsedResume:
    text = normalize_bullets(text)
    sections = split_sections(text)
    experience_lines = sections.get("experience", [])
    entries = _experience_entries(experience_lines, today)

    if entries:
        work_ranges = [e.dates for e in entries]
    else:
        # No recognisable experience section: fall back to every date range outside education.
        non_education = "\n".join(
            ln for name, lines in sections.items() if name != "education" for ln in lines
        )
        work_ranges = find_date_ranges(non_education, today)

    return ParsedResume(
        text=text,
        sections=sections,
        experience_entries=entries,
        date_ranges=work_ranges,
        highest_degree=highest_degree(sections.get("education") and "\n".join(sections["education"]) or text),
        has_email=bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)),
        has_phone=bool(re.search(r"(?:\+?\d[\s().-]*){9,}", text)),
    )
