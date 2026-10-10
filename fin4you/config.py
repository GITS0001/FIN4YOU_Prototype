import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROTOTYPE_DIR = DATA_DIR / "prototype"
MEDIA_DIR = DATA_DIR / "media"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
DB_PATH = DATA_DIR / "fin4you.db"

# Model Artifact Paths
CATEGORIZER_MODEL_PATH = ARTIFACTS_DIR / "categorizer_pipeline.joblib"
CATEGORIZER_META_PATH = ARTIFACTS_DIR / "categorizer_metadata.json"

# Operational Thresholds
CONFIDENCE_HIGH_THRESHOLD = 0.85
CONFIDENCE_MEDIUM_THRESHOLD = 0.60

# Ensure artifacts directory exists
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
