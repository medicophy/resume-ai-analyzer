"""Skill taxonomy loading and skill detection in free text."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

SKILLS_FILE = Path(__file__).resolve().parent.parent / "data" / "skills.json"

# A term must not be glued to other word characters. '+', '#' and '.' count as part of a
# term ("C++", "C#", ".NET"), so they must not appear right next to a match either.
_BEFORE = r"(?<![\w+#.])"
_AFTER = r"(?![\w+#]|\.\w)"
# Case-sensitive short terms (Go, R, C) are easily confused with ordinary words
# ("Go-to-market", "R&D"), so they get a stricter right-hand boundary.
_AFTER_STRICT = r"(?![\w+#&'-]|\.\w)"


@dataclass(frozen=True)
class Skill:
    name: str
    category: str
    aliases: tuple[str, ...] = ()
    case_sensitive: tuple[str, ...] = ()
    related: tuple[str, ...] = ()


@dataclass
class SkillCatalog:
    skills: dict[str, Skill]
    _patterns: dict[str, re.Pattern[str]] = field(default_factory=dict, repr=False)

    def pattern(self, name: str) -> re.Pattern[str]:
        if name not in self._patterns:
            self._patterns[name] = _compile(self.skills[name])
        return self._patterns[name]

    def find_in(self, text: str) -> list[str]:
        """Return skill names mentioned in text, in catalog order."""
        return [name for name in self.skills if self.pattern(name).search(text)]

    def mentions(self, name: str, text: str) -> bool:
        return bool(self.pattern(name).search(text))


def _term_regex(term: str, strict: bool) -> str:
    # Let a space in a term match any run of whitespace or a hyphen ("ci cd" ~ "ci-cd").
    escaped = r"[\s\-]+".join(re.escape(part) for part in term.split())
    return _BEFORE + escaped + (_AFTER_STRICT if strict else _AFTER)


def _compile(skill: Skill) -> re.Pattern[str]:
    insensitive_terms = [skill.name, *skill.aliases]
    # Terms listed as case-sensitive must never also be matched case-insensitively.
    blocked = {t.lower() for t in skill.case_sensitive}
    insensitive = [_term_regex(t, strict=False) for t in insensitive_terms if t.lower() not in blocked]
    sensitive = [_term_regex(t, strict=True) for t in skill.case_sensitive]

    parts = []
    if insensitive:
        parts.append("(?i:" + "|".join(insensitive) + ")")
    parts.extend(sensitive)
    return re.compile("|".join(parts))


@lru_cache(maxsize=1)
def load_catalog() -> SkillCatalog:
    data = json.loads(SKILLS_FILE.read_text(encoding="utf-8"))
    skills = {
        entry["name"]: Skill(
            name=entry["name"],
            category=entry.get("category", "Other"),
            aliases=tuple(entry.get("aliases", [])),
            case_sensitive=tuple(entry.get("case_sensitive", [])),
            related=tuple(entry.get("related", [])),
        )
        for entry in data["skills"]
    }
    return SkillCatalog(skills=skills)
