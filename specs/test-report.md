# Reporte de Pruebas de Software (Test Report - 4S — Four S)

- **Proyecto ID:** PROYECTO_TRES
- **Suite:** Pytest (FastAPI TestClient)
- **Entorno de Aislamiento:** Sandbox Local

## Resultado
- **Estado General:** PASS

### Pytest Sandbox Execution Log
```text
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/monsalves/Escritorio/electivo-agentes/Fabrica BÁSICA APP WEB 15.46.51/Fabrica BÁSICA APP WEB
configfile: pytest.ini
plugins: anyio-4.13.0
collected 4 items

tests/test_main.py ....                                                  [100%]

=============================== warnings summary ===============================
../../../.venv/lib64/python3.14/site-packages/fastapi/testclient.py:1
  /home/monsalves/Escritorio/electivo-agentes/Fabrica BÁSICA APP WEB 15.46.51/Fabrica BÁSICA APP WEB/.venv/lib64/python3.14/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

app/main.py:14
  /home/monsalves/Escritorio/electivo-agentes/Fabrica BÁSICA APP WEB 15.46.51/Fabrica BÁSICA APP WEB/sandbox/PROYECTO_TRES/backend/app/main.py:14: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

app/main.py:90
  /home/monsalves/Escritorio/electivo-agentes/Fabrica BÁSICA APP WEB 15.46.51/Fabrica BÁSICA APP WEB/sandbox/PROYECTO_TRES/backend/app/main.py:90: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.13/migration/
    class UserResponse(BaseModel):

../../../.venv/lib64/python3.14/site-packages/pydantic/_internal/_config.py:386
  /home/monsalves/Escritorio/electivo-agentes/Fabrica BÁSICA APP WEB 15.46.51/Fabrica BÁSICA APP WEB/.venv/lib64/python3.14/site-packages/pydantic/_internal/_config.py:386: UserWarning: Valid config keys have changed in V2:
  * 'orm_mode' has been renamed to 'from_attributes'
    warnings.warn(message, UserWarning)

app/main.py:109
  /home/monsalves/Escritorio/electivo-agentes/Fabrica BÁSICA APP WEB 15.46.51/Fabrica BÁSICA APP WEB/sandbox/PROYECTO_TRES/backend/app/main.py:109: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.13/migration/
    class PerfilMaestroResponse(BaseModel):

app/main.py:121
  /home/monsalves/Escritorio/electivo-agentes/Fabrica BÁSICA APP WEB 15.46.51/Fabrica BÁSICA APP WEB/sandbox/PROYECTO_TRES/backend/app/main.py:121: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.13/migration/
    class MaestroDetailResponse(BaseModel):

app/main.py:137
  /home/monsalves/Escritorio/electivo-agentes/Fabrica BÁSICA APP WEB 15.46.51/Fabrica BÁSICA APP WEB/sandbox/PROYECTO_TRES/backend/app/main.py:137: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.13/migration/
    class ServiceResponse(BaseModel):

app/main.py:159
  /home/monsalves/Escritorio/electivo-agentes/Fabrica BÁSICA APP WEB 15.46.51/Fabrica BÁSICA APP WEB/sandbox/PROYECTO_TRES/backend/app/main.py:159: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.13/migration/
    class EvaluationResponse(BaseModel):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 4 passed, 8 warnings in 1.09s =========================


```