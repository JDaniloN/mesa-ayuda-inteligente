"""Bearer de la API propia. No es el token del mock.

HTTPBearer deja el candado Authorize en /docs; un Header llamado
authorization no lo envía Swagger (cabecera reservada, igual que el mock).
"""

from __future__ import annotations

import hmac

from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.errores import cuerpo

ESQUEMA_BEARER = HTTPBearer(auto_error=False)


def exigir_token(
    request: Request,
    credenciales: HTTPAuthorizationCredentials | None = Security(ESQUEMA_BEARER),
) -> None:
    esperado = getattr(request.app.state, "api_token", "") or ""
    if not esperado.strip():
        raise HTTPException(
            status_code=503,
            detail=cuerpo(
                "configuracion",
                "Falta API_TOKEN en el entorno. No se versiona.",
            ),
        )
    if credenciales is None or not (credenciales.credentials or "").strip():
        raise HTTPException(
            status_code=401,
            detail=cuerpo(
                "no_autorizado",
                "Falta la cabecera Authorization Bearer.",
            ),
        )
    recibido = credenciales.credentials.strip()
    if not hmac.compare_digest(recibido, esperado):
        raise HTTPException(
            status_code=401,
            detail=cuerpo(
                "no_autorizado",
                "Token rechazado. Revise API_TOKEN.",
            ),
        )
