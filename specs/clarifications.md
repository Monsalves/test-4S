# Aclaraciones de Requisitos (4S — Four S)

## 1. Supuestos asumidos
- **PERSISTENCIA:** Se utiliza una base de datos SQLite (`db.sqlite3`) para asegurar la máxima portabilidad, atomicidad y facilidad de ejecución local en Sandbox y entornos locales.
- **ESTADO INICIAL DE SOLICITUD:** Comienza siempre en estado `pendiente`.
- **RATING INICIAL:** Un maestro recién creado tiene calificación promedio 0.0 y total de calificaciones 0.
- **CALIFICACIÓN:** Un cliente solo puede calificar un servicio si el estado del servicio asociado es `completado`.

## 2. Decisiones de diseño
- Las especialidades de los maestros se almacenan en la base de datos como una cadena delimitada por comas (ej. "electricidad, gasfiteria") para agilizar el motor de búsqueda en SQLite.
- El chat se implementa mediante un simulador reactivo en el frontend para evitar las dependencias complejas de WebSockets en la suite inicial de pruebas locales.