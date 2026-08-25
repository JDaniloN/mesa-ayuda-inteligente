"""Puerto: la API solo habla con esto, no con el proveedor HTTP."""

from typing import Protocol

from src.ia.modelos import Clasificacion


class PuertoClasificador(Protocol):
    def clasificar(self, texto: str) -> Clasificacion:
        """Asigna categoría y prioridad a un texto libre."""
