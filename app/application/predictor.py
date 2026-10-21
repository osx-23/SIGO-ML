from functools import lru_cache
import joblib
import pandas as pd
from fastapi import HTTPException
from app.api.schemas import PrediccionAsistenciaRequest
from app.core.config import MODEL_PATH


@lru_cache(maxsize=1)
def load_artifact():
    if not MODEL_PATH.is_file():
        raise HTTPException(status_code=503, detail="No hay modelo entrenado disponible")
    # Solo cargar archivos producidos por nuestro entrenamiento: joblib usa pickle.
    return joblib.load(MODEL_PATH)


def predict(req: PrediccionAsistenciaRequest) -> dict:
    data = load_artifact()
    meta = data["metadata"]
    row = pd.DataFrame([{
        "fecha": req.fecha,
        "plaza_id": req.plazaId,
        "turno_id": req.turnoId,
        "programados": req.programados,
        "dia_semana": req.fecha.weekday(),
        "mes": req.fecha.month,
    }])
    if data["selected"] == "random_forest":
        raw = float(data["model"].predict(row[["plaza_id", "turno_id", "programados", "dia_semana", "mes"]])[0])
    else:
        from training.train import baseline_predict
        raw = baseline_predict(row, data["group_means"], data["global_mean"])[0]

    count = max(0, min(req.programados, round(raw)))
    return {
        "plazaId": req.plazaId,
        "turnoId": req.turnoId,
        "fecha": req.fecha,
        "programados": req.programados,
        "ausenciasEstimadas": count,
        "coberturaEstimada": req.programados - count,
        "modelo": data["selected"],
        "version": meta["version"],
        "origenDatos": meta["origen_datos"],
        "advertencia": "DEMO: no utilizar para decisiones operativas" if meta["origen_datos"] == "demo" else None,
    }
