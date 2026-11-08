import io

import pytest
from docx import Document

from services.ats import run_ats_checks
from services.bullets import is_bullet, normalize_bullets
from services.extractor import extract_text
from services.resume_parser import parse_resume
from tests.conftest import TODAY, make_pdf

ROLE = "EXPERIENCE\nEngineer, Acme\nJan 2020 - Present\n{0}Built REST APIs in Python\n{0}Cut deploy time by 60%\n{0}Mentored 3 juniors\n"


@pytest.mark.parametrize(
    "glyph",
    [
        "• ", "◦ ", "○ ", "● ", "▪ ", "■ ", "□ ", "◆ ", "❖ ", "➢ ", "► ", "✓ ", "→ ",
        "o ",          # Word's second-level bullet in Courier New
        "- ", "– ", "* ",
        " ",     # Symbol-font bullet as extracted from Word PDFs
        " ",     # Wingdings square
        " ",     # Wingdings arrow
        " ",     # Wingdings check mark
        "§ ", "Ø ", "ü ",  # Wingdings bullets extracted without a Unicode mapping
        "•",           # no space after the glyph
        "○\n",         # glyph on its own line, text on the next
    ],
)
def test_bullet_styles_are_recognised(glyph):
    resume = parse_resume(ROLE.format(glyph), TODAY)
    bullets = resume.bullets("experience")
    assert len(bullets) == 3
    assert all(b.startswith("• ") for b in bullets)
    assert len(resume.experience_entries) == 1


def test_numbered_lists_count_as_bullets():
    text = ROLE.replace("{0}", "{}").format("1. ", "2) ", "3. ")
    assert len(parse_resume(text, TODAY).bullets("experience")) == 3


@pytest.mark.parametrize(
    "line",
    ["+1 555 123 4567", "o'clock", "-5% churn reduction", "Oracle Database", "– Present", "- 2021",
     "— Jan 2019", "Senior Engineer, Acme", "only-hyphenated-word"],
)
def test_lines_that_are_not_bullets(line):
    assert normalize_bullets(line) == line
    assert not is_bullet(line)


def test_lone_dash_line_is_not_a_bullet_marker():
    # A lone "-" is often a separator; it must not turn the next line into a bullet.
    assert normalize_bullets("-\nSenior Engineer") == "-\nSenior Engineer"


def test_word_list_bullets_in_docx():
    doc = Document()
    doc.add_paragraph("EXPERIENCE")
    doc.add_paragraph("Engineer, Acme")
    doc.add_paragraph("Jan 2020 - Present")
    for text in ("Built REST APIs in Python", "Cut deploy time by 60%"):
        doc.add_paragraph(text, style="List Bullet")
    doc.add_paragraph("Numbered item", style="List Number")
    doc.add_paragraph("Plain paragraph")
    buf = io.BytesIO()
    doc.save(buf)
    lines = extract_text(buf.getvalue(), "cv.docx").text.splitlines()
    assert lines[3:] == ["• Built REST APIs in Python", "• Cut deploy time by 60%", "• Numbered item", "Plain paragraph"]


def test_symbol_font_bullets_are_not_icons():
    ext = extract_text(make_pdf("placeholder"), "cv.pdf")
    text = ROLE.format(" ") + "EDUCATION\nBSc\nSKILLS\nPython\nj@x.com"
    ext.text = normalize_bullets(text)
    checks = {c.id: c for c in run_ats_checks(ext, parse_resume(ext.text, TODAY)).checks}
    assert checks["icons"].status == "pass"
    assert checks["bullets"].status == "pass"
