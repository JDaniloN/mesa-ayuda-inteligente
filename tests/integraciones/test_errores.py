from src.integraciones.errores import (
    ErrorAutorizacion,
    ErrorLimiteTasa,
    ErrorNoEncontrado,
    ErrorProveedor,
    ErrorServicio,
    ErrorTimeout,
    ErrorValidacion,
    error_conexion,
    error_desde_respuesta,
    error_timeout,
)


def test_401_pide_revisar_token_sin_filtrarlo():
    err = error_desde_respuesta(401, "Token ausente o inválido.")
    assert isinstance(err, ErrorAutorizacion)
    assert "MOCK_TOKEN" in str(err)
    assert "demo-token" not in str(err)


def test_404_usa_detalle_del_proveedor():
    err = error_desde_respuesta(404, "Solicitud no encontrada.")
    assert isinstance(err, ErrorNoEncontrado)
    assert "no encontrada" in str(err).lower()


def test_422_es_validacion():
    err = error_desde_respuesta(422, "Cuerpo inválido")
    assert isinstance(err, ErrorValidacion)


def test_429_pide_esperar():
    err = error_desde_respuesta(429)
    assert isinstance(err, ErrorLimiteTasa)
    assert "límite" in str(err).lower()


def test_500_pide_reintentar():
    err = error_desde_respuesta(500, "Error interno del proveedor. Reintente.")
    assert isinstance(err, ErrorServicio)
    assert "Intente de nuevo" in str(err) or "Reintente" in str(err)


def test_503_tambien_es_fallo_del_servicio():
    err = error_desde_respuesta(503)
    assert isinstance(err, ErrorServicio)


def test_status_no_mapeado_queda_generico():
    err = error_desde_respuesta(418)
    assert type(err) is ErrorProveedor
    assert "418" in str(err)


def test_mensaje_timeout_incluye_segundos():
    err = error_timeout(5.0)
    assert isinstance(err, ErrorTimeout)
    assert "5 s" in str(err)


def test_mensaje_conexion_incluye_url():
    err = error_conexion("http://localhost:8080")
    assert isinstance(err, ErrorServicio)
    assert "http://localhost:8080" in str(err)
    assert "mock" in str(err).lower()
