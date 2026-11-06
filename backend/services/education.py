"""Degree detection shared by the resume and job-description parsers."""

from __future__ import annotations

import re

DEGREE_RANK = {"associate": 1, "bachelor": 2, "master": 3, "doctorate": 4}

# Abbreviations need care: "MS Office", "BA" in "BA team", "MA" the state. Short forms are
# therefore only accepted with dots (B.S.) or when followed by "in"/"of" (BS in Physics).
_FOLLOW = r"(?=\s*(?:in|of)\b|\s*\()"
DEGREE_PATTERNS: dict[str, re.Pattern[str]] = {
    "doctorate": re.compile(
        r"\b(?:ph\.?\s?d\b|doctorate|doctoral|doctor of (?:philosophy|science|engineering)|d\.phil\b)"
        r"|\bM\.D\.(?!\w)",
        re.IGNORECASE,
    ),
    "master": re.compile(
        r"(?<!scrum )\bmaster(?:['’]?s)?\b(?! data)|\bm\.(?:s|sc|a|eng|tech|phil)\.?(?!\w)|\bmsc\b|\bmba\b"
        rf"|\bm\.?tech\b|\bmeng\b|(?-i:\b(?:MS|MA){_FOLLOW})",
        re.IGNORECASE,
    ),
    "bachelor": re.compile(
        r"\bbachelor(?:['’]?s)?\b|\bb\.(?:s|sc|a|e|eng|tech|com)\.?(?!\w)|\bbsc\b|\bb\.?tech\b|\bbeng\b"
        rf"|(?-i:\b(?:BS|BA|BE){_FOLLOW})|\bundergraduate degree\b",
        re.IGNORECASE,
    ),
    "associate": re.compile(r"\bassociate(?:'?s)? degree\b|\bassociate of\b", re.IGNORECASE),
}


def degrees_in(text: str) -> list[str]:
    """Degree levels mentioned in the text, highest first."""
    found = [level for level, pattern in DEGREE_PATTERNS.items() if pattern.search(text)]
    return sorted(found, key=DEGREE_RANK.__getitem__, reverse=True)


def highest_degree(text: str) -> str | None:
    found = degrees_in(text)
    return found[0] if found else None
