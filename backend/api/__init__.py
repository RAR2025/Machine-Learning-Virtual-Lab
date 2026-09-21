"""HTTP API assembly: FastAPI app + router wiring.

Route modules (one concern each):
  * backend.api.analyze  — POST /api/analyze
  * backend.api.cleaning — POST /api/clean
  * backend.api.training — POST /api/train
  * backend.api.models   — GET /api/models, POST /api/models/select
  * backend.api.split    — POST /api/split (stratified, stored per experiment)
  * backend.api.system   — health, reset, confusion images, SPA fallback
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import analyze, cleaning, models, split, system, training
from backend.core.config import APP_TITLE, APP_VERSION, CORS_ORIGINS


def create_app() -> FastAPI:
    app = FastAPI(title=APP_TITLE, version=APP_VERSION)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Specific routers first; the SPA catch-all in `system` goes last.
    app.include_router(analyze.router)
    app.include_router(cleaning.router)
    app.include_router(training.router)
    app.include_router(models.router)
    app.include_router(split.router)
    app.include_router(system.router)

    return app


app = create_app()
