"""Application entry point (kept stable for `uvicorn backend.main:app`).

The real app is assembled in :mod:`backend.api`; routes live in
``backend/api/*.py``, business logic in ``backend/services/*``,
shared state in ``backend/core/state.py``.
"""

try:
    from backend.api import app
except ModuleNotFoundError:
    # Support `uvicorn main:app` run from inside the backend/ directory:
    # add the project root to sys.path so the `backend` package resolves.
    import os
    import sys

    sys.path.insert(
        0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    from backend.api import app

__all__ = ["app"]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
