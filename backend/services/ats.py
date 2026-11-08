"""Checks for how easily an applicant tracking system (ATS) can read a resume.

These are about the document itself, not the job, so they produce a separate score
instead of changing the job match score.
"""

from __future__ import annotations

import re

from models.schemas import AtsCheck, AtsReport
from services.bullets import is_bullet
from services.extractor import Extraction
from services.resume_parser import ParsedResume

SEVERITY_WEIGHT = {"critical": 3.0, "major": 2.0, "minor": 1.0}
STATUS_CREDIT = {"pass": 1.0, "warn": 0.5, "fail": 0.0}

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
# Icon fonts (Font Awesome etc.) use the Unicode private use area; emoji live above U+1F000.
ICON_CHARS = re.compile("[-\U0001f000-\U0001faff☀-➿]")
QUANTIFIED = re.compile(r"\d|%|\$|€|£")
_MONTH = re.compile(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)", re.IGNORECASE)


def _check(id: str, label: str, status: str, severity: str, message: str, fix: str | None = None) -> AtsCheck:
    return AtsCheck(id=id, label=label, status=status, severity=severity, message=message,
                    fix=fix if status != "pass" else None)


def _text_readable(ext: Extraction) -> AtsCheck:
    if ext.quality == "good":
        return _check("text", "Text can be read", "pass", "critical", "All text was extracted cleanly.")
    return _check("text", "Text can be read", "warn" if ext.quality == "low" else "fail", "critical",
                  "Very little text could be read; parts of the resume may be images or outlined text.",
                  "Export the resume from Word or Google Docs as a text-based PDF or DOCX, not a scan or image.")


def _contact(ext: Extraction, resume: ParsedResume) -> list[AtsCheck]:
    checks = []
    in_header_only = not resume.has_email and EMAIL.search(ext.layout.header_footer_text)
    if resume.has_email:
        checks.append(_check("email", "Email address", "pass", "critical", "An email address was found."))
    elif in_header_only:
        checks.append(_check("email", "Email address", "fail", "critical",
                             "Your email is only in the page header or footer, which many ATS skip.",
                             "Move your contact details into the main body at the top of the page."))
    else:
        checks.append(_check("email", "Email address", "fail", "critical", "No email address was found.",
                             "Add your email address at the top of the resume."))
    checks.append(
        _check("phone", "Phone number", "pass", "minor", "A phone number was found.")
        if resume.has_phone else
        _check("phone", "Phone number", "warn", "minor", "No phone number was found.",
               "Add a phone number next to your email.")
    )
    return checks


def _sections(resume: ParsedResume) -> AtsCheck:
    found = set(resume.sections) - {"header"}
    missing = [s for s in ("experience", "education", "skills") if s not in found]
    if not missing:
        return _check("sections", "Standard section headings", "pass", "major",
                      "Experience, Education and Skills headings were all recognised.")
    status = "fail" if "experience" in missing else "warn"
    names = ", ".join(m.capitalize() for m in missing)
    return _check("sections", "Standard section headings", status, "major",
                  f"No recognisable heading for: {names}.",
                  "Use plain headings such as 'Experience', 'Education' and 'Skills' so an ATS can file "
                  "each part of your resume correctly.")


def _dates(resume: ParsedResume) -> list[AtsCheck]:
    checks = []
    if "experience" not in resume.sections:
        return checks
    if resume.experience_entries:
        checks.append(_check("dates", "Employment dates", "pass", "major",
                             f"Found dates for {len(resume.experience_entries)} role(s)."))
    else:
        checks.append(_check("dates", "Employment dates", "fail", "major",
                             "No start and end dates were found in your experience section.",
                             "Give every role a date range such as 'Jan 2020 – Present'."))
        return checks

    styles = {("month" if _MONTH.search(e.dates.raw) or re.search(r"\d/\d", e.dates.raw) else "year")
              for e in resume.experience_entries}
    if len(styles) > 1:
        checks.append(_check("date_format", "Consistent date format", "warn", "minor",
                             "Some roles use month and year, others only the year.",
                             "Use the same format for every role, e.g. 'Jan 2020 – Mar 2023'."))
    else:
        checks.append(_check("date_format", "Consistent date format", "pass", "minor",
                             "All roles use the same date format."))
    return checks


