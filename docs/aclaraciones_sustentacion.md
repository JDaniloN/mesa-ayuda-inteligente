# Aclaraciones para la sustentación (uso personal)

**Este archivo no es entrega.** El evaluador y el reclutador solo ven
`README.md` y los docs listados ahí. Si un hecho, cifra o decisión está
solo aquí, nadie de afuera lo va a leer. Antes de la sustentación, revisa
que el README ya cuente la historia oficial.

Aquí queda el “cómo lo digo” y los cambios en vivo. El orden sigue las
etapas del README.

Cómo se comprobó el SQL en este equipo: `python sql/correr.py` (24 ago 2026).

---

## Etapa 1 — SQL

### ¿Por qué no ejecutaste las consultas en MySQL?

El enunciado pide **SQL estándar**. El encabezado de `materiales/datos/esquema.sql`
dice que está verificado en MySQL/MariaDB y qué cambiaría en Oracle. No exige
instalar un servidor.

En este Windows el cliente `mysql` **no está en el PATH**. Instalar MySQL
Server son 15–40 minutos y no suma: las consultas no usan `AUTO_INCREMENT`,
variables de sesión ni funciones exclusivas de MySQL.

**Qué hice.** `sql/correr.py` carga una **copia en memoria** del mismo
`esquema.sql` con SQLite. El original de `materiales/` no se toca.

**Qué descarté.** Instalar MySQL “para la foto”. Docker (MariaDB) existe en el
equipo; no lo usé porque SQLite ya demostró las tres consultas.

**Si piden el motor del material.** Las tres `.sql` se pegan en MySQL/MariaDB
sin reescribirlas. PowerShell no acepta `<`; usar
`Get-Content archivo.sql -Raw | mysql ...`.

### COALESCE en la consulta 01

**Cómo lo digo:** *El JOIN evita que el área desaparezca. El COALESCE evita
que el indicador quede nulo. Son dos fallos distintos. En este catálogo no se
nota; el día que den de alta un área sin tickets, el dashboard no muestra
“vacío”.*

Las 8 filas actuales no cambian si se quita `COALESCE` (todas las áreas tienen
tickets). El borde está en `test_agregacion_area_sin_tickets_no_desaparece`.
No usé `IFNULL`: no es SQL estándar.

**Si piden quitarlo en vivo.** Se quitan las dos llamadas a `COALESCE` en
`sql/01_agregacion_por_area.sql`. Las 8 filas no cambian. Hay que ajustar el
test del área fantasma: `no_cerrados` y `reaperturas_promedio` pasarían a
`None`.

### 36 vs 28 en la consulta 03

**Cómo lo digo:** *Reabierto es un estado; reaperturas es un hecho. Pregunté
por el hecho. El historial solo aporta la fecha, y si el log está incompleto
no borro el ticket.*

Si piden la foto de hoy (28 filas), un solo cambio en
`sql/03_tickets_reabiertos.sql`. El `LEFT JOIN` se deja:

```sql
-- ahora (36): el hecho
WHERE t.reaperturas > 0

-- si piden la foto de hoy (28)
WHERE t.estado = 'Reabierto'
```

Luego `python sql/correr.py`. No toca `correr.py` ni el esquema.

No uses `INNER JOIN` al historial para “llegar a 28”: en este dataset
coincide, pero mide el log, no el estado.

---

## Etapa 1 — Las tres funciones del enunciado

El enunciado pide **tres funciones y un caso de borde**. Función = un `def`
en Python, no el script entero. Unitaria = se llama sola, con datos
inventados, sin el CSV de 2.000 ni el mock en 8080.

Las tres que enseño: `normalizar_fecha`, `normalizar_categoria`,
`eliminar_duplicados` en `src/datos/limpiar.py`.

```
python -m pytest tests/datos/test_limpiar.py -k "fecha or categoria or duplicados" -q
```

Si piden un borde en vivo: `test_fecha_invalida_lanza_error` (`32/13/2025`) o
`test_exporta_archivo_inexistente`.

### 1. `normalizar_fecha`

**Cómo lo digo.** *El enunciado dice tres formatos. No usé `to_datetime` a
ciegas porque mezcla día/mes. Cada formato tiene su parser. Vacío no es
error; “ayer” sí.*

**Si me piden cambiarla en vivo.** Que `"  07/03/2026  "` recorte espacios
(ya lo hace) o que un cuarto formato se rechace, no se parchee.

### 2. `normalizar_categoria`

**Cómo lo digo.** *SOFTWARE y software son la misma categoría mal escrita.
Acceso y Accesos pueden ser dos colas distintas. Uní lo primero; no inventé
lo segundo. Lo comprobé con las ids repetidas: solo cambiaban mayúsculas.*

