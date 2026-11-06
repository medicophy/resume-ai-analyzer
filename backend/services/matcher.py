"""Match job-description skills against the resume, with evidence lines."""

from __future__ import annotations

from models.schemas import Evidence, SkillMatch
from services.jd_parser import JobRequirements
from services.resume_parser import APPLIED_SECTIONS, ParsedResume
from services.skills import SkillCatalog, load_catalog

MAX_EVIDENCE = 3

# How much each status counts towards the skills score. A skill that is only listed earns
# less than one shown in use, so a resume that is just a keyword list can't score like a
# resume that backs those skills up with experience.
STATUS_CREDIT = {"demonstrated": 1.0, "listed": 0.6, "related": 0.35, "missing": 0.0}


def _find_evidence(skill: str, resume: ParsedResume, catalog: SkillCatalog, sections_known: bool) -> tuple[list[Evidence], bool]:
    """Return evidence lines (applied sections first) and whether any is in an applied section."""
    applied: list[Evidence] = []
    other: list[Evidence] = []
    for section, lines in resume.sections.items():
        for line in lines:
            if catalog.mentions(skill, line):
                is_applied = section in APPLIED_SECTIONS or not sections_known
                (applied if is_applied else other).append(Evidence(section=section, text=line[:300]))
    return (applied + other)[:MAX_EVIDENCE], bool(applied)


def sections_recognized(resume: ParsedResume) -> bool:
    return any(name != "header" for name in resume.sections)


def match_skills(resume: ParsedResume, jd: JobRequirements) -> list[SkillMatch]:
    catalog = load_catalog()
    # Without recognisable headings we can't tell a skills list from experience, so give
    # every mention full credit rather than penalising an unusual layout.
    known = sections_recognized(resume)
    found: dict[str, tuple[list[Evidence], bool]] = {}

    def lookup(skill: str) -> tuple[list[Evidence], bool]:
        if skill not in found:
            found[skill] = _find_evidence(skill, resume, catalog, known)
        return found[skill]

    matches: list[SkillMatch] = []
    for skill, priority in jd.skills.items():
        meta = catalog.skills[skill]
        evidence, applied = lookup(skill)
        if evidence:
            status = "demonstrated" if applied else "listed"
            matches.append(SkillMatch(skill=skill, category=meta.category, priority=priority,
                                      status=status, evidence=evidence))
            continue

        related = next((r for r in meta.related if lookup(r)[0]), None)
        if related:
            matches.append(SkillMatch(skill=skill, category=meta.category, priority=priority,
                                      status="related", related_to=related, evidence=lookup(related)[0]))
        else:
            matches.append(SkillMatch(skill=skill, category=meta.category, priority=priority, status="missing"))

    order = {"required": 0, "preferred": 1}
    matches.sort(key=lambda m: order[m.priority])
    return matches
