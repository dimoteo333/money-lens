"""Money Lens API walking skeleton.

M0-02 scope only: application scaffold and health endpoint.
No OCR, LLM, financial calculation, or cloud deployment logic here.
"""

from __future__ import annotations

import os

from fastapi import FastAPI

APP_NAME = "money-lens-api"
API_VERSION = "0.1.0"


def create_app() -> FastAPI:
    app = FastAPI(
        title=APP_NAME,
        version=API_VERSION,
        description="금융상품 의사결정 지원 MVP API (walking skeleton)",
    )

    @app.get("/health")
    def health() -> dict:
        """Liveness probe.

        Deliberately exposes only service identity and status.
        Never returns provider, secret, configuration, or environment data.
        """
        return {"status": "ok", "service": APP_NAME, "version": API_VERSION}

    return app


app = create_app()

# Fail fast on misconfigured local storage in later stages; kept inert here so
# the walking skeleton runs without external dependencies.
assert os.environ.get("APP_ENV", "local") in {"local", "ci", "demo"}, "unknown APP_ENV"
