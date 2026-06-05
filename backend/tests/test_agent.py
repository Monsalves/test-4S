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
    # Empty query or instruction < 5 chars should return validation error (422 Unprocessable Entity)
    response = client.post("/api/agent/run", json={"instruccion": "Hola"})
    assert response.status_code == 422

    response = client.post("/api/agent/run", json={"instruccion": "   "})
    assert response.status_code == 422

def test_agent_run_contingency_and_audit():
    # 1. Run a DevOps instruction. Since GEMINI_API_KEY is empty/unset, it triggers fallback
    instruction = "limpiar logs del servidor y optimizar base de datos"
    response = client.post("/api/agent/run", json={"instruccion": instruction})
    
    assert response.status_code == 200
    data = response.json()
    
    # Assertions on response schema
    assert "audit_id" in data
    assert "rationale" in data
    assert "commands" in data
    assert "file_edits" in data
    assert data["source"] == "contingency_fallback"
    
    audit_id = data["audit_id"]
    
    # 2. Get historical audit bitacora
    audit_response = client.get("/api/agent/audit")
    assert audit_response.status_code == 200
    audits = audit_response.json()
    assert len(audits) >= 1
    
    current_audit = next((a for a in audits if a["id"] == audit_id), None)
    assert current_audit is not None
    assert current_audit["instruccion"] == instruction
    assert current_audit["estado"] == "pendiente"
    
    # 3. Update audit status to approved/completado
    status_response = client.post(
        f"/api/agent/audit/{audit_id}/status",
        json={"estado": "completado", "detalles_ejecucion": '{"status": "success"}'}
    )
    assert status_response.status_code == 200
    assert status_response.json()["estado"] == "completado"
    
    # Verify DB update in list
    audit_response_updated = client.get("/api/agent/audit")
    updated_audit = next((a for a in audit_response_updated.json() if a["id"] == audit_id), None)
    assert updated_audit["estado"] == "completado"
    assert "success" in updated_audit["detalles_ejecucion"]

def test_agent_analyze_endpoint():
    response = client.post("/api/agent/analyze")
    assert response.status_code == 200
    data = response.json()
    assert "report" in data
    assert "source" in data
    # Fallback mode since key is not configured
    assert data["source"] == "local_fallback"
    assert "REPORTE DE RECURSOS" in data["report"]
