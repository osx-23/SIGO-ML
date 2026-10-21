"""Entrenamiento local con validación temporal y modelo de referencia.

Ejemplo:
python -m training.train --input data/dataset_demo.csv --demo
"""
import argparse
from pathlib import Path
from datetime import datetime, timezone
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

FEATURES = ["plaza_id", "turno_id", "programados", "dia_semana", "mes"]


def baseline_means(train):
    grouped = train.groupby(["plaza_id", "turno_id"])["ausentes"].mean().to_dict()
    return grouped, float(train["ausentes"].mean())


def baseline_predict(df, means, global_mean):
    return np.array([means.get((int(row.plaza_id), int(row.turno_id)), global_mean)
                     for row in df.itertuples(index=False)], dtype=float)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="artifacts/asistencia.joblib")
    parser.add_argument("--demo", action="store_true", help="Marca predicciones como demostración")
    args = parser.parse_args()

    df = pd.read_csv(args.input, parse_dates=["fecha"])
    expected = {"fecha", "plaza_id", "turno_id", "programados", "ausentes"}
    if not expected.issubset(df.columns):
        raise ValueError(f"Faltan columnas: {sorted(expected - set(df.columns))}")
    if df["fecha"].isna().any() or df[list(expected - {"fecha"})].isna().any().any():
        raise ValueError("El dataset contiene valores nulos")
    if ((df["ausentes"] < 0) | (df["ausentes"] > df["programados"])).any():
        raise ValueError("Ausencias fuera del rango de programados")
    if df.duplicated(subset=["fecha", "plaza_id", "turno_id"]).any():
        raise ValueError("Hay duplicados por fecha, plaza y turno")

    df = df.sort_values("fecha").reset_index(drop=True)
    dates = sorted(df["fecha"].dt.normalize().unique())
    if len(dates) < 30:
        raise ValueError("Se requieren por lo menos 30 días diferentes para esta prueba de entrenamiento")
    cutoff = dates[int(len(dates) * .8)]
    train = df[df["fecha"] < cutoff].copy()
    valid = df[df["fecha"] >= cutoff].copy()
    if train.empty or valid.empty:
        raise ValueError("No se pudo realizar una división temporal de entrenamiento/validación")
    for part in (train, valid):
        part["dia_semana"] = part["fecha"].dt.dayofweek
        part["mes"] = part["fecha"].dt.month

    means, global_mean = baseline_means(train)
    pred_base = baseline_predict(valid, means, global_mean)
    mae_base = mean_absolute_error(valid["ausentes"], pred_base)

    transformer = ColumnTransformer([
        ("categoricas", OneHotEncoder(handle_unknown="ignore"), ["plaza_id", "turno_id"]),
        ("numericas", "passthrough", ["programados", "dia_semana", "mes"]),
    ])
    model = Pipeline([
        ("variables", transformer),
        ("modelo", RandomForestRegressor(n_estimators=80, max_depth=6, min_samples_leaf=5,
                                         random_state=42, n_jobs=1)),
    ])
    model.fit(train[FEATURES], train["ausentes"])
    pred_ml = model.predict(valid[FEATURES])
    mae_ml = mean_absolute_error(valid["ausentes"], pred_ml)
    selected = "random_forest" if mae_ml < mae_base else "baseline"
    meta = {"version": "0.1.0", "origen_datos": "demo" if args.demo else "real",
            "registros_train": int(len(train)), "registros_validacion": int(len(valid)),
            "primer_dia_train": str(train["fecha"].min().date()),
            "ultimo_dia_train": str(train["fecha"].max().date()),
            "mae_baseline": round(float(mae_base), 4), "mae_ml": round(float(mae_ml), 4),
            "entrenado_en": datetime.now(timezone.utc).isoformat()}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"selected": selected, "model": model if selected == "random_forest" else None,
                 "group_means": means, "global_mean": global_mean, "metadata": meta}, path)
    print("MAE baseline:", round(mae_base, 3))
    print("MAE Random Forest:", round(mae_ml, 3))
    print("Modelo seleccionado:", selected)
    print("Origen:", meta["origen_datos"])
    print("Archivo:", path)


if __name__ == "__main__":
    main()
