# Mesa de Ayuda Inteligente

Prueba técnica de nivelación — Familia de cargos IA · LA FORTUNA S.A.

## Nivel objetivo

Ingeniero IA Middle II.

## Hasta qué etapa llegué

Etapa 0 hecha. Etapa 1 en curso: limpieza del CSV cerrada (faltan mock y SQL).

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

### Etapa 1 — Limpieza del CSV

El script lee el histórico, normaliza, valida, quita duplicados y escribe el limpio, los rechazados y el resumen área × prioridad.

**Fechas.** Tres formatos del material: `YYYY-MM-DD`, `DD/MM/YYYY` y `DD-Ene-2026`. Se parsean con reglas explícitas; no se usa `to_datetime` a ciegas. `fecha_cierre` vacía se conserva (ticket abierto). Una fecha presente e ilegible rechaza la fila.

**Categorías.** Catálogo de escritura (mayúsculas y tildes): `SOFTWARE` → `Software`, `nomina` → `Nómina`. Vacío → `Sin clasificar`, porque esa etiqueta ya existe en el CSV.

Alternativa descartada: unir sinónimos (`Acceso`/`Accesos`/`Gestión de accesos`, `Hardware`/`Equipos`, etc.). Se miraron las 39 ids repetidas (`src/datos/validar_uniones.py`): las copias no cruzan esos pares, solo cambian mayúsculas. Otra alternativa, recortar al catálogo de `esquema.sql`, se descartó porque el SQL no trae Vacaciones, Capacitación ni Compras, que sí están en el histórico y en las políticas.

**Estado y canal.** Misma regla de escritura (`abierto` → `Abierto`, `Telefono` → `Teléfono`). No se junta `formulario` con `Formulario web`: no hay evidencia de que sean el mismo canal.

**Duplicados.** Una fila por `id`, se queda la primera. En este CSV las copias son el mismo ticket; las únicas diferencias eran mayúsculas de categoría.

**Área vacía.** Se conserva en el limpio (no se inventa un área). En el resumen aparece como `Sin área`.

**Imputaciones.** `reaperturas` vacía → `0`. `solicitante` vacío → `No identificado`.

**Rechazo.** id vacío; `fecha_creacion` vacía o ilegible; `fecha_cierre` ilegible o anterior a la creación; prioridad, categoría, estado o canal no reconocidos; `reaperturas` no numérica. Un archivo sin encabezado o inexistente lanza error explícito. Un CSV solo con cabecera produce salidas vacías, no un fallo.

**Fuera de este entregable.** Consumo del mock y las tres consultas SQL (siguen pendientes en la etapa 1). No se unifican sinónimos de categoría. El original de `materiales/` no se toca.
