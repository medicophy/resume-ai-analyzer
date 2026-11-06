import io
from datetime import date
from pathlib import Path

import fitz
import pytest
from docx import Document

FIXTURES = Path(__file__).parent / "fixtures"
TODAY = date(2026, 11, 6)


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def make_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_textbox(fitz.Rect(40, 40, 570, 800), text, fontsize=9)
    return doc.tobytes()


def make_docx(text: str) -> bytes:
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.fixture
def jd_backend() -> str:
    return read_fixture("jd_backend.txt")
