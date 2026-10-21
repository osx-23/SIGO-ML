"""Auditoría de datos agregados de Inventario: NO genera predicciones.

Formato CSV: plaza_id,producto_id,periodo,consumo
La vista SIGO-TEST deriva consumos entre conteos finalizados; no es una
serie de ventas reales. Los periodos abiertos quedan excluidos de
la evaluación de suficiencia.
"""

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED = ("plaza_id", "producto_id", "periodo", "consumo")


def auditar(path: str | Path, fecha_corte: date | None = None) -> dict:
    """Valida el CSV y mide cuánto historial mensual cerrado está disponible."""
    fecha_corte = fecha_corte or date.today()
    raw = pd.read_csv(path)
    missing = sorted(set(REQUIRED) - set(raw.columns))
    if missing:
        raise ValueError(f"Faltan columnas: {missing}")

    df = raw.loc[:, REQUIRED].copy()
    df["periodo"] = pd.to_datetime(df["periodo"], format="%Y-%m-%d", errors="coerce")
    for column in ("plaza_id", "producto_id", "consumo"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if df.isna().any().any():
        raise ValueError("El CSV contiene fechas, cantidades o identificadores no válidos")
    if not np.isfinite(df[["plaza_id", "producto_id", "consumo"]].to_numpy(dtype=float)).all():
        raise ValueError("Hay valores numéricos no finitos")
    for column in ("plaza_id", "producto_id"):
        if (df[column] <= 0).any() or (df[column] % 1 != 0).any():
            raise ValueError(f"Identificadores inválidos: {column}")
    if (df["consumo"] < 0).any():
        raise ValueError("No se admiten consumos negativos")
    if (df["periodo"].dt.day != 1).any():
        raise ValueError("El periodo debe ser el primer día del mes")
    if df.duplicated(subset=["plaza_id", "producto_id", "periodo"]).any():
        raise ValueError("Hay registros duplicados por plaza, producto y mes")

    mes_abierto = pd.Timestamp(fecha_corte.replace(day=1))
    completos = df[df["periodo"] < mes_abierto].copy()
    incompletos = df[df["periodo"] >= mes_abierto].copy()
    series = completos.groupby(["plaza_id", "producto_id"])["periodo"].nunique()
    meses = int(completos["periodo"].nunique())
    series_con_seis_meses = int((series >= 6).sum())

    # Seis meses es solo un umbral exploratorio. No implica que la
    # predicción haya sido validada, ni que el modelo sea confiable.
    estado = (
        "datos_para_evaluacion_inicial"
        if meses >= 6 and series_con_seis_meses > 0
        else "historial_insuficiente"
    )
    return {
        "registros_csv": int(len(df)),
        "series_total": int(df.groupby(["plaza_id", "producto_id"]).ngroups),
        "registros_meses_completos": int(len(completos)),
        "registros_meses_abiertos_o_futuros": int(len(incompletos)),
        "meses_completos": meses,
        "series_con_al_menos_seis_meses_completos": series_con_seis_meses,
        "primer_mes_completo": (
            completos["periodo"].min().strftime("%Y-%m") if not completos.empty else None
        ),
        "ultimo_mes_completo": (
            completos["periodo"].max().strftime("%Y-%m") if not completos.empty else None
        ),
        "estado": estado,
        "puede_entrenar_modelo_productivo": False,
        "nota": "Los consumos derivan de conteos y entradas; no son ventas ni salidas diarias verificadas.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Auditar historial agregado de Inventario")
    parser.add_argument("--input", required=True, help="CSV agregado; nunca subir datos reales")
    parser.add_argument("--fecha-corte", default=date.today().isoformat())
    args = parser.parse_args()
    result = auditar(args.input, date.fromisoformat(args.fecha_corte))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
