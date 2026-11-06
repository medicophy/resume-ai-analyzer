import io

import fitz
import pytest
from docx import Document

from services.extractor import UnsupportedFileError, extract_text
from tests.conftest import make_docx, make_pdf, read_fixture


def test_pdf_text():
    e = extract_text(make_pdf(read_fixture("resume_strong.txt")), "cv.pdf")
    assert e.file_type == "pdf" and e.quality == "good"
    assert "Acme Corp" in e.text


def test_docx_keeps_table_order():
    doc = Document()
    doc.add_paragraph("EXPERIENCE")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Engineer, Acme"
    table.cell(0, 1).text = "Jan 2020 - Present"
    doc.add_paragraph("EDUCATION")
    buf = io.BytesIO()
    doc.save(buf)
    e = extract_text(buf.getvalue(), "cv.docx")
    assert e.text.splitlines() == ["EXPERIENCE", "Engineer, Acme", "Jan 2020 - Present", "EDUCATION"]


def test_docx_plain():
    e = extract_text(make_docx("Jane Doe\nPython developer"), "CV.DOCX")
    assert e.file_type == "docx" and "Python developer" in e.text


def test_image_only_pdf_is_empty():
    doc = fitz.open()
    doc.new_page()
    e = extract_text(doc.tobytes(), "scan.pdf")
    assert e.quality == "empty" and e.warnings


@pytest.mark.parametrize(
    ("data", "name"),
    [
        (b"plain text", "cv.txt"),
        (b"plain text", "cv.pdf"),  # extension lies about the content
        (make_pdf("hello"), "cv.docx"),  # PDF renamed to .docx
        (b"\xd0\xcf\x11\xe0legacy", "cv.doc"),
        (b"PK\x03\x04garbage", "cv.docx"),  # corrupt zip
    ],
)
def test_rejects_unsupported_or_mismatched_files(data, name):
    with pytest.raises(UnsupportedFileError):
        extract_text(data, name)
