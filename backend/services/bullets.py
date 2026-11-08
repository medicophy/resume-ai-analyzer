"""Recognise list bullets however a resume encodes them, and normalise them to "• ".

Resumes use many bullet glyphs: filled and hollow circles, squares, arrows, check marks,
Word's second-level "o", and Symbol/Wingdings characters that PDF extraction returns as
Unicode private-use code points. PDF extraction also often puts the glyph on its own line.
"""

from __future__ import annotations

import re

BULLET = "•"

# Unambiguous glyphs: a bullet even without a following space ("•Built ...").
_GLYPHS = (
    "•◦○●◉◎⦿⦾∙·"          # circles and dots
    "▪▫■□◾◽◼◻❏❐❑❒"         # squares
    "◆◇❖♦⬥⬦"               # diamonds
    "‣➢➣➤►▶▸▹▷➔→⇒➜➞➟⮚"     # arrows and triangles
    "✓✔✗✘☐☑★☆✦✧"           # check marks and stars
    "⁃"                     # hyphen bullet
    # Symbol / Wingdings bullets as returned by PDF text extraction (private use area):
    ""
)
# Characters that are only bullets when followed by whitespace ("- text", "o text").
# "§", "Ø" and "ü" are Wingdings bullets (square, arrow, check mark) extracted from PDFs
# whose font has no Unicode mapping.
_SPACED = "-–—*+~o§Øü"

_GLYPH_CLASS = "[" + re.escape(_GLYPHS) + "]"
_SPACED_CLASS = "[" + re.escape(_SPACED) + "]"
# "– Present" or "- 2021" on its own line is the end of a date range split by PDF
# extraction, not a bullet.
_DATE_AHEAD = (
    r"(?i:present|current|now|today|(?:19|20)\d{2}\b"
    r"|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?,?\s+(?:19|20)\d{2})"
)
_LEADING = re.compile(rf"^\s*(?:{_GLYPH_CLASS}+\s*|{_SPACED_CLASS}\s+(?!{_DATE_AHEAD}))(?=\S)")
# A glyph alone on its line (PDF extraction often splits it from its text). Only
# unambiguous glyphs count: a lone "-" or "o" line is more likely a separator.
_ONLY_GLYPH = re.compile(rf"^\s*{_GLYPH_CLASS}+\s*$")
_NUMBERED = re.compile(r"^\s*\(?\d{1,2}[.)]\s+")


def strip_bullet(line: str) -> str:
    """The line without its leading bullet (or the line unchanged)."""
    return _LEADING.sub("", line, count=1)


def is_bullet(line: str) -> bool:
    return bool(_LEADING.match(line) or _NUMBERED.match(line))


def normalize_bullets(text: str) -> str:
    """Rewrite every bulleted line to start with "• "; join glyphs left alone on a line."""
    out: list[str] = []
    pending = False
    for line in text.splitlines():
        if _ONLY_GLYPH.match(line):
            pending = True
            continue
        if not line.strip():
            out.append(line)
            continue
        if pending or _LEADING.match(line):
            out.append(f"{BULLET} {strip_bullet(line).strip()}")
            pending = False
        else:
            out.append(line)
    return "\n".join(out)
