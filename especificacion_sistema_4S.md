# Especificación del sistema web: 4S — Four S

## 1. Nombre del sistema

**4S (Four S) — Plataforma Web de Servicios de Oficio, Maestros y Coordinación de Trabajos**

---

## 2. Objetivo general

Desarrollar una aplicación web responsiva que conecte a clientes con maestros de oficios (jardinería, carpintería, electricidad, gasfitería, pintura, entre otros), permitiendo buscar, calificar, contactar y coordinar trabajos de manera ágil y confiable.

El sistema debe permitir:

- Registrar maestros con perfil completo, portafolio, disponibilidad y zona de cobertura.
- Buscar y filtrar maestros por categoría, ubicación, precio referencial y calificación.
- Calificar maestros mediante un sistema de puntuación y comentarios luego de contratar.
- Coordinar citas y contacto mediante un chat interno entre cliente y maestro.
- Gestionar solicitudes de servicio con estados claros y trazabilidad.
- Administrar categorías de oficios y configuraciones generales de la plataforma.
- Operar desde escritorio, tablet y móvil mediante interfaz responsiva.
- Guardar información en base de datos **MySQL o MariaDB**.

Este sistema está pensado para una fábrica de agentes de IA que deba construir software web transaccional, modular, validable, documentado y fácil de mantener.

---

## 3. Alcance del sistema

El sistema será una aplicación web multiusuario para gestión de servicios de oficio.

Debe incluir:

- Backend web con API REST.
- Base de datos MySQL o MariaDB.
- Frontend web responsivo con React + Bootstrap.
- Autenticación, roles y permisos.
- Registro y gestión de perfiles de maestros.
- Registro y gestión de perfiles de clientes.
- Buscador con filtros avanzados de maestros.
- Sistema de calificaciones y reseñas.
- Chat interno entre cliente y maestro.
- Gestión de solicitudes y citas de servicio.
- Dashboard según rol de usuario.
- Notificaciones internas.
- Auditoría de acciones críticas.
- Estructura clara de archivos.
- Documentación de instalación, ejecución y pruebas.

No se incluyen en esta primera versión:

- Pasarela de pago integrada (el pago se acuerda entre cliente y maestro externamente).
- Aplicación móvil nativa.
- Integración con organismos tributarios o facturación electrónica.
- Geolocalización en tiempo real por GPS.
- Inteligencia artificial predictiva avanzada.
- Verificación de identidad biométrica de maestros.

---

## 4. Tipo de aplicación

Aplicación web transaccional multiusuario.

El sistema puede ejecutarse localmente o en un servidor privado usando backend, frontend y base de datos separados.

Tecnologías sugeridas:

- Backend: Python 3 con FastAPI.
- Base de datos: MySQL o MariaDB.
- ORM: SQLAlchemy.
- Migraciones: Alembic.
- Frontend: React + Bootstrap.
- Cliente HTTP: Axios o Fetch API.
- Autenticación: JWT.
- WebSocket para chat en tiempo real.
- Documentación API: Swagger/OpenAPI automático de FastAPI.

Arquitectura mínima:

```text
frontend-react-bootstrap/
backend-fastapi/
database-mysql-mariadb/
docs/
tests/
```

---

# 5. Funcionalidades principales

## 5.1 Autenticación y usuarios

El sistema debe permitir acceso seguro por usuario y contraseña.

Campos mínimos de usuario:

- ID.
- Nombre completo.
- Email.
- Contraseña encriptada.
- Tipo de usuario: cliente o maestro.
- Estado: activo, inactivo, suspendido.
- Foto de perfil opcional.
- Fecha de creación.
- Fecha de actualización.

Roles mínimos:

- Cliente.
- Maestro.
- Administrador de la plataforma.

Reglas:

- El email debe ser único.
- La contraseña no debe almacenarse en texto plano.
- Un usuario inactivo o suspendido no puede iniciar sesión.
- Cada acción crítica debe registrar usuario, fecha, entidad y acción.
- El tipo de usuario se define al momento del registro y no puede cambiarse sin intervención de administrador.

---

## 5.2 Registro de clientes

El sistema debe permitir que un usuario se registre como cliente.

Campos mínimos:

- Nombre completo.
- Email.
- Contraseña.
- Teléfono opcional.
- Ciudad o comuna.
- Foto de perfil opcional.

Reglas:

- El email es obligatorio y único.
- El nombre debe tener entre 3 y 100 caracteres.
- El teléfono debe tener formato válido si se informa.
- Un cliente recién registrado queda en estado activo.

---

## 5.3 Registro y perfil de maestro

