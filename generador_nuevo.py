"""Genera datos para el informe y, salvo --solo-procesar, inicia Flask."""
import argparse

from app import app, procesar_datos

parser = argparse.ArgumentParser(description="Generador del informe operativo CNRT")
parser.add_argument("--desde", help="Fecha inicial (YYYY-MM-DD)")
parser.add_argument("--hasta", help="Fecha final (YYYY-MM-DD)")
parser.add_argument("--solo-procesar", action="store_true", help="Genera datos.json sin iniciar el servidor")
args = parser.parse_args()

resultado = procesar_datos(args.desde, args.hasta)
print(f"Datos generados: {resultado['metadata']['total_registros']:,} registros.")
if not args.solo_procesar:
    app.run(host="127.0.0.1", port=5000, debug=False)
