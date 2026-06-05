# Plan de Despliegue (Deployment Plan)

- **Entorno Objetivo:** `Staging` -> `Production`
- **Método:** Monolito servido por Uvicorn y base de datos SQLite persistida como volumen de Docker o archivo físico local.

## Pasos Operativos
1. Levantar el servidor de FastAPI en puerto 8000:
   `uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Copiar index.html de frontend al directorio de servicio estático (Nginx o bypass local).
3. Ejecutar Smoke Tests en la ruta del API.