# Declaración de uso de asistentes de IA

Nivel objetivo: Ingeniero IA Middle II.

Una tabla de cinco preguntas por etapa. Declarar el uso no resta; ocultarlo anula el proceso.

## Etapa 0 — Contextualización

Validé y entendí el problema y el reto antes de desarrollar.


| Pregunta                                        | Respuesta                                                                                                                                                                                                                                                                                                                         |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ¿Qué herramientas usaste y para qué?            | Usé Cursor en el IDE como apoyo para extraer el texto del Anexo A y organizar la lectura frente a `materiales/README_PARTICIPANTE.md`, las políticas, el CSV, `esquema.sql`, el mock, `legacy_module.py` y los requerimientos N5. Me apoyé en la misma herramienta para ordenar la guía de proceso y el borrador de este archivo. |
| ¿Qué generaste y conservaste tal cual?          | Conservé el formato oficial de las cinco preguntas del numeral 6 del Anexo A y el mapa de etapas, pesos, reglas de acreditación y doce puntos críticos tal como los define el enunciado. No inventé criterios extra.                                                                                                              |
| ¿Qué generaste, tuviste que corregir y por qué? | Se genero la base del archivo "Declaracion uso IA", tuve que corregir el objetivo y el enfoque ya que la idea es generar la base para que de fomra manual yo pueda ingresar lo que se uso en cada etapa                                                                                                                           |
| ¿Qué decidiste escribir a mano y por qué?       | Por ahora escribir a mano la declaracion de uso de IA para hacer un seguimiento mas preciso y mantener un orden de desarrollo, es decir, lo que se va a desarrollar, lo que se esta desarrollando y lo que se desarrollo                                                                                                          |
| ¿Cómo verificaste lo generado?                  | Leí el Anexo A completo (8 páginas) y el contenido de la carpeta materiales para verificar que he tomado en cuenta TODOS los criterios, requisitos y etapas para completar la entrega con el objetivo planteado.                                                                                                                  |




## Etapa 1 — Fundamentos

Implementé la limpieza del CSV, el cliente del mock y las tres consultas SQL.


| Pregunta                                        | Respuesta                                                                                                                                                                                                                                                                                                                         |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ¿Qué herramientas usaste y para qué?            | Usé Cursor en el IDE como apoyo para armar `src/datos/limpiar.py`, el cliente de `src/integraciones/`, las tres consultas de `sql/` y las pruebas de `tests/datos/`, `tests/integraciones/` y `tests/sql/`. Me apoyé en la misma herramienta para contrastar el enunciado con el CSV, `esquema.sql` y el mock sin modificar `materiales/`. |
| ¿Qué generaste y conservaste tal cual?          | Conservé la separación en tres scripts SQL (agregación, join de tres tablas y reabiertos), el contrato de salida limpio / rechazados / resumen, y el cliente HTTP con GET y POST sobre el mock. No inventé un motor MySQL ni toqué `tickets_historicos.csv`, `esquema.sql` ni `servicio_mock/`.                                                                                                              |
| ¿Qué generaste, tuviste que corregir y por qué? | Se genero una primera limpieza que unía fechas con un parser genérico y categorías por “parecido”. Tuve que corregir fechas a reglas explícitas de los tres formatos del material, no unir Acceso/Accesos, dejar `reaperturas` vacía sin poner 0, y en SQL preguntar por el hecho (`reaperturas > 0`, 36 filas) y no por el estado de hoy (28). También corregí el timeout a 5 s porque el mock tarda hasta 2,5 s en una respuesta buena. |
| ¿Qué decidiste escribir a mano y por qué?       |                      |
| ¿Cómo verificaste lo generado?                  |                      |




## Etapa 2 — Autonomía e integración

Implementé la API propia, el clasificador de IA, las correcciones del legado, la configuración y la pantalla Angular opcional.


