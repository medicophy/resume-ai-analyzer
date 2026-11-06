from services.jd_parser import parse_job_description


def test_required_vs_preferred_and_ignored_sections(jd_backend):
    jd = parse_job_description(jd_backend)
    assert set(jd.required_skills) == {
        "REST APIs", "Microservices", "AWS", "Python", "SQL", "PostgreSQL", "Docker", "Kubernetes",
    }
    assert set(jd.preferred_skills) == {"Kafka", "RabbitMQ", "Terraform", "GraphQL"}
    # Company blurb and benefits are not requirements.
    for skill in ("Swift", "Kotlin", "Redis"):
        assert skill not in jd.skills
    assert jd.has_structure


def test_years_requirements(jd_backend):
    jd = parse_job_description(jd_backend)
    assert {(y.years, y.skill) for y in jd.years} == {(5, None), (3, "Python")}
    assert jd.general_years.years == 5


def test_education_requirement(jd_backend):
    edu = parse_job_description(jd_backend).education
    assert edu.level == "bachelor"
    assert edu.priority == "required"
    assert edu.equivalent_experience_ok


def test_labelled_line_is_not_a_heading():
    jd = parse_job_description("Location: Remote\n- Python and Docker required")
    assert set(jd.required_skills) == {"Python", "Docker"}


def test_inline_markers_override_section():
    jd = parse_job_description("Requirements\n- Python\n- Terraform is a plus")
    assert jd.skills == {"Python": "required", "Terraform": "preferred"}


def test_required_wins_over_preferred():
    jd = parse_job_description("Requirements\n- Python\nNice to have\n- Python 3 type hints")
    assert jd.skills["Python"] == "required"


def test_number_words_and_unrelated_years():
    jd = parse_job_description("Founded 10 years ago.\nRequirements\n- Three years of experience with Java")
    assert [(y.years, y.skill) for y in jd.years] == [(3, "Java")]


def test_no_structure_treats_everything_as_required():
    jd = parse_job_description("We need someone who knows React and TypeScript.")
    assert jd.skills == {"React": "required", "TypeScript": "required"}
    assert not jd.has_structure
