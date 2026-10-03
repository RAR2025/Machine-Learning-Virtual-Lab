"""HTTP API assembly: FastAPI app + router wiring."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import system
from backend.core.config import APP_TITLE, APP_VERSION, CORS_ORIGINS


def create_app() -> FastAPI:
    app = FastAPI(
        title=APP_TITLE,
        version=APP_VERSION,
        description="Real-Time Machine Learning Virtual Lab Decision Boundary Engine"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Optional boundary router hook (Member 2 Phase 3)
    try:
        from backend.api import boundary
        app.include_router(boundary.router)
    except (ImportError, AttributeError):
        pass

    # System & SPA fallback routes (always included last)
    app.include_router(system.router)

    return app


app = create_app()
