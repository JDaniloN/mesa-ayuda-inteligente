-- Tickets que se reabrieron al menos una vez.
-- El conjunto es reaperturas > 0 (ocurrió una reapertura), no el estado
-- actual. El historial va en LEFT JOIN: si no hay paso a Reabierto
-- (dato incompleto), el ticket igual sale y ultima_reapertura queda vacía.

SELECT
  t.codigo,
  t.estado,
  t.prioridad,
  t.reaperturas,
  t.fecha_creacion,
  t.fecha_cierre,
  a.nombre AS area,
  MAX(h.fecha_cambio) AS ultima_reapertura
FROM tickets t
INNER JOIN areas a ON a.id_area = t.id_area
LEFT JOIN historial_estado h
  ON h.id_ticket = t.id_ticket
 AND h.estado_nuevo = 'Reabierto'
WHERE t.reaperturas > 0
GROUP BY
  t.id_ticket,
  t.codigo,
  t.estado,
  t.prioridad,
  t.reaperturas,
  t.fecha_creacion,
  t.fecha_cierre,
  a.nombre
ORDER BY t.reaperturas DESC, ultima_reapertura DESC;
