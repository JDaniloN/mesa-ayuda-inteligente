# Aclaraciones para la sustentación

Respuestas cortas a preguntas que suelen hacer. No sustituyen el README: aquí está el “por qué” para decirlo en voz alta.

Cómo se comprobó el SQL en este equipo: `python sql/correr.py` (24 ago 2026).

---

## ¿Por qué no ejecutaste las consultas en MySQL?

El enunciado pide **SQL estándar**. El encabezado de `materiales/datos/esquema.sql` dice que está verificado en MySQL/MariaDB y qué cambiaría en Oracle. No exige instalar un servidor en el portátil de la prueba.

En este Windows el cliente `mysql` **no está en el PATH** (`El término 'mysql' no se reconoce`). Instalar MySQL Server son 15–40 minutos y no suma al criterio: las consultas no usan `AUTO_INCREMENT`, variables de sesión ni funciones exclusivas de MySQL.

**Qué hice.** `sql/correr.py` carga una **copia en memoria** del mismo `esquema.sql` con SQLite (viene con Python) y corre `sql/01_*.sql` … `03_*.sql`. El original de `materiales/` no se toca.

**Qué descarté.** Instalar MySQL “para la foto”. Docker (MariaDB) existe en el equipo; no lo usé porque SQLite ya demostró las tres consultas y el tiempo va a las etapas siguientes.

**Si piden el motor del material.** Las tres `.sql` se pueden pegar en MySQL/MariaDB sin reescribirlas. PowerShell no acepta `<`; ahí sería `Get-Content archivo.sql -Raw | mysql ...`.

---

## Resultados de las tres consultas

Comando: `python sql/correr.py` desde la raíz del repo.

### 01 — Agregación por área (8 filas)

Una fila por cada área del catálogo (LEFT JOIN desde `areas`).

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

Lectura: 8 áreas, 120 tickets en total. Operaciones es la que más reabre (promedio 0.94). Calidad casi no (0.09) y ninguna de sus 11 está cerrada.

### 02 — Join de tres tablas (120 filas)

`tickets` + `usuarios` + `areas`. Muestra: código, asunto, estado, prioridad, fecha, nombre y correo del solicitante, si el usuario está activo, área y sede.

Primeras filas (más recientes primero):

| codigo | asunto | estado | prioridad | fecha_creacion | solicitante | area |
|---|---|---|---|---|---|---|
| TK-00023 | Solicitud de incidente | Escalado | Baja | 2026-06-16 16:00:00 | Usuario Demo 026 | Calidad |
| TK-00093 | Solicitud de nómina | Reabierto | Media | 2026-06-09 12:00:00 | Usuario Demo 032 | Comercial |
| TK-00096 | Solicitud de red | Abierto | Media | 2026-05-27 15:00:00 | Usuario Demo 013 | Compras |

120 filas = todos los tickets del esquema; ninguno se queda sin usuario ni área (FK NOT NULL).

### 03 — Tickets reabiertos (36 filas)

Conjunto: `reaperturas > 0`. El historial es `LEFT JOIN` (si no hay paso a Reabierto, `ultima_reapertura` va vacía).

| codigo | estado | prioridad | reaperturas | area | ultima_reapertura |
|---|---|---|---:|---|---|
| TK-00073 | Reabierto | Alta | 3 | Operaciones | 2026-03-08 10:00:00 |
| TK-00040 | Reabierto | Baja | 3 | Aplicaciones | 2026-02-04 03:00:00 |
| TK-00084 | Reabierto | Media | 3 | Aplicaciones | 2025-12-11 17:00:00 |
| TK-00045 | Cerrado | Crítica | 1 | Operaciones | *(vacía)* |
| TK-00080 | Cerrado | Crítica | 1 | Talento Humano | *(vacía)* |
| TK-00106 | Escalado | Media | 1 | Infraestructura | *(vacía)* |

36 de 120: 28 siguen en Reabierto y **8** ya están en Abierto, Escalado, Cerrado o En proceso. Un `INNER JOIN` al historial o un `WHERE estado = 'Reabierto'` habría mostrado solo 28.

