"""Central backend settings: paths, CORS, app metadata (env-driven).

Loads `backend/.env` (see `backend/.env.example`). Every value has a
sensible default so the app runs with no .env file present.
"""
import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - allows running without the dep installed
    def load_dotenv(*_args, **_kwargs):  # type: ignore[no-redef]
        return False

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend/.env explicitly (plus CWD fallback for `uvicorn main:app` runs).
load_dotenv(os.path.join(PROJECT_ROOT, "backend", ".env"))
load_dotenv(os.path.join(os.getcwd(), ".env"))


def _getenv(key: str, default: str) -> str:
    value = os.getenv(key)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def _getenv_int(key: str, default: int) -> int:
    try:
        return int(_getenv(key, str(default)))
    except ValueError:
        return default


def _ensure_scheme(url: str) -> str:
    """Prepend a scheme when hosts inject a bare hostname (Render fromService).

    Render's `fromService ... property: host` yields `my-service.onrender.com`
    with no scheme; CORSMiddleware needs a full origin, so default to
    https (http for localhost).
    """
    u = url.strip().rstrip("/")
    if "://" in u:
        return u
    if u.startswith("localhost") or u.startswith("127.0.0.1"):
        return f"http://{u}"
    return f"https://{u}"


def _parse_origins(raw: str) -> list:
    return [_ensure_scheme(o) for o in (o.strip() for o in raw.split(",")) if o]


APP_TITLE = _getenv("APP_TITLE", "ML Virtual Lab - Decision Boundary Playground API")
APP_VERSION = _getenv("APP_VERSION", "2.0.0")

HOST = _getenv("HOST", "0.0.0.0")
PORT = _getenv_int("PORT", 8000)

FRONTEND_DIR = _getenv("FRONTEND_DIR", os.path.join(PROJECT_ROOT, "frontend", "dist"))
FRONTEND_URL = _ensure_scheme(_getenv("FRONTEND_URL", "http://localhost:5173"))

CORS_ORIGINS = _parse_origins(
    _getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:8000,http://127.0.0.1:8000",
    )
)
# Always allow the configured frontend URL even if omitted from CORS_ORIGINS.
if FRONTEND_URL not in CORS_ORIGINS:
    CORS_ORIGINS.append(FRONTEND_URL)
