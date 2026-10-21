-- SIGO-ML: exportar únicamente valores agregados de consumo.
-- La vista se crea en la migración de pedidos mensuales de SIGO-BACK.
-- No exportar identificadores de trabajadores ni datos personales.
-- ATENCIÓN: el mes en curso puede estar incompleto.
-- La auditoría de Python lo excluirá del historial cerrado.

SELECT
  plaza_id,
  producto_id,
  periodo,
  consumo
FROM public.v_inventario_consumo_mensual
WHERE periodo <= DATE_TRUNC('month', CURRENT_DATE)::date
ORDER BY plaza_id, producto_id, periodo;
