# SIGO-ML — primer prototipo de predicción de ausencias

Microservicio de prueba para SIGO, independiente de Angular y Spring Boot. No modifica SIGO-BACK ni SIGO-TEST.

## Requisitos
- MacBook Air M1 (Python 3.11 o 3.12 recomendado)
- Terminal, VS Code o PyCharm

## Iniciar (macOS)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m training.generate_demo
python -m training.train --input data/dataset_demo.csv --demo
export SIGO_ML_INTERNAL_TOKEN="token-local-solo-pruebas"
uvicorn app.main:app --reload --port 8000
```
En otra terminal ejecuta el siguiente ejemplo de prueba local. En producción utiliza un secreto aleatorio largo, diferente del valor de demostración:
```bash
curl -X POST http://127.0.0.1:8000/internal/v1/asistencia/predecir \
  -H "Content-Type: application/json" \
  -H "X-Internal-Token: token-local-solo-pruebas" \
  -d '{"plazaId":4,"turnoId":2,"fecha":"2026-11-05","programados":18}'
```
**La respuesta estará marcada como DEMO: no utilizar para decisiones operativas.**

## Pruebas
```bash
pytest -q
```

## Datos de SIGO-TEST
1. Ejecutar `sql/exportar_asistencia.sql` en el SQL Editor de **SIGO-TEST**.
2. Exportar el resultado CSV y guardarlo localmente como `data/asistencia_real.csv`.
3. Revisar que el CSV no contenga nombres, IDs personales o información médica.
4. Ejecutar `python -m training.train --input data/asistencia_real.csv` (sin `--demo`).
5. Revisar el MAE de la línea base y del modelo; si no mejora, se conserva la línea base.

**Importante:** el conjunto actual de SIGO-TEST cubre pocos meses. Antes de usarlo en producción, verificar estabilidad por plaza/turno, conjuntos de prueba posteriores y errores de predicción. No aplicar decisiones automáticas a trabajadores.

## Producción
Este ZIP es un starter técnico, no un despliegue productivo. Falta integrar a SIGO-BACK, logging, autorización de permisos por plaza, historial/auditoría de predicciones, gestión segura de artefactos y monitoreo del modelo. No publicar esta API sin protección de red/TLS y autenticación entre servicios.


## Inventario (fase inicial)

Se incorporó una auditoría de series de consumo mensual, con pruebas en GitHub
Actions. **Todavía no se realiza pronóstico de inventario**: primero hay que
validar los movimientos y contar con suficiente historial cerrado.

Consulta [docs/INVENTARIO_FASE_1.md](docs/INVENTARIO_FASE_1.md).
