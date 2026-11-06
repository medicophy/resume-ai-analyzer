from datetime import date

import pytest

from services.dates import find_date_ranges, total_years

TODAY = date(2026, 11, 6)


def idx(year: int, month: int) -> int:
    return year * 12 + month - 1


@pytest.mark.parametrize(
    ("text", "start", "end"),
    [
        ("Oct 2019 - Dec 2021", idx(2019, 10), idx(2021, 12)),  # "Oct" used to break parsing
        ("Nov 2018 – Jan 2020", idx(2018, 11), idx(2020, 1)),
        ("September 2017 — March 2019", idx(2017, 9), idx(2019, 3)),
        ("01/2020 - 03/2022", idx(2020, 1), idx(2022, 3)),
        ("2015 to 2020", idx(2015, 1), idx(2020, 12)),
        ("Oct 2019 - Present", idx(2019, 10), idx(2026, 11)),
        ("2025 - 2026", idx(2025, 1), idx(2026, 11)),  # year-only end is capped at today
    ],
)
def test_parses_ranges(text, start, end):
    (r,) = find_date_ranges(text, TODAY)
    assert (r.start, r.end) == (start, end)


def test_ignores_backwards_ranges():
    assert find_date_ranges("2022 - 2019", TODAY) == []


def test_total_years_merges_overlaps():
    ranges = find_date_ranges("Jan 2016 - Dec 2018\nJun 2018 - Jun 2019\nJan 2020 - Dec 2022", TODAY)
    # Jan 2016..Jun 2019 (42 months, overlap counted once) + 36 months = 78 months
    assert total_years(ranges) == 6.5