El sistema debe permitir que un usuario se registre como maestro con perfil detallado.

Campos mínimos:

- Nombre completo.
- Email.
- Contraseña.
- Teléfono.
- Foto de perfil.
- Descripción personal o presentación.
- Categorías de servicio ofrecidas (una o más).
- Precio referencial por hora o por trabajo opcional.
- Zona geográfica de cobertura (región, ciudad, comuna).
- Disponibilidad horaria: días y franjas horarias disponibles.
- Portfolio de trabajos realizados: imágenes y descripción de trabajos anteriores.
- Estado: activo, inactivo, suspendido.
- Calificación promedio calculada automáticamente.
- Total de calificaciones recibidas.

Reglas:

- El email es obligatorio y único.
- El teléfono es obligatorio para maestros.
- Debe seleccionarse al menos una categoría de servicio.
- La descripción debe tener al menos 20 caracteres.
- El precio referencial no puede ser negativo si se informa.
- La calificación promedio se recalcula automáticamente al registrar nuevas evaluaciones.
- Un maestro suspendido no aparece en resultados de búsqueda.
- Un maestro puede subir hasta 10 imágenes al portfolio.

---

## 5.4 Portfolio de trabajos

El sistema debe permitir que el maestro muestre trabajos realizados anteriormente.

Campos mínimos por ítem de portfolio:

- Título del trabajo.
- Descripción del trabajo.
- Categoría de servicio.
- Imágenes (una o más).
- Fecha aproximada del trabajo.
- Estado: visible u oculto.

Reglas:

- El título es obligatorio y debe tener entre 5 y 100 caracteres.
- Al menos una imagen es obligatoria por ítem.
- El maestro puede activar u ocultar ítems del portfolio sin eliminarlos.
- Un ítem eliminado se desactiva físicamente solo si no tiene referencias en solicitudes.

---

## 5.5 Disponibilidad horaria del maestro

El sistema debe permitir que el maestro indique su disponibilidad semanal.

Campos mínimos:

- Día de la semana.
- Hora de inicio.
- Hora de término.
- Estado: disponible o no disponible.

Reglas:

- El maestro puede definir múltiples bloques horarios por día.
- La hora de término debe ser mayor que la hora de inicio.
- La disponibilidad es orientativa y no bloquea automáticamente el calendario.

---

## 5.6 Buscador y catálogo de maestros

El sistema debe permitir que los clientes busquen y descubran maestros.

Filtros mínimos disponibles:

- Categoría de servicio.
- Región, ciudad o comuna.
- Precio referencial (rango mínimo y máximo).
- Calificación mínima.
- Disponibilidad: días de la semana.
- Texto libre (búsqueda por nombre o descripción).

Campos mostrados en resultados de búsqueda:

- Foto de perfil.
- Nombre.
- Categorías de servicio.
- Zona de cobertura.
- Precio referencial.
- Calificación promedio.
- Número de evaluaciones.
- Estado de disponibilidad.

Reglas:

- Solo se muestran maestros activos en los resultados.
- Los resultados deben poder ordenarse por calificación, precio o recencia.
- Los resultados deben ser paginados.
- La búsqueda debe responder en tiempo razonable.
- Si no hay resultados, debe mostrarse un mensaje claro.

---

## 5.7 Perfil público del maestro

El sistema debe mostrar la página de perfil completo de un maestro.

El perfil público debe mostrar:

- Foto de perfil.
- Nombre completo.
- Descripción personal.
- Categorías de servicio.
- Zona geográfica de cobertura.
- Precio referencial.
- Disponibilidad semanal.
- Portfolio de trabajos visibles.
- Calificación promedio con estrellas.
- Total de evaluaciones.
- Listado de evaluaciones y comentarios de clientes.
- Botón para iniciar chat o solicitar servicio.

Reglas:

- El perfil solo es visible si el maestro está activo.
- El teléfono y email del maestro no se muestran públicamente antes de que el cliente envíe una solicitud.
- El botón de contacto requiere que el cliente esté autenticado.

---

## 5.8 Sistema de calificaciones y reseñas

El sistema debe permitir que los clientes califiquen y comenten sobre un maestro luego de un servicio.

Campos mínimos de una evaluación:

- Cliente que evalúa.
- Maestro evaluado.
- Solicitud de servicio asociada.
- Puntuación: valor del 1 al 5.
- Comentario textual obligatorio.
- Fecha de la evaluación.
- Estado: visible u oculto.

Reglas:

