import os
from pathlib import Path

MODEL_PATH = Path(os.getenv("SIGO_ML_MODEL_PATH", "artifacts/asistencia.joblib"))
INTERNAL_TOKEN = os.getenv("SIGO_ML_INTERNAL_TOKEN", "")
