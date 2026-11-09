"""Vercel entry point: serves the FastAPI backend under /api.

Vercel routes every /api/* request here (see vercel.json). The backend itself defines
its routes without a prefix (/, /analyze, /ai-review), so it is mounted at /api.
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI  # noqa: E402

from main import app as backend_app  # noqa: E402

# The public wrapper exposes no docs or OpenAPI schema; the mounted backend serves the API.
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/api", backend_app)