- Un cliente solo puede evaluar a un maestro una vez por solicitud de servicio completada.
- No se puede evaluar si la solicitud no está en estado completado.
- La calificación promedio del maestro se recalcula automáticamente.
- El administrador puede ocultar una evaluación con motivo justificado.
- El maestro no puede modificar ni eliminar las evaluaciones recibidas.
- El comentario debe tener entre 10 y 500 caracteres.

---

## 5.9 Chat interno entre cliente y maestro

El sistema debe permitir comunicación directa entre cliente y maestro mediante mensajería interna.

Campos mínimos de un mensaje:

- Remitente.
- Destinatario.
- Contenido del mensaje.
- Fecha y hora de envío.
- Estado de lectura: leído o no leído.

Reglas:

- El chat solo puede iniciarse si el cliente ha enviado una solicitud al maestro o si el maestro acepta el contacto.
- El historial de conversación debe mantenerse y ser visible para ambas partes.
- Los mensajes no deben poderse eliminar por los usuarios.
- El sistema debe mostrar indicador de mensajes no leídos.
- Se recomienda WebSocket para mensajería en tiempo real. Como alternativa se puede implementar polling controlado.
- Un usuario suspendido no puede enviar mensajes.

---

## 5.10 Solicitudes de servicio

El sistema debe permitir que un cliente envíe una solicitud formal a un maestro.

Estados mínimos:

- Pendiente.
- Aceptada.
- En ejecución.
- Completada.
- Rechazada.
- Cancelada.

Campos mínimos:

- Cliente solicitante.
- Maestro solicitado.
- Categoría del servicio.
- Descripción del trabajo solicitado.
- Fecha sugerida por el cliente.
- Franja horaria sugerida.
- Dirección del trabajo.
- Estado.
- Fecha de creación.
- Fecha de última actualización.
- Observaciones del maestro opcionales.

Reglas:

- Un cliente puede tener múltiples solicitudes activas con distintos maestros.
- Un maestro puede aceptar o rechazar una solicitud pendiente.
- Una solicitud aceptada puede pasar a en ejecución cuando el maestro lo confirme.
- Solo el maestro puede marcar una solicitud como completada.
- El cliente puede cancelar la solicitud mientras esté en estado pendiente o aceptada.
- Solo una solicitud completada habilita la opción de evaluar al maestro.
- Una solicitud rechazada o cancelada no puede reactivarse.

---

## 5.11 Dashboard del cliente

El sistema debe mostrar al cliente un panel de inicio personalizado.

Información mínima:

- Bienvenida con nombre del cliente.
- Solicitudes activas con estado actualizado.
- Mensajes no leídos.
- Maestros recientemente contactados.
- Acceso rápido al buscador.
- Acceso rápido al historial de solicitudes.

Reglas:

- El dashboard solo muestra información del cliente autenticado.
- Los contadores deben reflejar datos reales en tiempo razonable.

---

## 5.12 Dashboard del maestro

El sistema debe mostrar al maestro un panel de inicio personalizado.

Información mínima:

- Bienvenida con nombre del maestro.
- Solicitudes pendientes de respuesta.
- Solicitudes aceptadas en curso.
- Mensajes no leídos.
- Calificación promedio actual.
- Total de servicios completados.
- Acceso rápido a editar perfil y portfolio.

Reglas:

- El dashboard solo muestra información del maestro autenticado.
- Las solicitudes pendientes deben ordenarse por fecha de llegada.

---

## 5.13 Panel de administración

El sistema debe permitir al administrador gestionar la plataforma.

Funciones mínimas del administrador:

- Ver y gestionar usuarios registrados (clientes y maestros).
- Activar, desactivar o suspender cuentas.
- Gestionar categorías de servicios.
- Consultar evaluaciones y ocultarlas con motivo justificado.
- Consultar solicitudes de servicio con todos sus estados.
- Ver auditoría de acciones críticas.
- Acceder a reportes generales de la plataforma.

Reglas:

- El administrador no puede eliminar físicamente usuarios con historial de actividad.
- El administrador no puede leer el contenido del chat entre usuarios sin auditoría justificada.
- Toda acción del administrador queda registrada en auditoría.

---

## 5.14 Gestión de categorías de servicios

El sistema debe permitir al administrador gestionar el catálogo de oficios disponibles.

Campos mínimos:

- Nombre de la categoría.
- Descripción.
- Ícono o imagen representativa opcional.
- Estado: activo o inactivo.

Categorías iniciales sugeridas:

- Jardinería.
- Carpintería.
- Electricidad.
- Gasfitería/Plomería.
- Pintura.
- Limpieza del hogar.
- Albañilería.
- Cerrajería.
- Instalación de pisos.
- Mudanzas.

