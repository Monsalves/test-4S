# Plan de Pruebas del Proyecto (4S — Four S)

## 1. Pruebas Unitarias y API (Backend)
- `test_register_user_success`: Valida que se crea un usuario (cliente o maestro) con éxito.
- `test_register_user_duplicate_email`: Valida que no se permita registrar un email existente (código 400).
- `test_maestros_listing_and_filtering`: Valida el listado y filtrado de maestros por especialidad y precio.
- `test_create_service_request`: Valida el flujo transaccional de creación de una solicitud de servicio.
- `test_service_state_transitions`: Valida que el maestro acepte y complete una solicitud.
- `test_evaluation_success`: Valida la creación de una reseña y el recálculo atómico del rating promedio del maestro.
- `test_evaluation_fails_before_completion`: Valida que se rechace (código 400) la calificación si el servicio no está en estado `completado`.
- `test_evaluation_invalid_puntuacion`: Valida que se rechace una puntuación fuera del rango 1-5 (código 422).