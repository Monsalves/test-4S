# Modelo de Datos (4S — Four S)

## 1. Entidades
- `Usuario`: Registro de clientes y maestros con email único y contraseña.
- `PerfilMaestro`: Información extendida para el rol de maestro.
- `SolicitudServicio`: Coordinación de trabajos y estados.
- `Evaluacion`: Valoración e historial de trabajos completados.

## 2. Campos
### Usuario
- `id` (INTEGER, PK, Auto)
- `nombre` (VARCHAR(150), required)
- `email` (VARCHAR(150), unique, required)
- `password` (VARCHAR(200), required)
- `tipo` (VARCHAR(20), required) -- cliente, maestro
- `estado` (VARCHAR(20), default "activo")
- `ciudad` (VARCHAR(100))
- `creado_at` (DATETIME)

### PerfilMaestro
- `maestro_id` (INTEGER, FK to Usuario, PK)
- `descripcion` (TEXT, required)
- `especialidades` (VARCHAR(250)) -- comma-separated
- `precio_hora` (FLOAT, default 0.0)
- `cobertura` (VARCHAR(100))
- `rating_promedio` (FLOAT, default 0.0)
- `total_evaluaciones` (INTEGER, default 0)

### SolicitudServicio
- `id` (INTEGER, PK, Auto)
- `cliente_id` (INTEGER, FK to Usuario)
- `maestro_id` (INTEGER, FK to Usuario)
- `descripcion` (TEXT, required)
- `categoria` (VARCHAR(100))
- `estado` (VARCHAR(20), default "pendiente") -- pendiente, aceptado, completado
- `creado_at` (DATETIME)
- `actualizado_at` (DATETIME)

### Evaluacion
- `id` (INTEGER, PK, Auto)
- `cliente_id` (INTEGER, FK to Usuario)
- `maestro_id` (INTEGER, FK to Usuario)
- `solicitud_id` (INTEGER, FK to SolicitudServicio)
- `puntuacion` (INTEGER, required) -- 1 a 5 estrellas
- `comentario` (TEXT, required)
- `creado_at` (DATETIME)

## 3. Comportamiento ante Fallo
- El registro de evaluaciones y recálculo de calificaciones debe ser transaccional atómico. Si la escritura falla, se revierte todo a su estado previo.