Reglas:

- El nombre de la categoría es obligatorio y único.
- No se puede eliminar físicamente una categoría con maestros asociados; debe desactivarse.
- Una categoría inactiva no aparece en el buscador ni en el registro de maestros.

---

## 5.15 Notificaciones internas

El sistema debe mostrar notificaciones a los usuarios según los eventos de la plataforma.

Notificaciones mínimas para el cliente:

- Maestro aceptó su solicitud.
- Maestro rechazó su solicitud.
- Maestro marcó el trabajo como completado.
- Nuevo mensaje del maestro.

Notificaciones mínimas para el maestro:

- Nueva solicitud de servicio recibida.
- Cliente canceló una solicitud.
- Cliente completó una evaluación.
- Nuevo mensaje del cliente.

Reglas:

- Las notificaciones deben mostrarse en la barra de navegación con contador de no leídas.
- El usuario puede marcar notificaciones como leídas.
- Las notificaciones no deben enviarse por correo electrónico en esta primera versión.

---

## 5.16 Búsqueda avanzada

El sistema debe permitir búsqueda rápida y avanzada de maestros.

Búsqueda rápida:

- Nombre del maestro.
- Nombre de categoría.
- Ciudad o comuna.

Búsqueda avanzada:

- Categoría.
- Región y ciudad.
- Rango de precio referencial.
- Calificación mínima.
- Disponibilidad por día de la semana.

Reglas:

- La búsqueda debe responder en tiempo razonable.
- Los resultados deben poder ordenarse y paginarse.
- Los filtros deben poder combinarse.

---

## 5.17 Reportes del administrador

El sistema debe permitir al administrador consultar reportes del estado general de la plataforma.

Reportes mínimos:

- Total de usuarios registrados por tipo y período.
- Maestros activos por categoría.
- Solicitudes por estado y período.
- Evaluaciones promedio por categoría.
- Maestros mejor calificados.
- Maestros con mayor número de solicitudes completadas.
- Clientes más activos.
- Solicitudes canceladas o rechazadas por período.

Formatos mínimos:

- Vista web.
- CSV.
- Excel/XLSX.

Reglas:

- Todo reporte debe permitir filtros por fecha cuando aplique.
- Solo el administrador puede acceder a los reportes.

---

## 5.18 Auditoría

El sistema debe registrar acciones relevantes.

Eventos mínimos auditados:

- Inicio y cierre de sesión.
- Creación, edición y desactivación de usuarios.
- Registro o actualización de perfil de maestro.
- Publicación o eliminación de ítem de portfolio.
- Creación, aceptación, rechazo o cancelación de solicitud.
- Publicación y ocultamiento de evaluaciones.
- Gestión de categorías.
- Acciones del administrador sobre cuentas.

Campos mínimos:

- Usuario.
- Fecha y hora.
- Módulo.
- Acción.
- Entidad afectada.
- ID de entidad.
- Valores anteriores cuando aplique.
- Valores nuevos cuando aplique.
- IP o identificador de sesión opcional.

Reglas:

- La auditoría no debe ser editable desde la interfaz.
- Solo el administrador puede consultarla.
- Debe permitir filtros por fecha, usuario y tipo de acción.

---

# 6. Modelo de datos principal

## 6.1 Tabla: usuarios

| Campo | Tipo | Descripción |
|---|---|---|
| id | INT PK | Identificador único |
| nombre | VARCHAR(100) | Nombre completo |
| email | VARCHAR(150) UNIQUE | Email de acceso |
| password_hash | VARCHAR(255) | Contraseña encriptada |
| tipo | ENUM | cliente, maestro, admin |
| estado | ENUM | activo, inactivo, suspendido |
| foto_perfil | VARCHAR(300) | URL de imagen |
| fecha_creacion | DATETIME | Fecha de registro |
| fecha_actualizacion | DATETIME | Última actualización |

---

## 6.2 Tabla: perfiles_maestro

| Campo | Tipo | Descripción |
|---|---|---|
| id | INT PK | Identificador único |
| usuario_id | INT FK | Referencia a usuarios |
| descripcion | TEXT | Presentación personal |
| telefono | VARCHAR(20) | Teléfono de contacto |
| precio_referencial | DECIMAL(10,2) | Precio por hora o trabajo |
| calificacion_promedio | DECIMAL(3,2) | Calculado automáticamente |
| total_evaluaciones | INT | Total acumulado |
| estado | ENUM | activo, inactivo, suspendido |

---

## 6.3 Tabla: zonas_cobertura

