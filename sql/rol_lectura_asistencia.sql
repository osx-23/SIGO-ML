-- Plantilla para SIGO-TEST: ejecutar en SQL Editor SOLO cuando se haya
-- generado una contraseña fuerte. Nunca subir la contraseña real a Git.
-- Sustituir REEMPLAZAR_CON_CLAVE_SEGURA antes de ejecutar.
CREATE ROLE sigo_ml_reader WITH LOGIN PASSWORD 'REEMPLAZAR_CON_CLAVE_SEGURA'
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOINHERIT;
GRANT CONNECT ON DATABASE postgres TO sigo_ml_reader;
GRANT USAGE ON SCHEMA public TO sigo_ml_reader;
GRANT SELECT ON TABLE public.asistencia_registro TO sigo_ml_reader;
-- No conceder acceso a trabajadores, ausencias individuales ni escritura.
-- En pooler compartido, usuario: sigo_ml_reader.<ref-proyecto>.
