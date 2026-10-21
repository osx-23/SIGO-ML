# SIGO-ML: Inventario, fase 1 (auditoría de historial)

Esta fase valida la calidad y cobertura temporal de los datos que podrían
servir para predecir **consumo mensual agregado por plaza y producto**.
**No se genera un modelo ni un endpoint de predicción todavía.**

## Fuente de datos

La vista `v_inventario_consumo_mensual` en SIGO-TEST calcula:

`consumo = max(0, stock_anterior + entradas_entre_conteos - stock_observado)`

Su cálculo solo es posible cuando hay **dos conteos finalizados consecutivos**
para la misma plaza y producto. La vista agrupa por mes de finalización del
conteo posterior. Por tanto, NO mide necesariamente el consumo de todo un mes
calendario si el intervalo entre conteos cruza meses; es un proxy.
Antes de utilizarlo para pronósticos habrá que resolver la atribución de
consumo a intervalos y meses, además de registrar recepciones y salidas.

## Exportación segura

1. Ejecutar `sql/exportar_consumo_inventario.sql` en SIGO-TEST, sin permisos de escritura.
2. Descargar únicamente columnas `plaza_id,producto_id,periodo,consumo`.
3. Guardar localmente el CSV como `data/consumo_inventario_real.csv`.
4. Nunca subir CSV reales ni credenciales: `.gitignore` excluye `data/*.csv`.
5. Analizar con:

```bash
python -m training.auditar_inventario --input data/consumo_inventario_real.csv
```

Si el CSV está vacío, se puede crear con los encabezados de la consulta.

## Interpretación

- Periodos del mes actual y futuros se excluyen de la evaluación de historial cerrado.
- Menos de 6 meses cerrados: `historial_insuficiente`.
- Con 6 meses cerrados y al menos una serie plaza-producto de 6 meses:
  `datos_para_evaluacion_inicial`. Esto **no** habilita uso productivo.
- No interpolar faltantes como consumo 0 sin comprobar si hubo conteo.
- No inferir ventas reales o demanda a partir de simples cambios en el stock.
- No emitir un requerimiento automático ni calcular MAE hasta tener un
  esquema de evaluación temporal y suficiente historial.

## Pruebas sintéticas en GitHub Actions

```bash
python -m training.generate_demo_inventory
python -m training.auditar_inventario --input data/dataset_inventario_demo.csv --fecha-corte 2026-10-21
pytest -q
```

El próximo paso será validar la fuente real (conteos, entradas y salidas),
preparar una serie mensual interpretable, establecer un baseline y medir
error contra periodos posteriores sin fuga temporal.
