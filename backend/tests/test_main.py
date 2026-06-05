import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, Base, get_db

client = TestClient(app)

def setup_module(module):
    # Drop and recreate all tables to ensure a fresh clean database for tests
    from app.main import engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_register_user_success():
    response = client.post("/api/users/register", json={
        "nombre": "Juan Perez",
        "email": "juan@example.com",
        "password": "secretpassword",
        "tipo": "cliente",
        "ciudad": "Quillota"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Juan Perez"
    assert data["email"] == "juan@example.com"
    assert data["tipo"] == "cliente"

def test_register_user_duplicate_email():
    # Register first
    client.post("/api/users/register", json={
        "nombre": "Pedro Gomez",
        "email": "pedro@example.com",
        "password": "secretpassword",
        "tipo": "maestro",
        "ciudad": "La Cruz"
    })
    # Register duplicate
    response = client.post("/api/users/register", json={
        "nombre": "Pedro Gomez Duplicado",
        "email": "pedro@example.com",
        "password": "secretpassword",
        "tipo": "cliente",
        "ciudad": "La Cruz"
    })
    assert response.status_code == 400
    assert "email ya está registrado" in response.json()["detail"]

def test_maestros_profile_and_filtering():
    # Register a maestro
    m_resp = client.post("/api/users/register", json={
        "nombre": "Mario Carpintero",
        "email": "mario@example.com",
        "password": "secretpassword",
        "tipo": "maestro",
        "ciudad": "Quillota"
    })
    maestro_id = m_resp.json()["id"]

    # Configure profile
    profile_resp = client.post("/api/maestros/profile", json={
        "maestro_id": maestro_id,
        "descripcion": "Especialista en muebles de madera y reparaciones.",
        "especialidades": "carpinteria,muebleria",
        "precio_hora": 15.0,
        "cobertura": "Quillota, La Calera"
    })
    assert profile_resp.status_code == 200
    data = profile_resp.json()
    assert data["precio_hora"] == 15.0
    assert "carpinteria" in data["especialidades"]

    # Test listing and filtering
    list_resp = client.get("/api/maestros?categoria=carpinteria&precio_max=20.0")
    assert list_resp.status_code == 200
    maestros = list_resp.json()
    assert len(maestros) >= 1
    assert maestros[0]["nombre"] == "Mario Carpintero"

def test_service_request_flow_and_recalculation():
    # Register a client
    c_resp = client.post("/api/users/register", json={
        "nombre": "Carlos Cliente",
        "email": "carlos@example.com",
        "password": "secretpassword",
        "tipo": "cliente",
        "ciudad": "Quillota"
    })
    cliente_id = c_resp.json()["id"]

    # Register a maestro
    m_resp = client.post("/api/users/register", json={
        "nombre": "Gervasio Gasfiter",
        "email": "gervasio@example.com",
        "password": "secretpassword",
        "tipo": "maestro",
        "ciudad": "Quillota"
    })
    maestro_id = m_resp.json()["id"]

    # Set profile for Gervasio
    client.post("/api/maestros/profile", json={
        "maestro_id": maestro_id,
        "descripcion": "Reparaciones de cañerías y grifos.",
        "especialidades": "gasfiteria",
        "precio_hora": 12.5,
        "cobertura": "Quillota"
    })

    # Create service request
    req_resp = client.post("/api/services", json={
        "cliente_id": cliente_id,
        "maestro_id": maestro_id,
        "descripcion": "Reparación de filtración en cocina",
        "categoria": "gasfiteria"
    })
    assert req_resp.status_code == 201
    solicitud_id = req_resp.json()["id"]
    assert req_resp.json()["estado"] == "pendiente"

    # Accept service
    accept_resp = client.put(f"/api/services/{solicitud_id}/status", json={"estado": "aceptado"})
    assert accept_resp.status_code == 200
    assert accept_resp.json()["estado"] == "aceptado"

    # Try rating before completion - should fail
    fail_eval_resp = client.post("/api/evaluations", json={
        "cliente_id": cliente_id,
        "maestro_id": maestro_id,
        "solicitud_id": solicitud_id,
        "puntuacion": 5,
        "comentario": "Excelente servicio!"
    })
    assert fail_eval_resp.status_code == 400

    # Complete service
    complete_resp = client.put(f"/api/services/{solicitud_id}/status", json={"estado": "completado"})
    assert complete_resp.status_code == 200
    assert complete_resp.json()["estado"] == "completado"

    # Rate service successfully
    eval_resp = client.post("/api/evaluations", json={
        "cliente_id": cliente_id,
        "maestro_id": maestro_id,
        "solicitud_id": solicitud_id,
        "puntuacion": 5,
        "comentario": "Excelente servicio, muy puntual y limpio."
    })
    assert eval_resp.status_code == 201
    assert eval_resp.json()["puntuacion"] == 5

    # Check maestro average rating updated
    maestro_detail = client.get(f"/api/maestros/{maestro_id}").json()
    assert maestro_detail["profile"]["rating_promedio"] == 5.0
    assert maestro_detail["profile"]["total_evaluaciones"] == 1