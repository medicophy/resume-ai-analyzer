import io

import fitz
from docx import Document

from services.ats import run_ats_checks
from services.extractor import extract_text
from services.resume_parser import parse_resume
from tests.conftest import TODAY, make_pdf, read_fixture


def report_for(data: bytes, name: str):
    ext = extract_text(data, name)
    return run_ats_checks(ext, parse_resume(ext.text, TODAY))


def by_id(report):
    return {c.id: c for c in report.checks}


def test_clean_resume_passes_everything():
    r = report_for(make_pdf(read_fixture("resume_strong.txt")), "cv.pdf")
    checks = by_id(r)
    failing = {c.id: c.status for c in r.checks if c.status != "pass"}
    # The strong fixture is short (about 150 words), so only the length check may warn.
    assert set(failing) <= {"length"}
    assert checks["email"].status == checks["sections"].status == checks["dates"].status == "pass"
    assert checks["columns"].status == "pass"
    assert r.score >= 90


def test_failed_checks_come_first_and_have_fixes():
    r = report_for(make_pdf("Jane Doe\nI build things.\nSKILLS\nPython"), "cv.pdf")
    statuses = [c.status for c in r.checks]
    assert statuses == sorted(statuses, key={"fail": 0, "warn": 1, "pass": 2}.__getitem__)
    for c in r.checks:
        assert (c.fix is None) == (c.status == "pass")
    assert by_id(r)["email"].status == "fail"
    assert by_id(r)["sections"].status == "fail"  # no Experience heading


def test_two_column_pdf_is_flagged():
    doc = fitz.open()
    page = doc.new_page()
    left = "\n".join(f"- Built service number {i} in Python with tests and docs." for i in range(12))
    right = "\n".join(f"Skill group {i}: Docker, Kubernetes, PostgreSQL, Redis" for i in range(12))
    page.insert_textbox(fitz.Rect(30, 40, 290, 800), "EXPERIENCE\n" + left, fontsize=9)
    page.insert_textbox(fitz.Rect(320, 40, 580, 800), "SKILLS\n" + right, fontsize=9)
    r = report_for(doc.tobytes(), "cv.pdf")
    assert by_id(r)["columns"].status == "warn"


def test_right_aligned_dates_are_not_columns():
    doc = fitz.open()
    page = doc.new_page()
    y = 40
    for i in range(6):
        page.insert_text((30, y), f"Senior Engineer at Company Number {i}, building backend systems", fontsize=9)
        page.insert_text((480, y), "2019 - 2021", fontsize=9)
        y += 30
    r = report_for(doc.tobytes(), "cv.pdf")
    assert by_id(r)["columns"].status == "pass"


def test_docx_tables_and_header_contact():
    doc = Document()
    doc.sections[0].header.paragraphs[0].text = "Jane Doe | jane@example.com"
    doc.add_paragraph("EXPERIENCE")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Engineer, Acme"
    table.cell(0, 1).text = "Jan 2020 - Present"
    buf = io.BytesIO()
    doc.save(buf)
    checks = by_id(report_for(buf.getvalue(), "cv.docx"))
    assert checks["tables"].status == "warn"
    assert checks["email"].status == "fail"
    assert "header" in checks["email"].message


def test_icons_and_unquantified_bullets():
    text = (
        " jane@example.com  555 123 4567  Berlin\n"
        "EXPERIENCE\nEngineer, Acme\nJan 2020 - Present\n"
        "- Built internal tools\n- Worked with the team\n- Fixed bugs\n- Wrote documentation\n"
        "EDUCATION\nBSc Physics\nSKILLS\nPython"
    )
    ext = extract_text(make_pdf("placeholder"), "cv.pdf")
    ext.text = text  # icon-font glyphs don't survive the test PDF font, so inject the text directly
    checks = by_id(run_ats_checks(ext, parse_resume(text, TODAY)))
    assert checks["icons"].status == "warn"
    assert checks["metrics"].status == "warn"


def test_mixed_date_formats():
    text = "j@x.com\nEXPERIENCE\nDev, A\nJan 2020 - Present\nDev, B\n2016 - 2019\nEDUCATION\nBSc\nSKILLS\nGo"
    ext = extract_text(make_pdf(text), "cv.pdf")
    checks = by_id(run_ats_checks(ext, parse_resume(ext.text, TODAY)))
    assert checks["date_format"].status == "warn"
