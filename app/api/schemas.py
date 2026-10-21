from datetime import date
from pydantic import BaseModel, Field


class PrediccionAsistenciaRequest(BaseModel):
    plazaId: int = Field(gt=0)
    turnoId: int = Field(gt=0)
    fecha: date
    programados: int = Field(ge=0)


class PrediccionAsistenciaResponse(BaseModel):
    plazaId: int
    turnoId: int
    fecha: date
    programados: int
    ausenciasEstimadas: int
    coberturaEstimada: int
    modelo: str
    version: str
    origenDatos: str
    advertencia: str | None = None
