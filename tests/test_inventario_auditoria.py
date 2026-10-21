"""Pruebas de validación del historial mensual antes de crear modelos de Inventario."""
from datetime import date

import pandas as pd
import pytest

from training.auditar_inventario import auditar


def guardar(tmp_path, filas):
    path = tmp_path / "consumo.csv"
    pd.DataFrame(filas, columns=["plaza_id", "producto_id", "periodo", "consumo"]).to_csv(
        path, index=False
    )
    return path


def test_octubre_abierto_no_cuenta_como_historial_cerrado(tmp_path):
    archivo = guardar(tmp_path, [
        (3, 9, "2026-10-01", 5),
        (3, 2, "2026-10-01", 7),
    ])
    res = auditar(archivo, date(2026, 10, 21))
    assert res["meses_completos"] == 0
    assert res["registros_meses_abiertos_o_futuros"] == 2
    assert res["estado"] == "historial_insuficiente"
    assert res["puede_entrenar_modelo_productivo"] is False


def test_seis_meses_cerrados_solo_permiten_evaluacion_inicial(tmp_path):
    filas = [
        (3, 9, f"2026-{mes:02d}-01", mes + 1) for mes in range(1, 7)
    ]
    res = auditar(guardar(tmp_path, filas), date(2026, 10, 21))
    assert res["meses_completos"] == 6
    assert res["series_con_al_menos_seis_meses_completos"] == 1
    assert res["estado"] == "datos_para_evaluacion_inicial"
    assert res["puede_entrenar_modelo_productivo"] is False


def test_rechaza_consumo_negativo(tmp_path):
    archivo = guardar(tmp_path, [(1, 2, "2026-09-01", -1)])
    with pytest.raises(ValueError, match="negativos"):
        auditar(archivo, date(2026, 10, 21))


def test_rechaza_duplicado_plaza_producto_mes(tmp_path):
    archivo = guardar(tmp_path, [
        (1, 2, "2026-09-01", 2),
        (1, 2, "2026-09-01", 3),
    ])
    with pytest.raises(ValueError, match="duplicados"):
        auditar(archivo, date(2026, 10, 21))


def test_rechaza_mes_parcial(tmp_path):
    archivo = guardar(tmp_path, [(1, 2, "2026-09-20", 3)])
    with pytest.raises(ValueError, match="primer día"):
        auditar(archivo, date(2026, 10, 21))
