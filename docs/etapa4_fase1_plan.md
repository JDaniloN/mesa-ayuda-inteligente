# Etapa 4 — Fase 1: plan documental (revisión)

**Propósito.** Definir, ítem por ítem, el paso a paso para resolverlo y cómo
controlar fallos para alcanzar el **criterio 4** (anticipación de errores +
alternativas justificadas). **Todavía no se implementa código ni se cierra
la etapa.**

**Flujo acordado**

1. **Fase 1 (este documento):** plan y diseño de control de errores.
2. **Tu revisión:** marcas qué aceptar, ajustar o descartar.
3. **Fase 2:** retroalimentación conjunta → redactar entregables finales
   (`arquitectura.md`, ADR, demo mínima si aplica) y cerrar etapa 4.

**Marco del enunciado (versión 3 días).** Se evalúa sobre **diseño y
decisiones**, no sobre el sistema completo. Basta una demo mínima parcial.
Punta a punta suma en escalabilidad, no es obligatorio.

---

## Mapa de ítems

| # | Ítem | Entregable previsto | ¿Código en fase 2? |
|---|---|---|---|
| 1 | Arquitectura + 3 ADR | `docs/arquitectura.md`, `docs/adr/001…003` | No (solo docs) |
| 2 | Orquestación (demo mínima) | `src/orquestacion/` + pruebas o flujo exportado | Opcional / mínima |
| 3 | Integración bidireccional | Cliente webhook + idempotencia + backoff | Sí, acotado |
| 4 | Diseño de datos | Sección en arquitectura + ADR 3 | No (no migrar DB) |
| 5 | Secretos, ambientes y costo | Tabla de presupuesto + política al superar techo | Docs; enganche a métricas existentes |
| 6 | Cierre / declaración IA | `docs/declaracion_uso_ia.md` etapa 4 | A mano |

---

## Ítem 1 — Documento de arquitectura y tres ADR

### Qué debe quedar

Un evaluador sigue una solicitud **sin leer código**:
`POST /solicitudes` → clasificar → consultar políticas → redactar o abstenerse
→ escalar si confianza baja / sin evidencia → (opcional) notificar por webhook.

Cada ADR responde: **elegido / descartado / por qué / consecuencia negativa
aceptada**.

### Paso a paso

1. Dibujar en texto (o Mermaid) los componentes ya existentes:
   API, `FachadaClasificador`, RAG, métricas, mock, Angular, futuro
   orquestador.
2. Escribir el flujo feliz y el flujo de abstención/escalamiento.
3. **ADR 1 — Orquestador**
   - Opciones: n8n, framework de agentes, código propio en
     `src/orquestacion/`.
   - Elegir una (recomendación preliminar: **código propio**) porque ya
     existen puertos HTTP, tests y Bearer; n8n añade otra runtime.
4. **ADR 2 — Integración bidireccional**
   - Opciones: solo outbound, inbound+outbound con cola, o sincrónico con
     idempotencia en memoria/DB.
   - Elegir: **sincrónico + clave de idempotencia + backoff** sobre el mock
     inmutable.
5. **ADR 3 — Datos**
   - Opciones: MySQL único, SQLite + Chroma, memoria + Chroma (hoy).
   - Elegir diseño **objetivo** (relacional + vectorial separado) sin migrar
     aún; declarar que la API sigue en memoria en la demo.
6. En cada ADR listar al menos **dos alternativas descartadas** con costo o
   riesgo concreto.

### Control de errores (criterio 4)

| Fallo anticipado | Control |
|---|---|
| ADR que solo afirma lo elegido | Exigir tabla “descartado / motivo / trade-off” |
| Diagrama desconectado del código real | Cada caja cita módulo o ruta HTTP existente |
| Prometer punta a punta sin demo | Etiquetar “diseño” vs “implementado” |
| Mezclar RAG y tickets en un solo motor | ADR 3 explica por qué el vector store es distinto |

### Evidencia de revisión (fase 1)

- [ ] Cuatro rutas de archivo definidas
- [ ] Flujo extremo a extremo narrado
- [ ] Tres ADR con alternativa elegida **y** descartadas

---

## Ítem 2 — Orquestación (demo mínima)

### Qué debe quedar

Aunque sea parcial:

1. Clasificar (`src/ia/`).
2. Consultar RAG (`src/rag/` / ya expuesto en HTTP).
3. Redactar con citas o abstenerse.
4. Escalar a persona si score bajo / `abstuvo` / sin evidencia.

### Paso a paso (si en fase 2 se implementa lo mínimo)

1. Definir un caso de uso de entrada: `asunto` + `descripcion` + `pregunta`
   opcional de política.
2. Crear `src/orquestacion/flujo.py` que orqueste en secuencia (sin n8n).
3. Resultado tipado: clasificación, respuesta/abstención, citas, `escalado:
   bool`, `motivo_escala`.
4. CLI: `python -m src.orquestacion` con dos escenarios:
   - feliz (vacaciones / incidente con cita),
   - abstención → escala.
