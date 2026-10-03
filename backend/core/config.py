"""Central backend settings: paths, CORS, app metadata."""
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")

APP_TITLE = "ML Virtual Lab - Decision Boundary Playground API"
APP_VERSION = "2.0.0"

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]
