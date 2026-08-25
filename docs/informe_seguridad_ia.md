# Informe de seguridad del código asistido por IA

**Fecha:** 2026-08-25  
**Alcance:** RAG de políticas, clientes OpenAI-compatibles y dependencias nuevas.

La revisión se concentró en riesgos introducidos por código generado o
modificado con asistencia de IA. No se encontraron claves embebidas: la API
conserva Bearer, comparación constante y `SecretStr`. Se corrigieron los
siguientes hallazgos antes de cerrar la fase 2.

## Hallazgos y correcciones

### 1. Inyección de instrucciones en la pregunta — Alta

**Evidencia.** `src/rag/generador.py` concatenaba directamente la pregunta
después de `Pregunta:` y usaba marcadores `[N]` para los fragmentos. Un usuario
podía escribir otro marcador y simular contexto autorizado.

**Corrección aplicada.** Pregunta y fragmentos ahora viajan como campos de un
objeto JSON rotulado `DATOS_NO_CONFIABLES_JSON`; el mensaje de sistema ordena
tratar ambos campos como datos y nunca ejecutar instrucciones incluidas en
ellos. `tests/rag/test_generador.py` envía un marcador `[99]` adversarial y
comprueba que permanece dentro de `pregunta_usuario`, separado de los
fragmentos recuperados.

### 2. Exposición de información operativa del proveedor — Media

**Evidencia.** Los errores de embeddings/generación incluían el código HTTP
del proveedor y `src/api/rutas_politicas.py` copiaba el mensaje interno al
cuerpo 503. Un cliente autenticado podía distinguir clave rechazada, cuota o
fallo del proxy.

**Corrección aplicada.** La API responde el mensaje genérico «El servicio de
consulta de políticas no está disponible». El código interno y el tipo de
operación quedan únicamente en logs estructurados, sin cuerpo ni credencial.
`tests/api/test_politicas.py::test_error_rag_no_expone_detalle_del_proveedor`
demuestra que un detalle privado con `HTTP 401` no aparece en la respuesta.

### 3. Recuperación vectorial sin límite fijo — Media

**Evidencia.** `Retriever._rankear` solicitaba tantos candidatos como
fragmentos existieran en Chroma. El costo por petición crecía linealmente con
el índice y se multiplicaba en preguntas compuestas.

**Corrección aplicada.** `MAX_CANDIDATOS = 200` limita cada búsqueda, mientras
que `limite` continúa acotando la respuesta. La prueba
`test_pool_vectorial_tiene_tope_fijo` simula 10.000 fragmentos y comprueba que
solo se solicitan 200 candidatos. Este control reduce amplificación; no
reemplaza un rate limit de infraestructura.

### 4. Dependencias RAG flotantes — Media

**Evidencia.** `pdfplumber` y `chromadb` no tenían versión, por lo que dos
instalaciones podían resolver código distinto.

**Corrección aplicada.** `requirements.txt` fija las versiones probadas
`pdfplumber==0.11.10` y `chromadb==1.5.9`; el analizador de CI queda fijado en
`requirements-dev.txt`.

## Riesgo residual

Las expansiones de cláusulas son contexto deliberado y conservan metadatos
reales, pero no tienen score vectorial propio. También falta rate limiting por
token/IP y escaneo automatizado de CVE. Son mejoras de defensa en profundidad,
no bloqueos para la demo interna autenticada.

## Alternativas descartadas

- WAF o rate limit de infraestructura: fuera del alcance de la demo local.
- Escaneo CVE continuo en CI: añade ruido sin pin previo de dependencias.
- Citar solo hits `direct`: se conservó la expansión porque las preguntas
  compuestas (p. ej. hurto §5.1/§5.2) la necesitan; el residual queda
  declarado arriba.
