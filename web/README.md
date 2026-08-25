# Pantalla Angular de solicitudes

Cliente opcional de la etapa 2. Consume `GET /solicitudes`, aplica filtros
exactos y muestra los estados de carga, vacío y error.

## Ejecutar

Con la API en `http://127.0.0.1:8000`:

```powershell
cd web
npm ci
npm start
```

Abrir `http://localhost:4200`. El proxy reenvía `/api/*` a la API local y no
contiene credenciales.

## Token

La pantalla solicita el `API_TOKEN` local y lo mantiene exclusivamente en un
servicio en memoria:

- no se compila en `environment.ts`;
- no se guarda en `localStorage`, `sessionStorage`, cookies ni URL;
- no se imprime;
- solo se adjunta a rutas relativas `/api/`;
- se elimina al recibir 401, al pulsar “Eliminar token”, al destruir el
  componente o al recargar.

El campo empieza como `password`; “Mostrar” revela únicamente el valor que el
usuario está escribiendo y “Ocultar” lo protege otra vez. Al pulsar “Validar y
consultar”, la pantalla limpia el campo, hace una consulta protegida y solo
muestra “Token autenticado” después de recibir 200. Un 401 elimina el valor.
El formulario cancela explícitamente el envío HTML y el campo no tiene atributo
`name`, defensa doble para que el navegador no serialice el token en la URL.

Esta es una decisión de demostración, no autenticación productiva. Un frontend
no puede ocultar permanentemente una credencial; producción requiere identidad
corporativa, HTTPS y tokens personales de corta duración.

## Verificar

```powershell
npm test -- --watch=false
npm run build
```

Las pruebas fijan que el token no se persiste ni se envía a dominios externos,
que los filtros generan la consulta correcta y que 401 elimina la credencial
de memoria.
