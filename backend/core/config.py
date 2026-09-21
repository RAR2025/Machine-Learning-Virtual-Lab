"""Central backend settings: paths, CORS, app metadata."""

import os

# .../Machine-Learning-Virtual-Lab
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")

APP_TITLE = "Auto ML Problem Detector API"
APP_VERSION = "1.0.0"

CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]

CONFUSION_PREFIX = "confusion_matrix_"
CONFUSION_SUFFIX = ".png"
