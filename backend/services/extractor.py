"""Text extraction from PDF and DOCX resumes."""

from __future__ import annotations

import io
import logging
import zipfile
from dataclasses import dataclass, field
from typing import Literal

import fitz  # PyMuPDF
import pdfplumber
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

logger = logging.getLogger(__name__)

Quality = Literal["good", "low", "empty"]

# Below this many characters per page, a PDF is probably a scan or uses outlined text.
LOW_TEXT_CHARS_PER_PAGE = 200


class UnsupportedFileError(ValueError):
    """The upload is not a readable PDF or DOCX file."""


@dataclass
class Extraction:
    text: str
    file_type: Literal["pdf", "docx"]
    page_count: int
    quality: Quality
    warnings: list[str] = field(default_factory=list)

    @property
    def char_count(self) -> int:
        return len(self.text)


def detect_file_type(file_bytes: bytes, filename: str) -> Literal["pdf", "docx"]:
    """Identify the file by its contents; the extension must agree."""
    name = filename.lower()
    if file_bytes.startswith(b"%PDF"):
        if not name.endswith(".pdf"):
            raise UnsupportedFileError("File content is a PDF but the name does not end in .pdf.")
        return "pdf"
    if file_bytes.startswith(b"PK"):
        if not name.endswith(".docx"):
            raise UnsupportedFileError("Only .pdf and .docx files are supported.")
        return "docx"
    if name.endswith(".doc"):
        raise UnsupportedFileError("Legacy .doc files are not supported. Save the resume as .docx or PDF.")
    raise UnsupportedFileError("Only PDF and DOCX files are supported.")


def _quality(text: str, page_count: int) -> Quality:
    chars = len(text.strip())
    if chars == 0:
        return "empty"
    if chars / max(page_count, 1) < LOW_TEXT_CHARS_PER_PAGE:
        return "low"
    return "good"


def _pdf_with_pymupdf(file_bytes: bytes) -> tuple[str, int]:
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        # sort=True orders blocks top-to-bottom, left-to-right, which keeps
        # multi-column resumes far more readable than the raw content order.
        pages = [page.get_text("text", sort=True) for page in doc]
        return "\n".join(pages), len(pages)


def _pdf_with_pdfplumber(file_bytes: bytes) -> tuple[str, int]:
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages), len(pages)


def _extract_pdf(file_bytes: bytes) -> Extraction:
    try:
        text, page_count = _pdf_with_pymupdf(file_bytes)
    except Exception as exc:  # corrupt or encrypted PDFs raise various errors
        raise UnsupportedFileError("The PDF could not be opened. It may be corrupt or password-protected.") from exc

    warnings: list[str] = []
    quality = _quality(text, page_count)
    if quality != "good":
        try:
            alt_text, alt_pages = _pdf_with_pdfplumber(file_bytes)
        except Exception:
            logger.warning("pdfplumber fallback failed", exc_info=True)
        else:
            if len(alt_text.strip()) > len(text.strip()):
                text, page_count = alt_text, alt_pages
                quality = _quality(text, page_count)

    if quality == "empty":
        warnings.append(
            "No text could be read from this PDF. It is probably a scanned image; "
            "applicant tracking systems will not be able to read it either."
        )
    elif quality == "low":
        warnings.append(
            "Very little text could be read from this PDF, so results may be incomplete. "
            "If it was scanned or exported as images, export it again as a text PDF."
        )
    return Extraction(text=text, file_type="pdf", page_count=page_count, quality=quality, warnings=warnings)


def _docx_lines(doc) -> list[str]:
    """Paragraph and table text in document order (many templates lay out content in tables)."""
    lines: list[str] = []

    def walk(container) -> None:
        for child in container.iter_inner_content():
            if isinstance(child, Paragraph):
                if child.text.strip():
                    lines.append(child.text)
            elif isinstance(child, Table):
                for row in child.rows:
                    seen: set[int] = set()
                    for cell in row.cells:
                        if id(cell._tc) in seen:  # merged cells repeat the same element
                            continue
                        seen.add(id(cell._tc))
                        walk(cell)

    walk(doc)
    return lines


def _extract_docx(file_bytes: bytes) -> Extraction:
    try:
        doc = Document(io.BytesIO(file_bytes))
    except (zipfile.BadZipFile, KeyError, ValueError) as exc:
        raise UnsupportedFileError("The DOCX file could not be opened. It may be corrupt.") from exc

    lines = _docx_lines(doc)
    text = "\n".join(lines)
    # DOCX has no fixed pages; estimate roughly 45 non-empty lines per page.
    page_count = max(1, round(len(lines) / 45))
    quality: Quality = "empty" if not text.strip() else "good"
    warnings = ["No text could be read from this DOCX file."] if quality == "empty" else []
    return Extraction(text=text, file_type="docx", page_count=page_count, quality=quality, warnings=warnings)


def extract_text(file_bytes: bytes, filename: str) -> Extraction:
    file_type = detect_file_type(file_bytes, filename)
    return _extract_pdf(file_bytes) if file_type == "pdf" else _extract_docx(file_bytes)
