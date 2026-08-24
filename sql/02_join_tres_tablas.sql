-- Join de tres tablas: ticket + solicitante + área.
-- INNER JOIN: todo ticket del esquema tiene usuario y área (FK NOT NULL).
-- Alternativa descartada: tickets + adjuntos + historial; deja fuera
-- tickets sin archivo y no responde "quién pidió qué, de qué área".

SELECT
  t.codigo,
  t.asunto,
  t.estado,
  t.prioridad,
  t.fecha_creacion,
  u.nombre AS solicitante,
  u.correo,
  u.activo AS usuario_activo,
  a.nombre AS area,
  a.sede
FROM tickets t
INNER JOIN usuarios u ON u.id_usuario = t.id_usuario
INNER JOIN areas a ON a.id_area = t.id_area
ORDER BY t.fecha_creacion DESC, t.codigo;
