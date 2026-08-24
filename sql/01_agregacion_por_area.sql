-- Agregación por área.
-- Parte de areas (LEFT JOIN) para no ocultar un área sin tickets.
-- Abiertos = todo lo que no está Cerrado (En proceso, Escalado, Reabierto, Abierto).

SELECT
  a.nombre AS area,
  a.sede,
  COUNT(t.id_ticket) AS tickets,
  SUM(CASE WHEN t.estado <> 'Cerrado' THEN 1 ELSE 0 END) AS no_cerrados,
  ROUND(AVG(t.reaperturas), 2) AS reaperturas_promedio
FROM areas a
LEFT JOIN tickets t ON t.id_area = a.id_area
GROUP BY a.id_area, a.nombre, a.sede
ORDER BY tickets DESC, a.nombre;