**Cómo lo digo:** *Reabierto es un estado; reaperturas es un hecho. Pregunté por el hecho. El historial solo aporta la fecha, y si el log está incompleto no borro el ticket.*

---

## Las tres funciones del enunciado (pruebas unitarias)

El enunciado pide **tres funciones y un caso de borde**. Función = un `def` en Python, no el script entero. Unitaria = se llama sola, con datos inventados, sin el CSV de 2.000 ni el mock en 8080. Borde = lo que no es el camino feliz.

Las tres que enseño: `normalizar_fecha`, `normalizar_categoria`, `eliminar_duplicados` en `src/datos/limpiar.py`. Tests en `tests/datos/test_limpiar.py`.

```
python -m pytest tests/datos/test_limpiar.py -q
python -m pytest tests/datos/test_limpiar.py -k "fecha or categoria or duplicados" -q
```

Si piden “muéstrame un borde en vivo”: `test_fecha_invalida_lanza_error` (`32/13/2025`) o `test_exporta_archivo_inexistente`.

---

### 1. `normalizar_fecha`

**Qué hace.** Convierte los tres formatos del material a `YYYY-MM-DD`. Vacío se queda vacío (ticket sin cierre). Ilegible no se “adivina”: `parsear_fecha` lanza `ValueError` y la fila va a rechazados.

**Cómo lo digo.** *El enunciado dice tres formatos. No usé `to_datetime` a ciegas porque mezcla día/mes. Cada formato tiene su parser. Vacío no es error; “ayer” sí.*

**Feliz.** `"2025-03-08"` → igual. `"03/06/2025"` → `"2025-06-03"` (día/mes, no el de EE. UU.). `"20-Ene-2026"` → `"2026-01-20"`.

**Borde.** `""` → `""`. `"32/13/2025"` y `"ayer"` → `ValueError`. Test: `test_vacio_queda_vacio`, `test_fecha_invalida_lanza_error`.

**Qué descarté.** `pandas.to_datetime(..., errors="coerce")`: el `03/06` ambiguo y el `Ene` en español se silencian o se interpretan mal.

**Si me piden cambiarla en vivo.** Que `"  07/03/2026  "` recorte espacios (ya lo hace) o que un cuarto formato se rechace, no se parchee.

---

### 2. `normalizar_categoria`

**Qué hace.** Unifica **escritura** (mayúsculas y tildes) con un catálogo explícito. Vacío → `Sin clasificar` (esa etiqueta ya existe en el CSV). No une sinónimos.

**Cómo lo digo.** *SOFTWARE y software son la misma categoría mal escrita. Acceso y Accesos pueden ser dos colas distintas. Uní lo primero; no inventé lo segundo. Lo comprobé con las 39 ids repetidas: solo cambiaban mayúsculas.*

**Feliz.** `"SOFTWARE"` → `"Software"`. `"nomina"` / `"NOMINA"` → `"Nómina"`.

**Borde.** `""` y `None` → `"Sin clasificar"`. `"Acceso"` sigue Acceso y `"accesos"` sigue Accesos. Test: `test_categoria_unifica_escritura`, `test_categoria_no_junta_sinonimos`.

**Qué descarté.** Un mapa Acceso/Accesos/Gestión de accesos (`validar_uniones.py` no lo sostiene). Recortar al catálogo de `esquema.sql` (no trae Vacaciones, Capacitación ni Compras).

**Si me piden unir sinónimos en vivo.** No lo hago sin evidencia. Si insisten: un diccionario aparte, no tocar el catálogo de escritura, y una prueba que falle antes.

---

### 3. `eliminar_duplicados`

**Qué hace.** Una fila por `id`, se queda la **primera**. En este CSV las copias son el mismo ticket; la diferencia era mayúsculas de categoría (ya normalizada antes).

**Cómo lo digo.** *Duplicado en mesa de ayuda es el mismo caso, no dos personas. Keep first es determinista. Si uniera sinónimos antes de deduplicar, estaría inventando que Hardware y Equipos son el mismo ticket; en las 39 ids no ocurría.*

