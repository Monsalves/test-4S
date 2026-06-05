# Especificación SDD: 4S (Four S) — Plataforma Web de Servicios de Oficio (4S — Four S)

## 1. Nombre del sistema
- **Nombre:** 4S (Four S) — Plataforma Web de Servicios de Oficio, Maestros y Coordinación de Trabajos
- **Dueño:** PO de Fábrica (Usuario)
- **Fecha:** 2026-05-29
- **ID de Proyecto:** PROYECTO_TRES
- **Estado:** `spec_validated`

## 2. Objetivo
- **Qué problema resuelve:** Desarrollar una aplicación web responsiva que conecte a clientes con maestros de oficios, permitiendo registrar perfiles, buscar y filtrar maestros, calificar servicios, y gestionar solicitudes de trabajo con estados claros.
- **Para quién:** Clientes que requieren servicios de oficios (gasfitería, carpintería, etc.) y Maestros de oficio.
- **Resultado esperado:** Una app web transaccional responsiva con backend en FastAPI, SQLite para persistencia local robusta, y frontend dinámico con React + Bootstrap.

## 3. Usuarios y roles
| Rol | Qué puede hacer | Restricciones |
|---|---|---|
| Cliente | Registrarse, buscar/filtrar maestros, enviar solicitudes de servicio, calificar maestros una vez completado el servicio. | No puede editar perfiles de maestros. |
| Maestro | Registrarse, completar perfil público (especialidad, precio, cobertura, descripción), ver solicitudes de servicio, aceptar/completar trabajos. | No puede calificar a otros maestros. |
| Administrador | Gestión total de la plataforma (ver auditoría, desactivar usuarios). | Rol de supervisión global. |

## 4. Flujos transaccionales
| Flujo | Actor | Entrada | Acción | Salida | Error esperado |
|---|---|---|---|---|---|
| Registro Usuario | Cliente/Maestro | Nombre, Email, Password, Tipo, Ciudad | Crea usuario en DB con estado 'activo' | ID de usuario | Email duplicado, contraseña vacía |
| Registro Perfil Maestro | Maestro | Descripción, Especialidades, Precio Hora, Cobertura | Crea/actualiza perfil público de maestro en DB | Perfil guardado | Precio hora negativo, descripción vacía |
| Solicitar Servicio | Cliente | ID Maestro, descripción del trabajo, categoría | Inserta solicitud en DB en estado 'pendiente' | Solicitud creada | Maestro no existe, descripción corta |
| Aceptar/Completar Servicio | Maestro | ID Solicitud, acción (aceptar/completar) | Transiciona estado atómicamente | Estado actualizado | Solicitud no encontrada |
| Calificar Servicio | Cliente | ID Solicitud, Puntuación (1-5), Comentario | Registra reseña, actualiza promedio de calificación del maestro | Calificación guardada | Solicitud no completada, calificación fuera de rango (1-5) |

## 5. Requisitos funcionales
- **REQ-001 (Registro y Perfiles):** Endpoints para registro de usuarios y configuración de perfiles públicos de maestros.
- **REQ-002 (Buscador y Catálogo):** Buscador interactivo de maestros con filtros por especialidad, precio hora y calificación mínima.
- **REQ-003 (Gestión de Solicitudes):** Flujo transaccional de trabajos (pendiente -> aceptado -> completado) controlado de forma atómica.
- **REQ-004 (Sistema de Calificaciones):** Evaluaciones de 1 a 5 estrellas con recálculo automático y en tiempo real del promedio del maestro.
- **REQ-005 (Frontend Glassmorphism):** Interfaz premium, interactiva y responsiva con React + Bootstrap.

## 6. Requisitos no funcionales
- **Transaccionalidad:** Uso de SQLite con transacciones atómicas y rollback ante excepciones.
- **Usabilidad:** Interfaz limpia con indicadores visuales de estado y alertas flotantes de éxito/error.
- **Mantenibilidad:** Separación clara entre modelos, esquemas, rutas y frontend.

## 7. Datos
- **Usuario:** id, nombre, email, password (hashed), tipo (cliente/maestro), estado, ciudad, creado_at.
- **PerfilMaestro:** maestro_id (FK), descripcion, especialidades (comma-separated), precio_hora, cobertura, rating_promedio, total_evaluaciones.
- **SolicitudServicio:** id, cliente_id (FK), maestro_id (FK), descripcion, categoria, estado (pendiente/aceptado/completado), creado_at, actualizado_at.
- **Evaluacion:** id, cliente_id (FK), maestro_id (FK), solicitud_id (FK), puntuacion (int), comentario, creado_at.

## 8. Base de datos candidata
- **Base:** SQLite (`db.sqlite3`)
- **Justificación:** Base integrada ideal para testing y portabilidad en el Sandbox de desarrollo.

## 9. API Endpoints
- `/api/users/register`: POST para registrar clientes y maestros.
- `/api/users/login`: POST para autenticación (simulada/simple).
- `/api/maestros`: GET (con filtros de especialidad, precio, rating).
- `/api/maestros/profile`: POST para guardar/editar perfil de maestro.
- `/api/services`: POST (crear solicitud), GET (listar por rol).
- `/api/services/<built-in function id>/status`: PUT para transiciones (aceptado, completado).
- `/api/evaluations`: POST para calificar servicio completado.

## 10. Frontend Pantallas
- **Marketplace / Buscador:** Catálogo de maestros con barra de filtros dinámica y tarjetas.
- **Perfil del Maestro:** Ficha con portafolio simulado, disponibilidad e historial de reseñas.
- **Panel de Control:** Tablero del cliente y maestro para dar seguimiento a los trabajos.
- **Simulador de Chat:** Canal de coordinación directo entre maestro y cliente.

## 11. Criterios de aceptación (AC)
- **AC-001 (Buscador):** Filtrado reactivo en el frontend por especialidad y precio referencial.
- **AC-002 (Solicitud):** Cliente puede iniciar solicitud de trabajo y el maestro la recibe en su panel.
- **AC-003 (Estados de Trabajo):** El flujo transita correctamente y bloquea calificaciones en trabajos no completados.
- **AC-004 (Calificación Promedio):** Registrar una calificación recalcula el rating_promedio del maestro de forma exacta.

## 12. Pruebas esperadas
- Tests unitarios y de API con Pytest validando registro, filtros de búsqueda, transiciones de estado de servicio y cálculo de ratings.