from services.dates import total_years
from services.resume_parser import parse_resume
from tests.conftest import TODAY, read_fixture


def test_sections_detected():
    resume = parse_resume(read_fixture("resume_strong.txt"), TODAY)
    assert {"header", "summary", "experience", "education", "skills"} <= set(resume.sections)
    assert resume.has_email and resume.has_phone


def test_experience_entries_include_title_line():
    resume = parse_resume(read_fixture("resume_strong.txt"), TODAY)
    assert len(resume.experience_entries) == 2
    first, second = resume.experience_entries
    assert first.lines[0] == "Senior Software Engineer, Acme Corp"
    assert second.lines[0] == "Software Engineer, Beta Ltd"
    # The title of the second job must not be left attached to the first job.
    assert "Software Engineer, Beta Ltd" not in first.lines


def test_education_dates_not_counted_as_experience():
    resume = parse_resume(read_fixture("resume_strong.txt"), TODAY)
    # Jan 2016 .. Nov 2026; the 2011-2015 degree is excluded.
    assert total_years(resume.date_ranges) == 10.9
    assert resume.highest_degree == "bachelor"


def test_heading_variants():
    text = "PROFESSIONAL EXPERIENCE\nDev, X\n2020 - 2021\nTechnical Skills:\nPython\nEducation & Training\nBSc Physics"
    resume = parse_resume(text, TODAY)
    assert {"experience", "skills", "education"} <= set(resume.sections)