**Feliz.** Tres filas, dos con el mismo `id` → dos filas. Test: `test_elimina_duplicados_por_id`.

**Borde.** DataFrame sin columna `id`: no revienta, devuelve el mismo `df`. El borde de archivo (vacío, solo encabezado, inexistente) está en `exportar`: `test_exporta_archivo_vacio`, `test_exporta_solo_encabezado`, `test_exporta_archivo_inexistente`.

**Qué descarté.** Quedarme con la última (`keep="last"`): no hay regla de negocio que la última sea la “más correcta”. Fusionar columnas distintas: aquí no había conflicto real.

**Si me piden keep last en vivo.** Una línea en `drop_duplicates(..., keep="last")` y cambiar el test. Diría antes: *en este histórico no cambia el conteo de ids únicos; cambia cuál copia sobrevive si algún día difieren.*

---

**Cierre si preguntan “¿y el resto de tests?”** El mínimo son esas tres. El 4 está en los bordes de `exportar` y en `tests/sql/` (8 / 120 / 36; área sin tickets; reabierto sin log). El mock no cuenta para este ítem: es otro criterio (consumo de API).

---

## Otras preguntas fijas (etapa 1)

### ¿Por qué no filtraste `estado = 'Reabierto'`?

Porque eso es la foto de hoy, no el hecho. *Reabierto es un estado; reaperturas es un hecho. Pregunté por el hecho. El historial solo aporta la fecha, y si el log está incompleto no borro el ticket.*

### Si me piden 28 filas (estado actual) en vez de 36

Un solo cambio, en `sql/03_tickets_reabiertos.sql`. El `LEFT JOIN` al historial se deja: en estos 28 todos tienen fecha.

```sql
-- ahora (36): el hecho
WHERE t.reaperturas > 0

-- si piden la foto de hoy (28)
WHERE t.estado = 'Reabierto'
```

Luego `python sql/correr.py`. No toca `correr.py` ni el esquema.

No uses `INNER JOIN` al historial para “llegar a 28”: en este dataset coincide, pero mide el log, no el estado. Si el evaluador quiere tickets que **están** reabiertos, el filtro es `estado`.

### ¿Por qué `reaperturas` vacía no pasa a 0?

Porque 0 (o 1) es inventar un conteo. Había 93 vacíos; 27 ya estaban en Reabierto. Un reabierto no puede quedar en 0, y poner 1 también miente si fueron 2 o 3. El vacío se conserva. No se usa `No especificado`: el campo es numérico.

### ¿Por qué no uniste Acceso / Accesos / Gestión de accesos?

Normalicé **escritura** (mayúsculas y tildes). Unir sinónimos no está sostenido por los duplicados del CSV: las 39 ids repetidas solo cambían mayúsculas (`validar_uniones.py`). El catálogo de `esquema.sql` tampoco cubre Vacaciones, Capacitación ni Compras.

### ¿Por qué timeout 5 s y no 2 s?

El mock tarda hasta 2,5 s en una respuesta **buena**. Con 2 s se mezclaría latencia con fallo.

### ¿Por qué no reintentas el 500?

El 12 % no se “gana” a golpes. Un reintento sí hay en **429** si trae `Retry-After`. El backoff del 500 queda para la etapa 4. El POST lleva `Idempotency-Key` para no duplicar.

### En `/docs` puse el token y salió 401

Execute **no manda** la cabecera `authorization` (Swagger la trata como reservada). El curl de esa pantalla no lleva `-H authorization`. El cliente Python sí. En `/docs` el recuadro se rellena con `Bearer demo-token-prueba-2026`; aun así esta UI del mock no la envía.

### `curl` en PowerShell partió el JSON

`<` y `\"` no funcionan igual que en bash. El CLI `python -m src.integraciones.cliente` arma el JSON en Python.

### ¿Dónde está el token?

Solo en `MOCK_TOKEN`. No va en el repo. El valor de prueba está en `materiales/servicio_mock/README.md`.
