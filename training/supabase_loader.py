"""Consulta histórica agregada de asistencia, sin datos personales y sin modificar Supabase."""
from datetime import date
import os

import pandas as pd
import psycopg

COLUMNS = ["fecha", "plaza_id", "turno_id", "programados", "ausentes"]
QUERY = """
SELECT fecha, plaza_id, turno_id, programados, (programados - presentes) AS ausentes
FROM public.asistencia_registro
WHERE fecha <= %s
ORDER BY fecha, plaza_id, turno_id
"""


def validate_rows(rows):
    """Validación estricta: no descartar silenciosamente registros incorrectos."""
    df = pd.DataFrame(rows, columns=COLUMNS)
    if df.empty:
        raise ValueError("No hay registros históricos de asistencia")
    df["fecha"] = pd.to_datetime(df["fecha"], errors="raise")
    if df["fecha"].isna().any():
        raise ValueError("Hay fechas nulas")
    for col in COLUMNS[1:]:
        numeric = pd.to_numeric(df[col], errors="raise")
        if numeric.isna().any() or (numeric % 1 != 0).any():
            raise ValueError(f"Columna inválida: {col}")
        df[col] = numeric.astype("int64")
    if ((df["programados"] <= 0) | (df["ausentes"] < 0)
            | (df["ausentes"] > df["programados"])).any():
        raise ValueError("Asistencias fuera del rango esperado")
    if (df[["plaza_id", "turno_id"]] <= 0).any().any():
        raise ValueError("Plaza o turno inválidos")
    if df.duplicated(["fecha", "plaza_id", "turno_id"]).any():
        raise ValueError("Duplicados por fecha, plaza y turno; revisar origen")
    return df.sort_values(["fecha", "plaza_id", "turno_id"]).reset_index(drop=True)


def fetch_attendance(database_url=None, as_of=None):
    dsn = database_url or os.getenv("SIGO_ML_DATABASE_URL", "")
    if not dsn:
        raise RuntimeError("Falta SIGO_ML_DATABASE_URL (usuario PostgreSQL de solo lectura)")
    sslmode = os.getenv("SIGO_ML_DB_SSLMODE", "verify-full")
    if sslmode not in {"verify-full", "verify-ca", "require"}:
        raise ValueError("SIGO_ML_DB_SSLMODE debe asegurar una conexión TLS")
    # prepare_threshold=None funciona también con el pooler de Supabase.
    with psycopg.connect(dsn, connect_timeout=15, sslmode=sslmode,
                         prepare_threshold=None) as conn:
        with conn.cursor() as cur:
            # Solo esta transacción es read-only; no modifica la sesión del pooler.
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(QUERY, (as_of or date.today(),))
            rows = cur.fetchall()
    return validate_rows(rows)