**Si me piden unir sinónimos en vivo.** No lo hago sin evidencia. Si insisten:
un diccionario aparte, no tocar el catálogo de escritura, y una prueba que
falle antes.

### 3. `eliminar_duplicados`

**Cómo lo digo.** *Duplicado en mesa de ayuda es el mismo caso, no dos
personas. Keep first es determinista. Si uniera sinónimos antes de
deduplicar, estaría inventando que Hardware y Equipos son el mismo ticket.*

**Si me piden keep last en vivo.** Una línea en
`drop_duplicates(..., keep="last")` y cambiar el test. Diría antes: *en este
histórico no cambia el conteo de ids únicos; cambia cuál copia sobrevive si
algún día difieren.*

**Cierre si preguntan “¿y el resto de tests?”** El mínimo son esas tres. El
resto está en los bordes de `exportar` y en `tests/sql/` (8 / 120 / 36; área
sin tickets; reabierto sin log). El mock no cuenta para este ítem: es otro
criterio.

---

## Etapa 1 — Otras preguntas fijas

### ¿Por qué `reaperturas` vacía no pasa a 0?

Porque 0 (o 1) es inventar un conteo. Había 93 vacíos; 27 ya estaban en
Reabierto. Un reabierto no puede quedar en 0, y poner 1 también miente si
fueron 2 o 3.

### ¿Por qué timeout 5 s y no 2 s?

El mock tarda hasta 2,5 s en una respuesta **buena**. Con 2 s se mezclaría
latencia con fallo.

### ¿Por qué no reintentas el 500?

El 12 % no se “gana” a golpes. Un reintento sí hay en **429** si trae
`Retry-After`. El backoff del 500 queda para la etapa 4.

### En `/docs` del mock puse el token y salió 401

Execute **no manda** la cabecera `authorization`. El cliente Python sí. El
valor de prueba está en `materiales/servicio_mock/README.md`.

### `curl` en PowerShell partió el JSON

`<` y `\"` no funcionan igual que en bash. El CLI
`python -m src.integraciones.cliente` arma el JSON en Python.

---

## Etapa 2 — API

OpenAPI: `http://127.0.0.1:8000/docs`. Token: `API_TOKEN` de `.env` (no el
del mock ni la de OpenAI). Candado **Authorize**. Arranque: `python -m src.api`.

### ¿Por qué el listado vacío es 200 y no 404?

**Cómo lo digo:** *404 es “esta solicitud no existe”. 200 vacío es “no hay
ninguna que cumpla el filtro”. Si el listado devolviera 404, el tablero vacío
se confundiría con una ruta rota.*

Vacaciones es categoría, no área. Filtrar `prioridad=Alta` da `[]` si el LLM
no asignó Alta (el degradado deja Media).

### ¿Por qué FastAPI y no Flask?

OpenAPI y validación salen del contrato Pydantic. Flask habría sido más código
para el mismo 422.

### ¿Por qué memoria y no SQLite?

Este ítem pide recursos y códigos, no el modelo relacional (etapa 4). Al
reiniciar se pierde el listado; está declarado.

### ¿Por qué comprobar idempotencia antes de llamar a IA?

**Cómo lo digo:** *El estado final ya era idempotente; ahora también lo es el
efecto costoso de clasificación.*

### ¿Por qué 503 si falta API_TOKEN?

Sin secreto configurado el servicio no está listo. Un 401 haría pensar que el
cliente se equivocó de token.

### `/health`

Como el mock: sin token, `estado: operativo`. Extra: `clasificador`. No prueba
que OpenAI tenga saldo: eso se ve en la terminal al clasificar (`http_429`).

---

## Etapa 2 — Clasificador de IA

Pruebas sin red: `python -m pytest tests/ia/ -q`.

### ¿Por qué el POST sigue en 201 si OpenAI falla?

**Cómo lo digo:** *El 401 o el 429 son de OpenAI. El 201 es de la mesa. Si
mezclo esos códigos, el Authorize de Swagger parece roto cuando lo que falló
fue la cuota.*

Evidencia: `test_post_201_si_el_llm_responde_500`. En vivo: quite
`IA_API_KEY`, reinicie, mismo POST.

### ¿Por qué no un regex de “vacaciones” / “urgente”?

Se evaluó **después** de ver el LLM. El camino principal ya etiqueta
Vacaciones/Crítica. Un texto ambiguo el propio modelo deja en `Sin clasificar`
con `origen=proveedor`: no es un fallo, es abstención. El degradado sin regex
dice la verdad: *no clasificamos, el ticket existe*.

### ¿Qué context engineering se aplicó?

Catálogo de la limpieza + sección 3 de `POL-TIC-05` + abstención + tres
ejemplos (caída general, solicitud planificada, inyección). Asunto y
descripción viajan como JSON y se declaran no confiables. Se descartó forzar
`response_format` para no excluir proveedores compatibles.

