# Descripción funcional de la API

## Qué problema resuelve

Los colaboradores de LA FORTUNA necesitan registrar solicitudes internas con
información suficiente para que la mesa de ayuda pueda consultarlas y
priorizarlas. Clasificarlas manualmente retrasa el ingreso y produce etiquetas
inconsistentes.

La API ofrece un único punto para:

1. Recibir y validar una solicitud.
2. Proponer categoría y prioridad automáticamente.
3. Entregar un identificador para consultar el caso.
4. Permitir que la mesa liste y filtre la carga recibida.
5. Consultar políticas internas con respuesta citada o abstención explícita.

## Para quién

### Colaborador interno

Registra el problema y recibe un identificador `SOL-…`. Puede consultar el
registro después sin depender de que la clasificación automática haya estado
disponible.

### Agente de mesa de ayuda

Consulta solicitudes por identificador y filtra la bandeja por área, estado o
prioridad para revisar la carga más reciente.

### Aplicación interna

Una pantalla Angular u otra integración consume el contrato HTTP. No necesita
conocer OpenAI ni la lógica de clasificación. La implementación en `web/`
muestra la bandeja, aplica filtros y representa carga, vacío y fallos.

## Flujo principal

1. El colaborador informa asunto, descripción, área, identidad y canal.
2. La API rechaza datos incompletos antes de guardar.
3. El clasificador propone categoría y prioridad dentro del catálogo.
4. La solicitud se crea en estado `Abierto`.
5. La API responde `201` con identificador, clasificación y su origen.
6. La mesa puede consultarla o encontrarla en el listado.

## Consulta de políticas

Un agente o una integración pregunta en lenguaje natural. El servicio recupera
fragmentos de los PDF internos, genera una respuesta acotada a ese contexto y
devuelve citas verificables (documento, sección, título, página). Si no hay
evidencia suficiente, se abstiene con un mensaje fijo y sin citas: no improvisa
plazos ni artículos. El umbral `RAG_MIN_SCORE` (inicialmente 0.22) es
provisional y se calibra en el criterio de abstención.

## Continuidad cuando falla la IA

Registrar el caso es más importante que clasificarlo automáticamente. Si el
proveedor de IA no responde, la solicitud se crea igualmente con:

- Categoría: `Sin clasificar`.
- Prioridad: `Media`.
- Origen: `degradado`.

Esto permite que un agente la revise después. El sistema no presenta esa
clasificación como si proviniera del modelo.

## Reglas funcionales

- Un asunto debe tener al menos cinco caracteres.
- Una solicitud nueva comienza en estado `Abierto`.
- La categoría pertenece al catálogo cerrado del histórico.
- La prioridad es `Crítica`, `Alta`, `Media` o `Baja`.
- Una clave de idempotencia evita duplicar el mismo envío.
- Reutilizar esa clave con datos diferentes es un conflicto.
- Repetir la misma clave y los mismos datos reutiliza también la clasificación:
  no vuelve a consumir tiempo ni cuota del proveedor de IA.
- Un listado sin resultados es exitoso y devuelve una lista vacía.
- Los filtros actuales requieren coincidencia exacta.
- Cada respuesta entrega un identificador de seguimiento técnico
  `X-Request-ID`.
- Una consulta de políticas o bien cita fragmentos recuperados, o se abstiene;
  no mezcla fuentes inventadas.

## Escenarios esperados

### Registro correcto

El colaborador envía datos válidos, obtiene `201` y un identificador.

### Repetición por problema de red

La aplicación repite el POST con la misma `Idempotency-Key`. Obtiene `200` y
el mismo identificador; no se crea otro caso.

### Datos incompletos

La API devuelve `422` con un mensaje que identifica el incumplimiento.

### Solicitud inexistente

Consultar un identificador desconocido devuelve `404`.

### Proveedor de IA no disponible

La API crea la solicitud y marca `origen_clasificacion=degradado`.

### Filtro sin coincidencias

La bandeja devuelve `200` y `[]`; no se interpreta como ruta inexistente.

### Pregunta fuera de las políticas

`POST /politicas/consultar` con «¿Cuál es la capital de Japón?» se abstiene:
mensaje fijo, `citas: []`, sin llamada al generador.

## Beneficio esperado

- Menos trabajo manual al recibir casos.
- Etiquetas provenientes de un catálogo común.
- Continuidad operativa si el proveedor de IA falla.
- Menos duplicados causados por reintentos del cliente.
- Un contrato único para la interfaz y otras integraciones.
- Errores comprensibles y rastreables mediante `X-Request-ID`.

Estos beneficios son hipótesis funcionales. Su impacto deberá medirse con
datos reales antes de afirmar reducción de tiempos o aumento de precisión.

## Qué no resuelve todavía

- Persistencia: reiniciar el proceso borra los registros.
- Cambio de estado, asignación a agentes o cierre del ticket.
- Autenticación individual y permisos por rol.
- Notificaciones, correo o webhook de mensajería.
- Búsqueda parcial, paginación por cursor o reportes.
- Revisión humana asistida de los casos degradados.
- Integración con el sistema corporativo de tickets.
- Calibración de `RAG_MIN_SCORE` con un conjunto gold y métricas de retrieval.

Estas exclusiones evitan confundir la demostración técnica con un producto
listo para producción.

## Criterios de aceptación funcional

- Crear una solicitud válida devuelve un `SOL-…`.
- Consultar ese identificador devuelve la misma solicitud.
- Los filtros devuelven únicamente coincidencias exactas.
- Repetir una clave con el mismo cuerpo no duplica.
- Repetirla con otro cuerpo genera conflicto.
- Una entrada inválida conserva el formato uniforme de error.
- La caída del proveedor no impide registrar el caso.
- Ninguna respuesta o log expone credenciales.
- Una pregunta cubierta por las políticas cita documento y sección.
- Una pregunta fuera de dominio se abstiene y no inventa citas.