| Pregunta                                        | Respuesta                                                                                                                                                                                                                                                                                                                         |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ¿Qué herramientas usaste y para qué?            | Usé Cursor en el IDE como apoyo para implementar `src/api/`, el puerto de clasificación en `src/ia/`, las correcciones puntuales de `src/legacy/`, `src/configuracion.py`, los logs JSON y la bandeja de `web/`. Me apoyé en la misma herramienta para dejar el contrato en `/docs` y los markdown `docs/api_contrato.md`, `docs/api_funcional.md` y `docs/legacy_causas.md`. |
| ¿Qué generaste y conservaste tal cual?          | Conservé FastAPI + Pydantic (mismo estilo que el mock), los tres recursos de solicitudes, el desacople `PuertoClasificador` para no pegar OpenAI en la ruta, las tres pruebas del legado que fallan antes y pasan después, y el token de Angular solo en memoria. No versioné secretos ni reescribí `materiales/legacy/legacy_module.py`.                                                                                                              |
| ¿Qué generaste, tuviste que corregir y por qué? | Se genero un POST que devolvía error de mesa cuando fallaba OpenAI y un listado 404 cuando no había filas. Tuve que corregir a 201 degradado (`Sin clasificar` / `Media`) y 200 `[]` en el filtro vacío, porque el 401 de OpenAI no es el Authorize de Swagger y un tablero vacío no es una ruta rota. También quité un regex de “vacaciones/urgente”, evité guardar el token en `environment.ts` y en S3 no usé `estado.lower()`: el indicador pide el hecho histórico, no la foto de hoy. |
| ¿Qué decidiste escribir a mano y por qué?       |                      |
| ¿Cómo verificaste lo generado?                  |                      |




## Etapa 3 — Complejidad y calidad

Implementé el RAG de políticas, la abstención, el CI, el informe de seguridad, las métricas y el estándar de revisión.


| Pregunta                                        | Respuesta                                                                                                                                                                                                                                                                                                                         |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ¿Qué herramientas usaste y para qué?            | Usé Cursor en el IDE como apoyo para implementar `src/rag/`, `POST /politicas/consultar`, el workflow `.github/workflows/ci.yml`, `docs/informe_seguridad_ia.md`, las métricas de latencia/tokens y `docs/estandar_revision_codigo_ia.md`. Usé Gemini Notebook para generar las 10 preguntas con las que probé el RAG (vacaciones, incidentes, hurto, comisión, accesos, contraseñas, hardware y acumulación). Usé ChatGPT como apoyo puntual para contrastar enfoques de esta etapa. |
| ¿Qué generaste y conservaste tal cual?          | Conservé las 10 preguntas salidas de Gemini Notebook y las bajé a `tests/rag/test_consultas_compuestas.py` sin reescribir el enunciado de cada una. Conservé Chroma local, citas solo de metadatos del retriever, el mensaje fijo de abstención y el pipeline que corre Ruff + pytest en cada envío. No alteré los PDF de `materiales/politicas/`.                                                                                                              |
| ¿Qué generaste, tuviste que corregir y por qué? | Se genero un RAG que concatenaba la pregunta en el prompt, recuperaba un solo bloque y no cubría preguntas de dos hechos. Tuve que corregir el generador para tratar pregunta y fragmentos como JSON no confiable, partir la pregunta en subconsultas, expandir cláusulas hermanas (por ejemplo hurto 5.1/5.2) y topar el pool vectorial en 200 candidatos. También corregí que el 503 no filtrara el HTTP del proveedor, fijé versiones de `pdfplumber` y `chromadb`, y dejé tres rankings como `xfail` porque el embedding fake de CI no reproduce el índice real. |
| ¿Qué decidiste escribir a mano y por qué?       |                      |
| ¿Cómo verificaste lo generado?                  |                      |




## Etapa 4 — Arquitectura y orquestación

Pendiente.


| Pregunta                                        | Respuesta |
| ----------------------------------------------- | --------- |
| ¿Qué herramientas usaste y para qué?            |           |
| ¿Qué generaste y conservaste tal cual?          |           |
| ¿Qué generaste, tuviste que corregir y por qué? |           |
| ¿Qué decidiste escribir a mano y por qué?       |           |
| ¿Cómo verificaste lo generado?                  |           |




## Etapa 5 — Estrategia técnica y evaluación

Pendiente.


| Pregunta                                        | Respuesta |
| ----------------------------------------------- | --------- |
| ¿Qué herramientas usaste y para qué?            |           |
| ¿Qué generaste y conservaste tal cual?          |           |
| ¿Qué generaste, tuviste que corregir y por qué? |           |
| ¿Qué decidiste escribir a mano y por qué?       |           |
| ¿Cómo verificaste lo generado?                  |           |


