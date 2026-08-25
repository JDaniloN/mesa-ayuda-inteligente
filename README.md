# Mesa de Ayuda Inteligente

Prueba técnica de nivelación — Familia de cargos IA · LA FORTUNA S.A.

**Nivel objetivo:** Ingeniero IA Middle II.

Este README es la guía de evaluación y el guion del recorrido. Recorre las
etapas en orden: qué se implementó, cómo probarlo, qué debe aparecer y qué
sigue pendiente. Un solo README raíz, como pide el enunciado; las etapas 2 a 5
no abren otro.

---

## Cómo leer este repositorio

1. [Estado](#estado) — hasta dónde llegó la entrega.
2. [Guion del video](#guion-del-video-5-minutos) — checklist de grabación (demo real).
3. [Preparación](#preparación-una-sola-vez) — entorno, `.env` y mock.
4. [Etapa 0](#etapa-0--contextualización) — contextualización.
5. [Etapa 1](#etapa-1--fundamentos) — CSV, mock, SQL y pruebas.
6. [Etapa 2](#etapa-2--autonomía-e-integración) — API, IA, legado, config, Angular.
7. [Etapa 3](#etapa-3--complejidad-y-calidad) — RAG, abstención, CI, seguridad, métricas y artefacto.
8. [Etapa 4](#etapa-4--arquitectura-y-orquestación) — arquitectura y ADR hechos; demo/webhook pendientes.
9. [Etapa 5](#etapa-5--estrategia-y-evaluación) — plan fase 1; entregables finales pendientes.
10. [Mapa del código](#mapa-del-código)

`materiales/` es el paquete original. No se modifica.

Documentos de entrega en `docs/`:

| Documento | Etapa |
|---|---|
| `declaracion_uso_ia.md` | Todas (obligatoria) |
| `api_contrato.md`, `api_funcional.md` | 2 |
| `legacy_causas.md` | 2 |
| `evidencia_ci.md`, `evidencia_xfail_rag.md`, `informe_seguridad_ia.md`, `estandar_revision_codigo_ia.md` | 3 |
| `arquitectura.md`, `adr/001…003` | 4 (diseño cerrado) |
| `etapa4_fase1_plan.md` | 4 (plan previo; no sustituye los ADR) |
| `etapa5_fase1_plan.md` | 5 (plan; no sustituye decisión, métricas ni revisión del PR) |

Las rutas de los entregables finales de las etapas 4 y 5 están en cada ítem.

---

## Estado

**Hasta dónde llegó esta entrega:** etapas **0 a 3 implementadas y documentadas**.
De la etapa **4** están cerrados el documento de arquitectura y los tres ADR;
siguen pendientes la demo de orquestación, el cliente webhook y el corte de
presupuesto en código. La etapa **5** tiene plan de fase 1; sin entregables
finales.

| Estado | Etapa | Alcance |
|---|---|---|
| Hecha | 0. Contextualización | Enunciado, materiales y nivel objetivo Middle II |
| Implementación hecha | 1. Fundamentos | Limpieza del CSV, cliente del mock y tres consultas SQL |
| Implementación hecha | 2. Autonomía e integración | API, clasificador IA, legado, configuración, docs y Angular |
| Implementación hecha | 3. Complejidad y calidad | RAG, abstención, CI (verde y rojo), seguridad, métricas y estándar |
| Diseño parcial | 4. Arquitectura y orquestación | Arquitectura + 3 ADR hechos. Faltan demo, webhook en código y corte de presupuesto en código |
| Plan fase 1 | 5. Estrategia y evaluación | Plan en `docs/etapa5_fase1_plan.md`. Faltan decisión, gold ≥50, suite, ML, revisión del PR y video |

**Pendiente transversal antes de entregar:** la declaración de uso de IA
(`docs/declaracion_uso_ia.md`) ya cubre las etapas 0–5 según el trabajo
hecho (en 4 y 5: el plan de fase 1). Revisarla si se cierran entregables
nuevos de esas etapas.

---

## Guion del video (5 minutos)

Este bloque es el recorrido de grabación. Solo muestra lo **implementado**
(etapas 0–3) y, al final, el **diseño** de la etapa 4. No invente demo de
orquestación/webhook ni entregables de la etapa 5: el README ya los marca
pendientes.

### Antes de pulsar grabar

```
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m src.rag
python -m src.api
```

En otra terminal (solo si muestra el mock de la etapa 1):

```
cd materiales/servicio_mock
uvicorn app:app --port 8080
```

Comprobar:

| Chequeo | Esperado |
|---|---|
| http://127.0.0.1:8000/docs | Swagger de la API propia |
| Authorize | Bearer = `API_TOKEN` de `.env` (no la clave OpenAI) |
| `GET /health` | `estado: operativo` y `clasificador: proveedor` (con `IA_API_KEY`) |
| Índice RAG | Ya corrido `python -m src.rag` (si no, `/politicas/consultar` → 503) |

### Minuto a minuto (seguir en orden)

| Min | Qué decir / mostrar | Dónde | Resultado que debe verse |
|---|---|---|---|
| 0:00 | Qué es el repo, nivel Middle II, **hasta etapa 3 hecha**; etapa 4 en diseño; etapa 5 en plan | Este README → [Estado](#estado) | Tabla de estado sin contradicciones |
| 0:30 | Alta de solicitud con IA | Swagger `POST /solicitudes` + cuerpo del [ítem API](#api-propia) | **201**, `SOL-…`, categoría/prioridad, `origen_clasificacion` |
| 1:00 | Idempotencia | Mismo POST + misma cabecera `Idempotency-Key` (en Swagger: Parameters) | **200**, mismo id, sin segunda llamada “visible” |
| 1:20 | RAG de dos hechos (hero) | `POST /politicas/consultar` con la pregunta de **cierre y reapertura** abajo | Texto con **2 días hábiles** (cierre) y **5 días hábiles** (reabrir); citas `POL-TIC-05` §7 y §6.1 |
| 2:10 | Abstención sin inventar | Misma ruta, pregunta Japón | Mensaje fijo + `citas: []` |
| 2:40 | Calidad local | Terminal: `ruff check --select E9,F63,F7,F82 src tests` y `python -m pytest -q` | Ruff OK; **199 passed** |
| 3:10 | CI verde/rojo | `docs/evidencia_ci.md` + links de Actions | Diseño del pipeline; camino rojo con `demostrar_fallo` |
| 3:40 | Seguridad + métricas | Abrir `docs/informe_seguridad_ia.md`; Swagger `GET /metricas/resumen` | Cuatro hallazgos corregidos; agregados sin prompts |
| 4:10 | Etapa 4 (solo diseño) | `docs/arquitectura.md` + un ADR | Flujos etiquetados Implementado vs Diseño; **sin** correr `src/orquestacion` (solo stub) |
| 4:40 | Cierre honesto | Residuales | Umbral RAG sin gold set; demo/webhook etapa 4 y entregables etapa 5 **pendientes**; video + PC-GTH-68 al cerrar entrega |

### Cuerpos listos para pegar en Swagger

`POST /solicitudes` (Authorize previo):

```json
{
  "asunto": "No puedo ingresar al correo corporativo",
  "descripcion": "El acceso falla desde esta mañana.",
  "area": "Aplicaciones",
  "solicitante": "persona@lafortuna.com.co",
  "canal": "api"
}
```

`POST /politicas/consultar` — hero (cierre + reapertura):

```json
{
  "pregunta": "Tras solucionarse un incidente en la mesa de ayuda, ¿cuánto tiempo tiene el sistema para cerrarlo automáticamente si el usuario no responde, y cuánto tiempo tiene el usuario para reabrirlo si la falla vuelve a presentarse?",
  "limite": 4
}
```

`POST /politicas/consultar` — abstención:

```json
{
  "pregunta": "¿Cuál es la capital de Japón?",
  "limite": 4
}
```

Mensaje fijo de abstención (debe coincidir carácter a carácter):

```
No encontré información suficiente en las políticas proporcionadas para responder la pregunta.
```

Opcional si sobra tiempo: pregunta de **problema vs crítico** (citas §6.3 y §5.1):

```json
{
  "pregunta": "Si un ticket se reabre tres veces, ¿en qué se convierte y qué ocurre si un incidente es clasificado como crítico?",
  "limite": 4
}
```

### Qué no grabar como “ya hecho”

- `python -m src.orquestacion` / `tests/orquestacion/` — pendientes (paquete vacío).
- Webhook `/webhook/mensajeria` con backoff — pendiente etapa 4.
- `docs/decision_ia_vs_automatizacion.md`, gold ≥50, suite `tests/evaluacion/`, notebook ML — pendientes etapa 5.
- Angular (`http://localhost:4200`) — opcional; no bloquea el guion.

El detalle de cada comando está en las secciones de etapa más abajo; este
guion solo fija el orden y el resultado esperado en cámara.

---

## Preparación (una sola vez)

Python 3. Entorno virtual y variables en `.env` (no se pegan secretos en la
terminal ni se versionan). Todo se ejecuta desde la raíz del repo, salvo el
uvicorn del mock.

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

`requirements-dev.txt` incluye `requirements.txt` más Ruff (necesario para el
paso de calidad del video y del CI).
Editar `.env`:

| Variable | Para qué | Dónde se usa |
|---|---|---|
| `API_TOKEN` | Bearer de Swagger Authorize | API propia (etapa 2) |
| `MOCK_TOKEN` | Token del servicio simulado | Cliente del mock (etapa 1) |
| `IA_API_KEY` | OpenAI o compatible | Clasificar (etapa 2) y RAG (etapa 3) |

`.env.example` es el contrato para revisión. `.env` está en `.gitignore`.
La precedencia es sistema / GitHub / Docker → `.env` → valores predeterminados.
Si PowerShell conserva una variable antigua: `Remove-Item Env:NOMBRE`.

El mock es un proceso aparte y **no se modifica**:

```
cd materiales/servicio_mock
pip install -r requirements.txt
cd ..
```

Frontend opcional (Node 24 y npm), solo si se evalúa la pantalla Angular:

```
cd web
npm ci
cd ..
```

Dependencias backend: `pandas`, `pytest`, `httpx`, `pydantic`,
`pydantic-settings`, `fastapi`, `uvicorn`, `python-dotenv`, `pdfplumber`,
`chromadb`. SQLite viene con Python.

---

## Etapa 0 — Contextualización

### Qué se hizo

Se leyó el Anexo A, el paquete de `materiales/` y se fijó el nivel Middle II.
La declaración de uso de IA de esta etapa está llena a mano.

### Cómo probarlo

Abrir `docs/declaracion_uso_ia.md` y revisar la tabla de la etapa 0.

### Qué resultados aparecen

Cinco respuestas de la etapa 0 completas. Las tablas de las etapas 1–5
también están rellenadas en `docs/declaracion_uso_ia.md` según el trabajo
hecho (en 4 y 5: el plan de fase 1, no los entregables finales).

### Qué quedó pendiente

Nada de contextualización. Actualizar la declaración si se cierran
entregables nuevos de las etapas 4 o 5.

---

## Etapa 1 — Fundamentos

Tres ítems independientes: limpiar el histórico, consumir el mock y consultar
el esquema SQL. El CSV y el SQL **no son el mismo dataset** (2.000 filas con
ruido vs 120 tickets relacionales).

### Limpieza del CSV

**Qué se hizo.** `src/datos/limpiar.py` lee
`materiales/datos/tickets_historicos.csv` (no lo modifica) y escribe en
`data/salida/` (no se versiona):

- `tickets_limpios.csv`
- `tickets_rechazados.csv`
- `resumen_area_prioridad.csv`

Decisiones:

- Fechas: los tres formatos del material (`YYYY-MM-DD`, `DD/MM/YYYY`,
  `DD-Ene-2026`) con reglas explícitas; no se usa `to_datetime` a ciegas.
  `fecha_cierre` vacía se conserva (ticket abierto). Una fecha presente e
  ilegible rechaza la fila.
- Categoría, estado y canal: se unifica **escritura** (mayúsculas y tildes).
  `SOFTWARE` → `Software`, `nomina` → `Nómina`, `abierto` → `Abierto`.
  Categoría vacía → `Sin clasificar`. No se unen sinónimos (`Acceso` /
  `Accesos` / `Gestión de accesos`, `Hardware` / `Equipos`): las ids repetidas
  del archivo solo diferían en mayúsculas (`src/datos/validar_uniones.py`).
- Duplicados: una fila por `id`, se queda la primera.
- Área vacía se conserva; en el resumen aparece como `Sin área`. Solicitante
  vacío → `No identificado`. `reaperturas` vacía se deja vacía: no se inventa
  `0` ni `1`.
- Rechazo: id vacío; `fecha_creacion` vacía o ilegible; `fecha_cierre` ilegible
  o anterior a la creación; prioridad, categoría, estado o canal no
  reconocidos; `reaperturas` con texto que no es número.

**Cómo probarlo.**

```
python -m src.datos.limpiar
python -m pytest tests/datos/ -q
```

**Qué resultados aparecen.** El script imprime las tres rutas de salida. Sobre
este histórico:

| Archivo | Filas | Lectura |
|---|---|---|
| Original (intacta) | 2.000 | 1.960 ids distintos; el resto son copias |
| `tickets_limpios.csv` | 1.960 | Una fila por id, categorías unificadas en escritura |
| `tickets_rechazados.csv` | 0 | En este archivo el ruido era duplicados y mayúsculas, no filas inválidas |
| `resumen_area_prioridad.csv` | 36 | Cruce área × prioridad (Crítica / Alta / Media / Baja) |

Las tres funciones que cubre el enunciado (`normalizar_fecha`,
`normalizar_categoria`, `eliminar_duplicados`) y un caso de borde cada una:

| Función | Camino feliz | Borde |
|---|---|---|
| `normalizar_fecha` | `"03/06/2025"` → `"2025-06-03"`; `"20-Ene-2026"` → `"2026-01-20"` | `""` se conserva; `"32/13/2025"` y `"ayer"` lanzan `ValueError` |
| `normalizar_categoria` | `"SOFTWARE"` → `"Software"`; `"nomina"` → `"Nómina"` | `""` → `Sin clasificar`; `"Acceso"` no se mezcla con `"Accesos"` |
| `eliminar_duplicados` | Dos filas con el mismo `id` → una | DataFrame sin columna `id`: se devuelve igual; archivo vacío o inexistente se cubre en `exportar` |

**Qué quedó pendiente.** Nada de este ítem. No se unifican sinónimos de
categoría ni se recorta el catálogo al de `esquema.sql` (el SQL no trae
Vacaciones, Capacitación ni Compras, que sí están en el histórico y en las
políticas).

### Cliente del mock

**Qué se hizo.** `src/integraciones/cliente.py` consume la API simulada de
`materiales/servicio_mock/` (el servidor no se modifica): al menos un POST y
un GET, timeout de 5 s, errores comprensibles e `Idempotency-Key` en el POST.
`httpx` + Pydantic copian el esquema de `openapi.yaml`; no se importa `app.py`
del mock.

- Timeout 5 s: el mock puede tardar 2,5 s en una respuesta **buena**; 2 s
  mezclaría latencia con fallo.
- Un reintento si el 429 trae `Retry-After`. El 500 no se reintenta (el ~12 %
  aleatorio no se gana a pulso; el backoff queda para la etapa 4).
- Cada fallo es un `ErrorProveedor` con frase (timeout, sin conexión, 401 sin
  imprimir el token, 404, 422, 429, 500, JSON roto). Un asunto corto falla
  antes de gastar una llamada.

**Cómo probarlo.** En una terminal:

```
cd materiales/servicio_mock
uvicorn app:app --port 8080
```

En otra, con `MOCK_TOKEN` ya en `.env`:

```
python -m src.integraciones.cliente
python -m pytest tests/integraciones/ -q
```

El mock real es aleatorio (~12 % de 500). El camino feliz en la terminal no
basta. Sin suerte: quite `MOCK_TOKEN` (401) o apague uvicorn (sin conexión).

En `/docs` del mock, Execute **no manda** la cabecera `authorization` (Swagger
la trata como reservada). El cliente Python sí la envía. En PowerShell,
`curl.exe -d "{...}"` parte el JSON; use este CLI o `Invoke-RestMethod`.

**Qué resultados aparecen.** El CLI hace POST de una solicitud, GET por id y
GET del listado, e imprime las respuestas. Si el proveedor falla, imprime una
frase y sale con código 1. Las pruebas cubren timeout, 401, 404, 429, 500 y
JSON roto sin depender de la aleatoriedad del servidor.

**Qué quedó pendiente.** No se consume el webhook `/webhook/mensajeria` (etapa
4). No hay reintentos con retroceso en 500. No se versiona `solicitud.json`.

### Consultas SQL

**Qué se hizo.** Tres archivos en `sql/` sobre una **copia en memoria** de
`materiales/datos/esquema.sql` (120 tickets). El original no se toca.
`sql/correr.py` usa SQLite (viene con Python). El enunciado pide SQL estándar;
el encabezado del esquema lo verifica en MySQL/MariaDB, no exige instalar un
servidor. Las `.sql` se pueden pegar en MySQL sin reescribirlas.

| Archivo | Pregunta | Filas |
|---|---|---|
| `sql/01_agregacion_por_area.sql` | Tickets, no cerrados y promedio de reaperturas por área y sede | 8 |
| `sql/02_join_tres_tablas.sql` | Quién pidió qué, de qué área y sede | 120 |
| `sql/03_tickets_reabiertos.sql` | Tickets que se reabrieron al menos una vez, con la fecha de la última reapertura si el log la tiene | 36 |

Decisiones:

- Consulta 01: parte de `areas` (`LEFT JOIN`) para que un área sin tickets no
  desaparezca. `COALESCE` deja 0, no NULL, si el área no tiene filas. No
  cerrados = todo lo que no está `Cerrado`. En este catálogo las 8 áreas tienen
  tickets; el borde se ve en `test_agregacion_area_sin_tickets_no_desaparece`.
- Consulta 02: `INNER JOIN` de tickets + usuarios + áreas. En este esquema
  todo ticket tiene usuario y área (`FK NOT NULL`).
- Consulta 03: “tickets reabiertos” es el **hecho** (`reaperturas > 0`), no la
  foto de hoy (`estado = 'Reabierto'`). El historial va en `LEFT JOIN`: si no
  hay paso a Reabierto, el ticket igual sale y `ultima_reapertura` queda vacía.
  36 filas: 28 siguen en Reabierto; 8 ya están en Abierto, Escalado, Cerrado o
  En proceso. Filtrar por estado o usar `INNER JOIN` al log dejaría fuera esos
  8.

**Cómo probarlo.**

```
python sql/correr.py
python -m pytest tests/sql/ -q
```

Si más adelante hay cliente `mysql` en el PATH, las tres `.sql` se pegan tal
cual. PowerShell no acepta `<`:

```
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS mesa_ayuda;"
Get-Content materiales/datos/esquema.sql -Raw | mysql -u root -p mesa_ayuda
Get-Content sql/01_agregacion_por_area.sql -Raw | mysql -u root -p -t mesa_ayuda
```

**Qué resultados aparecen.** La consola imprime **todas** las filas y deja
`data/salida/consulta_01_agregacion_por_area.csv`,
`consulta_02_join_tres_tablas.csv` y `consulta_03_tickets_reabiertos.csv`.
La consola de Windows parte líneas largas; el CSV no.

Consulta 01 (8 áreas, 120 tickets en total). Operaciones es la que más reabre
(promedio 0.94). Calidad casi no (0.09) y ninguna de sus 11 está cerrada:

| area | sede | tickets | no_cerrados | reaperturas_promedio |
|---|---|---:|---:|---:|
| Contabilidad | Sede Principal | 20 | 16 | 0.75 |
| Aplicaciones | Sede Principal | 19 | 16 | 0.68 |
| Operaciones | Bodega Sur | 18 | 15 | 0.94 |
| Comercial | Sede Norte | 15 | 12 | 0.33 |
| Compras | Sede Norte | 15 | 10 | 0.27 |
| Talento Humano | Sede Principal | 13 | 11 | 0.69 |
| Calidad | Sede Principal | 11 | 11 | 0.09 |
| Infraestructura | Sede Principal | 9 | 6 | 0.11 |

Consulta 02: 120 filas (todos los tickets). Primeras, más recientes primero:
TK-00023 Escalado / Calidad, TK-00093 Reabierto / Comercial, TK-00096 Abierto /
Compras.

Consulta 03: 36 filas. Ejemplos del hecho vs la foto: TK-00073 sigue Reabierto
con fecha en el log; TK-00045 ya está Cerrado, `reaperturas = 1` y
`ultima_reapertura` vacía (el log no tiene el paso). Las pruebas fijan 8 / 120
/ 36 y esos dos bordes.

**Qué quedó pendiente.** No se instala MySQL “para la foto”. No se modifica
`esquema.sql`. No se filtra la consulta 03 por estado actual. Índices
propuestos, no aplicados: `tickets(estado)`, `tickets(reaperturas)`,
`historial_estado(estado_nuevo, fecha_cambio)`.

### Cierre de la etapa 1

**Estado:** implementación hecha (CSV, mock y SQL).

**Qué quedó pendiente.** Nada de esta etapa para la declaración: la tabla
de la etapa 1 en `docs/declaracion_uso_ia.md` está completa.

---

## Etapa 2 — Autonomía e integración

### API propia

**Qué se hizo.** FastAPI + Pydantic en `src/api/`. Tres recursos: crear
(`POST /solicitudes`), consultar estado (`GET /solicitudes/{id}`), listar con
filtros (`GET /solicitudes`). `GET /health` es público, como el mock, y añade
`clasificador` (`proveedor` / `sin_clave`) para no confundir “servicio arriba”
con “LLM configurado”.

- Persistencia en memoria con candado. Al reiniciar el proceso se pierde el
  listado (el modelo relacional es de la etapa 4).
- Bearer `API_TOKEN`, distinto de `MOCK_TOKEN` y de `IA_API_KEY`. Sin token
  configurado: **503**, no un 401 ambiguo.
- Códigos 201 / 200 / 401 / 404 / 409 / 422 / 503. Error uniforme
  `{ "error": { "codigo", "mensaje" } }`. Listado sin coincidencias: **200**
  `[]`, no 404 (`GET /solicitudes/SOL-NOEXISTE` sí es 404).
- `Idempotency-Key`: misma clave y mismo cuerpo → 200 y el mismo id **sin**
  volver a invocar IA; otro cuerpo → 409. La clave existente se resuelve
  antes de llamar al modelo.
- CORS restringido al Angular local, sin cookies ni comodines.
- OpenAPI se genera desde rutas y modelos (`/docs`, `/openapi.json`). No se
  versiona otra copia que pueda quedar vieja.
`tests/api/test_contrato_openapi.py` fija rutas, códigos y esquemas.

**Cómo probarlo.**

```
python -m src.api
python -m pytest tests/api/ tests/ia/ -q
```

Abrir http://127.0.0.1:8000/docs — Authorize con el `API_TOKEN` de `.env`
(no la clave de OpenAI). Cuerpo de ejemplo para `POST /solicitudes`:

```json
{
  "asunto": "No puedo ingresar al correo corporativo",
  "descripcion": "El acceso falla desde esta mañana.",
  "area": "Aplicaciones",
  "solicitante": "persona@lafortuna.com.co",
  "canal": "api"
}
```

**Qué resultados aparecen.**

- `GET /health` (sin token): `estado: operativo` y `clasificador`.
- `POST /solicitudes` autenticado: **201**, id `SOL-…`, estado `Abierto`,
  categoría y prioridad asignadas, `origen_clasificacion` `proveedor` o
  `degradado`.
- Cada respuesta lleva `X-Request-ID`. En stdout, un evento JSON por petición
  (método, ruta, estado, latencia), sin cuerpo ni credenciales.
- Repetir el POST con la misma `Idempotency-Key` y el mismo cuerpo: **200** y
  el mismo id.
- `GET /solicitudes?prioridad=Alta` sin coincidencias: **200** `[]`.

El camino feliz en Swagger no basta para el degradado: ver el siguiente ítem.

**Qué quedó pendiente.** Persistencia, cambio de estado, autenticación
corporativa, permisos por rol y paginación por cursor. Se mantiene la URL sin
`/v1` para no romper la prueba; una ruptura futura deberá introducir una ruta
versionada. Detalle de integración: `docs/api_contrato.md`. Contexto de
negocio: `docs/api_funcional.md`.

### Clasificador de IA

**Qué se hizo.** La API no habla con OpenAI: llama `clasificar`
(`PuertoClasificador` en `src/ia/`). El HTTP vive en
`src/ia/proveedor_http.py`. Así se inyecta un fijo en pruebas y se puede
cambiar de proveedor sin tocar `src/api/`.

- Contrato `/v1/chat/completions` (OpenAI y compatibles). Timeout **8 s** (un
  chat tarda más en el primer token que el mock). Un reintento solo para
  fallos transitorios (timeout, conexión, 408, 425, 429, 5xx). Un 401, JSON
  inválido o etiqueta fuera de catálogo degrada de inmediato.
- Catálogo cerrado: las etiquetas salen de `CATEGORIAS_VALIDAS` /
  `PRIORIDADES_VALIDAS` de la limpieza. Si el modelo inventa una, no se
  guarda.
- Prompt: criterios de prioridad de `POL-TIC-05`, abstención ante ambigüedad,
  asunto/descripción como JSON no confiable. Tres ejemplos (caída general,
  solicitud planificada, inyección). No se fuerza `response_format` para no
  excluir proveedores compatibles.
- Si no hay clave, timeout, 401, 429, 500, JSON roto o etiqueta fuera de
  catálogo: `Sin clasificar` / `Media`, `origen=degradado`, y el POST **sigue
  en 201**. El 401 de OpenAI no es el 401 de la mesa.
- No hay regex de negocio. Tras ver el LLM en vivo (vacaciones urgentes →
  Vacaciones/Crítica; texto ambiguo → el propio modelo elige Sin clasificar),
  un regex duplicaría el catálogo y falsearía casos.

**Cómo probarlo.** Las pruebas no necesitan red:

```
python -m pytest tests/ia/ tests/api/test_solicitudes.py -q
```

En vivo, degradado: deje `IA_API_KEY=` vacío en `.env`, reinicie
`python -m src.api` y repita el POST.

**Qué resultados aparecen.**

| Qué se ve | Quién respondió |
|---|---|
| POST `/solicitudes` **401** | Bearer de la mesa (`API_TOKEN` / Authorize) |
| Terminal `http_401` y POST **201** degradado | Clave de OpenAI inválida |
| Terminal `http_429` y POST **201** degradado | Cuota o tope de gasto de OpenAI |
| `origen=proveedor` | El LLM contestó y la etiqueta está en el catálogo |
| `GET /health` → `clasificador: proveedor` | Había URL y clave **al arrancar**, no que haya saldo |

El Playground de OpenAI no usa la `IA_API_KEY` local: cuenta ok ≠ POST
clasificado.

**Qué quedó pendiente.** No se versiona `IA_API_KEY`. No se usa Assistants ni
streaming. Un modelo local o Groq caben cambiando `IA_API_BASE_URL`; no van
en este entregable.

### Módulo heredado

**Qué se hizo.** El original queda intacto en
`materiales/legacy/legacy_module.py`. La copia de `src/legacy/` corrige
únicamente los tres defectos reportados:

| Síntoma | Causa | Corrección |
|---|---|---|
| S1 — el informe pierde tickets del primer y último día | Comparadores `>` y `<` en un período inclusivo | `inicio <= fecha <= fin` |
| S2 — el segundo resumen sale inflado | `{}` como default se evalúa una sola vez | `None` y diccionario nuevo; se conserva el acumulador explícito |
| S3 — el indicador de reaperturas queda corto | Contaba el estado actual, no el hecho | `reaperturas > 0`; un contador vacío no se inventa como `1` |

Causas, alternativas descartadas y pruebas: `docs/legacy_causas.md`.

**Cómo probarlo.**

```
python -m pytest tests/legacy/ -q
```

Las mismas regresiones fallaron con la copia original y pasan con las
correcciones.

**Qué resultados aparecen.** Suite en verde. S1 incluye ambos extremos del
período. S2 no comparte acumulador entre llamadas. S3 cuenta un ticket ya
cerrado que tiene `reaperturas > 0`.

**Qué quedó pendiente.** Nada de este ítem. No se reescribe el módulo ni se
toca el archivo entregado.

### Configuración, logs y secretos

**Qué se hizo.** `src/configuracion.py` valida puertos, timeouts, reintentos,
entorno y nivel de log; los tokens usan `SecretStr`. `src/observabilidad.py`
emite JSON a stdout y limita los campos permitidos: no registra
`Authorization`, claves, asunto, descripción, solicitante, prompt ni respuesta
del proveedor. El middleware correlaciona respuesta e IA con `X-Request-ID`.

El código, las pruebas y la documentación desarrollados no contienen claves
con formatos conocidos. `tests/seguridad/` también comprueba que `.env` no
esté rastreado. El paquete original incluye un patrón tipo `sk-proj-…` dentro
de `materiales/revision/pr_para_revision.diff` (artefacto defectuoso para la
revisión final); `materiales/` no se usa, copia ni modifica.

**Cómo probarlo.**

```
python -m pytest tests/configuracion/ tests/observabilidad/ tests/seguridad/ -q
git check-ignore .env
git ls-files .env
```

El primer comando de Git debe mostrar `.env`; el segundo no debe mostrar nada.

**Qué resultados aparecen.** Configuración inválida (timeout negativo, puerto
imposible, nivel desconocido) falla al cargar. Los logs son una línea JSON por
evento. Los secretos no aparecen en `repr` ni en stdout.

**Qué quedó pendiente.** Nada de este ítem para la etapa 2. Un escaneo más
estricto y el pipeline CI son de la etapa 3.

### Documentación de la API

**Qué se hizo.** OpenAPI es el contrato ejecutable. Markdown no lo duplica:

- `docs/api_contrato.md` — integración, idempotencia, límites, códigos.
- `docs/api_funcional.md` — qué resuelve, para quién, qué queda fuera.

**Cómo probarlo.** Contrastar `/docs` y `/openapi.json` con
`python -m pytest tests/api/test_contrato_openapi.py -q`, y los escenarios
funcionales con `tests/api/`.

**Qué resultados aparecen.** Swagger muestra POST 201 y 200 (idempotente),
Bearer, error uniforme y `X-Request-ID`. El documento funcional admite que
esto es una demostración integrable, no un producto de producción.

**Qué quedó pendiente.** Nada de este ítem.

### Pantalla Angular (opcional)

**Qué se hizo.** `web/` consume el listado con un proxy local, filtros exactos
y estados de carga, vacío, 401, 503 y desconexión. La tabla omite descripción
y solicitante. El token se pide como contraseña, vive solo en memoria y el
interceptor solo lo adjunta a rutas relativas `/api/`. No va en
`environment.ts`, URL, cookies, `localStorage` ni `sessionStorage`.

**Cómo probarlo.** Con la API en el puerto 8000, en otra terminal:

```
cd web
npm start
```

Abrir http://localhost:4200. Ingrese el mismo `API_TOKEN` que usa Swagger;
nunca la clave de OpenAI. “Mostrar” permite comprobarlo antes de enviarlo.
“Validar y consultar” hace una petición protegida, carga la lista y solo
entonces enciende el indicador autenticado.

```
npm test -- --watch=false
npm run build
```

**Qué resultados aparecen.** Bandeja con filtros. Token rechazado → 401 y se
borra. API sin `API_TOKEN` → 503. Lista sin coincidencias → vacío, no error.
Si la API entrega `X-Request-ID`, se muestra como referencia.

**Qué quedó pendiente.** No crea ni edita solicitudes, no implementa login
corporativo y no guarda el token entre recargas. Es una bandeja de consulta.

### Cierre de la etapa 2

**Estado:** implementación hecha (API, IA, legado, config, docs y Angular
opcional).

**Qué quedó pendiente.** Nada de esta etapa para la declaración: la tabla
de la etapa 2 en `docs/declaracion_uso_ia.md` está completa.

---

## Etapa 3 — Complejidad y calidad

**Estado:** implementación hecha. Los seis ítems de abajo están cerrados;
el residual del umbral RAG (sin gold set) queda declarado al final.

### RAG de políticas internas (este ítem)

**Qué se hizo.** `POST /politicas/consultar` recupera fragmentos de los PDF de
`materiales/politicas/` y responde citando documento, sección, título, página
e id del fragmento. La ingesta (`python -m src.rag`) fragmenta por cláusula,
embebe con el mismo proveedor OpenAI-compatible de la clasificación y persiste
en Chroma local (`data/salida/rag/`, no se versiona).

- Si el mejor hit queda bajo `RAG_MIN_SCORE`, se abstiene con mensaje fijo,
  `citas: []` y **no** llama al generador.
- El valor inicial `0.22` es **provisional**: basta para abstenerse ante
  «¿Cuál es la capital de Japón?» con embeddings de prueba. No es una
  calibración con gold set; ese residual quedó declarado en el ítem de
  abstención.
- Sin clave de embeddings o sin índice: **503**, sin vectores inventados.
- Si cambia el hash de los PDF, el modelo o la dimensión, se borra la
  colección para no dejar chunks huérfanos. Un índice de otro modelo responde
  `503 indice_incompatible`.
- Las citas salen solo de metadatos del retriever. Una pregunta con dos
  subobjetivos se parte de forma determinista (sin otro LLM), se recupera
  cada parte, se diversifica el top-k para no llenarlo de cláusulas hermanas
  y se expanden vecinos inmediatos del mismo padre (`5.2` puede incorporar
  `5.1`). El generador tiene instrucción de no copiar un plazo de una
  cláusula a otra. `RAG_MIN_SCORE` solo decide la abstención global; la
  cobertura por subconsulta es interna y no reutiliza ese umbral.

**Cómo probarlo.** Con `IA_API_KEY` e `IA_EMBEDDING_MODEL` en `.env`:

```
python -m src.rag
python -m src.api
python -m pytest tests/rag/ tests/api/test_politicas.py tests/api/test_contrato_openapi.py -q
```

En Swagger (`http://127.0.0.1:8000/docs`), `POST /politicas/consultar` con
Bearer. Usar los cuerpos del [guion del video](#guion-del-video-5-minutos).
Ejemplos mínimos:

```json
{
  "pregunta": "Tras solucionarse un incidente en la mesa de ayuda, ¿cuánto tiempo tiene el sistema para cerrarlo automáticamente si el usuario no responde, y cuánto tiempo tiene el usuario para reabrirlo si la falla vuelve a presentarse?",
  "limite": 4
}
```

```json
{ "pregunta": "¿Cuál es la capital de Japón?", "limite": 4 }
```

**Qué resultados aparecen.** La ingesta imprime documentos, fragmentos y
modelo. La pregunta de cierre/reapertura responde con plazos (**2** y **5**
días hábiles) y citas `POL-TIC-05` §7 y §6.1. La pregunta fuera de dominio
devuelve:

```
No encontré información suficiente en las políticas proporcionadas para responder la pregunta.
```

y `citas: []`.

**Qué quedó pendiente de este ítem.** No se sustituye Chroma, no hay reranker
LLM y `RAG_MIN_SCORE` no está calibrado con un gold set. Las tres regresiones
de cierre/reapertura y problema/crítico ya pasan (fake e índice real); detalle
en `docs/evidencia_xfail_rag.md`. El texto plano de tablas de POL-TIC-05 se
omite a favor de una representación clave-valor; no se altera `materiales/`.

### Abstención sin evidencia

El mismo endpoint devuelve un mensaje fijo y `citas: []` cuando el mejor hit
directo queda bajo `RAG_MIN_SCORE`; en ese camino no se llama al generador.
La prueba HTTP `test_http_se_abstiene_sin_evidencia_documental` usa «¿Cuál es
la capital de Japón?» y comprueba la respuesta completa.

**Fallos anticipados.** Pregunta fuera de dominio; score alto pero irrelevante;
pregunta cubierta parcialmente; índice vacío o sin embeddings. El umbral solo
mira hits `direct`; no se usa coverage por subconsulta para inventar la mitad
faltante.

**Alternativas descartadas.** Umbral por tipo de pregunta, LLM-as-judge antes
de abstenerse, y devolver “no sé” con citas débiles. El umbral único y el
mensaje fijo cumplen el criterio con una prueba HTTP demostrativa; la
calibración con gold set queda explícita como pendiente.

### Integración continua

`.github/workflows/ci.yml` corre en cada push y pull request con Python 3.10:
instala `requirements-dev.txt`, Ruff (errores críticos) y pytest. El
`workflow_dispatch` ofrece `demostrar_fallo` para un job rojo deliberado
después de calidad, sin introducir código inválido.

Evidencia: `docs/evidencia_ci.md`. Local equivalente:
**Ruff OK; 199 passed**. Remotas (evidencia del diseño verde/rojo; el conteo
de tests puede ser de un commit anterior al quitar los `xfail`):
[verde](https://github.com/JDaniloN/mesa-ayuda-inteligente/actions/runs/32885632111)
y
[roja](https://github.com/JDaniloN/mesa-ayuda-inteligente/actions/runs/32885796312).
Tras el próximo push, el job verde debe reflejar **199 passed**.

**Fallos anticipados.** Dependencias sin pin; evidencia remota inventada;
regresión de ranking si se desactiva la calibración léxica.

**Alternativas descartadas.** Matrix multi-OS, cobertura obligatoria, fail-fast
agresivo, y “romper” un test real para el camino rojo. Se eligió un solo
runner Ubuntu, reglas críticas de Ruff y un paso final condicional para
demostrar el rojo sin contaminar la rama.

### Seguridad del código asistido por IA

`docs/informe_seguridad_ia.md` documenta cuatro hallazgos con severidad,
evidencia y corrección aplicada: delimitadores del prompt, exposición de
errores del proveedor, pool vectorial sin tope y dependencias RAG flotantes.
Cada corrección tiene prueba automatizada.

**Fallos anticipados.** El modelo obedece instrucciones en la pregunta; el
503 filtra códigos del proveedor; una colección grande agota cuota/CPU; un
`pip install` resuelve versiones distintas.

**Alternativas descartadas.** WAF/rate limit de infraestructura, escaneo CVE
continuo, y citar solo hits `direct` (se conserva la expansión como contexto
deliberado, con riesgo residual declarado). Se priorizó lo corregible en el
código de la demo autenticada.

### Instrumentación

El middleware conserva `duration_ms` por petición y agrega total, errores 5xx,
promedio, máximo y latencia acumulada. Los tres clientes de IA registran
tokens de entrada, salida y total desde `usage`; si el proveedor no los
entrega, incrementan `uso_no_reportado` en vez de estimar.

`GET /metricas/resumen` requiere Bearer y solo expone agregados de la
instancia, sin prompts, cuerpos ni datos personales.

**Fallos anticipados.** Contadores concurrentes corruptos; inventar tokens;
exponer prompts en el resumen; perder el resumen al reiniciar.

**Alternativas descartadas.** Prometheus/OpenTelemetry, estimar tokens con
tiktoken, y persistir métricas en disco. Un acumulador en memoria thread-safe
cumple el criterio de la demo; no es facturación ni sustituye la consola del
proveedor.

### Artefacto para el equipo

`docs/estandar_revision_codigo_ia.md` es la guía breve reutilizable: alcance,
verificación de fuentes, entradas adversariales, exposición de datos,
pruebas, puerta mínima de commit y definición de terminado.

**Fallos anticipados.** Aceptar diffs “porque compiló”; mezclar alcance;
confundir afirmación del modelo con evidencia; omitir pruebas de error.

**Alternativas descartadas.** Guía de prompts genéricos, checklist de commits
sin puerta de calidad, y un manual largo. Se eligió revisión de código IA
porque cubre prompts, commits y seguridad en una sola página accionable.

### Cierre de la etapa 3

**Estado:** implementación hecha. Los seis ítems de esta etapa están
cerrados: RAG con citas, abstención con prueba HTTP, CI con evidencia verde
y roja (`docs/evidencia_ci.md`), informe de seguridad con correcciones
aplicadas, métricas de latencia/tokens y estándar de revisión de código IA.

Cada ítem declara fallos anticipados, alternativas descartadas y riesgos
residuales. Residual explícito del RAG: `RAG_MIN_SCORE` es provisional (sin
gold set). Los tres rankings de cierre/reapertura y problema/crítico ya
pasan; evidencia en `docs/evidencia_xfail_rag.md`.

**Qué quedó pendiente.** Nada de esta etapa para la declaración: la tabla
de la etapa 3 en `docs/declaracion_uso_ia.md` está completa. La calibración
del umbral con gold set pertenece a la etapa 5.

---

## Etapa 4 — Arquitectura y orquestación

Corresponde a Ingeniero IA Middle I. En la versión de tres días **se evalúa
sobre el diseño y las decisiones**, no sobre el sistema completo. Basta una
demostración mínima del flujo, aunque sea parcial. Si la orquestación llega a
funcionar de punta a punta, se reconoce en escalabilidad.

**Estado actual.** Cerrados: `docs/arquitectura.md` y los tres ADR en
`docs/adr/`. El plan de fase 1 permanece como traza en
`docs/etapa4_fase1_plan.md`. **Aún no acreditan solos la etapa completa:**
faltan demo mínima de orquestación, cliente webhook con backoff/pruebas y
(opcional) enganche del corte por presupuesto a métricas.

**Método (dos fases):**

1. Fase 1 — plan documental → `docs/etapa4_fase1_plan.md` (**hecho**).
2. Fase 2 — entregables: arquitectura + ADR (**hecho**); demo, webhook y
   costo operativo (**pendiente**).

Cada ítem de abajo indica qué ya se puede abrir y qué sigue en código.

### Documento de arquitectura y tres ADR

**Qué se hizo.** Cerrado:

| Entregable | Ruta |
|---|---|
| Diagrama de componentes, flujos E2E, datos, secretos y costo | `docs/arquitectura.md` |
| ADR 1 — orquestador (código propio) | `docs/adr/001-orquestador.md` |
| ADR 2 — integración bidireccional e idempotencia | `docs/adr/002-integracion-bidireccional.md` |
| ADR 3 — modelo relacional e indexación vectorial | `docs/adr/003-diseno-datos.md` |

Cada ADR deja alternativa elegida, alternativas descartadas, motivo,
consecuencia negativa aceptada y fallos anticipados. La arquitectura etiqueta
**Implementado** vs **Diseño** para no confundir docs con código.

**Cómo probarlo.** Abrir esos cuatro archivos y contrastarlos con el flujo
declarado: clasificar → consultar políticas → redactar respuesta → escalar
si la confianza es baja. Cada caja del diagrama cita módulo o ruta HTTP.

**Qué resultados aparecen.** Un evaluador puede seguir una solicitud desde el
POST hasta el escalamiento sin leer el código. Los tres ADR dicen qué se
descartó (n8n, cola asíncrona, vectores en SQL, etc.), no solo qué se eligió.

**Qué quedó pendiente.** Nada de este ítem documental. La demo en
`src/orquestacion/` y el cliente webhook siguen en los ítems siguientes.

### Orquestación (demo mínima)

**Qué se hizo.** Aún no (fase 2). El paquete `src/orquestacion/` existe como
reserva (`__init__.py` vacío); no hay demo ejecutable ni
`tests/orquestacion/`. El flujo a demostrar, aunque sea parcial:

1. Clasificar la solicitud (`src/ia/`).
2. Consultar el RAG (`src/rag/` / `POST /politicas/consultar`).
3. Redactar la respuesta anclada a citas, o abstenerse.
4. Escalar a una persona cuando la confianza sea baja o no haya evidencia.

La elección queda fijada en el ADR 1: **código propio** (n8n y frameworks de
agentes descartados). No se exige que quede funcionando completo.

**Cómo probarlo.** Cuando exista demo:

```
python -m pytest tests/orquestacion/ -q
python -m src.orquestacion
```

Si la demo es un flujo n8n, exportar el JSON a `docs/` y describir los nodos
en `docs/arquitectura.md`.

**Qué resultados aparecen.** Un caso feliz (vacaciones / incidente con cita)
y un caso de abstención que escala. No debe inventar plazos ni montos.

**Qué quedó pendiente.** La demo mínima y las pruebas. La justificación del
orquestador ya está en `docs/adr/001-orquestador.md`.

### Integración bidireccional con el mock

**Qué se hizo.** Aún no (fase 2). El segundo sistema es
`POST /webhook/mensajeria` de `materiales/servicio_mock/` (puede recibir el
mismo evento más de una vez y en desorden; no se modifica). El cliente de la
etapa 1 ya consume GET/POST; aquí se cierra el ciclo: recepción, envío de
vuelta, idempotencia, reintentos con retroceso y estado coherente en ambos
extremos. El backoff del 500, dejado fuera en la etapa 1, entra aquí.

**Cómo probarlo.** Mock en 8080 y, cuando exista el módulo:

```
python -m pytest tests/orquestacion/ tests/integraciones/ -q
```

Forzar 500 y 429 del mock; repetir el mismo `evento_id` y comprobar que no
duplica.

**Qué resultados aparecen.** Un evento enviado, un acuse `{ recibido: true }`,
un reintento con espera creciente y un segundo envío con la misma clave que
no crea otro ticket.

**Qué quedó pendiente.** El conector, la idempotencia bidireccional y las
pruebas de reintento.

### Diseño de datos (relacional y vectorial)

**Qué se hizo.** Documentado en `docs/arquitectura.md` §4 y
`docs/adr/003-diseno-datos.md`. La API de la etapa 2 guarda en memoria a
propósito. El diseño objetivo separa hechos relacionales (solicitud,
clasificación, consulta, escalamiento, evento_salida) del índice Chroma
(cosine, chunking por cláusula, sidecar hash/modelo/dimensión) que ya usa el
RAG. **No hay migración aplicada** en esta entrega.

**Cómo probarlo.** Leer esos dos documentos junto a
`materiales/datos/esquema.sql` y `src/rag/`.

**Qué resultados aparecen.** Tablas previstas y la justificación de por qué
el índice vectorial no vive en el mismo motor que los tickets.

**Qué quedó pendiente.** La migración SQLite/MySQL (fuera si el tiempo no
alcanza; queda declarado). El documento de diseño de este ítem está cerrado.

### Secretos, ambientes y control de costo

**Qué se hizo.** Documentado en `docs/arquitectura.md` §5. La etapa 2 ya
separa `.env` / `.env.example`, precedencia proceso → archivo → default,
`SecretStr` y `APP_ENV`. La arquitectura añade la tabla de supuestos de
tokens, el techo demo (USD 50), la política al superarlo (degradar IA / no
tumbar el alta) y el gap del contador por instancia.

**Cómo probarlo.** Contrastar `docs/arquitectura.md` §5 con `.env.example` y
con `GET /metricas/resumen` (latencia y tokens ya existen).

**Qué resultados aparecen.** Supuestos declarados, techo y acción al
rebasarlo, sin secretos en el repo.

**Qué quedó pendiente.** Enganchar el corte real (`modo_ahorro`) al código;
hoy la política está escrita. Persistencia del contador mensual = diseño
ADR 3.

### Cierre de la etapa 4

**Qué quedó pendiente.** Demo mínima de orquestación, cliente webhook con
backoff/pruebas e (opcional) corte de presupuesto en código. Ya cerrados:
arquitectura, tres ADR, diseño de datos documentado y política de costo.
Actualizar la declaración de IA de esta etapa si se implementa la demo o el
webhook.

---

## Etapa 5 — Estrategia y evaluación

Corresponde a Ingeniero IA Middle II. En tres días son **obligatorios** el
documento de decisión, las métricas previas y el conjunto de referencia. El
modelo clásico puede ser un cuaderno con línea base y matriz de confusión,
sin integrarlo a la API. Las métricas deben quedar en Git **antes** de
implementar la suite de evaluación.

**Estado actual.** Solo existe el **plan de fase 1** en
`docs/etapa5_fase1_plan.md` (paso a paso, orden Git y control de errores).
Ese plan **no acredita** la etapa: faltan decisión R-01…R-03, métricas
previas, gold ≥ 50, suite en CI, notebook ML, comparación, revisión del PR,
estándar de ingeniería y video.

**Método previsto (dos fases):**

1. Fase 1 — plan documental → `docs/etapa5_fase1_plan.md` (**hecho**).
2. Fase 2 — entregables en orden Git (métricas/gold **antes** que la suite).

El video de 5 min y la revisión de `pr_para_revision.diff` van con la entrega,
no ocupan la sesión en vivo. El detalle operativo de cada ítem está en el plan.

### Documento de decisión (R-01, R-02, R-03)

**Qué se hizo.** Aún no (fase 2). El enunciado está en
`materiales/n5/requerimientos_negocio.md`. Irá en
`docs/decision_ia_vs_automatizacion.md`. Para cada requerimiento: IA,
automatización tradicional o secuencia combinada; criterios (volumen,
estabilidad, costo, latencia, tolerancia al error, mantenimiento); costo
estimado; riesgo; y bajo qué condición se cambia la decisión.

Uno de los tres **no** debe resolverse con IA (punto crítico 10). Eso se
sustenta, no se disimula.

| Id | Problema | Restricción | Decisión | Condición de cambio |
|---|---|---|---|---|
| R-01 | 3.000 solicitudes/día, 12 categorías estables, lote cada hora | Error se corrige en < 1 min; no pega al usuario | Pendiente | Pendiente |
| R-02 | Consulta de políticas en lenguaje natural (~80/día, 18 % del tiempo) | Error de montos o plazos → reclamación formal | Pendiente | Pendiente |
| R-03 | Recordatorio a los 3 días hábiles y escalamiento al 5.º; texto fijo | Todos los días 8:00; no duplicar si corre dos veces | Pendiente | Pendiente |

**Cómo probarlo.** Leer el documento y contrastarlo con
`materiales/n5/requerimientos_negocio.md`. No hay respuesta “correcta”; se
evalúa el criterio.

**Qué resultados aparecen.** Tres decisiones distintas o combinadas, cada una
con números y con la condición que las revertiría. Quien califica debe ver
por qué la IA a veces es la peor opción.

**Qué quedó pendiente.** Redactar y cerrar las tres decisiones.

### Métricas previas y conjunto de referencia

**Qué se hizo.** Aún no (fase 2). Este ítem tiene que existir en el historial
**antes** de la suite y del modelo. Irá en `docs/metricas_previas.md` y en
`data/referencia/conjunto_referencia.csv` (parte de la plantilla
`materiales/n5/plantilla_conjunto_referencia.csv`; completar hasta ≥ 50 casos
etiquetados a mano). El original de `materiales/` no se modifica.

Valores a fijar antes de construir:

| Métrica | Umbral (por definir) | Para qué |
|---|---|---|
| Precisión objetivo por categoría | Pendiente | Clasificador (LLM y línea base clásica) |
| Latencia p95 aceptable | Pendiente | POST `/solicitudes` y consulta RAG |
| Tasa máxima de escalamiento | Pendiente | Orquestación / abstención |
| Casos gold | ≥ 50 | Clasificación, citas y abstención |

La plantilla ya trae cinco ejemplos (anticipación de vacaciones, hospedaje no
capital, abstención de teletrabajo, clasificación Hardware). El resto se
etiqueta a mano.

**Cómo probarlo.**

```
git log -- docs/metricas_previas.md data/referencia/conjunto_referencia.csv
```

La fecha del commit de métricas debe ser anterior a la suite que las mide.

**Qué resultados aparecen.** Umbrales numéricos y un CSV de ≥ 50 filas con
pregunta o texto, etiqueta esperada, documento/sección si aplica y
observación (incluido `SIN EVIDENCIA EN LOS DOCUMENTOS`).

**Qué quedó pendiente.** Fijar los umbrales, etiquetar los 50 casos y
commitearlos antes de implementar evaluación.

### Suite de evaluación automatizada

**Qué se hizo.** Aún no (fase 2). Irá en `tests/evaluacion/` y se enganchará
al CI de la etapa 3 (`.github/workflows/ci.yml`, ya operativo). Debe reportar
las métricas de arriba y **fallar** si el resultado cae bajo el umbral.

**Cómo probarlo.** Cuando exista:

```
python -m pytest tests/evaluacion/ -q
```

**Qué resultados aparecen.** Precisión por categoría, p95, tasa de
escalamiento o abstención, y un rojo deliberado si se baja el umbral en una
prueba.

**Qué quedó pendiente.** La suite y engancharla al CI. No se escribe antes
del commit de métricas.

### Modelo clásico, comparación y recomendación

**Qué se hizo.** Aún no (fase 2). Cuaderno previsto:
`notebooks/linea_base_clasificacion.ipynb` sobre
`materiales/datos/tickets_historicos.csv` (o el limpio de `data/salida/`).
Partición, línea base, matriz de confusión y lectura de negocio. No hace
falta integrarlo a `src/api/`.

La comparación LLM vs clásico (costo por mil solicitudes, latencia,
precisión, mantenimiento) cierra `docs/decision_ia_vs_automatizacion.md` con
una recomendación final.

**Cómo probarlo.** Abrir el cuaderno y ejecutar las celdas de partición,
línea base y matriz. Contrastar la tabla de comparación con los supuestos de
costo de la etapa 4.

**Qué resultados aparecen.** Una matriz leíble en términos de mesa de ayuda
(qué categorías se confunden) y una recomendación: cuándo el LLM, cuándo el
modelo clásico, cuándo no usar ninguno.

**Qué quedó pendiente.** El cuaderno y la tabla comparativa.

### Revisión del PR y estándar de ingeniería

**Qué se hizo.** Aún no (fase 2). Revisión escrita de
`materiales/revision/pr_para_revision.diff` en `docs/revision_pr.md`. El diff
es un artefacto defectuoso a propósito (clave en código, SQL concatenado,
etc.); no se copia ni se “arregla” el archivo de `materiales/`.

Estándar previsto: `docs/estandar_ingenieria_ia.md` — qué se permite generar
con IA, qué se revisa siempre y qué nunca se acepta sin prueba. Puede ampliar
`docs/estandar_revision_codigo_ia.md` (ya entregado en etapa 3) en lugar de
partir de cero.

**Cómo probarlo.** Abrir el diff y el documento de revisión. Cada hallazgo
debe citar archivo/línea, severidad y corrección propuesta. El estándar se
contrasta con `docs/declaracion_uso_ia.md`.

**Qué resultados aparecen.** Una lista de defectos (secretos, inyección SQL,
límites de fecha, N+1, mezcla de responsabilidades) y tres reglas de equipo
que se puedan aplicar en el siguiente PR.

**Qué quedó pendiente.** La revisión escrita y el estándar. El video de
recorrido (máximo 5 min) sigue el [guion del video](#guion-del-video-5-minutos):
qué se construyó, hasta qué etapa, dos decisiones (p. ej. degradado sin tumbar
el alta; abstenerse sin inventar) y qué se haría distinto. Se graba al cerrar
la entrega.

### Cierre de la etapa 5

**Qué quedó pendiente.** Los entregables de fase 2, el video y la
autoevaluación PC-GTH-68 (fuera de este repo). La declaración de esta etapa
ya refleja el plan de fase 1; actualizarla al cerrar decisión, gold, suite,
notebook o revisión del PR. El plan no sustituye esos entregables.

---

## Mapa del código

Las carpetas son por capacidad, no por número de etapa.

```
src/
  configuracion.py   contrato tipado de variables de entorno
  observabilidad.py  logs JSON y correlación por request_id
  datos/             limpieza, validación y resumen del CSV
  integraciones/     consumo del mock (GET/POST, errores, timeout)
  api/               recursos de la API propia
  ia/                categoría y prioridad, desacoplado
  legacy/            copia corregida del módulo heredado
  rag/               políticas, citas y abstención
  orquestacion/      reserva etapa 4 (stub; demo aún no implementada)
tests/               mismo mapa que src/; evaluacion/ en la etapa 5
sql/                 consultas de la etapa 1 y runner
docs/                declaración IA, contrato, funcional, legado, CI,
                     seguridad, estándar, arquitectura y planes
docs/adr/            ADR 001 orquestador, 002 webhook, 003 datos (etapa 4)
.github/workflows/   CI etapa 3 (ci.yml)
web/                 listado Angular con filtros (etapa 2, opcional)
notebooks/           línea base clásica (etapa 5, pendiente de fase 2)
materiales/          paquete original; no modificar mock ni PDF
data/salida/         CSV e índice RAG locales; no se versionan
data/referencia/     conjunto gold ≥ 50 casos (etapa 5, pendiente de fase 2)
```