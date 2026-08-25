# Contrato técnico de la API

Contrato de la API interna de Mesa de Ayuda Inteligente, versión `0.2.0`.
OpenAPI es la fuente ejecutable del contrato:

- Swagger UI: `http://127.0.0.1:8000/docs`
- Esquema: `http://127.0.0.1:8000/openapi.json`
- Arranque local: `python -m src.api`

No se versiona una copia estática de `openapi.json`: quedaría desactualizada.
`tests/api/test_contrato_openapi.py` fija rutas, códigos, esquemas y cabeceras.

## Convenciones

- URL base local: `http://127.0.0.1:8000`.
- Cuerpos: JSON UTF-8.
- Fechas: ISO 8601 en UTC.
- Identificadores: prefijo `SOL-`.
- Todas las respuestas llevan `X-Request-ID` con un UUID para correlacionar
  la respuesta con los logs JSON.
- Las rutas de solicitudes requieren Bearer. `/health` es público.

## Autenticación

Las rutas bajo `/solicitudes` esperan:

```http
Authorization: Bearer <API_TOKEN>
```

`API_TOKEN` se obtiene del entorno y no se versiona. Este mecanismo protege la
demo, pero no identifica usuarios ni implementa permisos por rol; debe
reemplazarse por el sistema corporativo antes de producción.

Respuestas posibles:

- `401 no_autorizado`: cabecera ausente o token rechazado.
- `503 configuracion`: el servicio arrancó sin `API_TOKEN`.

## Error uniforme

Los errores controlados e inesperados conservan la misma forma:

```json
{
  "error": {
    "codigo": "no_encontrado",
    "mensaje": "No se encontró la solicitud."
  }
}
```

El mensaje es comprensible y no contiene credenciales, cuerpos del proveedor
ni trazas internas. El `X-Request-ID` permite buscar el evento correspondiente.

## Modelo de entrada

`SolicitudEntrada`:

- `asunto`: obligatorio, 5–200 caracteres.
- `descripcion`: opcional, máximo 4000; valor predeterminado `""`.
- `area`: obligatoria, 2–80 caracteres.
- `solicitante`: obligatorio, 5–120 caracteres.
- `canal`: opcional, máximo 30; valor predeterminado `"api"`.

Categoría, prioridad, estado, fecha y origen de clasificación no son aceptados
desde el cliente: los asigna el servicio.

Ejemplo:

```json
{
  "asunto": "No puedo ingresar al correo corporativo",
  "descripcion": "El acceso falla desde esta mañana.",
  "area": "Aplicaciones",
  "solicitante": "persona@lafortuna.com.co",
  "canal": "api"
}
```

## Modelo de salida

`SolicitudSalida` agrega:

- `id`: identificador generado.
- `estado`: `Abierto`.
- `fecha_creacion`: fecha UTC.
- `categoria`: etiqueta del catálogo cerrado.
- `prioridad`: `Crítica`, `Alta`, `Media` o `Baja`.
- `origen_clasificacion`: `proveedor` o `degradado`.

La API actual no incluye una operación para cambiar el estado; por eso una
solicitud creada permanece `Abierto` mientras viva este almacenamiento.

## Crear una solicitud

```http
POST /solicitudes
```

Cabecera opcional:

```http
Idempotency-Key: <clave estable del cliente>
```

Flujo: validar → serializar la clave → recuperar si ya existe → estructurar
contexto → clasificar → guardar → responder. Peticiones con claves distintas
no se bloquean entre sí.

Respuestas:

- `201`: solicitud nueva.
- `200`: la misma clave y el mismo cuerpo ya existían; devuelve la solicitud
  anterior sin duplicarla ni volver a invocar el proveedor de IA.
- `401`: Bearer ausente o rechazado.
- `409`: la clave ya fue usada con un cuerpo diferente.
- `422`: cuerpo fuera del contrato.
- `500`: fallo inesperado.
- `503`: falta `API_TOKEN`.

La clave y su bloqueo viven en memoria y se pierden al reiniciar. La
serialización por clave también evita dos clasificaciones simultáneas para el
mismo reintento; el repositorio verifica de nuevo bajo su candado antes de
insertar.

## Consultar una solicitud

```http
GET /solicitudes/{id_solicitud}
```

Respuestas:

- `200`: solicitud encontrada.
- `401`: Bearer ausente o rechazado.
- `404`: el identificador no existe.
- `500`: fallo inesperado.
- `503`: falta `API_TOKEN`.

## Listar solicitudes

```http
GET /solicitudes
```

Parámetros opcionales:

- `area`: coincidencia exacta y sensible a mayúsculas.
- `estado`: coincidencia exacta y sensible a mayúsculas.
- `prioridad`: coincidencia exacta (`Crítica`, `Alta`, `Media`, `Baja`).
- `limite`: 1–200; valor predeterminado 50.

El resultado se ordena por fecha de creación descendente. Cero coincidencias
es una consulta válida: responde `200` con `[]`, no `404`.

## Estado del servicio

```http
GET /health
```

No requiere Bearer.

```json
{
  "estado": "operativo",
  "hora": "2026-08-25T07:32:49.300040Z",
  "clasificador": "proveedor"
}
```

`clasificador=proveedor` solo confirma que había URL y clave al arrancar; no
prueba saldo, conectividad ni disponibilidad de OpenAI. Si no había clave
aparece `sin_clave`.

## Proveedor de IA y degradación

El POST envía asunto y descripción como campos JSON separados. El prompt trata
esos campos como datos no confiables, rechaza instrucciones incluidas dentro
del ticket, incorpora la matriz de prioridad de `POL-TIC-05`, aporta ejemplos
y exige abstención cuando no hay evidencia suficiente.

El clasificador reintenta una vez solo ante errores potencialmente transitorios
(timeout, conexión, 408, 425, 429 y 5xx seleccionados). Un 401, JSON inválido o
etiqueta fuera de catálogo degrada inmediatamente: repetir el mismo contenido
no corregiría la causa. Si no hay clave o el proveedor no entrega una salida
válida, la solicitud se crea igualmente:

```json
{
  "categoria": "Sin clasificar",
  "prioridad": "Media",
  "origen_clasificacion": "degradado"
}
```

Un fallo del proveedor no se traduce en `502`: impediría registrar el ticket.
No se fuerza `response_format` porque algunos proveedores compatibles no lo
implementan; el parser y la validación contra el catálogo cierran el contrato.

## Configuración y operación

La precedencia es proceso → `.env` → valores predeterminados. Variables
principales:

- `API_TOKEN`, `API_HOST`, `API_PORT`.
- `IA_API_BASE_URL`, `IA_API_KEY`, `IA_MODEL`.
- `IA_TIMEOUT`, `IA_REINTENTOS`.
- `APP_ENV`, `LOG_LEVEL`.

Los eventos propios se escriben como JSON a stdout. No se registran
`Authorization`, claves, asunto, descripción ni solicitante.

## Límites y decisiones

- Persistencia en memoria: reiniciar borra solicitudes e idempotencia.
- Un solo Bearer compartido: no sustituye autenticación corporativa.
- Filtros exactos: no hay búsqueda parcial ni normalización.
- Límite simple: no hay cursor ni total de páginas.
- Sin prefijo `/v1`: se mantiene el contrato de la prueba. Una ruptura futura
  deberá introducir una ruta versionada.
- CORS habilitado únicamente para Angular local, sin cookies, con métodos
  `GET`/`POST` y las cabeceras `Authorization`, `Content-Type` e
  `Idempotency-Key`.

Estas limitaciones son explícitas; no se presentan como capacidades
productivas.
