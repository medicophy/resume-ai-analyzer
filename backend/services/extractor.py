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
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from services.bullets import normalize_bullets

logger = logging.getLogger(__name__)

Quality = Literal["good", "low", "empty"]

# Below this many characters per page, a PDF is probably a scan or uses outlined text.
LOW_TEXT_CHARS_PER_PAGE = 200


class UnsupportedFileError(ValueError):
    """The upload is not a readable PDF or DOCX file."""


@dataclass
class Layout:
    """Layout features that commonly trip up applicant tracking systems."""

    multi_column_pages: int = 0
    image_count: int = 0
    table_count: int = 0
    # Text that only exists in page headers/footers (DOCX); many ATS ignore these areas.
    header_footer_text: str = ""


@dataclass
class Extraction:
    text: str
    file_type: Literal["pdf", "docx"]
    page_count: int
    quality: Quality
    warnings: list[str] = field(default_factory=list)
    layout: Layout = field(default_factory=Layout)

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


def _page_has_columns(page) -> bool:
    """True when the page has substantial text side by side in two columns.

    A right-aligned date on the same line as a job title is common and harmless, so
    only lines of 25+ characters count, and the right-hand column must hold a real
    share of the page's text.
    """
    width = page.rect.width
    lines: list[tuple[float, float, float, float, int]] = []  # x0, y0, x1, y1, chars
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"]).strip()
            if text:
                x0, y0, x1, y1 = line["bbox"]
                lines.append((x0, y0, x1, y1, len(text)))
    total_chars = sum(ln[4] for ln in lines)
    if not total_chars:
        return False
    # Ignore short lines: right-aligned dates and locations are fine for an ATS.
    left = [ln for ln in lines if ln[2] <= width * 0.6 and ln[4] >= 25]
    right = [ln for ln in lines if ln[0] >= width * 0.4 and ln[4] >= 25]
    side_by_side = sum(1 for r in right if any(lt[1] < r[3] and r[1] < lt[3] for lt in left))
    return side_by_side >= 4 and sum(r[4] for r in right) >= 0.25 * total_chars


def _pdf_with_pymupdf(file_bytes: bytes) -> tuple[str, int, Layout]:
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        # sort=True orders blocks top-to-bottom, left-to-right.
        pages = [page.get_text("text", sort=True) for page in doc]
        layout = Layout(
            multi_column_pages=sum(1 for page in doc if _page_has_columns(page)),
            image_count=sum(len(page.get_images(full=False)) for page in doc),
        )
        return "\n".join(pages), len(pages), layout


def _pdf_with_pdfplumber(file_bytes: bytes) -> tuple[str, int]:
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages), len(pages)


def _extract_pdf(file_bytes: bytes) -> Extraction:
    try:
        text, page_count, layout = _pdf_with_pymupdf(file_bytes)
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
    return Extraction(text=text, file_type="pdf", page_count=page_count, quality=quality,
                      warnings=warnings, layout=layout)


def _is_list_paragraph(paragraph: Paragraph) -> bool:
    """True for bulleted or numbered Word list items (direct or via the paragraph style)."""
    p_pr = paragraph._p.pPr
    if p_pr is not None and p_pr.numPr is not None:
        num_id = p_pr.numPr.numId
        # numId 0 explicitly switches numbering off.
        return not (num_id is not None and num_id.val == 0)
    style = paragraph.style
    depth = 0
    while style is not None and depth < 10:
        s_pr = style.element.pPr
        if s_pr is not None and s_pr.numPr is not None:
            return True
        if style.name and style.name.lower().startswith(("list bullet", "list number")):
            return True
        style, depth = style.base_style, depth + 1
    return False


def _docx_lines(doc) -> list[str]:
    """Paragraph and table text in document order (many templates lay out content in tables)."""
    lines: list[str] = []

    def walk(container) -> None:
        for child in container.iter_inner_content():
            if isinstance(child, Paragraph):
                if child.text.strip():
                    # Word draws list bullets from numbering, so the glyph isn't in the text.
                    lines.append(f"• {child.text.strip()}" if _is_list_paragraph(child) else child.text)
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
    return Extraction(text=text, file_type="docx", page_count=page_count, quality=quality,
                      warnings=warnings, layout=_docx_layout(doc))


def _docx_layout(doc) -> Layout:
    header_footer: list[str] = []
    for section in doc.sections:
        for part in (section.header, section.footer, section.first_page_header, section.first_page_footer):
            if part is not None and not part.is_linked_to_previous:
                header_footer.extend(p.text for p in part.paragraphs if p.text.strip())
                for table in part.tables:
                    header_footer.extend(c.text for row in table.rows for c in row.cells if c.text.strip())
    body = doc.element.body
    return Layout(
        table_count=len(body.findall(".//" + qn("w:tbl"))),
        image_count=len(body.findall(".//" + qn("w:drawing"))) + len(body.findall(".//" + qn("w:pict"))),
        header_footer_text="\n".join(dict.fromkeys(header_footer)),
    )


def extract_text(file_bytes: bytes, filename: str) -> Extraction:
    file_type = detect_file_type(file_bytes, filename)
    extraction = _extract_pdf(file_bytes) if file_type == "pdf" else _extract_docx(file_bytes)
    # One bullet form for everything downstream (parsing, ATS checks, AI validation).
    extraction.text = normalize_bullets(extraction.text)
    return extraction
