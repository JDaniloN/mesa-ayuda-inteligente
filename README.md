# Mesa de Ayuda Inteligente

Prueba técnica de nivelación — Familia de cargos IA · LA FORTUNA S.A.

## Nivel objetivo

Ingeniero IA Middle II.

## Hasta qué etapa llegué

Etapa 0 hecha. Etapa 1 en curso: limpieza del CSV cerrada en este script (faltan mock, SQL y README de ejecución).

| Estado | Etapa | Qué es |
|---|---|---|
| Hecha | 0. Contextualización | Entendí el enunciado, los materiales y el alcance Middle II |
| En curso | 1. Fundamentos | CSV limpio, validación y resumen. Faltan mock y SQL |
| Pendiente | 2. Autonomía e integración | API, clasificador desacoplado, legado |
| Pendiente | 3. Complejidad y calidad | RAG, abstención, CI, seguridad |
| Pendiente | 4. Arquitectura y orquestación | Diseño, ADR y demo mínima |
| Pendiente | 5. Estrategia y evaluación | Decisión, métricas previas, ML clásico |

## Índice de entregables

| Etapa | Entregable | Dónde está | Cómo probarlo |
|---|---|---|---|
| 0 | Declaración de uso de IA | `docs/declaracion_uso_ia.md` | Abrir el archivo; la etapa 0 está llena a mano |
| 1 | Limpieza, validación y resumen | `src/datos/limpiar.py` | `python -m src.datos.limpiar` |
| 1 | Tickets limpios | `data/salida/tickets_limpios.csv` | Abrir el CSV; no se versiona |
| 1 | Rechazados | `data/salida/tickets_rechazados.csv` | Abrir el CSV; no se versiona |
| 1 | Resumen área × prioridad | `data/salida/resumen_area_prioridad.csv` | Abrir el CSV; no se versiona |
| 1 | Cliente del servicio mock | `src/integraciones/` | Pendiente al cerrar la etapa |
| 1 | Consultas SQL | `sql/` | Pendiente al cerrar la etapa |
| 1 | Pruebas de limpieza | `tests/datos/test_limpiar.py` | `python -m pytest tests/datos/test_limpiar.py` |
| 1 | Pruebas de integraciones | `tests/integraciones/` | Pendiente al cerrar la etapa |
| 2 | API REST (crear, estado, listar) | `src/api/` | Pendiente al cerrar la etapa |
| 2 | Clasificador desacoplado | `src/ia/` | Pendiente al cerrar la etapa |
| 2 | Pruebas de API e IA | `tests/api/`, `tests/ia/` | Pendiente al cerrar la etapa |
| 3 | RAG y abstención | `src/rag/` | Pendiente al cerrar la etapa |
| 3 | Pipeline de CI | `ci/` | Pendiente al cerrar la etapa |
| 3 | Pruebas de RAG | `tests/rag/` | Pendiente al cerrar la etapa |
| 4 | Orquestación | `src/orquestacion/` | Pendiente al cerrar la etapa |
| 4 | Arquitectura y ADR | `docs/` | Pendiente al cerrar la etapa |
| 5 | Decisión, métricas y revisión del PR | `docs/` | Pendiente al cerrar la etapa |
| Todas | Paquete original (solo lectura) | `materiales/` | No se modifica |

## Estructura

Un solo producto. Las carpetas son por capacidad, no por número de etapa.

```
src/
  datos/            limpieza, validación y resumen del CSV
  integraciones/    consumo del mock (GET/POST, errores, timeout)
  api/              recursos de la API propia
  ia/               categoría y prioridad (desacoplado del proveedor)
  rag/              políticas, citas y abstención
  orquestacion/     clasificar → consultar → responder → escalar
tests/              mismo mapa que src/
sql/                consultas de la etapa 1
docs/               declaración, arquitectura, ADR, decisión
ci/                 pipeline (etapa 3)
materiales/         paquete original; no modificar mock ni PDF
```

## Cómo instalar / ejecutar

```
pip install -r requirements.txt
python -m src.datos.limpiar
python -m pytest tests/datos/
```

El original está en `materiales/datos/tickets_historicos.csv` y no se modifica. La salida local (no se sube a Git) es `data/salida/`: limpio, rechazados y resumen área × prioridad.

## Supuestos y lo que quedó fuera

Se documentará en cada etapa. Si algo no se alcanza, se declara aquí.
