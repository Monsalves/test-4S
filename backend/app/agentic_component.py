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
class AgentRecommendationRequest(BaseModel):
    consulta: str = Field(..., min_length=5, max_length=500, description="Consulta del cliente detallando el problema o servicio requerido.")

class RecommendedMaestro(BaseModel):
    id: int
    nombre: str
    email: str
    especialidades: str
    precio_hora: float
    rating_promedio: float
    ciudad: str

class AgentRecommendationResponse(BaseModel):
    categoria_detectada: str
    diagnostico: str
    maestros_recomendados: List[RecommendedMaestro]
    source: str

# Local contingency heuristic fallback
def run_heuristic_contingency(consulta: str) -> Dict[str, str]:
    """
    Analyzes the text query and returns a category and diagnostic based on simple rules.
    This serves as our local fallback when the LLM is unavailable or lacks API keys.
    """
    consulta_lower = consulta.lower()
    
    # Keyword to category mapping
    categories = {
        "Gasfitería": ["agua", "llave", "filtración", "filtracion", "cañeria", "cañería", "tubo", "gotera", "wc", "baño", "lavaplatos", "sifón", "sifon"],
        "Carpintería": ["madera", "mueble", "puerta", "ventana", "cajón", "cajon", "silla", "mesa", "techo", "piso", "carpintero"],
        "Electricidad": ["luz", "cable", "enchufe", "corto", "electricista", "corriente", "interruptor", "automático", "automatico", "tensión", "tension"],
        "Pintura": ["pintar", "pintura", "pared", "casa", "brocha", "rodillo", "fachada", "óleo", "oleo", "látex", "latex"],
    }
    
    detected_category = "Gasfitería"  # Default fallback
    for category, keywords in categories.items():
        if any(keyword in consulta_lower for keyword in keywords):
            detected_category = category
            break
            
    diagnostics = {
        "Gasfitería": "Se detecta un posible problema de fontanería/gasfitería. Se recomienda revisar la llave de paso principal para evitar filtraciones mayores antes de la llegada del especialista.",
        "Carpintería": "Se identifica una solicitud relacionada con trabajos de madera o estructuras. Se aconseja despejar el área de trabajo y tener las medidas aproximadas a mano.",
        "Electricidad": "¡Atención! Posible falla eléctrica detectada. Por seguridad, corte el suministro eléctrico en el tablero general si hay cables expuestos o riesgo de cortocircuito.",
        "Pintura": "Solicitud de pintura o recubrimiento detectada. Se sugiere limpiar la superficie a tratar antes de comenzar el trabajo para asegurar la adherencia."
    }
    
    return {
        "categoria": detected_category,
        "diagnostico": diagnostics.get(detected_category, "Solicitud recibida. Analizando requerimiento para asignación óptima del especialista.")
    }