| Campo | Tipo | Descripción |
|---|---|---|
| id | INT PK | Identificador único |
| maestro_id | INT FK | Referencia a perfiles_maestro |
| region | VARCHAR(100) | Región geográfica |
| ciudad | VARCHAR(100) | Ciudad o provincia |
| comuna | VARCHAR(100) | Comuna o distrito |

---

## 6.4 Tabla: categorias_servicio

| Campo | Tipo | Descripción |
|---|---|---|
| id | INT PK | Identificador único |
| nombre | VARCHAR(100) UNIQUE | Nombre del oficio |
| descripcion | TEXT | Descripción de la categoría |
| icono_url | VARCHAR(300) | Ícono representativo |
| estado | ENUM | activo, inactivo |

---

## 6.5 Tabla: maestro_categorias

| Campo | Tipo | Descripción |
|---|---|---|
| id | INT PK | Identificador único |
| maestro_id | INT FK | Referencia a perfiles_maestro |
| categoria_id | INT FK | Referencia a categorias_servicio |

---

## 6.6 Tabla: disponibilidad_horaria

| Campo | Tipo | Descripción |
|---|---|---|
| id | INT PK | Identificador único |
| maestro_id | INT FK | Referencia a perfiles_maestro |
| dia_semana | ENUM | lunes a domingo |
| hora_inicio | TIME | Inicio de disponibilidad |
| hora_termino | TIME | Fin de disponibilidad |
| disponible | BOOLEAN | Activo o inactivo |

---

## 6.7 Tabla: portfolio_items

| Campo | Tipo | Descripción |
|---|---|---|
| id | INT PK | Identificador único |
| maestro_id | INT FK | Referencia a perfiles_maestro |
| titulo | VARCHAR(100) | Título del trabajo |
| descripcion | TEXT | Descripción del trabajo |
| categoria_id | INT FK | Categoría del trabajo |
| fecha_aprox | DATE | Fecha aproximada |
| estado | ENUM | visible, oculto |

---

## 6.8 Tabla: portfolio_imagenes

| Campo | Tipo | Descripción |
|---|---|---|
| id | INT PK | Identificador único |
| portfolio_item_id | INT FK | Referencia a portfolio_items |
| url_imagen | VARCHAR(300) | URL de la imagen |
| orden | INT | Orden de visualización |

---

## 6.9 Tabla: solicitudes_servicio

| Campo | Tipo | Descripción |
|---|---|---|
| id | INT PK | Identificador único |
| cliente_id | INT FK | Referencia a usuarios |
| maestro_id | INT FK | Referencia a perfiles_maestro |
| categoria_id | INT FK | Categoría del servicio |
| descripcion | TEXT | Descripción del trabajo |
| fecha_sugerida | DATE | Fecha propuesta por el cliente |
| franja_horaria | VARCHAR(50) | Horario preferido |
| direccion_trabajo | VARCHAR(300) | Lugar del servicio |
| estado | ENUM | pendiente, aceptada, en_ejecucion, completada, rechazada, cancelada |
| observacion_maestro | TEXT | Respuesta o notas del maestro |
| fecha_creacion | DATETIME | Fecha de la solicitud |
| fecha_actualizacion | DATETIME | Última actualización de estado |

---

## 6.10 Tabla: evaluaciones

| Campo | Tipo | Descripción |
|---|---|---|
| id | INT PK | Identificador único |
| solicitud_id | INT FK | Referencia a solicitudes_servicio |
| cliente_id | INT FK | Cliente que evalúa |
| maestro_id | INT FK | Maestro evaluado |
| puntuacion | INT | Valor entre 1 y 5 |
| comentario | TEXT | Reseña del servicio |
| estado | ENUM | visible, oculto |
| fecha_evaluacion | DATETIME | Fecha del comentario |

---

## 6.11 Tabla: mensajes_chat

| Campo | Tipo | Descripción |
|---|---|---|
| id | INT PK | Identificador único |
| solicitud_id | INT FK | Referencia a solicitudes_servicio |
| remitente_id | INT FK | Usuario que envía |
| destinatario_id | INT FK | Usuario que recibe |
| contenido | TEXT | Cuerpo del mensaje |
| leido | BOOLEAN | Estado de lectura |
| fecha_envio | DATETIME | Fecha y hora del mensaje |

---

## 6.12 Tabla: notificaciones

| Campo | Tipo | Descripción |
|---|---|---|
| id | INT PK | Identificador único |
| usuario_id | INT FK | Usuario destinatario |
| tipo | VARCHAR(50) | Tipo de notificación |
| mensaje | VARCHAR(300) | Texto de la notificación |
| leida | BOOLEAN | Estado de lectura |
| entidad_tipo | VARCHAR(50) | Entidad relacionada |
| entidad_id | INT | ID de la entidad relacionada |
| fecha_creacion | DATETIME | Fecha de la notificación |

