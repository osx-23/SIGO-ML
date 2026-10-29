# SIGO-ML: lectura directa y reentrenamiento seguro

## Alcance
SIGO-ML consulta solo fecha, plaza, turno, programados y ausentes agregados de
`public.asistencia_registro`. No carga nombres, IDs de trabajadores ni motivos.
Se mantienen los endpoints actuales de predicción. Ninguna predicción escribe en Supabase.

## Primer uso (SIGO-TEST)
1. Crear un usuario PostgreSQL con permiso SELECT **solamente** en
   `public.asistencia_registro` (plantilla `sql/rol_lectura_asistencia.sql`).
   Genera una contraseña fuerte y sustituye el marcador antes de ejecutarla
   mediante el SQL Editor. No publiques ni la contraseña ni la URI de conexión.
2. En local o Railway, configurar `SIGO_ML_DATABASE_URL` con la URI
   PostgreSQL del usuario de lectura. Copia el host y puerto desde **Connect**
   en el proyecto SIGO-TEST. Para pooler compartido: usuario
   `sigo_ml_reader.<ref>`. Usa TLS (por defecto `verify-full`; si el pooler
   no ofrece un certificado verificable, investigar antes de reducir la validación).
3. Ejecutar `python -m training.retrain`. El comando **no requiere exportar CSV**.
   Utiliza CSV temporal privado que se elimina al finalizar.
4. Comprobar que `GET /health/ready` devuelve `ready` al iniciar el servidor,
   y ejecutar `pytest -q` sin credenciales.

## Entrenamiento automático
Con `SIGO_ML_AUTO_TRAIN_ENABLED=true` el servidor ejecuta un entrenamiento
al arrancar y luego cada 7 días mientras esté encendido. Si un entrenamiento
falla, permanece el modelo anterior (si lo hay). Si ya existe un modelo real,
el nuevo se publica solo cuando disminuye el MAE en el conjunto de validación.
El modelo de demostración siempre puede reemplazarse por uno real válido.

Se publica con reemplazo atómico de `SIGO_ML_MODEL_PATH` y se limpia la caché
del predictor en el mismo proceso. `Dockerfile` utiliza un solo worker.
El almacenamiento de los contenedores puede ser efímero: tras cada reinicio
SIGO-ML vuelve a entrenar si la base está disponible; para conservar un
modelo previo durante cortes de Supabase, configurar un volumen persistente.

**Importante:** la comparación contra el modelo anterior en datos históricos
es un control preliminar, no prueba suficiente de mejoría en producción.
Validar por plaza/turno y monitorizar deriva y precisión temporal antes de
usar las predicciones para tomar decisiones operativas.

No habilitar el proceso en varias réplicas sin coordinación entre ellas.
Este paso **no** habilita por sí mismo `SIGO_ML_ENABLED` en SIGO-BACK ni
implementa todavía la proyección mensual en SIGO-FRONT.
