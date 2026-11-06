import pytest

from services.education import degrees_in


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("B.S. in Computer Science", ["bachelor"]),
        ("BS in Physics", ["bachelor"]),
        ("Bachelor of Engineering", ["bachelor"]),
        ("Master’s degree preferred", ["master"]),
        ("MSc Data Science", ["master"]),
        ("MS in Physics", ["master"]),
        ("Ph.D. Medical Physics", ["doctorate"]),
        ("Bachelor's or Master's degree", ["master", "bachelor"]),
    ],
)
def test_detects_degrees(text, expected):
    assert degrees_in(text) == expected


@pytest.mark.parametrize(
    "text",
    ["MS Office, Excel", "Scrum Master certified", "Master Data Management", "BA team lead",
     "must be in the office", "mastered SQL"],
)
def test_ignores_non_degrees(text):
    assert degrees_in(text) == []
