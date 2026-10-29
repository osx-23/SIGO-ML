from datetime import date

import pytest

from training.supabase_loader import validate_rows


def test_validar_historico_sin_datos_personales():
    frame = validate_rows([(date(2026, 10, 1), 4, 2, 18, 1)])
    assert list(frame.columns) == ["fecha", "plaza_id", "turno_id", "programados", "ausentes"]
    assert frame.loc[0, "ausentes"] == 1


def test_rechaza_duplicados_por_fecha_plaza_turno():
    row = (date(2026, 10, 1), 4, 2, 18, 1)
    with pytest.raises(ValueError, match="Duplicados"):
        validate_rows([row, row])


def test_rechaza_ausencias_mayores_a_programados():
    with pytest.raises(ValueError, match="fuera del rango"):
        validate_rows([(date(2026, 10, 1), 4, 2, 18, 19)])


def test_rechaza_conjunto_vacio():
    with pytest.raises(ValueError, match="No hay"):
        validate_rows([])
