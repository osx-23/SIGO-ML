from fastapi import Header, HTTPException, status
from app.core.config import INTERNAL_TOKEN


def require_internal_service(x_internal_token: str | None = Header(default=None)) -> None:
    if not INTERNAL_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configure SIGO_ML_INTERNAL_TOKEN antes de aceptar solicitudes",
        )
    # Comparación en tiempo constante; la autenticación de usuarios sigue en SIGO-BACK.
    import hmac
    if not x_internal_token or not hmac.compare_digest(x_internal_token, INTERNAL_TOKEN):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Servicio no autorizado")
