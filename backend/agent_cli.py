#!/usr/bin/env python3
import sys
import os
import argparse
import json
import shutil
import urllib.request
import urllib.error
import subprocess

DEFAULT_API_URL = "http://localhost:8000"

def get_base_url():
    port = os.getenv("PORT", "8000")
    return f"http://localhost:{port}"

def load_env_key():
    # Try to locate .env relative to this file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
    if not os.path.exists(env_path):
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", ".env")
    
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("GEMINI_API_KEY="):
                    val = line.strip().split("=", 1)[1].strip()
                    # Strip quotes if present
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]
                    elif val.startswith("'") and val.endswith("'"):
                        val = val[1:-1]
                    return val
    return os.getenv("GEMINI_API_KEY", "")

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

def cmd_run(args):
    """
    Sends an operational instruction to the agent, prints the proposed plan,
    and runs it locally after user confirmation.
    """
    url = f"{args.url}/api/agent/run"
    print(f"[*] Enviando instrucción al Agente: '{args.instruction}'")
    
    payload = {"instruccion": args.instruction}
    try:
        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={'Content-Type': 'application/json'},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=25.0) as response:
            if response.status == 200:
                res = json.loads(response.read().decode('utf-8'))
                audit_id = res.get("audit_id")
                rationale = res.get("rationale")
                commands = res.get("commands", [])
                file_edits = res.get("file_edits", [])
                
                print("\n=== PROPUESTA DEL AGENTE DE OPERACIONES ===")
                print(f"ID Auditoría:  {audit_id}")
                print(f"Justificación: {rationale}")
                
                if commands:
                    print("\nComandos Shell Sugeridos:")
                    for cmd in commands:
                        print(f"  > {cmd}")
                else:
                    print("\nComandos Shell: Ninguno")
                    
                if file_edits:
                    print("\nModificaciones de Archivos Sugeridas:")
                    for idx, edit in enumerate(file_edits):
                        print(f"  [{idx + 1}] Archivo: {edit.get('path')}")
                        print("  --- TEXTO A REEMPLAZAR ---")
                        print(edit.get('old_text'))
                        print("  --- TEXTO NUEVO ---")
                        print(edit.get('new_text'))
                        print("  --------------------------")
                else:
                    print("\nModificaciones de Archivos: Ninguna")
                print("===========================================\n")
                
                if not commands and not file_edits:
                    print("[*] El agente no propuso ninguna acción. Operación finalizada.")
                    update_audit_status(args.url, audit_id, "completado", "El agente no sugirió comandos ni ediciones.")
                    return
                    
                confirm = input("¿Desea aplicar estos cambios y ejecutar los comandos? (s/n): ").strip().lower()
                if confirm == 's':
                    print("[*] Ejecutando plan del agente...")
                    update_audit_status(args.url, audit_id, "aprobado", None)
                    
                    execution_details = {
                        "commands_executed": [],
                        "file_edits_applied": []
                    }
                    
                    # 1. Apply file edits
                    edit_errors = False
                    for edit in file_edits:
                        path = edit.get("path")
                        old = edit.get("old_text")
                        new = edit.get("new_text")
                        edit_res = apply_file_edit(path, old, new)
                        print(f"[*] {edit_res}")
                        execution_details["file_edits_applied"].append({
                            "path": path,
                            "result": edit_res
                        })
                        if "Error" in edit_res:
                            edit_errors = True
                            
                    # 2. Run shell commands
                    cmd_errors = False
                    for cmd in commands:
                        print(f"[*] Ejecutando: {cmd}")
                        try:
                            run_res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30.0)
                            stdout_str = run_res.stdout
                            stderr_str = run_res.stderr
                            code = run_res.returncode
                            print(f"  [Código {code}]")
                            if stdout_str:
                                print(f"  stdout: {stdout_str.strip()}")
                            if stderr_str:
                                print(f"  stderr: {stderr_str.strip()}")
                            execution_details["commands_executed"].append({
                                "command": cmd,
                                "returncode": code,
                                "stdout": stdout_str,
                                "stderr": stderr_str
                            })
                            if code != 0:
                                cmd_errors = True
                        except Exception as e:
                            print(f"[\u2717] Error ejecutando comando: {str(e)}")
                            execution_details["commands_executed"].append({
                                "command": cmd,
                                "error": str(e)
                            })
                            cmd_errors = True
                            
                    final_state = "fallido" if (edit_errors or cmd_errors) else "completado"
                    update_audit_status(args.url, audit_id, final_state, json.dumps(execution_details))
                    print(f"\n[*] Operación finalizada con estado: {final_state.upper()}")
                else:
                    print("[*] Operación rechazada por el usuario.")
                    update_audit_status(args.url, audit_id, "rechazado", None)
            else:
                print(f"[\u2717] Error: El servidor respondió con código {response.status}")
    except urllib.error.HTTPError as e:
        print(f"[\u2717] Error HTTP {e.code}: {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"[\u2717] Error de conexión al backend: {str(e.reason)}")

def update_audit_status(base_url, audit_id, status, details):
    url = f"{base_url}/api/agent/audit/{audit_id}/status"
    payload = {"estado": status, "detalles_ejecucion": details}
    try:
        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={'Content-Type': 'application/json'},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5.0) as response:
            return response.status == 200
    except Exception as e:
        print(f"[\u26A0] No se pudo actualizar el estado de auditoría en el backend: {str(e)}")
        return False

