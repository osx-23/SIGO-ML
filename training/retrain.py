"""Extrae desde Supabase, entrena, valida y publica el modelo local de forma atómica."""
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error

from training.supabase_loader import fetch_attendance
from training.train import FEATURES, baseline_predict


def score_model(artifact, frame):
    features = frame.copy()
    features["dia_semana"] = features["fecha"].dt.dayofweek
    features["mes"] = features["fecha"].dt.month
    if artifact["selected"] == "random_forest":
        predictions = artifact["model"].predict(features[FEATURES])
    else:
        predictions = baseline_predict(features, artifact["group_means"], artifact["global_mean"])
    return float(mean_absolute_error(features["ausentes"], predictions))


def validation_frame(df):
    dates = sorted(df["fecha"].dt.normalize().unique())
    if len(dates) < 30:
        raise ValueError("Se requieren al menos 30 fechas distintas")
    return df[df["fecha"] >= dates[int(len(dates) * 0.8)]].copy()


def candidate_is_better(candidate, current, validation, minimum_gain=0.0):
    if current["metadata"].get("origen_datos") == "demo":
        return True
    if current["metadata"].get("origen_datos") != "real":
        raise ValueError("Origen desconocido del modelo instalado")
    previous_mae = score_model(current, validation)
    candidate_mae = score_model(candidate, validation)
    print(f"MAE anterior: {previous_mae:.4f}; MAE nuevo: {candidate_mae:.4f}")
    return candidate_mae < previous_mae - minimum_gain


def retrain(database_url=None, model_path=None):
    df = fetch_attendance(database_url)
    validation = validation_frame(df)
    target = Path(model_path or os.getenv("SIGO_ML_MODEL_PATH", "artifacts/asistencia.joblib"))
    target.parent.mkdir(parents=True, exist_ok=True)
    minimum_gain = float(os.getenv("SIGO_ML_MIN_MAE_GAIN", "0"))
    if minimum_gain < 0:
        raise ValueError("SIGO_ML_MIN_MAE_GAIN no puede ser negativo")

    # Temporales fuera del repositorio; nunca publicamos CSV ni datos personales.
    with TemporaryDirectory(prefix=".sigo-ml-", dir=target.parent) as workdir:
        csv = Path(workdir) / "historico.csv"
        candidate_path = Path(workdir) / "nuevo.joblib"
        df.to_csv(csv, index=False)
        subprocess.run(
            [sys.executable, "-m", "training.train",
             "--input", str(csv), "--output", str(candidate_path)],
            check=True,
        )
        # joblib solamente carga artefactos locales creados por nuestro código.
        candidate = joblib.load(candidate_path)
        if target.is_file():
            current = joblib.load(target)
            if not candidate_is_better(candidate, current, validation, minimum_gain):
                print("Se conserva el modelo anterior: el candidato no mejora el MAE")
                return False
        os.replace(candidate_path, target)
    print(f"Modelo validado y actualizado: {target}")
    return True


if __name__ == "__main__":
    retrain()
