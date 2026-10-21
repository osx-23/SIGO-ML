import os
from fastapi.testclient import TestClient

# La variable se configura antes de importar el proyecto.
os.environ["SIGO_ML_INTERNAL_TOKEN"] = "token-seguro-de-prueba"

from app.main import app  # noqa: E402

client = TestClient(app)
PAYLOAD = {"plazaId": 4, "turnoId": 2, "fecha": "2026-11-05", "programados": 18}


def test_health_live():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "up"


def test_sin_token_devuelve_401():
    assert client.post("/internal/v1/asistencia/predecir", json=PAYLOAD).status_code == 401


def test_entrada_invalida_devuelve_422():
    response = client.post("/internal/v1/asistencia/predecir",
        json={**PAYLOAD, "programados": -1},
        headers={"X-Internal-Token": "token-seguro-de-prueba"})
    assert response.status_code == 422


def test_no_devuelve_cifras_inventadas_si_no_hay_modelo(monkeypatch):
    from app.application import predictor
    from fastapi import HTTPException
    predictor.load_artifact.cache_clear()
    def missing():
        raise HTTPException(status_code=503, detail="No hay modelo")
    monkeypatch.setattr(predictor, "load_artifact", missing)
    response = client.post("/internal/v1/asistencia/predecir", json=PAYLOAD,
        headers={"X-Internal-Token": "token-seguro-de-prueba"})
    assert response.status_code == 503
