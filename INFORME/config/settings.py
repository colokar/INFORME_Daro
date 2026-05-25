# =========================================================
# CONFIGURACIÓN CENTRALIZADA DEL PROYECTO CNRT
# =========================================================
# 
# Centraliza todas las constantes, rutas y parámetros
# de configuración para fácil mantenimiento y escalabilidad.
# =========================================================

import os
from pathlib import Path

# =========================================================
# DIRECTORIOS BASE
# =========================================================
BASE_DIR = Path(__file__).parent.parent
PROJECT_ROOT = BASE_DIR.parent

EXCEL_DIR = BASE_DIR / "Excel"
ARCHIVOS_PROCESADOS = BASE_DIR / "archivos" / "procesados"
EXCELS_DESCARGADOS = BASE_DIR / "archivos" / "excels_descargados"
LOGS_DIR = BASE_DIR / "logs"

# Crear directorios si no existen
for directory in [EXCEL_DIR, ARCHIVOS_PROCESADOS, EXCELS_DESCARGADOS, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# =========================================================
# ARCHIVOS DE SALIDA
# =========================================================
JSON_SALIDA = BASE_DIR / "datos.json"
LOG_FILE = LOGS_DIR / "procesamiento.log"

# =========================================================
# MAPEO DE REGIONES
# =========================================================
MAPA_REGIONES = {
    "AMBA": [
        "RETIRO", "CAPITAL FEDERAL", "LA PLATA", "EZEIZA", 
        "MATANZA", "BUENOS AIRES", "LANUS", "QUILMES", 
        "AVELLANEDA", "MORON", "LOMAS"
    ],
    "COSTA": ["MAR DEL PLATA", "BAHIA BLANCA", "NECOCHEA"],
    "CEN": [
        "CORDOBA", "ROSARIO", "SANTA FE", "PARANA", 
        "ENTRE RIOS", "RIO CUARTO"
    ],
    "CUY": ["MENDOZA", "SAN JUAN", "SAN LUIS"],
    "NEA": ["CHACO", "CORRIENTES", "FORMOSA", "MISIONES"],
    "NOA": [
        "SALTA", "JUJUY", "TUCUMAN", "SANTIAGO DEL ESTERO", 
        "CATAMARCA", "LA RIOJA"
    ],
    "PAT": [
        "NEUQUEN", "CHUBUT", "RIO NEGRO", "SANTA CRUZ", 
        "TIERRA DEL FUEGO", "USHUAIA", "RIO GALLEGOS"
    ]
}

REGIONES_ORDENADAS = ["AMBA", "CEN", "CUY", "NEA", "NOA", "COSTA", "PAT"]

# =========================================================
# MODOS DE PROCESAMIENTO
# =========================================================
# "A": 1 registro por fila (dominios en lista)
# "B": 1 registro por dominio (expansión)
MODO_PROCESAMIENTO = "A"

# =========================================================
# PARÁMETROS DE FLASK
# =========================================================
FLASK_DEBUG = True
FLASK_PORT = 5000
FLASK_HOST = "127.0.0.1"

# =========================================================
# PARÁMETROS DE DESCARGA AUTOMÁTICA (PLAYWRIGHT)
# =========================================================
CNRT_URL = "https://www.cnrt.gob.ar"  # Reemplazar con URL real
CNRT_USERNAME = os.getenv("CNRT_USERNAME", "")
CNRT_PASSWORD = os.getenv("CNRT_PASSWORD", "")
PLAYWRIGHT_HEADLESS = True
PLAYWRIGHT_TIMEOUT = 30000  # en milisegundos

# =========================================================
# VALIDACIONES DE DATOS
# =========================================================
TIPOS_TRANSPORTE_VALIDOS = ["CA", "PA"]
TIPOS_INCIDENCIA_VALIDOS = ["ALCOHOLEMIA", "SUSTANCIA"]
ARTICULOS_VALIDOS = ["108", "110"]

# =========================================================
# DICCIONARIOS DE INCIDENCIAS
# =========================================================
KEYWORDS_ALCOHOLEMIA = ["POS", "POSITIVO", "+", "ALCOHOL"]
KEYWORDS_SUSTANCIAS = ["POS", "POSITIVO", "+", "SUSTANCIA"]

# =========================================================
# COLUMNAS ESPERADAS EN EXCEL
# =========================================================
COLUMNAS_ESPERADAS = [
    "FECHA", "HORA", "REGIONAL", "LUGAR", 
    "DOMINIO", "DOMINIO2", "DOMINIO3",
    "TRANSPORTE", "ITEMS INFRACCION", "RETIENE",
    "ACTA OBS", "LATITUD", "LONGITUD",
    "ALCOHOLEMIA CHOFER 1", "ALCOHOLEMIA CHOFER 2", "ALCOHOLEMIA CHOFER 3",
    "SUSTANCIAS CHOFER 1", "SUSTANCIAS CHOFER 2", "SUSTANCIAS CHOFER 3"
]

# =========================================================
# LOGGING
# =========================================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
