# Plan de Rollback (Rollback Plan)

En caso de fallo crítico en despliegue:
1. Detener el proceso del servidor Uvicorn de inmediato.
2. Revertir base de datos `db.sqlite3` a la última copia de seguridad automática (tomada previo a migración).
3. Levantar la versión de software anterior (commit de git anterior o patch previo).