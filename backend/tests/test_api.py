import pytest
from fastapi.testclient import TestClient

from config import settings
from main import app
from tests.conftest import make_pdf, read_fixture

client = TestClient(app)


def post(data: bytes, name: str, jd: str):
    return client.post("/analyze", files={"file": (name, data, "application/octet-stream")},
                       data={"job_description": jd})


def test_health():
    assert client.get("/").json()["status"] == "online"


def test_analyze_success(jd_backend):
    resp = post(make_pdf(read_fixture("resume_strong.txt")), "jane.pdf", jd_backend)
    assert resp.status_code == 200
    body = resp.json()
    assert body["filename"] == "jane.pdf"
    assert 0 <= body["overall_score"] <= 100
    # Fields the current frontend relies on.
    assert body["match_score"] == body["overall_score"]
    assert isinstance(body["missing_keywords"], list) and body["char_count"] > 0


def test_missing_job_description():
    resp = post(make_pdf("Python"), "cv.pdf", "   ")
    assert resp.status_code == 400 and "job description" in resp.json()["detail"]


def test_unsupported_file(jd_backend):
    resp = post(b"hello", "cv.txt", jd_backend)
    assert resp.status_code == 400


def test_empty_file(jd_backend):
    assert post(b"", "cv.pdf", jd_backend).status_code == 400


def test_oversized_file(jd_backend, monkeypatch):
    monkeypatch.setattr(settings, "max_upload_mb", 1)
    resp = post(b"%PDF" + b"0" * (1024 * 1024 + 10), "big.pdf", jd_backend)
    assert resp.status_code == 413


def test_internal_errors_are_not_leaked(jd_backend, monkeypatch):
    import web.routes

    def boom(*args, **kwargs):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(web.routes, "analyze", boom)
    resp = post(make_pdf("Python"), "cv.pdf", jd_backend)
    assert resp.status_code == 500
    assert "secret" not in resp.json()["detail"]
