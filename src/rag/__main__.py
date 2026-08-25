"""Ingesta local de políticas: python -m src.rag"""

from src.rag.servicio import ServicioPoliticas


def main() -> None:
    servicio = ServicioPoliticas.desde_configuracion()
    try:
        resultado = servicio.ingestar()
    finally:
        servicio.close()
    print(
        "Ingesta RAG: {documentos} documentos, {fragmentos} fragmentos, "
        "modelo {modelo}.".format(**resultado)
    )


if __name__ == "__main__":
    main()
