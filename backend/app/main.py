import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite3")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
Base = declarative_base()

# SQLAlchemy Models
class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(200), nullable=False)
    tipo = Column(String(20), nullable=False) # cliente, maestro
    estado = Column(String(20), default="activo")
    ciudad = Column(String(100), nullable=True)
    creado_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("PerfilMaestroDB", uselist=False, back_populates="usuario", lazy="joined")

class PerfilMaestroDB(Base):
    __tablename__ = "perfiles_maestro"
    maestro_id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    descripcion = Column(String(500), nullable=False)
    especialidades = Column(String(250), nullable=False) # Comma-separated list (e.g. "gasfiteria,carpinteria")
    precio_hora = Column(Float, default=0.0)
    cobertura = Column(String(100), nullable=True)
    rating_promedio = Column(Float, default=0.0)
    total_evaluaciones = Column(Integer, default=0)

    usuario = relationship("UsuarioDB", back_populates="profile")

class SolicitudServicioDB(Base):
    __tablename__ = "solicitudes_servicio"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    maestro_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    descripcion = Column(String(500), nullable=False)
    categoria = Column(String(100), nullable=False)
    estado = Column(String(20), default="pendiente") # pendiente, aceptado, completado
    creado_at = Column(DateTime, default=datetime.utcnow)
    actualizado_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cliente = relationship("UsuarioDB", foreign_keys=[cliente_id], lazy="joined")
    maestro = relationship("UsuarioDB", foreign_keys=[maestro_id], lazy="joined")

class EvaluacionDB(Base):
    __tablename__ = "evaluaciones"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    maestro_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    solicitud_id = Column(Integer, ForeignKey("solicitudes_servicio.id"), nullable=False)
    puntuacion = Column(Integer, nullable=False) # 1 a 5
    comentario = Column(String(500), nullable=False)
    creado_at = Column(DateTime, default=datetime.utcnow)

