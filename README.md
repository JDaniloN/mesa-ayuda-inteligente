# Mesa de Ayuda Inteligente

Prueba técnica de nivelación — Familia de cargos IA · LA FORTUNA S.A.

## Nivel objetivo

Ingeniero IA Middle II.

## Hasta qué etapa llegué

Etapa 0 hecha. Etapa 1 en curso: CSV, mock y SQL escritos (falta que valides el SQL).

| Estado | Etapa | Qué es |
|---|---|---|
| Hecha | 0. Contextualización | Entendí el enunciado, los materiales y el alcance Middle II |
| En curso | 1. Fundamentos | CSV, mock y SQL. SQL comprobado con SQLite (`python sql/correr.py`) |
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
| 1 | Cliente del servicio mock | `src/integraciones/cliente.py` | `python -m src.integraciones.cliente` (mock en 8080 y `MOCK_TOKEN`) |
| 1 | Consultas SQL | `sql/` | `python sql/correr.py` |
| 1 | Aclaraciones de sustentación | `docs/aclaraciones_sustentacion.md` | Abrir el archivo; MySQL, resultados SQL y preguntas fijas |
| 1 | Pruebas de limpieza | `tests/datos/test_limpiar.py` | `python -m pytest tests/datos/test_limpiar.py` |
| 1 | Pruebas de integraciones | `tests/integraciones/` | `python -m pytest tests/integraciones/` |
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
python -m pytest tests/datos/ tests/integraciones/
```

Cliente del mock (el servidor simulado se levanta aparte y no se modifica):

```
cd materiales/servicio_mock
pip install -r requirements.txt
uvicorn app:app --port 8080
```

En otra terminal, con el token solo en el entorno (PowerShell: `$env:MOCK_TOKEN="demo-token-prueba-2026"`):

```
python -m src.integraciones.cliente
```

Consultas SQL: el material está en MySQL/MariaDB. En este Windows **no hay cliente `mysql`** (no es un error de las consultas). Para comprobarlas aquí:

```
python sql/correr.py
```

Carga `esquema.sql` en SQLite en memoria, imprime **todas** las filas y deja CSV en `data/salida/consulta_*.csv` (no se versionan). El original no se modifica.

Si más adelante tiene MySQL/MariaDB en el PATH, PowerShell:

```
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS mesa_ayuda;"
Get-Content materiales/datos/esquema.sql -Raw | mysql -u root -p mesa_ayuda
Get-Content sql/01_agregacion_por_area.sql -Raw | mysql -u root -p -t mesa_ayuda
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

**Imputaciones.** `solicitante` vacío → `No identificado`. `reaperturas` vacía se deja vacía: no se pone `0` ni `1` (en Reabierto el conteo real podría ser 2 o 3). Tampoco `No especificado`: es un campo numérico. Un texto no dígito sí se rechaza.

**Rechazo.** id vacío; `fecha_creacion` vacía o ilegible; `fecha_cierre` ilegible o anterior a la creación; prioridad, categoría, estado o canal no reconocidos; `reaperturas` con texto que no es número (el vacío no rechaza). Un archivo sin encabezado o inexistente lanza error explícito. Un CSV solo con cabecera produce salidas vacías, no un fallo.

**Fuera de este entregable.** No se unifican sinónimos de categoría. El original de `materiales/` no se toca.

### Etapa 1 — Cliente del servicio mock

El cliente vive en `src/integraciones/`. El mock en `materiales/servicio_mock/` no se modifica: falla a propósito (latencia 0,1–2,5 s, 12 % de 500, 5 % de 429).

**Librería.** `httpx`, con timeout de primer nivel. Alternativa descartada: `requests` en un script suelto (no reutilizable en la etapa 2).

**Contrato.** Pydantic copia el esquema de `openapi.yaml` (`SolicitudEntrada` / `SolicitudSalida`). No se importa `app.py` del mock: ese código es el servidor, no una librería. Un asunto corto falla **antes** de gastar una llamada. Alternativa descartada: mandar `dict` y enterarse con un 422 dos segundos después.

**Timeout.** 5 s (`MOCK_TIMEOUT`). El mock puede tardar 2,5 s en una respuesta buena; un timeout de 2 s confundiría latencia con fallo.

**Reintentos.** Un reintento si el 429 trae `Retry-After`. El 500 no se reintenta aquí (el 12 % no se “gana” a pulso; el backoff queda para la etapa 4). El POST lleva `Idempotency-Key` para no duplicar si ese reintento se dispara.

**Secretos.** Token solo en `MOCK_TOKEN`. URL opcional `MOCK_URL` (por defecto `http://localhost:8080`). El valor de prueba está en `materiales/servicio_mock/README.md`, no en `src/`.

**Errores.** `httpx` no se filtra. Cada fallo es un `ErrorProveedor` con frase: timeout, sin conexión, 401 (sin imprimir el token), 404, 422, 429, 500. Un 200/201 con JSON roto también se traduce (no se traga un cuerpo inválido). El CLI imprime esa frase, cierra el cliente y sale con código 1.

**Cómo se demuestra el criterio 4.** El mock real es aleatorio (~12 % de 500): el camino feliz en la terminal no basta. La evidencia de timeout, 401, 404, 429, 500 y cuerpo inválido está en `python -m pytest tests/integraciones/ -q`. En vivo, sin suerte: quite `MOCK_TOKEN` (401), apague uvicorn (sin conexión). `/docs` muestra el esquema; Execute **no manda** `authorization` (cabecera reservada). En PowerShell, `curl.exe -d "{...}"` parte el JSON; use el CLI o `Invoke-RestMethod`.

**Fuera de este entregable.** Webhook `/webhook/mensajeria` (etapa 4). Reintentos con retroceso en 500.

### Etapa 1 — Consultas SQL

Tres archivos en `sql/`, sobre `materiales/datos/esquema.sql`. SQL estándar (MySQL/MariaDB). El original no se modifica.

**01 — Agregación por área.** `areas LEFT JOIN tickets`: un área sin tickets seguiría apareciendo con ceros. Cuenta total, no cerrados y promedio de reaperturas.

**02 — Join de tres tablas.** `tickets` + `usuarios` + `areas`: quién pidió qué y de qué sede. Alternativa descartada: tickets + adjuntos + historial (deja fuera casos sin archivo y no responde la pregunta de negocio).

**03 — Tickets reabiertos.** El conjunto es `reaperturas > 0`. El historial entra con `LEFT JOIN` solo para la fecha de la última reapertura. Alternativa descartada: `estado = 'Reabierto'` o `INNER JOIN` al historial (en este esquema dejaba fuera 8 tickets que ya no están en Reabierto).

**Índices propuestos** (el esquema no crea ninguno a propósito, más allá de PK/FK de InnoDB):

- `tickets(estado)` — listados y el conteo de no cerrados.
- `tickets(reaperturas)` — el filtro de la consulta 03.
- `historial_estado(estado_nuevo, fecha_cambio)` — la última reapertura.

No se aplican en el `.sql` original; son propuesta para cuando el volumen deje de ser el de prueba.

**Fuera de este entregable.** Instalar MySQL en el equipo no es requisito de la prueba; el dialecto del material es MySQL/MariaDB y las consultas son SQL estándar. Oracle exigiría secuencia + `TIMESTAMP`, como dice el encabezado de `esquema.sql`.
