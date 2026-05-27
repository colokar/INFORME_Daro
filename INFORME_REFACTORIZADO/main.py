# =========================================================
# MAIN.PY - PUNTO DE ENTRADA PRINCIPAL
# =========================================================
#
# FLUJO COMPLETO:
# 1. Procesa datos de Excel
# 2. Inicia servidor Flask
#
# IMPORTANTE:
# - Ejecutar SOLO este archivo
# - NO ejecutar app.py o procesador.py directamente
# - Evita doble ejecución y problemas de reloader
# =========================================================

import sys
import argparse
from pathlib import Path

from procesador import procesar_completo
from app import app
from config import FLASK_PORT
from utils import imprimir_titulo, imprimir_info, imprimir_ok


def main():
    """Punto de entrada principal del sistema."""
    
    # =========================================================
    # PARSE ARGUMENTOS
    # =========================================================
    
    parser = argparse.ArgumentParser(
        description="Sistema CNRT - Procesamiento de Fiscalizaciones"
    )
    parser.add_argument(
        "--modo",
        choices=["A", "B"],
        default="A",
        help="Modo de procesamiento (A: por fila, B: por dominio)"
    )
    parser.add_argument(
        "--desde",
        help="Fecha desde (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--hasta",
        help="Fecha hasta (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--solo-procesar",
        action="store_true",
        help="Solo procesar, no iniciar servidor"
    )
    parser.add_argument(
        "--solo-servidor",
        action="store_true",
        help="Solo iniciar servidor (sin procesar)"
    )
    
    args = parser.parse_args()
    
    # =========================================================
    # FLUJO PRINCIPAL
    # =========================================================
    
    # Opción 1: Solo procesar
    if args.solo_procesar:
        if procesar_completo(modo=args.modo, fecha_desde=args.desde, fecha_hasta=args.hasta):
            imprimir_ok("Procesamiento completado")
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Opción 2: Solo servidor
    if args.solo_servidor:
        imprimir_titulo("INICIANDO SERVIDOR WEB")
        imprimir_info(f"URL: http://127.0.0.1:{FLASK_PORT}")
        print()
        app.run(debug=True, use_reloader=False, host="127.0.0.1", port=FLASK_PORT)
        return
    
    # Opción 3: Procesamiento + Servidor (DEFAULT)
    imprimir_titulo("SISTEMA CNRT - MODO COMPLETO")
    print()
    
    # Procesar
    if not procesar_completo(modo=args.modo, fecha_desde=args.desde, fecha_hasta=args.hasta):
        imprimir_info("Abortando: No se pudo procesar los datos")
        sys.exit(1)
    
    # Iniciar servidor
    imprimir_titulo("INICIANDO SERVIDOR WEB")
    imprimir_info(f"URL: http://127.0.0.1:{FLASK_PORT}")
    imprimir_info("Presione CTRL+C para detener el servidor")
    print()
    
    try:
        app.run(debug=True, use_reloader=False, host="127.0.0.1", port=FLASK_PORT)
    except KeyboardInterrupt:
        print()
        imprimir_ok("Servidor detenido")
        sys.exit(0)


if __name__ == "__main__":
    main()