---

## 6.13 Tabla: auditoria

| Campo | Tipo | Descripción |
|---|---|---|
| id | INT PK | Identificador único |
| usuario_id | INT FK | Usuario que ejecutó la acción |
| fecha_hora | DATETIME | Timestamp de la acción |
| modulo | VARCHAR(50) | Módulo del sistema |
| accion | VARCHAR(50) | Tipo de acción ejecutada |
| entidad_tipo | VARCHAR(50) | Entidad afectada |
| entidad_id | INT | ID de la entidad |
| valores_anteriores | JSON | Estado previo |
| valores_nuevos | JSON | Estado resultante |
| ip_sesion | VARCHAR(50) | IP o identificador de sesión |

---

# 7. Flujos principales

## 7.1 Flujo: Cliente busca y contrata un maestro

```text
1. Cliente inicia sesión o se registra.
2. Cliente accede al buscador.
3. Cliente aplica filtros: categoría, ciudad, calificación, precio.
4. Sistema muestra listado de maestros activos que cumplen los filtros.
5. Cliente hace clic en un maestro para ver su perfil completo.
6. Cliente revisa portfolio, disponibilidad y calificaciones.
7. Cliente hace clic en "Solicitar servicio".
8. Cliente completa el formulario: descripción, fecha sugerida, franja horaria, dirección.
9. Sistema crea solicitud en estado "Pendiente" y notifica al maestro.
10. Maestro recibe notificación, revisa solicitud y decide aceptar o rechazar.
11. Sistema actualiza estado y notifica al cliente.
12. Si fue aceptada, ambos pueden comunicarse mediante el chat interno.
13. Maestro ejecuta el trabajo y lo marca como completado.
14. Sistema habilita al cliente para dejar evaluación.
15. Cliente evalúa con puntuación y comentario.
16. Sistema recalcula calificación promedio del maestro.
```

---

## 7.2 Flujo: Maestro gestiona su perfil

```text
1. Maestro inicia sesión o se registra.
2. Maestro completa su perfil: descripción, categorías, zona, disponibilidad.
3. Maestro sube ítems al portfolio con imágenes y descripciones.
4. Maestro revisa su dashboard con solicitudes pendientes.
5. Maestro responde solicitudes desde el panel.
6. Maestro recibe notificaciones y accede al chat con clientes.
7. Maestro marca trabajos completados.
8. Maestro revisa evaluaciones recibidas desde su perfil.
```

---

## 7.3 Flujo: Administrador gestiona la plataforma

```text
1. Administrador inicia sesión.
2. Administrador revisa panel general con KPIs de la plataforma.
3. Administrador gestiona usuarios: activa, desactiva o suspende cuentas.
4. Administrador revisa y oculta evaluaciones inapropiadas.
5. Administrador gestiona el catálogo de categorías de servicios.
6. Administrador consulta reportes y exporta datos.
7. Administrador revisa el log de auditoría ante eventos críticos.
```

---

# 8. Reglas de negocio globales

- Todo movimiento de estado de una solicitud debe quedar registrado con fecha, hora y usuario responsable.
- Solo un cliente autenticado puede enviar solicitudes o mensajes.
- Solo un maestro activo aparece en el buscador.
- Solo puede evaluarse una solicitud completada y solo una vez por cliente.
- Un maestro no puede evaluarse a sí mismo.
- La calificación promedio se calcula como el promedio simple de todas las evaluaciones visibles.
- Un usuario suspendido no puede iniciar sesión ni realizar acciones.
- El administrador puede suspender usuarios sin eliminarlos.
- No se permite eliminación física de usuarios, solicitudes ni evaluaciones con historial.
- El chat solo existe en el contexto de una solicitud activa o historial de una solicitud terminada.
- Las notificaciones se generan automáticamente por cambios de estado de solicitudes y mensajes.
- Los datos de contacto del maestro (teléfono y email) solo se revelan al cliente luego de que la solicitud sea aceptada.

---

# 9. Indicadores del panel de administración

KPIs mínimos:

- Total de usuarios registrados.
- Total de maestros activos.
- Total de clientes activos.
- Total de solicitudes del mes.
- Solicitudes completadas del mes.
- Solicitudes canceladas o rechazadas del mes.
- Promedio general de calificaciones de la plataforma.
- Categorías con mayor demanda.
- Maestros mejor evaluados.

