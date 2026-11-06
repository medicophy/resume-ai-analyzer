"""Date-range parsing and experience-duration arithmetic."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

_MONTH_NAME = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"
# "Oct 2019", "October, 2019", "10/2019", "2019"
_DATE = rf"(?:{_MONTH_NAME},?\s+|(?:0?[1-9]|1[0-2])\s*/\s*)?(?:19|20)\d{{2}}"
_CURRENT = r"(?:present|current|now|today|ongoing|date)"
_SEPARATOR = r"\s*(?:[-–—]+|\bto\b|\buntil\b)\s*"

DATE_RANGE = re.compile(rf"(?P<start>{_DATE}){_SEPARATOR}(?P<end>{_DATE}|{_CURRENT}\b)", re.IGNORECASE)
_SINGLE_DATE = re.compile(
    rf"(?:(?P<month_name>{_MONTH_NAME}),?\s+|(?P<month_num>0?[1-9]|1[0-2])\s*/\s*)?(?P<year>(?:19|20)\d{{2}})",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class DateRange:
    start: int  # absolute month index: year * 12 + (month - 1)
    end: int
    raw: str
    has_months: bool

    @property
    def months(self) -> int:
        return self.end - self.start + 1


def _month_index(token: str, is_end: bool, today: date) -> tuple[int, bool] | None:
    token = token.strip()
    if re.fullmatch(_CURRENT, token, re.IGNORECASE):
        return today.year * 12 + today.month - 1, True
    m = _SINGLE_DATE.fullmatch(token)
    if not m:
        return None
    year = int(m.group("year"))
    if m.group("month_name"):
        month, has_month = MONTHS[m.group("month_name")[:3].lower()], True
    elif m.group("month_num"):
        month, has_month = int(m.group("month_num")), True
    else:
        # Year only: assume the whole year on both ends ("2018 - 2020" = Jan 2018..Dec 2020).
        month, has_month = (12 if is_end else 1), False
    return year * 12 + month - 1, has_month


def find_date_ranges(text: str, today: date | None = None) -> list[DateRange]:
    today = today or date.today()
    now = today.year * 12 + today.month - 1
    ranges: list[DateRange] = []
    for m in DATE_RANGE.finditer(text):
        start = _month_index(m.group("start"), is_end=False, today=today)
        end = _month_index(m.group("end"), is_end=True, today=today)
        if not start or not end:
            continue
        # A year-only end date in the current year must not run past today.
        end_idx = min(end[0], now)
        if end_idx < start[0]:
            continue
        ranges.append(DateRange(start=start[0], end=end_idx, raw=m.group(0), has_months=start[1] and end[1]))
    return ranges


def total_years(ranges: list[DateRange]) -> float:
    """Total time covered by the ranges, counting overlapping periods only once."""
    if not ranges:
        return 0.0
    merged: list[list[int]] = []
    for r in sorted(ranges, key=lambda r: r.start):
        if merged and r.start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], r.end)
        else:
            merged.append([r.start, r.end])
    months = sum(end - start + 1 for start, end in merged)
    return round(months / 12, 1)
