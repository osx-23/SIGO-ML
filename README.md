# SIGO-ML — predicción de ausencias

Microservicio FastAPI de SIGO. No modifica datos oficiales en SIGO-TEST.
La integración experimental desde SIGO-BACK utiliza el token interno.

## Requisitos
- Python 3.11 o 3.12
- Dependencias: `pip install -r requirements.txt`
- Pruebas: `pytest -q`

## Entrenar con datos reales SIN exportación manual
Seguir [ENTRENAMIENTO_AUTOMATICO.md](docs/ENTRENAMIENTO_AUTOMATICO.md)
para crear un usuario PostgreSQL de solo lectura, configurar
`SIGO_ML_DATABASE_URL` en el entorno y ejecutar:

```bash
python -m training.retrain
```

Después de comprobar la conexión y las pruebas, activar
`SIGO_ML_AUTO_TRAIN_ENABLED=true` en el servidor para reentrenar al
arrancar y luego semanalmente. Las credenciales jamás van al repositorio.
El modelo nuevo solo reemplaza al anterior si mejora la evaluación de MAE
(o si reemplaza un artefacto DEMO).

## Iniciar API
```bash
export SIGO_ML_INTERNAL_TOKEN="usa-un-token-seguro-largo"
uvicorn app.main:app --reload --port 8000
```

Consultar `GET /health/ready` y hacer solicitudes autenticadas al endpoint
`POST /internal/v1/asistencia/predecir`.

## Entrenamiento manual alternativo (CSV)
Sigue existiendo `sql/exportar_asistencia.sql` como opción de respaldo.
`python -m training.train --input data/asistencia_real.csv`
El modelo conserva una comparación entre baseline y Random Forest.

Este repositorio es un prototipo, no una certificación de producción.
La automatización requiere conexión, volumen persistente opcional y
supervisión. No utilizar predicciones para sancionar trabajadores ni para
modificar automáticamente la programación.
