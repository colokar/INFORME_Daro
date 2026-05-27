# =========================================================
# APP.PY - SERVIDOR FLASK (SIN PROCESAMIENTO)
# =========================================================
# 
# IMPORTANTE:
# - SOLO contiene rutas Flask
# - NO ejecuta procesamiento automáticamente
# - NO usa reloader para evitar doble ejecución
# - El procesamiento se ejecuta desde procesador.py
# =========================================================

import json
import logging
from pathlib import Path
from flask import Flask, jsonify, render_template

from config import DATOS_JSON_PATH

# =========================================================
# CONFIGURACIÓN FLASK
# =========================================================

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["JSON_AS_ASCII"] = False
logging.getLogger("werkzeug").setLevel(logging.WARNING)


# =========================================================
# RUTAS
# =========================================================

@app.route("/")
def index():
    """Sirve la página principal."""
    return render_template("index.html")


@app.route("/resumen")
def get_resumen():
    """Devuelve el JSON procesado."""
    try:
        if not Path(DATOS_JSON_PATH).exists():
            return jsonify({
                "error": "datos.json no encontrado",
                "instrucciones": "Ejecute: python procesador.py"
            }), 404
        
        with open(DATOS_JSON_PATH, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return jsonify(datos)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Error JSON: {e}"}), 500
    except Exception as error:
        return jsonify({"error": str(error)}), 500


# =========================================================
# NOTA: Este archivo SOLO se ejecuta como módulo
# NO se ejecuta directamente. Ver main.py
# =========================================================