class AuditoriaAgenteDB(Base):
    __tablename__ = "auditoria_agente"
    id = Column(Integer, primary_key=True, index=True)
    instruccion = Column(String(500), nullable=False)
    plan_propuesto = Column(String(5000), nullable=False) # JSON format string
    estado = Column(String(50), nullable=False, default="pendiente") # pendiente, aprobado, rechazado, completado, fallido
    detalles_ejecucion = Column(String(5000), nullable=True) # JSON output string
    creado_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="4S — Plataforma Web de Servicios de Oficio", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "index.html")
    if os.path.exists(frontend_path):
        with open(frontend_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Frontend not found"

# Pydantic Schemas
class UserRegister(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150)
    email: str = Field(..., min_length=5, max_length=150)
    password: str = Field(..., min_length=4)
    tipo: str = Field(..., pattern="^(cliente|maestro)$")
    ciudad: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    tipo: str
    estado: str
    ciudad: Optional[str] = None
    creado_at: datetime

    class Config:
        orm_mode = True

class MaestroProfileCreate(BaseModel):
    maestro_id: int
    descripcion: str = Field(..., min_length=10, max_length=500)
    especialidades: str = Field(..., min_length=2, max_length=250)
    precio_hora: float = Field(..., ge=0.0)
    cobertura: str = Field(..., min_length=2, max_length=100)

class PerfilMaestroResponse(BaseModel):
    maestro_id: int
    descripcion: str
    especialidades: str
    precio_hora: float
    cobertura: Optional[str] = None
    rating_promedio: float
    total_evaluaciones: int

    class Config:
        orm_mode = True

class MaestroDetailResponse(BaseModel):
    id: int
    nombre: str
    email: str
    ciudad: Optional[str] = None
    profile: Optional[PerfilMaestroResponse] = None

    class Config:
        orm_mode = True

class ServiceCreate(BaseModel):
    cliente_id: int
    maestro_id: int
    descripcion: str = Field(..., min_length=10, max_length=500)
    categoria: str = Field(..., min_length=2, max_length=100)

class ServiceResponse(BaseModel):
    id: int
    cliente_id: int
    maestro_id: int
    descripcion: str
    categoria: str
    estado: str
    creado_at: datetime
    actualizado_at: datetime
    cliente: UserResponse
    maestro: UserResponse

    class Config:
        orm_mode = True

class EvaluationCreate(BaseModel):
    cliente_id: int
    maestro_id: int
    solicitud_id: int
    puntuacion: int = Field(..., ge=1, le=5)
    comentario: str = Field(..., min_length=5, max_length=500)

class EvaluationResponse(BaseModel):
    id: int
    cliente_id: int
    maestro_id: int
    solicitud_id: int
    puntuacion: int
    comentario: str
    creado_at: datetime

    class Config:
        orm_mode = True

class AgentRunRequest(BaseModel):
    instruccion: str = Field(..., min_length=5)

class AgentAuditStatusUpdateRequest(BaseModel):
    estado: str = Field(..., pattern="^(aprobado|rechazado|completado|fallido)$")
    detalles_ejecucion: Optional[str] = None

class AgentAuditResponse(BaseModel):
    id: int
    instruccion: str
    plan_propuesto: str
    estado: str
    detalles_ejecucion: Optional[str]
    creado_at: datetime

    class Config:
        orm_mode = True

# Helper Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Endpoints
@app.post("/api/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister):
    db = SessionLocal()
    existing = db.query(UsuarioDB).filter(UsuarioDB.email == user.email).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="El email ya está registrado.")
    
    db_user = UsuarioDB(
        nombre=user.nombre,
        email=user.email,
        password=user.password, # Plaintext for simple educational demo/tests
        tipo=user.tipo,
        ciudad=user.ciudad
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Automatically create blank profile for maestro
    if user.tipo == "maestro":
        profile = PerfilMaestroDB(
            maestro_id=db_user.id,
            descripcion="Presentación del maestro en la plataforma.",
            especialidades="general",
            precio_hora=10.0,
            cobertura=user.ciudad or "Nacional"
        )
        db.add(profile)
        db.commit()

    db.close()
    return db_user

@app.post("/api/users/login", response_model=UserResponse)
def login_user(user: UserLogin):
    db = SessionLocal()
    db_user = db.query(UsuarioDB).filter(UsuarioDB.email == user.email, UsuarioDB.password == user.password).first()
    db.close()
    if not db_user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
    return db_user

@app.post("/api/maestros/profile", response_model=PerfilMaestroResponse)
def save_maestro_profile(profile: MaestroProfileCreate):
    db = SessionLocal()
    db_user = db.query(UsuarioDB).filter(UsuarioDB.id == profile.maestro_id, UsuarioDB.tipo == "maestro").first()
    if not db_user:
        db.close()
        raise HTTPException(status_code=404, detail="Maestro no encontrado.")
    
    db_profile = db.query(PerfilMaestroDB).filter(PerfilMaestroDB.maestro_id == profile.maestro_id).first()
    if not db_profile:
        db_profile = PerfilMaestroDB(maestro_id=profile.maestro_id)
        db.add(db_profile)
    
    db_profile.descripcion = profile.descripcion
    db_profile.especialidades = profile.especialidades.lower()
    db_profile.precio_hora = profile.precio_hora
    db_profile.cobertura = profile.cobertura
    db.commit()
    db.refresh(db_profile)
    db.close()
    return db_profile

@app.get("/api/maestros", response_model=List[MaestroDetailResponse])
def get_maestros(
    categoria: Optional[str] = None,
    ciudad: Optional[str] = None,
    precio_max: Optional[float] = None,
    rating_min: Optional[float] = None
):
    db = SessionLocal()
    query = db.query(UsuarioDB).join(PerfilMaestroDB).filter(UsuarioDB.tipo == "maestro", UsuarioDB.estado == "activo")
    
    if categoria:
        query = query.filter(PerfilMaestroDB.especialidades.like(f"%{categoria.lower()}%"))
    if ciudad:
        query = query.filter(UsuarioDB.ciudad.like(f"%{ciudad}%") | PerfilMaestroDB.cobertura.like(f"%{ciudad}%"))
    if precio_max is not None:
        query = query.filter(PerfilMaestroDB.precio_hora <= precio_max)
    if rating_min is not None:
        query = query.filter(PerfilMaestroDB.rating_promedio >= rating_min)
        
    maestros = query.all()
    db.close()
    return maestros

@app.get("/api/maestros/{id}", response_model=MaestroDetailResponse)
def get_maestro_detail(id: int):
    db = SessionLocal()
    maestro = db.query(UsuarioDB).filter(UsuarioDB.id == id, UsuarioDB.tipo == "maestro").first()
    db.close()
    if not maestro:
        raise HTTPException(status_code=404, detail="Maestro no encontrado.")
    return maestro

@app.post("/api/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(service: ServiceCreate):
    db = SessionLocal()
    cliente = db.query(UsuarioDB).filter(UsuarioDB.id == service.cliente_id, UsuarioDB.tipo == "cliente").first()
    maestro = db.query(UsuarioDB).filter(UsuarioDB.id == service.maestro_id, UsuarioDB.tipo == "maestro").first()
    
    if not cliente or not maestro:
        db.close()
        raise HTTPException(status_code=404, detail="Cliente o Maestro no encontrado.")
        
    db_service = SolicitudServicioDB(
        cliente_id=service.cliente_id,
        maestro_id=service.maestro_id,
        descripcion=service.descripcion,
        categoria=service.categoria,
        estado="pendiente"
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    db.close()
    return db_service

@app.get("/api/services", response_model=List[ServiceResponse])
def get_services(user_id: int, role: str):
    db = SessionLocal()
    if role == "cliente":
        services = db.query(SolicitudServicioDB).filter(SolicitudServicioDB.cliente_id == user_id).all()
    elif role == "maestro":
        services = db.query(SolicitudServicioDB).filter(SolicitudServicioDB.maestro_id == user_id).all()
    else:
        db.close()
        raise HTTPException(status_code=400, detail="Rol inválido para consultar servicios.")
    db.close()
    return services

@app.put("/api/services/{id}/status", response_model=ServiceResponse)
def update_service_status(id: int, status_update: dict):
    db = SessionLocal()
    db_service = db.query(SolicitudServicioDB).filter(SolicitudServicioDB.id == id).first()
    if not db_service:
        db.close()
        raise HTTPException(status_code=404, detail="Solicitud de servicio no encontrada.")
    
    nuevo_estado = status_update.get("estado")
    if nuevo_estado not in ["aceptado", "completado"]:
        db.close()
        raise HTTPException(status_code=400, detail="Estado no permitido.")
        
    db_service.estado = nuevo_estado
    db_service.actualizado_at = datetime.utcnow()
    db.commit()
    db.refresh(db_service)
    db.close()
    return db_service

@app.post("/api/evaluations", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
def create_evaluation(eval_req: EvaluationCreate):
    db = SessionLocal()
    # Validate service is completed
    solicitud = db.query(SolicitudServicioDB).filter(
        SolicitudServicioDB.id == eval_req.solicitud_id,
        SolicitudServicioDB.cliente_id == eval_req.cliente_id,
        SolicitudServicioDB.maestro_id == eval_req.maestro_id
    ).first()
    
    if not solicitud:
        db.close()
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
        
    if solicitud.estado != "completado":
        db.close()
        raise HTTPException(status_code=400, detail="No se puede evaluar un servicio no completado.")
        
    # Check if already evaluated
    existing_eval = db.query(EvaluacionDB).filter(EvaluacionDB.solicitud_id == eval_req.solicitud_id).first()
    if existing_eval:
        db.close()
        raise HTTPException(status_code=400, detail="Este servicio ya ha sido calificado.")
        
    db_eval = EvaluacionDB(
        cliente_id=eval_req.cliente_id,
        maestro_id=eval_req.maestro_id,
        solicitud_id=eval_req.solicitud_id,
        puntuacion=eval_req.puntuacion,
        comentario=eval_req.comentario
    )
    db.add(db_eval)
    
    # Recalculate rating
    profile = db.query(PerfilMaestroDB).filter(PerfilMaestroDB.maestro_id == eval_req.maestro_id).first()
    if profile:
        actual_total = profile.total_evaluaciones
        actual_rating = profile.rating_promedio
        nuevo_total = actual_total + 1
        nuevo_promedio = ((actual_rating * actual_total) + eval_req.puntuacion) / nuevo_total
        profile.total_evaluaciones = nuevo_total
        profile.rating_promedio = round(nuevo_promedio, 2)
        
    db.commit()
    db.refresh(db_eval)
    db.close()
    return db_eval

@app.get("/api/evaluations", response_model=List[EvaluationResponse])
def get_evaluations(maestro_id: int):
    db = SessionLocal()
    evals = db.query(EvaluacionDB).filter(EvaluacionDB.maestro_id == maestro_id).all()
    db.close()
    return evals

# Agentic System Operations and Health Check Endpoints
import json

@app.post("/api/agent/run")
async def run_agent_instruction(payload: AgentRunRequest):
    from app.agentic_component import get_agent_execution_plan
    db = SessionLocal()
    try:
        plan = await get_agent_execution_plan(payload.instruccion, db)
        
        # Save to database with status 'pendiente'
        db_audit = AuditoriaAgenteDB(
            instruccion=payload.instruccion,
            plan_propuesto=json.dumps(plan),
            estado="pendiente"
        )
        db.add(db_audit)
        db.commit()
        db.refresh(db_audit)
        
        return {
            "audit_id": db_audit.id,
            "rationale": plan.get("rationale", ""),
            "commands": plan.get("commands", []),
            "file_edits": plan.get("file_edits", []),
            "source": plan.get("source", "contingency_fallback")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/agent/audit/{audit_id}/status")
def update_agent_audit_status(audit_id: int, payload: AgentAuditStatusUpdateRequest):
    db = SessionLocal()
    try:
        db_audit = db.query(AuditoriaAgenteDB).filter(AuditoriaAgenteDB.id == audit_id).first()
        if not db_audit:
            raise HTTPException(status_code=404, detail="Auditoría no encontrada")
        db_audit.estado = payload.estado
        if payload.detalles_ejecucion is not None:
            db_audit.detalles_ejecucion = payload.detalles_ejecucion
        db.commit()
        db.refresh(db_audit)
        return {"status": "updated", "audit_id": audit_id, "estado": db_audit.estado}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/agent/audit", response_model=List[AgentAuditResponse])
def get_agent_audits():
    db = SessionLocal()
    try:
        audits = db.query(AuditoriaAgenteDB).order_by(AuditoriaAgenteDB.id.desc()).all()
        return audits
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/agent/analyze")
async def analyze_system_endpoint():
    from app.agentic_component import get_agent_monitoring_report
    db = SessionLocal()
    try:
        result = await get_agent_monitoring_report(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/health")
def health_check():
    db = SessionLocal()
    db_ok = False
    try:
        # Check SQLite DB connection
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        db_status = f"Error: {str(e)}"
    else:
        db_status = "ok"
    finally:
        db.close()
        
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    agent_status = "ok" if gemini_key else "fallback_mode_only (no key)"
    
    overall = "healthy" if db_ok else "unhealthy"
    
    return {
        "status": overall,
        "database": db_status,
        "agentic_dependency": agent_status,
        "timestamp": datetime.utcnow().isoformat()
    }