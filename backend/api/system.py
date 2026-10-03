"""System routes: health check, ping, and SPA frontend fallback."""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.core.config import FRONTEND_DIR, APP_TITLE, APP_VERSION

router = APIRouter()


@router.get("/api/health")
def health_check():
    """Health status and metadata endpoint."""
    return {
        "status": "ok",
        "app": APP_TITLE,
        "version": APP_VERSION,
        "engine": "scikit-learn",
        "frontend_built": os.path.isdir(FRONTEND_DIR)
    }


@router.get("/{full_path:path}")
def serve_frontend(full_path: str):
    """Serve the built React frontend. Falls back to index.html for SPA routing."""
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found.")

    file_path = os.path.join(FRONTEND_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)

    return {
        "message": "Frontend not built yet. For development, run 'npm run dev' in the frontend directory."
    }