def _layout(ext: Extraction) -> list[AtsCheck]:
    lay = ext.layout
    checks = []
    if lay.multi_column_pages:
        checks.append(_check("columns", "Single-column layout", "warn", "major",
                             f"{lay.multi_column_pages} page(s) appear to use two columns. Many ATS read "
                             "across columns line by line, mixing up your content.",
                             "Use a single-column layout, or check that the text reads in order when copied."))
    elif ext.file_type == "pdf":
        checks.append(_check("columns", "Single-column layout", "pass", "major", "No multi-column layout detected."))
    if lay.table_count:
        checks.append(_check("tables", "No layout tables", "warn", "major",
                             f"The document uses {lay.table_count} table(s). Some ATS skip or scramble table contents.",
                             "Replace tables with plain paragraphs and bullet points."))
    if lay.image_count:
        checks.append(_check("images", "No images or graphics", "warn", "minor",
                             f"Found {lay.image_count} image(s). An ATS ignores images, including text, "
                             "logos or skill charts inside them.",
                             "Make sure nothing important is only shown as an image (photos, icons, rating bars)."))
    return checks


def _icons(text: str) -> AtsCheck:
    count = len(ICON_CHARS.findall(text))
    if count <= 2:
        return _check("icons", "No icons or symbols", "pass", "minor", "No icon characters found.")
    return _check("icons", "No icons or symbols", "warn", "minor",
                  f"Found {count} icon or emoji characters; an ATS shows them as garbage or drops them.",
                  "Replace icons (phone, email, location symbols) with plain text labels.")


def _length(ext: Extraction) -> AtsCheck:
    words = len(ext.text.split())
    if words < 200:
        return _check("length", "Resume length", "warn", "minor",
                      f"The resume has only about {words} words.",
                      "Add more detail on your responsibilities and results; most resumes have 400–800 words.")
    if words > 1200 or ext.page_count > 3:
        return _check("length", "Resume length", "warn", "minor",
                      f"The resume is long ({words} words, {ext.page_count} pages).",
                      "Keep it to 1–2 pages and focus on the most relevant experience.")
    return _check("length", "Resume length", "pass", "minor", f"About {words} words; a good length.")


def _bullets(resume: ParsedResume) -> list[AtsCheck]:
    lines = resume.sections.get("experience", [])
    if not lines:
        return []
    bullets = [ln for ln in lines if is_bullet(ln)]
    checks = []
    if len(bullets) < 3:
        checks.append(_check("bullets", "Bullet points", "warn", "minor",
                             "Your experience has few or no bullet points.",
                             "List achievements as short bullet points; they are easier to scan and parse."))
        return checks
    checks.append(_check("bullets", "Bullet points", "pass", "minor", f"{len(bullets)} bullet points in experience."))
    share = sum(1 for b in bullets if QUANTIFIED.search(b)) / len(bullets)
    if share < 0.3:
        checks.append(_check("metrics", "Quantified results", "warn", "minor",
                             f"Only {round(share * 100)}% of your bullet points include a number.",
                             "Add measurable results where you can: percentages, amounts, counts, time saved."))
    else:
        checks.append(_check("metrics", "Quantified results", "pass", "minor",
                             f"{round(share * 100)}% of your bullet points include a number."))
    return checks


def run_ats_checks(ext: Extraction, resume: ParsedResume) -> AtsReport:
    checks = [_text_readable(ext), *_contact(ext, resume), _sections(resume), *_dates(resume),
              *_layout(ext), _icons(ext.text), _length(ext), *_bullets(resume)]
    total = sum(SEVERITY_WEIGHT[c.severity] for c in checks)
    earned = sum(SEVERITY_WEIGHT[c.severity] * STATUS_CREDIT[c.status] for c in checks)
    order = {"fail": 0, "warn": 1, "pass": 2}
    sev = {"critical": 0, "major": 1, "minor": 2}
    checks.sort(key=lambda c: (order[c.status], sev[c.severity]))
    return AtsReport(score=round(earned / total * 100, 1), checks=checks)
