"""Arranque de la API usando API_HOST y API_PORT."""

import uvicorn

from src.configuracion import obtener_configuracion


def main() -> None:
    config = obtener_configuracion()
    uvicorn.run(
        "src.api.app:app",
        host=config.api_host,
        port=config.api_port,
    )


if __name__ == "__main__":
    main()
