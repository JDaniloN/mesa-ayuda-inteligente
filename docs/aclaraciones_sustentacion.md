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
