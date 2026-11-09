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

from main import create_app  # noqa: E402

# Neither the wrapper nor the mounted backend exposes interactive docs or the OpenAPI schema.
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/api", create_app(enable_docs=False))
