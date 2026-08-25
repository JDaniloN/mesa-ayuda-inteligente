# ADR 002 — Integración bidireccional con el servicio mock

| Campo | Valor |
|---|---|
| Estado | Aceptado |
| Fecha | 2026-08-25 |
| Etapa | 4 |
| Relacionado | [Arquitectura](../arquitectura.md), ADR 001, `materiales/servicio_mock/` |

## Contexto

El segundo sistema simulado expone `POST /webhook/mensajeria` (OpenAPI del
mock). Puede recibir el **mismo evento más de una vez y en desorden**. El
mock **no se modifica**: latencia variable, ~12 % de 500 y ~5 % de 429.

En la etapa 1 el cliente ya hace GET/POST de solicitudes con timeout y un
reintento de 429; el backoff ante 500 quedó explícitamente fuera.

Hay que cerrar: envío, acuse, idempotencia, reintentos con retroceso y
estado coherente en nuestro lado.

## Decisión

**Cliente sincrónico** en `src/integraciones/` (o invocado desde el
orquestador) con:

1. `evento_id` estable (p. ej. hash de `id_solicitud` + acción).
2. Idempotencia en nuestro lado: mismo `evento_id` no duplica efecto local
   ni reenvía si ya hay `ack`.
3. Reintentos con backoff ante timeout / 5xx / 429 (respetar `Retry-After`).
4. Tope de intentos (p. ej. 3: 0,5 s → 1 s → 2 s); estado final `agotado`.
5. Disparo principal **al escalar** (y opcionalmente al crear, si se
   documenta); no martillar el mock en cada lectura.

Persistencia del registro de envíos en la demo: **memoria** (alineado a la
API actual). Tabla `evento_salida` en el diseño relacional (ADR 3).

## Alternativas descartadas

| Alternativa | Por qué se descartó | Consecuencia si se hubiera elegido |
|---|---|---|
| **Solo outbound sin idempotencia** | El mock puede duplicar o reordenar; sin clave el segundo extremo ve tickets o avisos duplicados. | Más simple de codear; inaceptable ante reintentos reales. |
| **Cola / worker asíncrono** (Redis, Celery, etc.) | Infraestructura nueva para una demo de tres días; complica secretos y CI. | Mejor desacople y reintentos; costo operativo alto para el alcance. |
| **Modificar el mock** para “ser estable” | Viola el material; elimina el problema que el enunciado evalúa. | Pruebas verdes engañosas; resta en robustez. |
| **Inbound HTTP propio + outbound** completo en la misma entrega | Doble superficie (exponer webhook nuestro + consumir el del mock) sin tiempo para ambos con pruebas. | Más “bidireccional” de libro; se prioriza el contrato que el material ya da (`/webhook/mensajeria`) más el ciclo de acuse. |

## Consecuencia negativa aceptada

El registro de “ya enviado / ack” en **memoria** se pierde al reiniciar el
proceso: tras un reinicio se podría reenviar el mismo `evento_id`. Mitigación
documentada: el mock respeta idempotencia si reutilizamos clave donde aplica;
el diseño objetivo persiste `evento_salida` (ADR 3). En la demo se declara el
límite.

## Fallos anticipados

| Fallo | Control |
|---|---|
| Mismo evento dos veces | Idempotencia por `evento_id`; prueba de no-duplicado |
| Eventos fuera de orden | Estado por id, no “último mensaje gana” sin clave |
| 500 aleatorio del mock | Backoff + tope; no bucle infinito |
| 429 | Esperar `Retry-After` o backoff; no martillar |
| Timeout | Tratar como transitorio; log sin body ni token |
| 4xx de contrato (salvo 429) | No reintentar |
| Ack ausente o JSON inválido | Fallo controlado → `agotado` o reintento según política |

## Contrato de referencia (mock, sin modificar)

- Ruta: `POST /webhook/mensajeria`
- Auth: Bearer `MOCK_TOKEN`
- Respuesta esperada: `{ "recibido": true, "evento_id": ..., "hora": ... }`
- Fuente: `materiales/servicio_mock/openapi.yaml` y `app.py`

## Estado de implementación

| Pieza | Estado |
|---|---|
| Decisión y este ADR | Hecho |
| Cliente GET/POST solicitudes | Hecho (etapa 1) |
| `enviar_mensajeria` + backoff + pruebas | Pendiente |
| Persistencia `evento_salida` | Diseño (ADR 3) |