5. Pruebas en `tests/orquestacion/` con dobles (sin OpenAI).
6. Si se eligiera n8n: exportar JSON a `docs/` y describir nodos en
   arquitectura (alternativa; no recomendada para el tiempo).

### Control de errores (criterio 4)

| Fallo anticipado | Control |
|---|---|
| Inventar plazos cuando RAG se abstiene | Si `abstuvo`, no llamar generador; marcar escalado |
| Fallo de IA tumba el flujo | Clasificación ya degrada; el orquestador no debe abortar el ticket |
| Confianza no definida | Usar señales ya existentes: `abstuvo`, score &lt; `RAG_MIN_SCORE`, origen `degradado` |
| Orquestador llama al proveedor directo | Solo vía fachada / servicio de políticas (puertos) |
| Demo sin caso rojo | Obligatorio un test de abstención→escala |

### Alternativas a decidir en tu revisión

- A) Solo documentar el flujo (válido en 3 días).
- B) Demo mínima en código propio (recomendado si hay tiempo).
- C) n8n exportado (más setup, menos alineado al repo).

---

## Ítem 3 — Integración bidireccional con el mock

### Qué debe quedar

Cerrar el ciclo con `materiales/servicio_mock/` **sin modificarlo**:

- Enviar evento a `POST /webhook/mensajeria`.
- Recibir acuse `{ recibido: true }`.
- Idempotencia: mismo `evento_id` no duplica efecto.
- Reintentos con **backoff** ante 500/429 (quedó fuera en etapa 1).
- Estado coherente en ambos extremos (lado nuestro: “enviado / ack /
  agotado”).

### Paso a paso

1. Releer contrato del mock (headers, cuerpo, códigos de error).
2. Extender `src/integraciones/` (o módulo de orquestación) con
   `enviar_mensajeria(evento)`.
3. Clave de idempotencia = `evento_id` estable (hash de ticket+acción).
4. Política de reintento: p. ej. 3 intentos, espera 0.5s → 1s → 2s (o
   similar documentada).
5. Distinguir errores:
   - 4xx de contrato → no reintentar (salvo 429),
   - 5xx / timeout → reintentar con backoff,
   - ack ausente o cuerpo inválido → fallo controlado.
6. Pruebas con `httpx.MockTransport` o mock real en 8080:
   - primer envío OK,
   - 500 luego OK,
   - mismo `evento_id` dos veces,
   - 429 con espera.
7. Documentar en ADR 2 la consecuencia aceptada: en memoria se pierde el
   registro de envíos al reiniciar (hasta existir DB).

### Control de errores (criterio 4)

| Fallo anticipado | Control |
|---|---|
| Mock recibe el mismo evento 2 veces | Idempotencia por `evento_id` en nuestro lado y prueba de no-duplicado |
| Eventos fuera de orden | Estado por id, no por “último mensaje gana” sin clave |
| 500 “aleatorio” del mock | Backoff + tope de intentos; no bucle infinito |
| 429 | Respetar espera; no martillar |
| Timeout | Contar como transitorio; registrar métrica/log sin body |
| Modificar el mock | Prohibido; todo el control es en nuestro cliente |

### Alternativas a decidir

- Persistencia de “ya enviado”: memoria (demo) vs tabla (diseño ADR 3).
- ¿El orquestador dispara el webhook solo al escalar, o también al crear?

---

## Ítem 4 — Diseño de datos (relacional y vectorial)

### Qué debe quedar

Documento (no migración obligatoria) que una:

- Modelo relacional objetivo (tickets, clasificación, consulta política,
  escalamiento, evento webhook).
- Estrategia vectorial ya usada: chunking, embeddings, cosine,
  `RAG_MIN_SCORE`, sidecar de hash/modelo/dimensión.
- Por qué **no** viven en el mismo motor.

### Paso a paso

1. Partir de `materiales/datos/esquema.sql` (histórico) y del modelo API
   actual (`SolicitudSalida`, citas RAG, métricas).
2. Proponer tablas mínimas:
   - `solicitud`
   - `clasificacion` (origen proveedor/degradado)
   - `consulta_politica` (pregunta, abstuvo, fragmento_ids)
   - `escalamiento` (motivo, destino)
   - `evento_salida` (`evento_id`, estado, intentos)
3. Describir el índice Chroma: path, colección, metadatos de chunk, invalidación
   por hash de PDF.
4. Escribir ADR 3: MySQL/SQLite para hechos; Chroma para similitud.
5. Declarar explícitamente: **demo actual sigue en memoria**; el diseño es
   la meta de etapa 4.

### Control de errores (criterio 4)

| Fallo anticipado | Control |
|---|---|
| Mezclar embeddings en filas SQL | ADR lo prohíbe; vector store aparte |
| Índice huérfano tras cambiar PDF/modelo | Sidecar + borrado de colección (ya existe) |
| Perder trazabilidad de abstención | Tabla/campo `abstuvo` + motivo |
| Prometer migración hecha | README: “diseño; migración fuera si no hay tiempo” |
| Idempotencia solo en RAM | Documentar límite y tabla `evento_salida` futura |

