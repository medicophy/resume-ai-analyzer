"""The Vercel entry point (api/index.py at the repo root) must serve the backend under /api."""

import importlib.util
import json
from pathlib import Path

from fastapi.testclient import TestClient

from config import Settings
from tests.conftest import make_pdf, read_fixture

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_vercel_app():
    spec = importlib.util.spec_from_file_location("vercel_entry", REPO_ROOT / "api" / "index.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


client = TestClient(load_vercel_app())


def test_status_under_api_prefix():
    body = client.get("/api/").json()
    assert body["status"] == "online" and "ai_enabled" in body


def test_analyze_under_api_prefix(jd_backend):
    resp = client.post(
        "/api/analyze",
        files={"file": ("cv.pdf", make_pdf(read_fixture("resume_strong.txt")), "application/pdf")},
        data={"job_description": jd_backend},
    )
    assert resp.status_code == 200
    assert resp.json()["overall_score"] > 80


def test_no_public_docs():
    # Both the wrapper and the mounted backend must hide them (the backend's own
    # /docs would otherwise appear at /api/docs).
    for path in ("/docs", "/openapi.json", "/api/docs", "/api/redoc", "/api/openapi.json"):
        assert client.get(path).status_code == 404, path


def test_local_app_keeps_docs():
    from main import app as local_app

    local = TestClient(local_app)
    assert local.get("/docs").status_code == 200
    assert local.get("/openapi.json").status_code == 200


def test_upload_limit_fits_vercel():
    # Vercel rejects request bodies over 4.5 MB. Check the code default, not the local
    # backend/.env, which may override it on a developer machine.
    default_mb = Settings.model_fields["max_upload_mb"].default
    assert default_mb * 1024 * 1024 + 100_000 < 4.5 * 1024 * 1024


def test_vercel_config_matches_entry_point():
    config = json.loads((REPO_ROOT / "vercel.json").read_text(encoding="utf-8"))
    assert "api/index.py" in config["functions"]
    assert config["outputDirectory"] == "frontend/dist"
    assert "--mode vercel" in config["buildCommand"]
    env_vercel = (REPO_ROOT / "frontend" / ".env.vercel").read_text(encoding="utf-8")
    assert "VITE_API_URL=/api" in env_vercel
    sources = [r["source"] for r in config["rewrites"]]
    # API rules first; the page fallback (client-side routes like /results) must come last
    # and must never catch /api paths.
    assert sources[:2] == ["/api", "/api/(.*)"]
    assert config["rewrites"][-1]["destination"] == "/index.html"
    import re
    fallback = re.compile("^" + sources[-1] + "$")
    assert fallback.match("/results") and fallback.match("/privacy") and fallback.match("/")
    assert not fallback.match("/api/analyze") and not fallback.match("/api")
    excluded = config["functions"]["api/index.py"]["excludeFiles"]
    assert "backend/data" not in excluded  # the skill list must ship with the function


def test_runtime_requirements_are_shared():
    backend_reqs = (REPO_ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
    assert "-r ../requirements.txt" in backend_reqs
    runtime = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8")
    for pkg in ("fastapi", "pymupdf", "pdfplumber", "python-docx", "httpx", "python-multipart"):
        assert pkg in runtime
    assert "pytest" not in runtime and "uvicorn" not in runtime
