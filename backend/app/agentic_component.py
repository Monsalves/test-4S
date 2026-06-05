import os
import sys
import logging
import asyncio
import httpx
import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session
from app.main import UsuarioDB, PerfilMaestroDB

# Setup dedicated logging for the agent
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, "agentic.log")

# Setup logging handlers
logger = logging.getLogger("agentic_component")
logger.setLevel(logging.INFO)
# Clear existing handlers to prevent duplicate logging
if logger.handlers:
    logger.handlers.clear()

file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler(sys.stdout)
stream_formatter = logging.Formatter('%(levelname)s: %(message)s')
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)

# Load configuration from environment with defaults
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
AGENT_TIMEOUT = float(os.getenv("AGENT_TIMEOUT", "6.0"))
AGENT_MAX_RETRIES = int(os.getenv("AGENT_MAX_RETRIES", "3"))

# Define Pydantic models for validation
class AgentExecutionRequest(BaseModel):
    instruccion: str = Field(..., min_length=5, max_length=1000, description="Instrucción de administración del sistema en lenguaje natural.")

class ProposedFileEdit(BaseModel):
    path: str = Field(..., description="Ruta del archivo a modificar relativo a la raíz del backend.")
    old_text: str = Field(..., description="Contenido de líneas exactas a buscar.")
    new_text: str = Field(..., description="Contenido nuevo de reemplazo.")

class ProposedPlan(BaseModel):
    rationale: str = Field(..., description="Explicación técnica del plan de acción propuesto.")
    commands: List[str] = Field(default=[], description="Lista de comandos shell recomendados a ejecutar.")
    file_edits: List[ProposedFileEdit] = Field(default=[], description="Lista de ediciones de archivos propuestas.")

def collect_system_telemetry(db: Session) -> Dict[str, Any]:
    """
    Recopila métricas del servidor en caliente (disco, memoria, estado DB y logs recientes)
    para alimentar el contexto del agente.
    """
    import shutil
    # 1. Uso de disco
    total, used, free = shutil.disk_usage("/")
    disk_info = {
        "total_gb": round(total / (1024**3), 2),
        "used_gb": round(used / (1024**3), 2),
        "free_gb": round(free / (1024**3), 2),
    }

    # 2. Uso de memoria
    mem_info = {"total_kb": 0, "free_kb": 0, "available_kb": 0}
    if os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    if "MemTotal" in line:
                        mem_info["total_kb"] = int(line.split()[1])
                    elif "MemFree" in line:
                        mem_info["free_kb"] = int(line.split()[1])
                    elif "MemAvailable" in line:
                        mem_info["available_kb"] = int(line.split()[1])
        except Exception:
            pass

    # 3. Estado de Base de Datos
    db_ok = False
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    # 4. Logs recientes
    log_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "agentic.log")
    recent_logs = []
    if os.path.exists(log_file_path):
        try:
            with open(log_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                recent_logs = [l.strip() for l in lines[-15:]]
        except Exception:
            pass

    # 5. Estructura de archivos del backend
    proj_files = []
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for root, dirs, files in os.walk(base_dir):
        if "__pycache__" in root or ".git" in root or ".venv" in root or "logs" in root:
            continue
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), base_dir)
            proj_files.append(rel_path)

    return {
        "disk": disk_info,
        "memory": mem_info,
        "database_connected": db_ok,
        "recent_logs": recent_logs,
        "project_files": proj_files[:40]
    }

