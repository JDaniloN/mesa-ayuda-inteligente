# Mesa de Ayuda Inteligente

Prueba técnica de nivelación — Familia de cargos IA · LA FORTUNA S.A.

## Nivel objetivo

Ingeniero IA Middle II.

## Contenido

Un solo README raíz, como pide el enunciado: hasta qué etapa llegué y dónde está cada entregable. Las etapas 2 a 5 no abren otro README; dejan contrato, ADR y decisión en `docs/` y este índice se actualiza.

**Este archivo (etapa 1)**

1. [Hasta qué etapa llegué](#hasta-qué-etapa-llegué)
2. [Índice de entregables](#índice-de-entregables)
3. [Estructura](#estructura)
4. [Cómo instalar](#cómo-instalar)
5. [Cómo ejecutar](#cómo-ejecutar)
6. [Qué hace](#qué-hace)
7. [Qué supuse](#qué-supuse)
8. [Qué dejé fuera](#qué-dejé-fuera)

**`docs/` — ahora y lo que irá para Middle II**

| Etapa | Documento | Estado |
|---|---|---|
| 0–1 | `docs/declaracion_uso_ia.md` | Etapa 0 llena a mano; etapa 1 pendiente |
| 1–2 | `docs/aclaraciones_sustentacion.md` | Hecho (SQL, mock, API, IA, legado, configuración) |
| 2 | `docs/api_contrato.md` + `docs/api_funcional.md` | Hecho |
| 3 | Guía breve de prompts, commits o revisión de código generado por IA | Pendiente |
| 4 | Arquitectura, flujo extremo a extremo y tres ADR | Pendiente |
| 5 | Decisión IA vs automatización, métricas previas, revisión del PR | Pendiente |
| Entrega | Video de 5 min y revisión escrita de `pr_para_revision.diff` | Pendiente |

**Lectura corta para el evaluador.** Instalar y ejecutar están abajo. El criterio (alternativas descartadas, 36 vs 28, timeout 5 s, degradado sin regex y causas del legado) está en *Qué supuse* y en `docs/`. El código implementado está en `src/datos/`, `src/integraciones/`, `src/api/`, `src/ia/`, `src/legacy/` y `sql/`.

## Hasta qué etapa llegué

Etapa 0 hecha. Etapa 1: CSV, mock y SQL cerrados. Falta llenar a mano la declaración de uso de IA de la etapa 1.

| Estado | Etapa | Qué es |
|---|---|---|
| Hecha | 0. Contextualización | Enunciado, materiales y alcance Middle II |
| En curso | 1. Fundamentos | Limpieza del CSV, cliente del mock y tres consultas SQL |
| En curso | 2. Autonomía e integración | API, IA, legado, configuración y documentación. Falta Angular |
| Pendiente | 3. Complejidad y calidad | RAG, abstención, CI, seguridad |
| Pendiente | 4. Arquitectura y orquestación | Diseño, ADR y demo mínima |
| Pendiente | 5. Estrategia y evaluación | Decisión, métricas previas, ML clásico |

El README de esta etapa cubre lo que pide el enunciado: **cómo instalar, cómo ejecutar, qué hace, qué supuse y qué dejé fuera.** El “por qué” para decirlo en voz alta está en `docs/aclaraciones_sustentacion.md`.

## Índice de entregables

| Etapa | Entregable | Dónde está | Cómo probarlo |
|---|---|---|---|
| 0 | Declaración de uso de IA | `docs/declaracion_uso_ia.md` | Abrir el archivo; la etapa 0 está llena a mano |
| 1 | Limpieza, validación y resumen | `src/datos/limpiar.py` | `python -m src.datos.limpiar` |
| 1 | Tickets limpios | `data/salida/tickets_limpios.csv` | Abrir el CSV; no se versiona |
| 1 | Rechazados | `data/salida/tickets_rechazados.csv` | Abrir el CSV; no se versiona |
| 1 | Resumen área × prioridad | `data/salida/resumen_area_prioridad.csv` | Abrir el CSV; no se versiona |
| 1 | Cliente del servicio mock | `src/integraciones/cliente.py` | `python -m src.integraciones.cliente` (mock en 8080 y `MOCK_TOKEN`) |
| 1 | Consultas SQL | `sql/` | `python sql/correr.py` |
| 1 | Resultado de las consultas | `data/salida/consulta_*.csv` | Abrir los CSV; no se versionan |
| 1 | Aclaraciones de sustentación | `docs/aclaraciones_sustentacion.md` | Abrir el archivo |
| 1 | Pruebas de limpieza | `tests/datos/test_limpiar.py` | `python -m pytest tests/datos/` |
| 1 | Pruebas de integraciones | `tests/integraciones/` | `python -m pytest tests/integraciones/` |
| 1 | Pruebas de las consultas SQL | `tests/sql/` | `python -m pytest tests/sql/` |
| 2 | API propia (crear, estado, listar) | `src/api/` | `python -m pytest tests/api/` |
| 2 | Clasificador IA (puerto + HTTP + degradado) | `src/ia/` | `python -m pytest tests/ia/` |
| 2 | Correcciones S1–S3 del legado | `src/legacy/` y `docs/legacy_causas.md` | `python -m pytest tests/legacy/` |
| 2 | Configuración tipada y logs JSON | `src/configuracion.py` y `src/observabilidad.py` | `python -m pytest tests/configuracion/ tests/observabilidad/` |
| 2 | Contrato técnico de la API | `docs/api_contrato.md` | `/docs`, `/openapi.json` y `python -m pytest tests/api/test_contrato_openapi.py` |
| 2 | Descripción funcional de la API | `docs/api_funcional.md` | Contrastar escenarios con `tests/api/` |
| 2–5 | IA, RAG, orquestación, ADR | `src/`, `tests/`, `docs/`, `ci/` | Pendiente al cerrar cada etapa |
| Todas | Paquete original (solo lectura) | `materiales/` | No se modifica |

## Estructura

Un solo producto. Las carpetas son por capacidad, no por número de etapa.

```
src/
  configuracion.py   contrato tipado de variables de entorno
  observabilidad.py logs JSON y correlación por request_id
  datos/            limpieza, validación y resumen del CSV
  integraciones/    consumo del mock (GET/POST, errores, timeout)
  api/              recursos de la API propia (etapa 2)
  ia/               categoría y prioridad, desacoplado (etapa 2)
  legacy/           copia corregida del módulo heredado (etapa 2)
  rag/              políticas, citas y abstención (etapa 3)
  orquestacion/     clasificar → consultar → responder → escalar (etapa 4)
tests/              mismo mapa que src/
sql/                consultas de la etapa 1 y runner
docs/               declaración, aclaraciones, arquitectura, ADR
ci/                 pipeline (etapa 3)
materiales/         paquete original; no modificar mock ni PDF
data/salida/        CSV locales; no se versionan
```

---

## Cómo instalar

Python 3. Entorno virtual y variables en `.env` (no se pegan secretos en la terminal ni se versionan).

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Editar `.env`: `API_TOKEN` (Swagger), `MOCK_TOKEN` (mock) e `IA_API_KEY` (OpenAI, opcional). `.env.example` es el contrato para revisión; `.env` está en `.gitignore`.

Dependencias: `pandas`, `pytest`, `httpx`, `pydantic`, `pydantic-settings`, `fastapi`, `uvicorn`, `python-dotenv`. SQLite viene con Python.

El mock es un proceso aparte y no se modifica:

```
cd materiales/servicio_mock
pip install -r requirements.txt
```

---

## Cómo ejecutar

Todo desde la raíz del repo, salvo el `uvicorn` del mock.

**Limpieza del CSV**

```
python -m src.datos.limpiar
```

Lee `materiales/datos/tickets_historicos.csv` (no lo modifica) y escribe en `data/salida/`: `tickets_limpios.csv`, `tickets_rechazados.csv`, `resumen_area_prioridad.csv`.

**Cliente del mock**

En una terminal:

```
cd materiales/servicio_mock
uvicorn app:app --port 8080
```

En otra (`.env` ya con `MOCK_TOKEN`):

```
python -m src.integraciones.cliente
```

Hace POST de una solicitud, GET por id y GET del listado. Si el proveedor falla, imprime una frase y sale con código 1. En PowerShell, `curl.exe -d "{...}"` parte el JSON; use este CLI o `Invoke-RestMethod`. En `/docs` del mock, Execute **no manda** la cabecera `authorization`.

**Consultas SQL**

```
python sql/correr.py
```

Carga una copia en memoria de `materiales/datos/esquema.sql` con SQLite, imprime **todas** las filas y deja `data/salida/consulta_01_agregacion_por_area.csv`, `consulta_02_join_tres_tablas.csv` y `consulta_03_tickets_reabiertos.csv`. El original no se toca. La consola de Windows parte líneas largas; el CSV no.

Si más adelante hay cliente `mysql` en el PATH, las tres `.sql` se pegan tal cual. PowerShell no acepta `<`:

```
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS mesa_ayuda;"
Get-Content materiales/datos/esquema.sql -Raw | mysql -u root -p mesa_ayuda
Get-Content sql/01_agregacion_por_area.sql -Raw | mysql -u root -p -t mesa_ayuda
```

**Pruebas**

```
python -m pytest -q
```

El enunciado pide **al menos tres funciones y un caso de borde**. Ya está cubierto: `normalizar_fecha`, `normalizar_categoria` y `eliminar_duplicados`, con bordes (fecha ilegible, archivo vacío o inexistente, `reaperturas` vacía). El mock añade timeout, 401, 404, 429, 500 y JSON roto. `tests/sql/` fija 8 / 120 / 36 y dos bordes del esquema feliz: un área sin tickets no desaparece; un reabierto sin paso en el log igual sale.

El mock real es aleatorio (~12 % de 500): el camino feliz en la terminal no basta. En vivo, sin suerte: quite `MOCK_TOKEN` (401) o apague uvicorn (sin conexión).

**API propia (etapa 2, este ítem)**

```
python -m src.api
```

`API_HOST` y `API_PORT` salen de la configuración. La precedencia es sistema/GitHub/Docker → `.env` → valores predeterminados. Si PowerShell conserva una variable antigua, elimínela con `Remove-Item Env:NOMBRE`; el archivo local no debe pisar la configuración de un despliegue.

OpenAPI: http://127.0.0.1:8000/docs — Bearer el `API_TOKEN` de `.env` (no la clave de OpenAI). `GET /health` (sin token) incluye `clasificador`: `proveedor` o `sin_clave`. Cada respuesta devuelve `X-Request-ID` y cada petición deja un evento JSON en stdout con método, ruta, estado y latencia, sin cuerpo ni credenciales. Tres recursos: `POST /solicitudes`, `GET /solicitudes/{id}`, `GET /solicitudes`. La categoría/prioridad las asigna `src/ia/`. Si el LLM responde, `origen_clasificacion=proveedor`; si no hay clave, timeout, 401/429/500 o etiqueta fuera del catálogo → **201 igual**, `degradado` (`Sin clasificar` / `Media`). El 401 de OpenAI no es el 401 de la mesa.

El camino feliz en Swagger no basta. Evidencia del degradado: `python -m pytest tests/ia/ tests/api/test_solicitudes.py -q`. En vivo: deje `IA_API_KEY=` vacío en `.env`, reinicie `python -m src.api` y repita el POST.

```
python -m pytest tests/api/ tests/ia/ -q
```

---

## Qué hace

### Limpieza del CSV

Lee el histórico (2.000 filas con ruido), normaliza fechas y escritura de categorías, estado y canal, quita duplicados por `id`, valida y produce el limpio, los rechazados y un resumen área × prioridad.

### Cliente del mock

Consume la API simulada: al menos un GET y un POST, con timeout, errores comprensibles e `Idempotency-Key` en el POST. El servidor en `materiales/servicio_mock/` no se modifica.

### Consultas SQL

Tres archivos sobre `esquema.sql` (120 tickets; **otro dataset** que el CSV):

| Archivo | Qué responde | Filas |
|---|---|---|
| `sql/01_agregacion_por_area.sql` | Tickets, no cerrados y promedio de reaperturas por área y sede | 8 |
| `sql/02_join_tres_tablas.sql` | Quién pidió qué, de qué área y sede | 120 |
| `sql/03_tickets_reabiertos.sql` | Tickets que se reabrieron al menos una vez, con la fecha de la última reapertura si el log la tiene | 36 |

### API propia (etapa 2)

Tres recursos: crear (`POST /solicitudes`), consultar estado (`GET /solicitudes/{id}`), listar con filtros (`GET /solicitudes`). `GET /health` como el mock (sin token, `estado: operativo`) más `clasificador` (`proveedor` / `sin_clave`) para no confundir “servicio arriba” con “LLM configurado”. Validación Pydantic, códigos 201/200/401/404/409/422/503 y error uniforme `{ "error": { "codigo", "mensaje" } }`. Listado sin coincidencias: **200** `[]`, no 404. Clasificación: LLM (catálogo cerrado de la limpieza) o degradado `Sin clasificar`/`Media` si el proveedor falla; el POST no pasa a 500.

El contrato ejecutable vive en `/openapi.json` y Swagger `/docs`; `tests/api/test_contrato_openapi.py` evita que rutas, códigos o esquemas se separen del comportamiento. `docs/api_contrato.md` explica integración, idempotencia y límites. `docs/api_funcional.md` explica qué resuelve, para quién y qué queda fuera.

### Módulo heredado (etapa 2)

El original queda intacto en `materiales/legacy/legacy_module.py`. La copia de `src/legacy/` corrige únicamente los tres defectos reportados: incluye ambos extremos del período, evita compartir el acumulador entre llamadas y cuenta tickets reabiertos por el hecho histórico (`reaperturas > 0`), no por el estado actual. Las mismas regresiones fallaron con la copia original y pasan con las correcciones; causas y alternativas están en `docs/legacy_causas.md`.

### Configuración y observabilidad (etapa 2)

`src/configuracion.py` valida puertos, timeouts, reintentos, entorno y nivel de log; los tokens usan `SecretStr`. `.env` sirve para desarrollo y nunca se versiona; `.env.example` contiene solo el contrato. `src/observabilidad.py` emite JSON a stdout y limita los campos permitidos para no registrar `Authorization`, claves, asunto, descripción ni solicitante. El middleware correlaciona la respuesta y los eventos de IA mediante `X-Request-ID`.

---

## Qué supuse

**CSV — fechas.** Los tres formatos del material (`YYYY-MM-DD`, `DD/MM/YYYY`, `DD-Ene-2026`) se parsean con reglas explícitas; no se usa `to_datetime` a ciegas. `fecha_cierre` vacía se conserva (ticket abierto). Una fecha presente e ilegible rechaza la fila.

**CSV — categorías, estado y canal.** Normalizo escritura (mayúsculas y tildes): `SOFTWARE` → `Software`, `nomina` → `Nómina`, `abierto` → `Abierto`. Categoría vacía → `Sin clasificar` (esa etiqueta ya existe en el CSV). No junto `formulario` con `Formulario web`.

**CSV — duplicados.** Una fila por `id`, se queda la primera. En este archivo las copias son el mismo ticket; las únicas diferencias eran mayúsculas de categoría.

**CSV — vacíos.** Área vacía se conserva en el limpio; en el resumen aparece como `Sin área`. Solicitante vacío → `No identificado`. `reaperturas` vacía se deja vacía: no se pone `0` ni `1` (en Reabierto el conteo real podría ser 2 o 3). Tampoco `No especificado`: el campo es numérico. Un texto no dígito sí se rechaza.

**CSV — rechazo.** id vacío; `fecha_creacion` vacía o ilegible; `fecha_cierre` ilegible o anterior a la creación; prioridad, categoría, estado o canal no reconocidos; `reaperturas` con texto que no es número. Un archivo sin encabezado o inexistente lanza error explícito. Un CSV solo con cabecera produce salidas vacías, no un fallo.

**Mock — librería y contrato.** `httpx` con timeout de primer nivel, reutilizable en la etapa 2. Pydantic copia el esquema de `openapi.yaml`; no se importa `app.py` del mock. Un asunto corto falla antes de gastar una llamada.

**Mock — timeout y reintentos.** 5 s: el mock puede tardar 2,5 s en una respuesta buena; 2 s mezclaría latencia con fallo. Un reintento si el 429 trae `Retry-After`. El 500 no se reintenta aquí (el 12 % no se gana a pulso).

**Mock — secretos y errores.** Token solo en `MOCK_TOKEN`. Cada fallo es un `ErrorProveedor` con frase (timeout, sin conexión, 401 sin imprimir el token, 404, 422, 429, 500, JSON roto). No se filtra `httpx`.

**SQL — motor.** El enunciado pide SQL estándar. El encabezado de `esquema.sql` lo verifica en MySQL/MariaDB; no exige instalar un servidor. En este Windows no hay cliente `mysql`. `correr.py` usa SQLite en memoria sobre una **copia** del mismo archivo. Las `.sql` se pueden pegar en MySQL sin reescribirlas.

**SQL — 01.** Parte de `areas` (`LEFT JOIN`) para no ocultar un área sin tickets. `COALESCE` deja 0, no NULL, si el área no tiene filas. No cerrados = todo lo que no está `Cerrado`.

**SQL — 02.** `tickets` + `usuarios` + `areas` (quién pidió qué). `INNER JOIN`: en este esquema todo ticket tiene usuario y área (`FK NOT NULL`).

**SQL — 03.** “Tickets reabiertos” no es sinónimo de `reaperturas`. El conjunto es `reaperturas > 0` (el hecho), no `estado = 'Reabierto'` (la foto de hoy). El historial va en `LEFT JOIN`: si no hay paso a Reabierto, el ticket igual sale y `ultima_reapertura` queda vacía. En este esquema: 36 filas; 28 siguen en Reabierto; 8 ya están en Abierto, Escalado, Cerrado o En proceso y no tienen fecha en el log. Si en sustentación piden la foto de hoy: una línea, `WHERE t.estado = 'Reabierto'` → 28 filas (`docs/aclaraciones_sustentacion.md`).

**SQL — índices.** El esquema no crea ninguno a propósito. Propuestos, no aplicados: `tickets(estado)`, `tickets(reaperturas)`, `historial_estado(estado_nuevo, fecha_cambio)`.

**API — marco.** FastAPI + Pydantic (mismo estilo que el mock). Alternativa descartada: Flask a mano (más código para validar y para OpenAPI).

**API — persistencia.** Memoria con candado. Alternativa descartada: SQLite ya (es diseño de datos de la etapa 4). Al reiniciar el proceso se pierde el listado.

**API — secretos.** Bearer `API_TOKEN`, distinto de `MOCK_TOKEN`. Viven en `.env` (no en el repo; el contrato es `.env.example`). Sin token configurado: 503, no un 401 ambiguo. `Idempotency-Key`: misma clave y mismo cuerpo → 200 y el mismo id; otro cuerpo → 409.

**API — documentación.** OpenAPI se genera desde rutas y modelos y se fija con pruebas; no se versiona otro `openapi.json` que pueda quedar obsoleto. Markdown añade decisiones técnicas y contexto funcional sin copiar todo el esquema. Se mantiene la URL sin `/v1` para no romper la prueba; una ruptura futura deberá introducir una ruta versionada.

**IA — desacople.** La API llama `clasificar` (`PuertoClasificador`), no a OpenAI. Así se inyecta un fijo en pruebas y mañana se cambia de proveedor sin tocar `src/api/`. Alternativa descartada: pegar `httpx` en la ruta del POST.

**IA — contrato HTTP.** `/v1/chat/completions` (OpenAI y compatibles: Groq, modelo local). Timeout **8 s** (el mock eran 5 s: latencia máxima 2,5 s; un chat tarda más en el primer token). Un reintento ante cualquier fallo del proveedor; si el segundo también falla → degradado. Alternativa descartada: reintentar solo 429 (un 500 transitorio también merece un segundo tiro; un 401 se gasta una llamada de más, se acepta por no ramificar).

**IA — catálogo cerrado.** Las etiquetas salen de `CATEGORIAS_VALIDAS` / `PRIORIDADES_VALIDAS` de la limpieza. Si el modelo inventa una, no se guarda: degradado. Alternativa descartada: fiarse del JSON del LLM (rompe el resumen área × prioridad).

**IA — degradado, no regex.** Si no hay clave, timeout, 401, 429, 500, JSON roto o etiqueta fuera de catálogo: `Sin clasificar` / `Media` y `origen=degradado`. El ticket **sí se crea** (201). Tras ver el LLM en vivo (vacaciones urgentes → Vacaciones/Crítica; texto ambiguo → el propio modelo elige Sin clasificar), el regex de negocio **sigue fuera**: duplicaría el catálogo, falsearía “vacaciones” en un correo de software, y el `origen` dejaría de decir la verdad. Alternativa descartada: 502 si OpenAI falla (el colaborador se queda sin solicitud).

**IA — secretos y diagnóstico.** `IA_API_KEY` solo en `.env`; no va al repo ni al cuerpo de error. El Playground de OpenAI no usa esa clave: cuenta ok ≠ POST clasificado. `GET /health` dice si hay proveedor al arranque; el motivo del degradado sale en la terminal (`http_401`, `http_429`, `timeout`), sin imprimir el token. Alternativa descartada: `$env:` en cada sesión (se olvida, se pega en capturas y no sirve para revisar el PR).

**Configuración — precedencia y validación.** El entorno del proceso gana sobre `.env`, como requieren GitHub Actions, Docker y un despliegue. `pydantic-settings` centraliza tipos y falla temprano ante un timeout negativo, un puerto inválido o un nivel de log desconocido. Alternativa descartada: mantener `os.environ.get()` disperso (cada módulo interpretaría de forma distinta el mismo valor).

**Logs — stdout y campos permitidos.** Se usa `logging` estándar con JSON, sin crear archivos locales ni añadir otra biblioteca. El `request_id` permite seguir petición → IA → respuesta. Solo se serializan campos permitidos; el cuerpo del ticket, correo, tokens, prompt y respuesta del proveedor quedan fuera. Alternativa descartada: registrar el cuerpo completo para depurar (filtra datos personales y secretos).

**Secretos — alcance del escaneo.** El código, las pruebas y la documentación desarrollados no contienen claves con formato `sk-proj-…`; `tests/seguridad/` lo fija. El paquete original incluye un patrón de ese tipo dentro de `materiales/revision/pr_para_revision.diff`, precisamente como artefacto defectuoso para la revisión final. No se usa, copia ni modifica.

**Legado — corrección mínima.** No se reescribe ni se modifica el archivo entregado. S1 respeta el contrato inclusivo; S2 usa `None` sin eliminar el acumulador explícito; S3 cuenta tickets con contador positivo y no inventa `1` cuando falta el dato. Se descartó corregir S3 con `estado.lower()` porque solo arreglaría mayúsculas, no tickets que cambiaron de estado después de reabrirse.

---

## Qué dejé fuera

**CSV.** No unifico sinónimos de categoría (`Acceso` / `Accesos` / `Gestión de accesos`, `Hardware` / `Equipos`). Las 39 ids repetidas no cruzan esos pares (`src/datos/validar_uniones.py`). Recortar al catálogo de `esquema.sql` también se descartó: el SQL no trae Vacaciones, Capacitación ni Compras, que sí están en el histórico y en las políticas. El original de `materiales/` no se toca.

**Mock.** No se consume el webhook `/webhook/mensajeria` (etapa 4). No hay reintentos con retroceso en 500 (también etapa 4). No se versiona `solicitud.json`.

**SQL.** No se instala MySQL “para la foto”. Docker (MariaDB) existe en el equipo; no se usó porque SQLite ya demostró las tres consultas. Oracle exigiría secuencia + `TIMESTAMP`, como dice el encabezado de `esquema.sql`. No se modifica `esquema.sql`. No se filtra la consulta 03 por `estado = 'Reabierto'` ni con `INNER JOIN` al historial: en este esquema dejaría fuera 8 tickets.

**Etapa 1 aún abierta.** Declaración de uso de IA de esta etapa, a mano, en `docs/declaracion_uso_ia.md`.

**API.** Persistencia, cambio de estado, autenticación corporativa, permisos por rol y paginación por cursor.

**IA.** No hay regex de categoría. No se versiona `IA_API_KEY`. No se usa Assistants ni streaming. Un modelo local o Groq caben cambiando `IA_API_BASE_URL`; no van en este entregable.

**Etapa 2 (resto).** Pantalla Angular opcional con listado y filtros.