def apply_file_edit(rel_path, old_text, new_text):
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    # Try resolving path directly, inside app/ or project root
    abs_path = os.path.abspath(os.path.join(backend_dir, rel_path))
    if not os.path.exists(abs_path):
        abs_path = os.path.abspath(os.path.join(backend_dir, "app", rel_path))
        if not os.path.exists(abs_path):
            abs_path = os.path.abspath(os.path.join(os.path.dirname(backend_dir), rel_path))
            if not os.path.exists(abs_path):
                return f"Error: Archivo no encontrado en '{rel_path}'"
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
        if old_text not in content:
            return f"Error: Texto original a reemplazar no encontrado en {rel_path}."
        new_content = content.replace(old_text, new_text, 1)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return f"Éxito: Archivo {rel_path} modificado."
    except Exception as e:
        return f"Error escribiendo {rel_path}: {str(e)}"

def cmd_audit(args):
    """
    Retrieves and displays the history of agent operations from the database.
    """
    url = f"{args.url}/api/agent/audit"
    print("[*] Solicitando bitácora de auditoría histórica...")
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10.0) as response:
            if response.status == 200:
                audits = json.loads(response.read().decode('utf-8'))
                print("\n=== BITÁCORA DE AUDITORÍA HISTÓRICA DEL AGENTE ===")
                if not audits:
                    print("  No hay registros de auditoría aún.")
                else:
                    header = f"  {'ID':<4} | {'Fecha/Hora (UTC)':<20} | {'Estado':<11} | {'Instrucción':<40}"
                    print(header)
                    print("  " + "-" * len(header))
                    for a in audits:
                        created = a.get("creado_at", "")[:19].replace("T", " ")
                        inst = a.get("instruccion", "")
                        if len(inst) > 40:
                            inst = inst[:37] + "..."
                        print(f"  {a.get('id'):<4} | {created:<20} | {a.get('estado').upper():<11} | {inst:<40}")
                print("===================================================\n")
            else:
                print(f"[\u2717] Error: El servidor respondió con código {response.status}")
    except urllib.error.HTTPError as e:
        print(f"[\u2717] Error HTTP {e.code}: {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"[\u2717] Error de conexión: {str(e.reason)}")

def cmd_logs(args):
    """
    Displays the contents of the agentic log file.
    """
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

def cmd_analyze(args):
    """
    Sends a request to the backend `/api/agent/analyze` endpoint to run
    AI-powered diagnostics using telemetry and Gemini.
    """
    print("[*] Solicitando análisis de diagnóstico al backend...")
    url = f"{args.url}/api/agent/analyze"
    try:
        req = urllib.request.Request(url, method="POST")
        with urllib.request.urlopen(req, timeout=30.0) as response:
            if response.status == 200:
                res = json.loads(response.read().decode('utf-8'))
                report_text = res.get("report", "")
                source = res.get("source", "gemini_agent")
                print("\n=======================================================")
                print(f" REPORTE AGÉNTICO DE MANTENIMIENTO ({source.upper()}) ")
                print("=======================================================")
                print(report_text)
                print("=======================================================\n")
            else:
                print(f"[\u2717] Error: El servidor respondió con código {response.status}")
    except Exception as e:
        print(f"[\u2717] Error al conectar con el backend para análisis: {str(e)}")

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
    
    # Subcommand: run (devops system operations)
    parser_run = subparsers.add_parser("run", help="Envía una instrucción operativa al agente para planificar y ejecutar mejoras.")
    parser_run.add_argument("instruction", help="Texto de la instrucción de mantenimiento (ej: 'limpiar logs de docker y optimizar sqlite').")
    
    # Subcommand: audit (DB audit history)
    subparsers.add_parser("audit", help="Inspecciona el historial de auditoría de las operaciones realizadas por el agente.")
    
    # Subcommand: logs
    parser_logs = subparsers.add_parser("logs", help="Inspecciona el archivo de logs del agente agéntico en el servidor.")
    parser_logs.add_argument("--lines", type=int, default=30, help="Número de líneas a mostrar (defecto: 30)")
    
    # Subcommand: analyze (AI-powered system agent monitor)
    subparsers.add_parser("analyze", help="Usa el agente de Gemini para analizar logs y hardware y emitir diagnóstico.")
    
    args = parser.parse_args()
    
    if args.command == "health":
        cmd_health(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "audit":
        cmd_audit(args)
    elif args.command == "logs":
        cmd_logs(args)
    elif args.command == "analyze":
        cmd_analyze(args)

if __name__ == "__main__":
    main()
