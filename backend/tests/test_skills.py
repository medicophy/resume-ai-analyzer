import json

import pytest

from services.skills import SKILLS_FILE, load_catalog


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Built REST APIs in Python and FastAPI", {"Python", "FastAPI", "REST APIs"}),
        ("C/C++ and C# on .NET", {"C", "C++", "C#", ".NET"}),
        ("java and javascript", {"Java", "JavaScript"}),
        ("used k8s and Docker", {"Kubernetes", "Docker"}),
        ("CI-CD pipelines", {"CI/CD"}),
        ("Wrote Go services", {"Go"}),
        ("statistical analysis in R", {"R", "Statistics"}),
        ("ML models", {"Machine Learning"}),
        ("Advanced Excel", {"Excel"}),
        ("Spring Boot microservices", {"Spring Boot", "Microservices"}),
    ],
)
def test_detects_skills(text, expected):
    assert set(load_catalog().find_in(text)) == expected


@pytest.mark.parametrize(
    "text",
    [
        "R&D team working on go-to-market plans",
        "I excel at teamwork",
        "Spring 2020 internship",
        "administered 5 ml doses",
        "the rest of the team",
        "a swift response to express interest",
    ],
)
def test_ignores_everyday_words(text):
    assert load_catalog().find_in(text) == []


def test_catalog_is_consistent():
    data = json.loads(SKILLS_FILE.read_text(encoding="utf-8"))
    names = [s["name"] for s in data["skills"]]
    assert len(names) == len(set(names))
    for skill in data["skills"]:
        for related in skill.get("related", []):
            assert related in names, f"{skill['name']} references unknown skill {related}"