Gráficos mínimos:

- Solicitudes por estado.
- Solicitudes por categoría.
- Registros de nuevos usuarios por mes.
- Distribución de calificaciones (1 a 5 estrellas).
- Top 10 maestros mejor calificados.

---

# 10. Seguridad y permisos

Permisos mínimos por módulo:

```text
auth.register
auth.login
users.read_own
users.update_own
maestro.profile_create
maestro.profile_update
maestro.portfolio_manage
solicitudes.create
solicitudes.read_own
solicitudes.update_own
solicitudes.accept_reject
evaluaciones.create
evaluaciones.read
chat.send
chat.read_own
admin.users_manage
admin.categories_manage
admin.evaluaciones_moderate
admin.reports_read
admin.audit_read
```

Reglas:

- Todo endpoint protegido debe validar token JWT.
- Todo endpoint crítico debe validar el permiso específico del rol.
- Las contraseñas deben almacenarse con hash seguro (bcrypt o argon2).
- No se deben exponer errores técnicos al usuario final.
- Las acciones críticas deben quedar auditadas.
- Las rutas de administración deben estar completamente separadas y protegidas.

---

# 11. Validaciones mínimas

Validaciones de frontend y backend:

- Campos obligatorios no vacíos.
- Longitud mínima y máxima de textos.
- Email con formato válido.
- Contraseña con mínimo 8 caracteres.
- Puntuación de evaluación entre 1 y 5.
- Precio referencial no negativo.
- Hora de término mayor que hora de inicio en disponibilidad.
- Al menos una categoría seleccionada al registrar maestro.
- Solicitud solo creada si cliente está autenticado.
- Evaluación solo creada si solicitud está completada.
- Mensaje solo enviado si usuario está activo y la solicitud existe.
- Permisos suficientes para acciones críticas.

---

# 12. Casos de prueba funcionales mínimos

## CP-01 Registro de cliente válido

Datos:

- Nombre: Juan Pérez.
- Email: juan@ejemplo.com.
- Contraseña: 12345678.

Resultado esperado:

- Cliente creado en estado activo.
- Email queda único.
- Auditoría registrada.

---

## CP-02 Registro de cliente con email duplicado

Resultado esperado:

- Sistema rechaza la operación.
- Muestra mensaje claro.
- No crea registro duplicado.

---

## CP-03 Registro de maestro válido

Datos:

- Nombre: Pedro Rojas.
- Email: pedro@ejemplo.com.
- Teléfono: +56912345678.
- Categoría: Jardinería.
- Zona: Región de La Araucanía, Villarrica.

Resultado esperado:

- Maestro creado en estado activo.
- Aparece en buscador filtrado por Jardinería y Villarrica.

---

## CP-04 Registro de maestro sin categoría

Resultado esperado:

- Sistema rechaza la operación.
- Muestra mensaje indicando que se requiere al menos una categoría.

---

## CP-05 Cliente busca maestros con filtros válidos

Datos:

- Categoría: Carpintería.
- Ciudad: Temuco.
- Calificación mínima: 4.

Resultado esperado:

- Sistema muestra solo maestros activos de Carpintería en Temuco con promedio ≥ 4.
- Resultados paginados.

---

## CP-06 Cliente envía solicitud de servicio

Datos:

- Maestro destino: activo.
- Descripción: instalar estantería.
- Fecha: próxima semana.

Resultado esperado:

- Solicitud creada en estado pendiente.
- Maestro recibe notificación.

---

## CP-07 Maestro acepta solicitud

Resultado esperado:

- Estado cambia a aceptada.
- Cliente recibe notificación.
- Chat habilitado entre ambos.

---

## CP-08 Cliente intenta evaluar sin servicio completado

Resultado esperado:

- Sistema rechaza la operación.
- Muestra mensaje indicando que el servicio no está completado.

---

## CP-09 Cliente evalúa servicio completado

Datos:

- Puntuación: 5.
- Comentario: excelente trabajo.

Resultado esperado:

- Evaluación registrada.
- Calificación promedio del maestro recalculada.
- Evaluación visible en perfil público del maestro.

---

## CP-10 Maestro suspendido intenta iniciar sesión

Resultado esperado:

- Sistema bloquea acceso.
- Muestra mensaje de cuenta suspendida.

---

## CP-11 Mensaje enviado en chat activo

Resultado esperado:

- Mensaje registrado con fecha y hora.
- Aparece en el historial del destinatario.
- Notificación generada para el destinatario.

---

## CP-12 Acceso a ruta de administración sin permiso

Resultado esperado:

