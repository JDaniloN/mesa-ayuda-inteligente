# Estándar breve para revisar código generado por IA

Objetivo: usar IA para acelerar, sin delegarle la responsabilidad técnica al
autor ni mezclar evidencia real con afirmaciones del modelo.

## Antes de aceptar el cambio

1. **Definir alcance.** Indicar archivos permitidos, contrato que no debe
   romperse y datos que no pueden salir del equipo.
2. **Pedir cambios pequeños.** Una intención por diff; evitar refactor y
   funcionalidad en el mismo bloque.
3. **Verificar la fuente.** Toda API, dependencia, cita o regla de negocio debe
   existir en código, documentación oficial o datos entregados. «Lo dijo el
   modelo» no es evidencia.
4. **Buscar fallos seguros.** Revisar entradas vacías/adversariales, timeout,
   reintentos, concurrencia, falta de secretos, costo y mensajes de error.
5. **Revisar exposición.** Nunca registrar prompts, cuerpos, tokens Bearer,
   claves, correos ni respuestas privadas del proveedor.
6. **Exigir pruebas.** Añadir camino feliz, error controlado y regresión del
   defecto. Los dobles no deben llamar a servicios externos.

## Puerta mínima antes del commit

```bash
ruff check --select E9,F63,F7,F82 src tests
python -m pytest -q
git diff --check
```

El revisor humano debe leer el diff completo y poder explicar:

- qué problema resuelve;
- qué supuesto hizo la IA;
- cómo se comprobó;
- qué riesgo queda pendiente.

## Etiquetas de decisión

- **Aceptar:** contrato, seguridad y pruebas quedan claros.
- **Corregir:** la idea sirve, pero falta validación, prueba o manejo de error.
- **Rechazar:** inventa APIs/reglas, oculta fallos, expone datos o amplía el
  alcance sin justificación.

## Definición de terminado

Código y documentación coinciden; CI queda verde; no hay secretos ni artefactos
locales en Git; la declaración de uso de IA registra qué se conservó, qué se
corrigió y cómo se verificó.

## Qué no es este documento

No es una guía genérica de prompts ni un estándar de mensajes de commit. Si el
equipo necesita esos artefactos, se derivan de esta puerta: primero el diff
seguro y verificable; después el estilo del mensaje.