async def fetch_gemini_analysis(consulta: str) -> Dict[str, str]:
    """
    Calls Google Gemini API using raw HTTP calls to avoid complex SDK dependencies,
    with custom timeout and exponential retries.
    """
    if not GEMINI_API_KEY:
        raise ValueError("Clave GEMINI_API_KEY no configurada.")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Eres un asistente agéntico inteligente para la plataforma de servicios de oficios '4S'.
    Analiza la siguiente solicitud de un cliente y clasifícala en una de estas categorías: 'Gasfitería', 'Carpintería', 'Electricidad', 'Pintura', 'Otros'.
    Además, proporciona un diagnóstico inicial breve y preventivo para el cliente.
    
    Debes responder ÚNICAMENTE con un objeto JSON válido, con la siguiente estructura:
    {{
      "categoria": "Categoría detectada",
      "diagnostico": "Breve diagnóstico inicial descriptivo y preventivo de no más de dos líneas."
    }}
    
    Solicitud del cliente: "{consulta}"
    JSON:
    """
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    headers = {"Content-Type": "application/json"}
    
    # Retry loop with exponential backoff
    for attempt in range(1, AGENT_MAX_RETRIES + 1):
        try:
            logger.info(f"Intento {attempt} de llamada a Gemini API...")
            async with httpx.AsyncClient() as client:
                response = await asyncio.wait_for(
                    client.post(url, json=payload, headers=headers),
                    timeout=AGENT_TIMEOUT
                )
                
            if response.status_code == 200:
                result_json = response.json()
                text_response = result_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # Strip potential markdown code block backticks if returned by the LLM
                if text_response.startswith("```json"):
                    text_response = text_response[7:]
                if text_response.endswith("```"):
                    text_response = text_response[:-3]
                text_response = text_response.strip()
                
                parsed_res = json.loads(text_response)
                # Quick validation
                if "categoria" in parsed_res and "diagnostico" in parsed_res:
                    return parsed_res
                else:
                    raise ValueError("JSON de respuesta incompleto")
                    
            elif response.status_code in [429, 500, 503]:
                logger.warning(f"Error {response.status_code} de la API. Reintentando...")
            else:
                logger.error(f"Error fatal de API: {response.status_code} - {response.text}")
                raise ValueError(f"HTTP Error {response.status_code}")
                
        except asyncio.TimeoutError:
            logger.warning(f"Timeout (límite: {AGENT_TIMEOUT}s) alcanzado en el intento {attempt}.")
        except Exception as e:
            logger.warning(f"Error en intento {attempt}: {str(e)}")
            
        # Exponential backoff delay (1s, 2s, 4s...)
        if attempt < AGENT_MAX_RETRIES:
            delay = 2 ** (attempt - 1)
            await asyncio.sleep(delay)
            
    raise RuntimeError("Se agotaron todos los intentos de conexión a Gemini API.")

def get_recommended_maestros(categoria: str, db: Session) -> List[RecommendedMaestro]:
    """
    Queries SQLite database for active maestros matching the given category.
    """
    # Fetch profiles
    profiles = db.query(PerfilMaestroDB).all()
    recommended = []
    
    for profile in profiles:
        # Check if category is within specialties (case insensitive search)
        specialties = [s.strip().lower() for s in profile.especialidades.split(",")]
        if categoria.lower() in specialties or any(categoria.lower() in spec for spec in specialties):
            # Fetch user details
            maestro_user = db.query(UsuarioDB).filter(UsuarioDB.id == profile.maestro_id, UsuarioDB.tipo == "maestro").first()
            if maestro_user and maestro_user.estado == "activo":
                recommended.append(RecommendedMaestro(
                    id=maestro_user.id,
                    nombre=maestro_user.nombre,
                    email=maestro_user.email,
                    especialidades=profile.especialidades,
                    precio_hora=profile.precio_hora,
                    rating_promedio=profile.rating_promedio,
                    ciudad=maestro_user.ciudad
                ))
                
    # Sort recommendations by rating (highest first)
    recommended.sort(key=lambda x: x.rating_promedio, reverse=True)
    return recommended

async def get_agent_recommendation(consulta: str, db: Session) -> AgentRecommendationResponse:
    """
    Main entry point for agent recommendation. Implements input validation,
    observability logs, LLM parsing, and local contingency fallback.
    """
    # 1. Input Validation
    try:
        validated_input = AgentRecommendationRequest(consulta=consulta)
        clean_query = validated_input.consulta
    except ValidationError as ve:
        logger.error(f"Error de validación de entrada: {ve.errors()}")
        raise ve
        
    logger.info(f"Iniciando recomendación agéntica para consulta: '{clean_query}'")
    start_time = asyncio.get_event_loop().time()
    
    # 2. Try LLM matching
    try:
        analysis = await fetch_gemini_analysis(clean_query)
        detected_category = analysis["categoria"]
        diagnostico = analysis["diagnostico"]
        source = "gemini_agent"
        logger.info(f"Recomendación agéntica resuelta con Gemini. Categoría: '{detected_category}'")
    except Exception as e:
        logger.warning(f"Error al llamar a la API agéntica ({str(e)}). Activando plan de contingencia (fallback local).")
        # 3. Fallback to Local Heuristic
        fallback_res = run_heuristic_contingency(clean_query)
        detected_category = fallback_res["categoria"]
        diagnostico = fallback_res["diagnostico"]
        source = "contingency_fallback"
        
    # 4. Search matches in local Database
    maestros = get_recommended_maestros(detected_category, db)
    elapsed_time = asyncio.get_event_loop().time() - start_time
    logger.info(f"Búsqueda finalizada en {elapsed_time:.3f}s. Encontrados {len(maestros)} maestros para '{detected_category}' ({source}).")
    
    return AgentRecommendationResponse(
        categoria_detectada=detected_category,
        diagnostico=diagnostico,
        maestros_recomendados=maestros,
        source=source
    )
