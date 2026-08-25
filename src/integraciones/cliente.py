"""Cliente del servicio mock de solicitudes.

Timeout 5 s (la latencia del mock llega a 2,5 s). Un reintento si
responde 429 con Retry-After. El 500 no se reintenta aquí: eso es
orquestación de la etapa 4. El token sale de MOCK_TOKEN, no del código.
"""

from __future__ import annotations

import time
from typing import Optional

import httpx
from pydantic import ValidationError

from src.configuracion import Configuracion
from src.integraciones.errores import (
    ErrorAutorizacion,
    ErrorProveedor,
    ErrorValidacion,
    error_conexion,
    error_desde_respuesta,
    error_timeout,
)
from src.integraciones.modelos import SolicitudEntrada, SolicitudSalida

URL_POR_DEFECTO = "http://localhost:8080"
TIMEOUT_S = 5.0


class ClienteMock:
    def __init__(
        self,
        base_url: str,
        token: str,
        timeout_s: float = TIMEOUT_S,
        http: Optional[httpx.Client] = None,
    ) -> None:
        if not (token or "").strip():
            raise ErrorAutorizacion(
                "Falta el token. Defina MOCK_TOKEN; no se versiona."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self._token = token.strip()
        self._propios = http is None
        self._http = http or httpx.Client(
            base_url=self.base_url,
            timeout=timeout_s,
        )

    @classmethod
    def desde_configuracion(cls, configuracion: Configuracion) -> ClienteMock:
        token = configuracion.mock_token.get_secret_value().strip()
        if not token:
            raise ErrorAutorizacion(
                "Falta MOCK_TOKEN. Defínalo en el entorno; no se versiona."
            )
        url = configuracion.mock_url.strip() or URL_POR_DEFECTO
        return cls(
            base_url=url,
            token=token,
            timeout_s=configuracion.mock_timeout,
        )

    @classmethod
    def desde_entorno(cls) -> ClienteMock:
        try:
            config = Configuracion()
        except ValidationError as exc:
            campos = {str(error["loc"][0]) for error in exc.errors()}
            if "mock_timeout" in campos:
                raise ErrorValidacion(
                    "MOCK_TIMEOUT debe ser un número mayor que 0."
                ) from exc
            raise ErrorValidacion("La configuración del entorno no es válida.") from exc
        return cls.desde_configuracion(config)

    def close(self) -> None:
        if self._propios:
            self._http.close()

    def listar(
        self,
        area: Optional[str] = None,
        estado: Optional[str] = None,
        limite: int = 50,
    ) -> list[SolicitudSalida]:
        params: dict[str, str | int] = {"limite": limite}
        if area:
            params["area"] = area
        if estado:
            params["estado"] = estado
        respuesta = self._pedir("GET", "/solicitudes", params=params)
        cuerpo = _json_o_error(respuesta)
        if not isinstance(cuerpo, list):
            raise ErrorValidacion("El listado del servicio no es una lista.")
        return [_parsear_salida(item) for item in cuerpo]

    def crear(
        self,
        asunto: str,
        area: str,
        solicitante: str,
        descripcion: str = "",
        canal: str = "api",
        clave_idempotencia: Optional[str] = None,
    ) -> SolicitudSalida:
        try:
            entrada = SolicitudEntrada(
                asunto=asunto,
                descripcion=descripcion,
                area=area,
                solicitante=solicitante,
                canal=canal,
            )
        except ValidationError as exc:
            raise ErrorValidacion(_mensaje_validacion(exc)) from exc
        extra = {}
        if clave_idempotencia:
            extra["Idempotency-Key"] = clave_idempotencia
        respuesta = self._pedir(
            "POST",
            "/solicitudes",
            json=entrada.model_dump(),
            headers=extra,
        )
        return _parsear_salida(_json_o_error(respuesta))

    def obtener(self, id_solicitud: str) -> SolicitudSalida:
        ident = (id_solicitud or "").strip()
        if not ident:
            raise ErrorValidacion("Falta el id de la solicitud.")
        respuesta = self._pedir("GET", f"/solicitudes/{ident}")
        return _parsear_salida(_json_o_error(respuesta))

    def _pedir(
        self,
        metodo: str,
        ruta: str,
        *,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        reintentar_429: bool = True,
    ) -> httpx.Response:
        cabeceras = {"Authorization": f"Bearer {self._token}"}
        if headers:
            cabeceras.update(headers)
        try:
            respuesta = self._http.request(
                metodo,
                ruta,
                json=json,
                params=params,
                headers=cabeceras,
            )
        except httpx.TimeoutException as exc:
            raise error_timeout(self.timeout_s) from exc
        except httpx.ConnectError as exc:
            raise error_conexion(self.base_url) from exc
        except httpx.RequestError as exc:
            raise error_conexion(self.base_url) from exc

        if respuesta.status_code == 429 and reintentar_429:
            espera = respuesta.headers.get("Retry-After")
            if espera is not None:
                try:
                    segundos = max(0, int(espera))
                except ValueError:
                    segundos = 0
                time.sleep(segundos)
                return self._pedir(
                    metodo,
                    ruta,
                    json=json,
                    params=params,
                    headers=headers,
                    reintentar_429=False,
                )
        if respuesta.is_success:
            return respuesta
        raise error_desde_respuesta(respuesta.status_code, _detalle(respuesta))


def _json_o_error(respuesta: httpx.Response):
    try:
        return respuesta.json()
    except ValueError as exc:
        raise ErrorValidacion(
            "El servicio devolvió un cuerpo que no es JSON."
        ) from exc


def _parsear_salida(data: object) -> SolicitudSalida:
    try:
        return SolicitudSalida.model_validate(data)
    except ValidationError as exc:
        raise ErrorValidacion(
            "El servicio devolvió un cuerpo que no cumple el contrato. "
            + _mensaje_validacion(exc)
        ) from exc


def _detalle(respuesta: httpx.Response) -> str:
    try:
        data = respuesta.json()
    except ValueError:
        return respuesta.text
    if isinstance(data, dict) and "detail" in data:
        detalle = data["detail"]
        return detalle if isinstance(detalle, str) else str(detalle)
    return respuesta.text


def _mensaje_validacion(exc: ValidationError) -> str:
    partes = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err["loc"])
        partes.append(f"{loc}: {err['msg']}")
    return "La solicitud no cumple el contrato. " + "; ".join(partes)


def main() -> int:
    cliente = None
    try:
        cliente = ClienteMock.desde_entorno()
        creada = cliente.crear(
            asunto="Consulta de prueba del cliente mock",
            area="Aplicaciones",
            solicitante="usuario001@lafortuna.com.co",
            clave_idempotencia="demo-cli-1",
        )
        print(f"POST ok: {creada.id} ({creada.estado})")
        una = cliente.obtener(creada.id)
        print(f"GET id ok: {una.id}")
        lista = cliente.listar()
        print(f"GET ok: {len(lista)} solicitud(es)")
        return 0
    except ErrorProveedor as exc:
        print(str(exc))
        return 1
    finally:
        if cliente is not None:
            cliente.close()


if __name__ == "__main__":
    raise SystemExit(main())
