# ADR 001 — Orquestador del flujo mesa de ayuda

| Campo | Valor |
|---|---|
| Estado | Aceptado |
| Fecha | 2026-08-25 |
| Etapa | 4 |
| Relacionado | [Arquitectura](../arquitectura.md), ADR 002, ADR 003 |

## Contexto

Hay que encadenar: clasificar → consultar políticas (RAG) → redactar o
abstenerse → escalar a una persona si la confianza es baja. El enunciado
permite n8n, un framework de agentes o implementación propia.

Ya existen en el repo: API FastAPI, `FachadaClasificador`, `ServicioPoliticas`,
métricas, tests con dobles y Bearer. El paquete `src/orquestacion/` está
reservado.

## Decisión

**Código propio** en `src/orquestacion/` (flujo secuencial tipado, CLI y
pruebas con dobles). No n8n ni framework de agentes en esta entrega.

La demo puede ser parcial; punta a punta completo suma en escalabilidad, no
es obligatorio en tres días.

## Alternativas descartadas

| Alternativa | Por qué se descartó | Consecuencia si se hubiera elegido |
|---|---|---|
| **n8n** | Añade otra runtime, credenciales y un artefacto JSON aparte del repo Python/pytest. El tiempo de setup compite con ADR y webhook. | Flujo visual claro, pero peor trazabilidad en CI y más superficie de secretos. |
| **Framework de agentes** (LangGraph, Crew, etc.) | Overhead de grafo/estado para un pipeline lineal de cuatro pasos. Facilita “alucinar” herramientas y complica el modo degradado ya resuelto en la fachada. | Más flexibilidad futura; más riesgo de no poder explicar el flujo en sustentación. |
| **Solo documentar el flujo sin módulo** | Válido en tres días, pero debilita la evidencia de orquestación frente a un evaluador que pide demo mínima. | Cero código que romper; menos puntos en el criterio de orquestación. |

## Consecuencia negativa aceptada

Hay que mantener el orquestador delgado: si crece lógica de negocio dentro
del flujo, se vuelve otro monolito. Mitigación: el orquestador **solo** llama
a puertos ya existentes (`clasificar`, `consultar_politica`) y no habla con
OpenAI ni con el mock HTTP directo (el webhook vive en integraciones; ADR 2).

## Fallos anticipados

| Fallo | Control |
|---|---|
| Inventar plazos cuando el RAG se abstiene | Si `abstuvo`, no llamar generador; `escalado=true` |
| Fallo del LLM tumba el ticket | La clasificación ya degrada; el flujo no aborta el alta |
| “Confianza” indefinida | Usar `abstuvo`, score &lt; `RAG_MIN_SCORE`, `origen=degradado` |
| Orquestador acoplado al proveedor | Solo fachada / servicio de políticas |
| Demo sin caso rojo | Obligatorio escenario abstención → escala |

## Estado de implementación

| Pieza | Estado |
|---|---|
| Decisión y este ADR | Hecho |
| `src/orquestacion/flujo.py` + CLI + tests | Pendiente (demo mínima) |
| Flujo narrado en arquitectura §2 | Hecho |
