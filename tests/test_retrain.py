import pandas as pd
import pytest

from training.retrain import candidate_is_better, score_model, validation_frame


def artifact(mean, origin="real"):
    return {"selected": "baseline", "group_means": {(4, 2): mean},
            "global_mean": mean, "metadata": {"origen_datos": origin}}


def test_promover_solamente_si_disminuye_el_mae():
    days = pd.date_range("2026-09-01", periods=30)
    data = pd.DataFrame({
        "fecha": days, "plaza_id": [4] * 30, "turno_id": [2] * 30,
        "programados": [18] * 30, "ausentes": [1] * 30,
    })
    valid = validation_frame(data)
    assert len(valid) > 0
    assert score_model(artifact(1), valid) == 0.0
    assert candidate_is_better(artifact(1), artifact(3), valid)
    assert not candidate_is_better(artifact(3), artifact(1), valid)
    assert not candidate_is_better(artifact(1), artifact(1), valid)


def test_reemplaza_modelo_demo_por_modelo_real():
    valid = pd.DataFrame({"fecha": pd.to_datetime(["2026-10-10"]),
                          "plaza_id": [4], "turno_id": [2],
                          "programados": [18], "ausentes": [1]})
    assert candidate_is_better(artifact(1), artifact(4, "demo"), valid)


def test_no_entrenar_con_pocas_fechas():
    df = pd.DataFrame({"fecha": pd.to_datetime(["2026-10-01"])})
    with pytest.raises(ValueError, match="30"):
        validation_frame(df)
