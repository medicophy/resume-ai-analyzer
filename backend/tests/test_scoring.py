from services.analyzer import analyze
from tests.conftest import TODAY, make_pdf, read_fixture


def run(resume_fixture: str, jd: str):
    return analyze(make_pdf(read_fixture(resume_fixture)), "resume.pdf", jd, today=TODAY)


def test_strong_resume_scores_highest(jd_backend):
    strong = run("resume_strong.txt", jd_backend)
    keywords = run("resume_keyword_list.txt", jd_backend)
    marketing = run("resume_marketing.txt", jd_backend)
    assert strong.overall_score > keywords.overall_score > marketing.overall_score
    assert strong.overall_score >= 80
    assert marketing.overall_score <= 25


def test_strong_resume_details(jd_backend):
    r = run("resume_strong.txt", jd_backend)
    statuses = {m.skill: m.status for m in r.skills}
    assert all(statuses[s] == "demonstrated" for s in ("Python", "Docker", "Kubernetes", "PostgreSQL"))
    assert statuses["Kafka"] == "missing"
    python = next(m for m in r.skills if m.skill == "Python")
    assert python.evidence and python.evidence[0].section == "experience"
    assert all(c.met for c in r.experience.checks)
    assert r.education.met


def test_keyword_list_gets_partial_credit_and_suggestions(jd_backend):
    r = run("resume_keyword_list.txt", jd_backend)
    assert {m.status for m in r.skills if m.priority == "required"} == {"listed"}
    assert any("only appears in your skills list" in s.message for s in r.suggestions)
    years = next(c for c in r.experience.checks if c.skill is None)
    assert not years.met and years.resume_years == 4.5


def test_unrelated_resume_is_capped(jd_backend):
    r = run("resume_marketing.txt", jd_backend)
    assert r.breakdown.skills.score == 0
    assert any("capped" in w for w in r.warnings)
    assert set(r.missing_keywords) >= {"Python", "Docker"}


def test_components_without_requirements_are_skipped():
    r = analyze(make_pdf(read_fixture("resume_strong.txt")), "r.pdf", "We need Python and Docker.", today=TODAY)
    assert r.breakdown.experience is None and r.breakdown.education is None
    assert r.breakdown.skills.weight == 1.0
    assert r.overall_score == 100.0


def test_jd_without_skills_warns():
    r = analyze(make_pdf(read_fixture("resume_strong.txt")), "r.pdf", "Friendly team, great office.", today=TODAY)
    assert r.overall_score is None
    assert any("No recognisable skills" in w for w in r.warnings)