- Sistema bloquea la acción.
- Muestra mensaje de autorización insuficiente.

---

# 13. Pantallas principales

Pantallas mínimas:

1. Landing page o página de inicio pública.
2. Registro de cliente.
3. Registro de maestro.
4. Inicio de sesión.
5. Buscador y catálogo de maestros.
6. Perfil público del maestro.
7. Formulario de solicitud de servicio.
8. Dashboard del cliente.
9. Historial de solicitudes del cliente.
10. Chat de solicitud.
11. Formulario de evaluación.
12. Dashboard del maestro.
13. Gestión de perfil del maestro.
14. Gestión de portfolio.
15. Gestión de disponibilidad.
16. Solicitudes recibidas (vista del maestro).
17. Dashboard del administrador.
18. Gestión de usuarios.
19. Gestión de categorías.
20. Moderación de evaluaciones.
21. Reportes de la plataforma.
22. Auditoría.
23. Notificaciones.
24. Configuración de cuenta propia.

---

# 14. Diseño responsivo

El sistema debe adaptarse a los siguientes tamaños:

```text
Móvil:      320px a 767px
Tablet:     768px a 1023px
Escritorio: 1024px o superior
```

Reglas de interfaz:

- En móvil, el menú debe colapsar en hamburguesa.
- Las tarjetas de maestros deben adaptarse a una columna en móvil.
- Los formularios deben usar una columna en móvil y dos o más en escritorio.
- Los botones críticos deben tener confirmación.
- El chat debe comportarse como ventana de mensajería en móvil.
- El dashboard debe reorganizar tarjetas y gráficos según pantalla.
- El portfolio debe mostrarse en grilla responsiva.
- Las acciones frecuentes deben ser visibles y fáciles de usar en pantallas pequeñas.

---

# 15. Estructura sugerida del backend

```text
backend/
  app/
    main.py
    config.py
    database.py
    auth/
    users/
    maestros/
    clientes/
    categorias/
    solicitudes/
    evaluaciones/
    chat/
    notificaciones/
    reportes/
    dashboard/
    audit/
    settings/
    shared/
  migrations/
  tests/
  requirements.txt
  README.md
```

Reglas:

- Cada módulo debe tener rutas, modelos, esquemas y servicios.
- La lógica de negocio no debe quedar directamente en los endpoints.
- Las validaciones deben aplicarse en esquemas y servicios.
- Las operaciones críticas deben usar transacciones de base de datos.
- El módulo de chat debe manejar conexiones WebSocket en un router separado.

---

# 16. Estructura sugerida del frontend

```text
frontend/
  src/
    api/
    auth/
    components/
    layouts/
    pages/
      home/
      buscar/
      perfil-maestro/
      solicitudes/
      chat/
      evaluaciones/
      dashboard-cliente/
      dashboard-maestro/
      admin/
      configuracion/
    routes/
    hooks/
    utils/
    styles/
  public/
  package.json
  README.md
```

Reglas:

- Usar componentes reutilizables.
- Separar páginas, servicios API y componentes visuales.
- Manejar estados de carga, error y éxito.
- Validar formularios antes de enviar al backend.
- Proteger rutas según autenticación y rol.
- El contexto de autenticación debe estar disponible globalmente.

---

# 17. Entregables técnicos mínimos

El proyecto debe entregar:

- Código backend FastAPI.
- Código frontend React + Bootstrap.
- Scripts de base de datos o migraciones Alembic.
- Archivo `.env.example`.
- README de instalación.
- README de ejecución local.
- Documentación de endpoints principales.
- Modelo de datos resumido.
- Checklist de pruebas.
- Datos iniciales de ejemplo: categorías, usuarios de prueba, maestros y solicitudes.
- Usuario administrador inicial.
- Guía breve de uso del sistema.

---

# 18. Definición final del producto mínimo viable

El producto mínimo viable debe ser una aplicación web llamada **4S (Four S)**, desarrollada con **FastAPI, React, Bootstrap y MySQL/MariaDB**, que permita conectar clientes con maestros de oficios de forma ágil y confiable.

Debe incluir autenticación, registro de clientes, registro y perfiles de maestros, portfolio de trabajos, disponibilidad horaria, zonas de cobertura, buscador con filtros, calificaciones y reseñas, chat interno por solicitud, gestión de solicitudes de servicio con estados, dashboard personalizado por rol, notificaciones internas, panel de administración, reportes, auditoría y diseño responsivo.

El sistema debe estar organizado, documentado, validado y listo para ser implementado por una fábrica de agentes de IA como software web transaccional pequeño, robusto y ampliable.
