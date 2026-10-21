from fastapi import FastAPI, Depends, HTTPException
from app.api.schemas import PrediccionAsistenciaRequest, PrediccionAsistenciaResponse
from app.application.predictor import predict, load_artifact
from app.core.security import require_internal_service

app = FastAPI(title="SIGO-ML", version="0.1.0")


@app.get("/health/live")
def live():
    return {"status": "up"}


@app.get("/health/ready")
def ready():
    try:
        artifact = load_artifact()
        return {"status": "ready", "modelo": artifact["selected"]}
    except HTTPException:
        raise HTTPException(status_code=503, detail="Modelo no disponible")


@app.post(
    "/internal/v1/asistencia/predecir",
    response_model=PrediccionAsistenciaResponse,
    dependencies=[Depends(require_internal_service)],
)
def predecir_asistencia(request: PrediccionAsistenciaRequest):
    return predict(request)
