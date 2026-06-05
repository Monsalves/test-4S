#!/usr/bin/env python3
import sys
import os
import argparse
import json
import urllib.request
import urllib.error

DEFAULT_API_URL = "http://localhost:8000"

def get_base_url():
    port = os.getenv("PORT", "8000")
    return f"http://localhost:{port}"

def cmd_health(args):
    """
    Checks and prints the health status of the API service.
    """
    url = f"{args.url}/api/health"
    print(f"[*] Conectando a {url}...")
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5.0) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                status = data.get("status", "unknown").upper()
                
                # Print with colors (standard ANSI)
                color = "\033[92m" if status == "HEALTHY" else "\033[91m"
                reset = "\033[0m"
                
                print("\n=== REPORTE DE SALUD DEL SISTEMA ===")
                print(f"Estado General:       {color}{status}{reset}")
                print(f"Base de Datos:        {data.get('database')}")
                print(f"Dependencia Agéntica: {data.get('agentic_dependency')}")
                print(f"Timestamp Servidor:   {data.get('timestamp')}")
                print("====================================\n")
            else:
                print(f"[\u2717] Error: El servidor respondió con código {response.status}")
    except urllib.error.HTTPError as e:
        print(f"[\u2717] Error HTTP {e.code}: {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"[\u2717] Error de conexión: {str(e.reason)}")
        print("Asegúrese de que el servidor FastAPI esté corriendo y el puerto sea accesible.")
    except Exception as e:
        print(f"[\u2717] Error inesperado: {str(e)}")

def cmd_test(args):
    """
    Sends a query to the agent recommendation engine and formats the response.
    """
    url = f"{args.url}/api/agent/recommend"
    print(f"[*] Solicitando recomendación para: '{args.query}'")
    
    payload = {"consulta": args.query}
    try:
        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url, 
            data=data_bytes, 
            headers={'Content-Type': 'application/json'},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15.0) as response:
            if response.status == 200:
                res = json.loads(response.read().decode('utf-8'))
                print("\n=== RESPUESTA DEL ASISTENTE AGÉNTICO ===")
                print(f"Categoría Detectada: {res.get('categoria_detectada')}")
                print(f"Origen de Decisión:  {res.get('source')}")
                print(f"Diagnóstico Inicial:\n  {res.get('diagnostico')}\n")
                
                maestros = res.get("maestros_recomendados", [])
                print("Maestros Recomendados:")
                if not maestros:
                    print("  No se encontraron maestros disponibles en esta especialidad/ciudad.")
                else:
                    # Format a text table
                    header = f"  {'ID':<4} | {'Nombre':<25} | {'Precio/Hora':<12} | {'Rating':<6} | {'Ciudad':<15}"
                    print(header)
                    print("  " + "-" * len(header))
                    for m in maestros:
                        rating = f"{m.get('rating_promedio'):.2f}"
                        precio = f"${m.get('precio_hora'):.2f}"
                        print(f"  {m.get('id'):<4} | {m.get('nombre'):<25} | {precio:<12} | {rating:<6} | {m.get('ciudad'):<15}")
                print("========================================\n")
            else:
                print(f"[\u2717] Error {response.status}")
    except urllib.error.HTTPError as e:
         print(f"[\u2717] Error HTTP {e.code}: {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"[\u2717] Error de conexión: {str(e.reason)}")
    except Exception as e:
        print(f"[\u2717] Error: {str(e)}")

def cmd_logs(args):
    """
    Displays the contents of the agentic log file.
    """
    # Locate log file relative to agent_cli.py
    log_path = os.path.join(os.path.dirname(__file__), "logs", "agentic.log")
    
    if not os.path.exists(log_path):
        print(f"[\u2717] El archivo de logs no existe en la ruta esperada: {log_path}")
        print("Realice alguna interacción con el agente para generar logs.")
        return
        
    print(f"[*] Leyendo las últimas {args.lines} líneas de {log_path}:\n")
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            last_lines = lines[-args.lines:]
            for line in last_lines:
                print(line, end="")
    except Exception as e:
        print(f"[\u2717] Error al leer el archivo de logs: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description="Cliente CLI Agéntico de Mantenimiento y Diagnóstico para la Plataforma 4S.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--url", 
        default=get_base_url(),
        help=f"URL base de la API de FastAPI (defecto: http://localhost:<PORT_ENV_OR_8000>)"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcomandos de mantenimiento")
    
    # Subcommand: health
    subparsers.add_parser("health", help="Verifica el estado de salud de la API, base de datos y llaves API.")
    
    # Subcommand: test
    parser_test = subparsers.add_parser("test", help="Prueba el motor de recomendación agéntica con una consulta.")
    parser_test.add_argument("query", help="Texto de la consulta que enviará el cliente.")
    
    # Subcommand: logs
    parser_logs = subparsers.add_parser("logs", help="Inspecciona el archivo de logs del agente agéntico en el servidor.")
    parser_logs.add_argument("--lines", type=int, default=30, help="Número de líneas a mostrar (defecto: 30)")
    
    args = parser.parse_args()
    
    if args.command == "health":
        cmd_health(args)
    elif args.command == "test":
        cmd_test(args)
    elif args.command == "logs":
        cmd_logs(args)

if __name__ == "__main__":
    main()