### 401, 429 y degradado no son lo mismo

La tabla viva está en el README (clasificador de IA). De memoria: POST 401 =
Bearer de la mesa. Terminal `http_401` + POST 201 = clave de OpenAI.
`clasificador: proveedor` en `/health` solo dice que había clave al arrancar.

---

## Etapa 2 — Legado

```
python -m pytest tests/legacy/ -q
```

### S1

**Cómo lo digo:** *La documentación y el código se contradecían. No cambié el
contrato: cambié dos comparadores y fijé ambos límites con una prueba.*

Un rango semiabierto `inicio <= fecha < primer_dia_siguiente` es válido, pero
cambiaría el significado de `fin`.

### S2

**Cómo lo digo:** *No era un error de suma; era estado escondido entre
llamadas. `None` crea una cesta nueva, pero mantuve el acumulador explícito
para no romper compatibilidad.*

### S3

**Cómo lo digo:** *El estado es la foto de hoy; reaperturas es el hecho
histórico. Cuento tickets con contador positivo, no sumo eventos.*

`estado.lower()` solo arreglaría mayúsculas, no tickets que cambiaron de
estado después de reabrirse. Un contador vacío no se transforma en `1`.

---

## Etapa 2 — Configuración y logs

### Precedencia

**Cómo lo digo:** *El código es el mismo en todos los entornos. Solo cambia
la configuración externa: proceso primero, archivo local después y valores
seguros al final.*

Una variable vieja de PowerShell se elimina; no se invierte la precedencia de
producción para ocultarla.

### Log estructurado

**Cómo lo digo:** *Un texto libre se lee; un JSON también se consulta. El
`X-Request-ID` de la respuesta es el mismo que acompaña la petición y los
intentos de IA.*

Stdout, no un `.log`: contenedores recogen stdout. No se serializan
`Authorization`, tokens, prompt, asunto, descripción ni solicitante.

Evidencia:

```powershell
python -m pytest tests/configuracion/ tests/observabilidad/ -q
git check-ignore .env
git ls-files .env
```

El primer comando de Git debe mostrar `.env`; el segundo no debe mostrar nada.
`materiales/revision/pr_para_revision.diff` trae un patrón `sk-proj-…` a
propósito; no se toca.

---

## Etapa 2 — Documentación de la API

**Cómo lo digo:** *OpenAPI dice cómo integrarse; el documento funcional dice
para qué vale. Si mezclo ambos, el desarrollador no encuentra códigos y el
negocio recibe detalles de cabeceras que no necesita.*

No se versiona `openapi.json`: FastAPI lo genera; el test fija el contrato.
El POST documenta 201 y 200 porque el reintento idempotente es un camino
normal. No hay `/v1` para no romper consumidores por una necesidad que el
ejercicio todavía no tiene.

---

## Etapa 2 — Angular opcional

**Cómo lo digo:** *No prometo secreto donde técnicamente no puede existir. En
la demo el usuario introduce API_TOKEN, queda solo en memoria y producción
debe usar identidad corporativa con tokens personales y cortos.*

El interceptor solo añade `Authorization` a URLs que empiezan por `/api/`.
No hay `localStorage`, cookie ni `name` en el campo (el form no debe armar
`?api-token=...`). El indicador pasa a verde solo después de un GET 200.

Descartado: crear solicitudes, editar estado, login simulado y dashboard.

---

## Etapa 3 — RAG

**Cómo lo digo:** *El conocimiento vive junto al código de la demo. Si mañana
el volumen crece, el puerto del almacén se puede sustituir sin cambiar la
ruta HTTP; no lo hice ahora porque no había incompatibilidad real.*

Sobre el umbral: *El número está a la vista en `.env.example` para poder
moverlo. No lo presento como precisión medida. Solo decide si la pregunta
entera está fuera de dominio; no lo uso para decir si cubrí cada mitad.*

Si cambian PDF o modelo: el sidecar guarda hash, modelo y dimensión. Distintos
→ se borra la colección. Citas solo de metadatos del retriever. Tablas de
POL-TIC-05: representación clave-valor, sin alterar `materiales/`.

Preguntas de dos hechos: *No subí el `limite` del contrato. Parto la pregunta
con reglas, recupero cada parte, limito hermanas del mismo título y, si entra
una cláusula `N.M`, puedo traer el vecino. El modelo tiene prohibido copiar
un plazo de un fragmento a otra parte de la pregunta.*

Descartado: reranker con LLM, HyDE, GraphRAG, otro vector store, vectores
falsos en producción y penalizar en bloque las FAQ (hundían `POL-GTH-01` §8,
que era el mejor vector de la consulta de vacaciones).
