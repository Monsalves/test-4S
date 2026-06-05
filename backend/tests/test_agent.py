import pytest
from fastapi.testclient import TestClient
from app.main import app, Base

client = TestClient(app)

def setup_module(module):
    # Ensure fresh DB tables before running agent tests
    from app.main import engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "ok"
    assert "agentic_dependency" in data

def test_agent_validation_error():
    # Empty query or query < 5 chars should return validation error (400 Bad Request)
    response = client.post("/api/agent/recommend", json={"consulta": "Hola"})
    assert response.status_code == 400

    response = client.post("/api/agent/recommend", json={"consulta": "   "})
    assert response.status_code == 400

def test_agent_recommendation_fallback_and_db_query():
    # 1. Register a maestro user with specialty 'gasfitería'
    reg_response = client.post("/api/users/register", json={
        "nombre": "Mario Bros",
        "email": "mario@nintendo.com",
        "password": "supersecretpassword",
        "tipo": "maestro",
        "ciudad": "Quillota"
    })
    assert reg_response.status_code == 201
    maestro_id = reg_response.json()["id"]

    # Update maestro profile with Gasfitería specialty
    profile_response = client.post("/api/maestros/profile", json={
        "maestro_id": maestro_id,
        "descripcion": "Experto plomero con años de experiencia reparando tuberías.",
        "especialidades": "gasfitería, cañerías",
        "precio_hora": 15.0,
        "cobertura": "Quillota"
    })
    assert profile_response.status_code == 200

    # 2. Make query containing water/leak keywords to activate fallback
    # Since GEMINI_API_KEY is empty in test environment, it will use local contingency fallback
    recommend_response = client.post("/api/agent/recommend", json={
        "consulta": "Tengo una filtración de agua urgente en la cocina"
    })
    
    assert recommend_response.status_code == 200
    data = recommend_response.json()
    
    # Assertions
    assert data["categoria_detectada"] == "Gasfitería"
    assert data["source"] == "contingency_fallback"
    assert "Se detecta un posible problema de fontanería" in data["diagnostico"]
    
    # Check recommended maestros list contains Mario Bros
    maestros = data["maestros_recomendados"]
    assert len(maestros) >= 1
    mario_maestro = next((m for m in maestros if m["id"] == maestro_id), None)
    assert mario_maestro is not None
    assert mario_maestro["nombre"] == "Mario Bros"
    assert "gasfitería" in mario_maestro["especialidades"]
    assert mario_maestro["precio_hora"] == 15.0