def run_heuristic_contingency(instruction: str, telemetry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Plan de contingencia local que analiza heurísticamente la instrucción
    para sugerir comandos seguros en caso de fallo de la API de Gemini.
    """
    inst_lower = instruction.lower()
    commands = []
    rationale = "Modo de contingencia local activado (Heurística). "
    
    if "clean" in inst_lower or "limpiar" in inst_lower or "logs" in inst_lower:
        commands.append("echo '' > backend/logs/agentic.log")
        rationale += "Se sugiere la limpieza del archivo de logs del agente para liberar espacio."
    elif "restart" in inst_lower or "reiniciar" in inst_lower:
        commands.append("docker-compose restart")
        rationale += "Se sugiere el comando para reiniciar los contenedores de la aplicación."
    elif "health" in inst_lower or "status" in inst_lower or "estado" in inst_lower:
        rationale += f"Telemetría local actual: Disco Libre={telemetry['disk']['free_gb']} GB, Memoria Libre={telemetry['memory']['free_kb']} KB."
    else:
        rationale += f"La instrucción '{instruction}' es compleja y no se puede resolver en modo de contingencia local."

    return {
        "rationale": rationale,
        "commands": commands,
        "file_edits": []
    }

async def fetch_gemini_ops_plan(instruction: str, telemetry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envía la instrucción y telemetría a Gemini-2.5-Flash para estructurar el plan operativo.
    """
    if not GEMINI_API_KEY:
        raise ValueError("Clave GEMINI_API_KEY no configurada.")
        
    url = f"https://genergenerativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    # Wait, let's fix URL prefix: it is generativelanguage, not genergenerativelanguage
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Eres un agente inteligente experto en operaciones y mantenimiento de sistemas (DevOps y Administrador de Sistemas Linux) para la plataforma de servicios '4S'.
    Se te ha encomendado ejecutar una instrucción del administrador del sistema.
    
    Tu tarea es analizar el estado actual del servidor (telemetría), los archivos del proyecto y la instrucción del usuario, y proponer un plan de acción atómico y seguro.
    
    --- TELEMETRÍA DEL SERVIDOR ---
    {json.dumps(telemetry, indent=2)}
    
    --- INSTRUCCIÓN DEL USUARIO ---
    "{instruction}"
    
    Debes responder ÚNICAMENTE con un objeto JSON válido que cumpla con la estructura descrita abajo. No incluyas comentarios en el JSON, ni bloques de código markdown externos.
    
    Estructura del JSON:
    {{
      "rationale": "Explicación técnica clara en español sobre lo que vas a hacer y por qué.",
      "commands": [
        "lista",
        "de",
        "comandos",
        "shell",
        "a",
        "ejecutar"
      ],
      "file_edits": [
        {{
          "path": "ruta relativa del archivo desde la raíz del backend (ej. app/main.py o agent_cli.py)",
          "old_text": "CANTIDAD DE LÍNEAS COMPLETAS EXACTAS A BUSCAR (deben coincidir textualmente con el archivo original, incluyendo sangrías/espacios)",
          "new_text": "NUEVO CONTENIDO que reemplazará a old_text exactamente"
        }}
      ]
    }}
    
    Notas de seguridad críticas:
    1. Si la instrucción del usuario pide algo destructivo o peligroso sin justificación, rehúsate proponiendo una explicación en 'rationale' y listas vacías en 'commands' y 'file_edits'.
    2. Si los cambios sugeridos implican modificar código, asegúrate de que el texto en 'old_text' coincida de forma textual con las líneas exactas existentes en el archivo.
    3. No ejecutes comandos interactivos que se queden esperando entrada del usuario (ej: sin el flag -y).
    """
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    headers = {"Content-Type": "application/json"}
    
    for attempt in range(1, AGENT_MAX_RETRIES + 1):
        try:
            logger.info(f"Intento {attempt} de llamada a Gemini API para plan operativo...")
            async with httpx.AsyncClient() as client:
                response = await asyncio.wait_for(
                    client.post(url, json=payload, headers=headers),
                    timeout=AGENT_TIMEOUT
                )
                
            if response.status_code == 200:
                result_json = response.json()
                text_response = result_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                if text_response.startswith("```json"):
                    text_response = text_response[7:]
                if text_response.endswith("```"):
                    text_response = text_response[:-3]
                text_response = text_response.strip()
                
                parsed_res = json.loads(text_response)
                # Schema validation
                if "rationale" in parsed_res:
                    return parsed_res
                else:
                    raise ValueError("JSON de respuesta incompleto")
                    
            elif response.status_code in [429, 500, 503]:
                logger.warning(f"Error temporal {response.status_code} de la API. Reintentando...")
            else:
                logger.error(f"Error fatal de API: {response.status_code} - {response.text}")
                raise ValueError(f"HTTP Error {response.status_code}")
                
        except asyncio.TimeoutError:
            logger.warning(f"Timeout alcanzado en el intento {attempt}.")
        except Exception as e:
            logger.warning(f"Error en intento {attempt}: {str(e)}")
            
        if attempt < AGENT_MAX_RETRIES:
            delay = 2 ** (attempt - 1)
            await asyncio.sleep(delay)
            
    raise RuntimeError("Se agotaron todos los intentos de conexión a Gemini API.")

async def get_agent_execution_plan(instruction: str, db: Session) -> Dict[str, Any]:
    """
    Punto de entrada principal para generar el plan operativo.
    Recopila telemetría, llama a Gemini, y maneja contingencias (fallbacks).
    """
    logger.info(f"Iniciando planificación operativa para instrucción: '{instruction}'")
    telemetry = collect_system_telemetry(db)
    
    try:
        plan = await fetch_gemini_ops_plan(instruction, telemetry)
        source = "gemini_agent"
    except Exception as e:
        logger.warning(f"Fallo en agente de Gemini ({str(e)}). Activando contingencia local.")
        plan = run_heuristic_contingency(instruction, telemetry)
        source = "contingency_fallback"
        
    plan["source"] = source
    logger.info(f"Plan generado exitosamente vía '{source}'. Rationale: '{plan.get('rationale')}'")
    return plan

async def get_agent_monitoring_report(db: Session) -> Dict[str, str]:
    """
    Generates a system maintenance/monitoring report using telemetry and Gemini.
    """
    telemetry = collect_system_telemetry(db)
    
    # Format a diagnostic report string similar to the old CLI format
    diagnostic_report = f"""====== REPORTE DE RECURSOS ======
Disco: Total={telemetry['disk'].get('total_gb', 0)} GB, Usado={telemetry['disk'].get('used_gb', 0)} GB, Libre={telemetry['disk'].get('free_gb', 0)} GB
Memoria: MemTotal={telemetry['memory'].get('total_kb', 0)} kB, MemFree={telemetry['memory'].get('free_kb', 0)} kB
Servidor API: Conectado (Salud=healthy, Base de Datos={'ok' if telemetry['database_connected'] else 'failed'})
=================================

====== BITÁCORA DE LOGS =======
{chr(10).join(telemetry['recent_logs']) if telemetry['recent_logs'] else 'Logs: No se encontraron logs generados.'}
===============================
"""
    
    if not GEMINI_API_KEY:
        return {
            "report": f"Advertencia: No se encontró la variable GEMINI_API_KEY.\n\nReporte local básico:\n{diagnostic_report}",
            "source": "local_fallback"
        }
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""Eres un agente administrador de sistemas experto para la plataforma de servicios 4S operando en un entorno EC2 con Docker Compose.
Analiza con cautela los siguientes datos de telemetría de hardware, estado del backend y logs recopilados del servidor.

Tu reporte debe incluir de forma estructurada:
1. **ESTADO GENERAL DEL SISTEMA**: (OK, ADVERTENCIA o CRÍTICO) con una justificación clara basada en los datos.
2. **ANÁLISIS DE RECURSOS**: Evaluación detallada del uso de disco y memoria. Comenta si hay riesgo de agotamiento de recursos.
3. **SALUD DE LA APLICACIÓN Y DB**: Validación del estado de la API y conectividad SQLite.
4. **AUDITORÍA DE BITÁCORA (LOGS)**: Detección de errores, advertencias o activaciones del modo de contingencia local (fallback).
5. **ACCIONES DE MANTENIMIENTO RECOMENDADAS**: Comandos de Linux o Docker Compose recomendados para mitigar problemas detectados (ej. limpieza de logs, reiniciar contenedores, depurar espacio de disco).

Datos en tiempo real del Servidor:
{diagnostic_report}
"""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    headers = {"Content-Type": "application/json"}
    
    for attempt in range(1, AGENT_MAX_RETRIES + 1):
        try:
            logger.info(f"Intento {attempt} de llamada a Gemini API para reporte de monitoreo...")
            async with httpx.AsyncClient() as client:
                response = await asyncio.wait_for(
                    client.post(url, json=payload, headers=headers),
                    timeout=AGENT_TIMEOUT
                )
                
            if response.status_code == 200:
                result_json = response.json()
                report_text = result_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                return {
                    "report": report_text,
                    "source": "gemini_agent"
                }
            elif response.status_code in [429, 500, 503]:
                logger.warning(f"Error temporal {response.status_code} de la API. Reintentando...")
            else:
                logger.error(f"Error fatal de la API: {response.status_code}")
                break
        except Exception as e:
            logger.warning(f"Error en intento {attempt}: {str(e)}")
            
        if attempt < AGENT_MAX_RETRIES:
            await asyncio.sleep(2 ** (attempt - 1))
            
    # Fallback to local report if Gemini is down
    return {
        "report": f"Error consultando al Agente de Gemini. Mostrando reporte local básico:\n\n{diagnostic_report}",
        "source": "local_fallback"
    }
