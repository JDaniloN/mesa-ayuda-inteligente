import pytest
from pydantic import ValidationError

from src.integraciones.modelos import SolicitudEntrada, SolicitudSalida


def test_entrada_valida():
    datos = SolicitudEntrada(
        asunto="Consulta de vacaciones",
        area="Talento Humano",
        solicitante="usuario001@lafortuna.com.co",
    )
    assert datos.canal == "api"
    assert datos.descripcion == ""


def test_asunto_corto_falla():
    with pytest.raises(ValidationError):
        SolicitudEntrada(
            asunto="Hola",
            area="Compras",
            solicitante="usuario001@lafortuna.com.co",
        )


def test_area_corta_falla():
    with pytest.raises(ValidationError):
        SolicitudEntrada(
            asunto="Necesito un certificado laboral",
            area="A",
            solicitante="usuario001@lafortuna.com.co",
        )


def test_solicitante_corto_falla():
    with pytest.raises(ValidationError):
        SolicitudEntrada(
            asunto="Necesito un certificado laboral",
            area="Compras",
            solicitante="ab",
        )


def test_salida_ignora_campos_extra():
    salida = SolicitudSalida.model_validate(
        {
            "id": "EXT-1",
            "asunto": "Consulta de vacaciones",
            "descripcion": "",
            "area": "Talento Humano",
            "solicitante": "usuario001@lafortuna.com.co",
            "canal": "api",
            "estado": "Abierto",
            "fecha_creacion": "2026-01-01T00:00:00+00:00",
            "_clave": "no-debe-romper",
        }
    )
    assert salida.id == "EXT-1"
    assert not hasattr(salida, "_clave")