### Evidencia

- [ ] Diagrama entidad-relación breve
- [ ] Justificación vectorial vs relacional
- [ ] Enlace a comportamiento RAG real (`src/rag/`)

---

## Ítem 5 — Secretos, ambientes y control de costo

### Qué debe quedar

- Ambientes: `development` / `test` / `production` (ya en config).
- Secretos: `.env` no versionado, `.env.example`, `SecretStr`, Bearer.
- **Presupuesto de tokens:** supuestos mensuales, techo, alerta, acción al
  superarlo (dejar de llamar LLM → degradado / abstención; **no** tumbar el
  alta de solicitudes).

### Paso a paso

1. Reutilizar métricas de etapa 3 (`GET /metricas/resumen`,
   `uso_no_reportado`).
2. Tabla de supuestos (ejemplo a calibrar en fase 2):

   | Concepto | Valor tentativo |
   |---|---|
   | Solicitudes/día | 100 (demo) / 3.000 (negocio R-01) |
   | Tokens clasificación (in+out) | ~800 |
   | Consultas RAG/día | 80 |
   | Tokens embeddings + generación | ~2.000 |
   | Precio modelo | según tarifa publicada |
   | Techo mensual USD | p. ej. 50 (demo) |

3. Definir política:
   - si `tokens_total` del mes (o contador de instancia) ≥ techo →
     `modo_ahorro=true`;
   - clasificación usa degradado;
   - RAG se abstiene o responde “servicio de IA limitado”;
   - POST solicitud sigue en 201.
4. Documentar que el contador actual es **por instancia** (se reinicia al
   apagar); el diseño de presupuesto “mensual real” requiere persistencia
   (ADR 3) — declarar el gap.
5. Alertas: log estructurado `presupuesto_excedido` (sin secretos).

### Control de errores (criterio 4)

| Fallo anticipado | Control |
|---|---|
| Inventar tokens si no hay `usage` | Ya: `uso_no_reportado`; presupuesto usa solo reportados + margen |
| Cortar el alta de tickets por cuota | Política: degradar IA, no 5xx en crear |
| Filtrar `IA_API_KEY` en logs | Whitelist de campos (ya existe) |
| Un solo `.env` para prod | Documentar precedencia proceso → archivo → default |
| Techo sin acción | Debe haber comportamiento observable (flag / log / modo) |

### Alternativas a decidir

- ¿Implementar el corte real en fase 2 o solo documentar la política?
- Techo por día vs por mes vs por instancia de demo.

---

## Ítem 6 — Cierre de etapa y declaración de IA

### Paso a paso

1. Tras tu revisión de este plan, acordar qué se documenta vs qué se codea.
2. Redactar entregables finales de fase 2.
3. Actualizar README sección etapa 4 (hecho / pendiente).
4. Llenar tabla etapa 4 en `docs/declaracion_uso_ia.md`.
5. (Opcional) notas de sustentación en `docs/aclaraciones_sustentacion.md`
   — no es entrega.

### Control de errores

| Fallo | Control |
|---|---|
| Declarar implementado lo solo diseñado | Etiquetas claras en README |
| Olvidar alternativas en ADR | Checklist de fase 2 |
| Ocultar uso de IA | Declaración obligatoria |

---

## Criterio 4 — checklist transversal de la etapa 4

Para cada ítem, antes de cerrar fase 2, debe existir:

1. **Al menos 3 fallos anticipados** con control concreto.
2. **Al menos 2 alternativas descartadas** con motivo.
3. **Consecuencia negativa aceptada** (trade-off explícito).
4. **Evidencia** (doc, test o URL) alineada a lo afirmado.

---

## Recomendación preliminar (para tu revisión)

| Ítem | Propuesta para fase 2 |
|---|---|
| Arquitectura + ADR | **Hacer completo** (núcleo evaluado) |
| Orquestación | **Demo mínima en código propio** si hay tiempo; si no, flujo solo en doc |
| Bidireccional | **Cliente + backoff + pruebas**; persistencia de envíos en memoria |
| Diseño de datos | **Solo documento**; sin migración |
| Costo | **Tabla + política documentada**; corte real opcional enganchado a métricas |
| Declaración IA | **A mano** al cerrar |

---

## Preguntas para tu revisión (fase 1 → fase 2)

Responde sobre este documento:

1. ¿Confirmas **código propio** como orquestador (ADR 1), o prefieres n8n?
2. ¿La demo de orquestación es obligatoria para ti o basta el diseño?
3. ¿Implementamos backoff/idempotencia del webhook en fase 2 o solo ADR?
4. ¿El corte por presupuesto debe ser código real o solo política escrita?
5. ¿Algún ítem de los seis lo sacamos del alcance de esta entrega?

Cuando respondas, en fase 2 cerramos con los entregables acordados y el
contraste de alternativas ya fijado.
