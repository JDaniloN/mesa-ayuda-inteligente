"""Errores del servicio de solicitudes.

El cliente HTTP mapea status y fallos de red a estas clases.
No se expone httpx. Ningún mensaje incluye el token.
"""


class ErrorProveedor(Exception):
    """Fallo al hablar con el servicio de solicitudes."""


class ErrorTimeout(ErrorProveedor):
    """El proveedor no respondió a tiempo."""


class ErrorAutorizacion(ErrorProveedor):
    """Token ausente o rechazado (401)."""


class ErrorNoEncontrado(ErrorProveedor):
    """La solicitud no existe (404)."""


class ErrorValidacion(ErrorProveedor):
    """Cuerpo inválido (contrato local o 422 del proveedor)."""


class ErrorLimiteTasa(ErrorProveedor):
    """Demasiadas peticiones (429)."""


class ErrorServicio(ErrorProveedor):
    """Fallo del proveedor (5xx) o no hay conexión."""


def error_desde_respuesta(status: int, detalle: str = "") -> ErrorProveedor:
    """Traduce un código HTTP a error con mensaje comprensible."""
    texto = (detalle or "").strip()
    if status == 401:
        return ErrorAutorizacion(
            "No autorizado ante el servicio de solicitudes. Revise MOCK_TOKEN."
        )
    if status == 404:
        return ErrorNoEncontrado(
            texto or "No se encontró la solicitud en el servicio."
        )
    if status == 422:
        return ErrorValidacion(
            texto or "El cuerpo de la solicitud no cumple el contrato."
        )
    if status == 429:
        return ErrorLimiteTasa(
            "El servicio alcanzó el límite de peticiones. Espere y reintente."
        )
    if status >= 500:
        return ErrorServicio(
            texto or "El servicio de solicitudes falló. Intente de nuevo."
        )
    return ErrorProveedor(f"El servicio de solicitudes respondió {status}.")


def error_timeout(timeout_s: float) -> ErrorTimeout:
    return ErrorTimeout(
        f"El servicio de solicitudes no responde "
        f"(tiempo de espera {timeout_s:g} s). Intente de nuevo."
    )


def error_conexion(url: str) -> ErrorServicio:
    return ErrorServicio(
        f"No se pudo conectar a {url}. ¿Está el mock en marcha?"
    )
