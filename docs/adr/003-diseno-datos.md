# ADR 003 — Diseño de datos relacional y vectorial

| Campo | Valor |
|---|---|
| Estado | Aceptado |
| Fecha | 2026-08-25 |
| Etapa | 4 |
| Relacionado | [Arquitectura](../arquitectura.md) §4, `materiales/datos/esquema.sql`, `src/rag/` |

## Contexto

La API de la etapa 2 guarda solicitudes en **memoria**. El RAG de la etapa 3
ya persiste fragmentos en **Chroma** local con embeddings OpenAI-compatibles.

El enunciado pide un modelo relacional para tickets y trazabilidad, más la
estrategia de indexación vectorial (tamaño de fragmento, modelo de embeddings,
métrica de similitud), sin exigir migrar todo en tres días.

## Decisión

1. **Hechos y trazabilidad** → almacén **relacional** (SQLite aceptable en
   demo; MySQL/MariaDB alineado al material). Tablas objetivo:
   `solicitud`, `clasificacion`, `consulta_politica`, `escalamiento`,
   `evento_salida` (detalle en arquitectura §4.1).
2. **Similitud semántica** → **Chroma** (u otro vector store) **separado**,
   con espacio **cosine**, chunking por cláusula, sidecar de
   hash/modelo/dimensión (ya implementado).
3. **Demo actual:** solicitudes siguen en memoria hasta que exista migración;
   el índice RAG permanece en `data/salida/rag/` (no versionado).

No se almacenan embeddings dentro de filas SQL. No se usa el vector store
como sistema de registro de tickets.

## Alternativas descartadas

| Alternativa | Por qué se descartó | Consecuencia si se hubiera elegido |
|---|---|---|
| **MySQL/SQLite único con vectores en BLOB/JSON** | Mezcla OLTP y ANN; invalidar por cambio de modelo/PDF es frágil; el esquema del material no contempla vectores. | Un solo backup; peor rendimiento y operaciones de reingesta. |
| **Todo en Chroma / solo vectorial** | No modela bien estados, idempotencia, FK ni historial de escalamiento. | Búsqueda semántica fácil; imposible auditar un ticket como hecho. |
| **Memoria + Chroma para siempre** (sin diseño relacional) | Suficiente para demo corta, pero no cumple el criterio de diseño de datos de Middle I. | Cero migración; cero trazabilidad tras reinicio. |
| **Migrar ya a MySQL obligatorio** | El enunciado en tres días no exige el sistema completo; instalar motor solo “para la foto” no suma (etapa 1 ya lo descartó con SQLite en memoria para SQL). | Foto más “prod”; tiempo robado a ADR/orquestación. |

## Justificación vectorial (comportamiento real)

| Parámetro | Elección | Motivo |
|---|---|---|
| Unidad de fragmento | Cláusula / sección numerada | Citas alineadas a POL-*-NN §x.y |
| Tamaño | Partir si &gt; ~800 tokens estimados | Cabe en contexto sin diluir la sección |
| Embeddings | `IA_EMBEDDING_MODEL` (p. ej. text-embedding-3-small) | Mismo proveedor que clasificación; sustituible por URL |
| Métrica | Cosine (`hnsw:space: cosine`) | Estándar para embeddings normalizados |
| Abstención | `RAG_MIN_SCORE` (provisional 0.22) | Mejor no responder que inventar; calibración = etapa 5 |
| Invalidación | Hash de PDF + modelo + dimensión | Evita chunks huérfanos tras cambiar corpus o modelo |

## Consecuencia negativa aceptada

Mientras la API esté en memoria, un reinicio borra solicitudes,
idempotencia y (futuros) acuses de webhook. Se acepta para la demo y se
mitiga documentando el modelo objetivo y, cuando haya tiempo, migrando solo
las tablas de hechos — **sin** mover vectores al mismo motor.

## Fallos anticipados

| Fallo | Control |
|---|---|
| Mezclar embeddings en SQL | Este ADR lo prohíbe |
| Índice huérfano tras cambiar PDF/modelo | Sidecar + borrado de colección (ya en `AlmacenChroma`) |
| Perder abstenciones en auditoría | Campo `abstuvo` + motivo en `consulta_politica` |
| Prometer migración hecha | README y arquitectura etiquetan **Diseño** |
| Idempotencia solo en RAM | Tabla `evento_salida` en el diseño; límite declarado hoy |

## Diagrama entidad-relación (objetivo)

```text
solicitud 1──1 clasificacion
    │
    ├──* consulta_politica
    ├──* escalamiento
    └──* evento_salida

(Chroma: fragmento_id ↔ metadatos codigo/seccion/pagina;
 no hay FK física hacia solicitud)
```

## Estado de implementación

| Pieza | Estado |
|---|---|
| Decisión y este ADR | Hecho |
| Chroma + chunking + sidecar | Hecho (etapa 3) |
| Tablas relacionales / migración | Pendiente (no bloquea la acreditación por diseño) |
| API en memoria | Hecho (demo) |
