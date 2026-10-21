-- SOLO LECTURA. Ejecuta este SELECT en SIGO-TEST; descarga el resultado como CSV.
-- No exporta nombres, documentos, motivos médicos ni IDs de trabajadores.
-- Mantén el CSV privado; no lo agregues al repositorio Git.
SELECT
    ar.fecha,
    ar.plaza_id,
    ar.turno_id,
    ar.programados,
    (ar.programados - ar.presentes) AS ausentes
FROM public.asistencia_registro ar
WHERE ar.fecha <= CURRENT_DATE
  AND ar.programados >= ar.presentes
  AND ar.programados >= 0
ORDER BY ar.fecha, ar.plaza_id, ar.turno_id;
