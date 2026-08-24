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
| 1 | `docs/aclaraciones_sustentacion.md` | Hecho (SQL, mock, preguntas fijas) |
| 2 | Contrato de la API + doc funcional (qué resuelve y para quién) | Pendiente |
| 3 | Guía breve de prompts, commits o revisión de código generado por IA | Pendiente |
| 4 | Arquitectura, flujo extremo a extremo y tres ADR | Pendiente |
| 5 | Decisión IA vs automatización, métricas previas, revisión del PR | Pendiente |
| Entrega | Video de 5 min y revisión escrita de `pr_para_revision.diff` | Pendiente |

**Lectura corta para el evaluador.** Instalar y ejecutar están abajo. El criterio (alternativas descartadas, 36 vs 28, timeout 5 s) está en *Qué supuse* y en `docs/aclaraciones_sustentacion.md`. El código de esta etapa: `src/datos/limpiar.py`, `src/integraciones/`, `sql/`.

## Hasta qué etapa llegué

Etapa 0 hecha. Etapa 1: CSV, mock y SQL cerrados. Falta llenar a mano la declaración de uso de IA de la etapa 1.

| Estado | Etapa | Qué es |
|---|---|---|
| Hecha | 0. Contextualización | Enunciado, materiales y alcance Middle II |
| En curso | 1. Fundamentos | Limpieza del CSV, cliente del mock y tres consultas SQL |
| Pendiente | 2. Autonomía e integración | API, clasificador desacoplado, legado |
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
| 2–5 | API, IA, RAG, orquestación, ADR | `src/`, `tests/`, `docs/`, `ci/` | Pendiente al cerrar cada etapa |
| Todas | Paquete original (solo lectura) | `materiales/` | No se modifica |

## Estructura

Un solo producto. Las carpetas son por capacidad, no por número de etapa.

```
src/
  datos/            limpieza, validación y resumen del CSV
  integraciones/    consumo del mock (GET/POST, errores, timeout)
  api/              recursos de la API propia (etapa 2)
  ia/               categoría y prioridad, desacoplado (etapa 2)
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

Python 3 con `pip`. Desde la raíz del repositorio:

```
pip install -r requirements.txt
```

Dependencias de esta etapa: `pandas`, `pytest`, `httpx`, `pydantic`. SQLite viene con Python; no hay que instalar un motor SQL para comprobar las consultas.

El mock es un proceso aparte y no se modifica. Sus dependencias:

```
cd materiales/servicio_mock
pip install -r requirements.txt
```

El token no va en el repo. El valor de prueba está en `materiales/servicio_mock/README.md`. En PowerShell, solo en la sesión:

```
$env:MOCK_TOKEN="demo-token-prueba-2026"
```

Opcional: `$env:MOCK_URL` (por defecto `http://localhost:8080`) y `$env:MOCK_TIMEOUT` (por defecto 5 segundos).

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

En otra, con `MOCK_TOKEN` ya definido:

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
python -m pytest tests/datos/ tests/integraciones/ tests/sql/ -q
```

El enunciado pide **al menos tres funciones y un caso de borde**. Ya está cubierto: `normalizar_fecha`, `normalizar_categoria` y `eliminar_duplicados`, con bordes (fecha ilegible, archivo vacío o inexistente, `reaperturas` vacía). El mock añade timeout, 401, 404, 429, 500 y JSON roto. `tests/sql/` fija 8 / 120 / 36 y dos bordes del esquema feliz: un área sin tickets no desaparece; un reabierto sin paso en el log igual sale.

El mock real es aleatorio (~12 % de 500): el camino feliz en la terminal no basta. En vivo, sin suerte: quite `MOCK_TOKEN` (401) o apague uvicorn (sin conexión).

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

---

## Qué dejé fuera

**CSV.** No unifico sinónimos de categoría (`Acceso` / `Accesos` / `Gestión de accesos`, `Hardware` / `Equipos`). Las 39 ids repetidas no cruzan esos pares (`src/datos/validar_uniones.py`). Recortar al catálogo de `esquema.sql` también se descartó: el SQL no trae Vacaciones, Capacitación ni Compras, que sí están en el histórico y en las políticas. El original de `materiales/` no se toca.

**Mock.** No se consume el webhook `/webhook/mensajeria` (etapa 4). No hay reintentos con retroceso en 500 (también etapa 4). No se versiona `solicitud.json`.

**SQL.** No se instala MySQL “para la foto”. Docker (MariaDB) existe en el equipo; no se usó porque SQLite ya demostró las tres consultas. Oracle exigiría secuencia + `TIMESTAMP`, como dice el encabezado de `esquema.sql`. No se modifica `esquema.sql`. No se filtra la consulta 03 por `estado = 'Reabierto'` ni con `INNER JOIN` al historial: en este esquema dejaría fuera 8 tickets.

**Etapa 1 aún abierta.** Declaración de uso de IA de esta etapa, a mano, en `docs/declaracion_uso_ia.md`.

**Etapas 2 a 5.** API propia, clasificador, legado, RAG, CI, orquestación, ADR, métricas y revisión del PR.
