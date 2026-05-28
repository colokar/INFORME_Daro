import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request
import pandas as pd

# Importamos las variables de tu archivo de configuración central
from config.settings import EXCEL_DIR, MODO_PROCESAMIENTO, FLASK_PORT, FLASK_HOST, FLASK_DEBUG

# Importamos los módulos de procesamiento modular que ya tenemos andando
from procesamiento.limpiar_excel import obtener_archivos_excel, combinar_excels, aplicar_filtro_fechas
from procesamiento.calculos import ProcesadorRegistros
from utils import setup_logger

logger = setup_logger("ServidorWeb")

app = Flask(__name__, 
            static_folder='static',    # Asegura que levante tus CSS/JS
            template_folder='templates') # Asegura que busque tu index.html

@app.route('/')
def index():
    """Ruta principal que sirve la interfaz del Dashboard."""
    # Intentará buscar index.html en tu carpeta templates o raíz según configuración
    try:
        return render_template('index.html')
    except Exception:
        # Por si tenés el index.html suelto en la raíz de INFORME
        root_path = Path(__file__).parent
        if (root_path / "index.html").exists():
            with open(root_path / "index.html", "r", encoding="utf-8") as f:
                return f.read()
        return "Error: No se encontró el archivo index.html en el proyecto.", 404

@app.route('/api/procesar', methods=['POST'])
def procesar_informe_dinamico():
    """
    Punto clave: Recibe las fechas del HTML, lee el Excel crudo en tiempo real,
    aplica filtros, sanea los datos y devuelve el JSON estructurado.
    """
    try:
        # 1. Extraer los rangos de fechas enviados por el usuario desde el HTML
        datos_recibidos = request.get_json() or {}
        fecha_desde = datos_recibidos.get('desde') or request.args.get('desde')
        fecha_hasta = datos_recibidos.get('hasta') or request.args.get('hasta')
        
        logger.info(f"Petición web recibida. Rango solicitado: {fecha_desde} hasta {fecha_hasta}")
        
        # 2. Localizar y combinar los archivos Excel que el usuario pegó en la carpeta
        archivos = obtener_archivos_excel(EXCEL_DIR)
        if not archivos:
            return jsonify({
                "status": "error",
                "message": f"No se encontró ningún archivo Excel en la carpeta interna: {EXCEL_DIR}. Recordá copiar el reporte descargado ahí."
            }), 400
            
        # Combinación nativa de Pandas
        df, _ = combinar_excels(archivos)
        
        # 3. Filtrar por las fechas de los inputs de la web (si el usuario ingresó alguna)
        # Si las fechas vienen vacías, procesará el Excel completo automáticamente
        if (fecha_desde and fecha_desde.strip()) or (fecha_hasta and fecha_hasta.strip()):
            logger.info("Aplicando filtro temporal dinámico de la web...")
            df = aplicar_filtro_fechas(df, fecha_desde, fecha_hasta)
            
        if df.empty:
            return jsonify({
                "status": "error",
                "message": "No se encontraron registros de fiscalización para el rango de fechas seleccionado."
            }), 400
            
        # 4. Procesar y sanear los datos con el motor que arreglamos en calculos.py
        # Esto quita Gendarmería, fiscalizadores fantasmas y arma la clave 'regiones'
        procesador = ProcesadorRegistros(modo=MODO_PROCESAMIENTO)
        resultados = procesador.procesar_dataframe(df)
        
        logger.info("✓ Procesamiento dinámico completado y enviado al navegador.")
        
        # 5. Mandar los datos netos al HTML
        return jsonify(resultados)
        
    except Exception as e:
        logger.error(f"Error procesando la solicitud web: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Ocurrió un error interno en el servidor: {str(e)}"
        }), 500

if __name__ == "__main__":
    logger.info(f"Iniciando Dashboard en modo interactivo: http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG
    )