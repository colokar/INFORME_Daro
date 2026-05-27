from pathlib import Path

# =========================================================
# RUTAS BASE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
EXCEL_FOLDER = BASE_DIR / "Excel"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Crear directorios si no existen
for directory in [EXCEL_FOLDER, LOGS_DIR, TEMPLATES_DIR, STATIC_DIR]:
    directory.mkdir(exist_ok=True)

# =========================================================
# ARCHIVOS DE SALIDA
# =========================================================

DATOS_JSON_PATH = BASE_DIR / "datos.json"
LOG_FILE = LOGS_DIR / "procesamiento.log"

# =========================================================
# CONFIGURACIÓN FLASK
# =========================================================

FLASK_DEBUG = True
FLASK_USE_RELOADER = False  # IMPORTANTE: Evita doble ejecución
FLASK_PORT = 5000

# =========================================================
# MAPA DE REGIONES NORMALIZADAS
# =========================================================

REGION_MAP = {
    "AMBA": [
        "RETIRO", "CAPITAL FEDERAL", "LA PLATA", "EZEIZA", "MATANZA",
        "BUENOS AIRES", "LANUS", "QUILMES", "AVELLANEDA", "MORON", "LOMAS"
    ],
    "COSTA": ["MAR DEL PLATA", "BAHIA BLANCA", "NECOCHEA"],
    "CEN": ["CORDOBA", "ROSARIO", "SANTA FE", "PARANA", "ENTRE RIOS", "RIO CUARTO"],
    "CUY": ["MENDOZA", "SAN JUAN", "SAN LUIS"],
    "NEA": ["CHACO", "CORRIENTES", "FORMOSA", "MISIONES"],
    "NOA": ["SALTA", "JUJUY", "TUCUMAN", "SANTIAGO DEL ESTERO", "CATAMARCA", "LA RIOJA"],
    "PAT": ["NEUQUEN", "CHUBUT", "RIO NEGRO", "SANTA CRUZ", "TIERRA DEL FUEGO", "USHUAIA", "RIO GALLEGOS"]
}

REGIONES_ORDENADAS = ["AMBA", "CEN", "CUY", "NEA", "NOA", "COSTA", "PAT"]

# =========================================================
# TRANSPORTES VÁLIDOS
# =========================================================

VALID_TRANSPORTES = {"CA", "PA"}

# =========================================================
# MODOS DE PROCESAMIENTO
# =========================================================

DEFAULT_MODO = "A"  # A: 1 registro por fila, B: 1 registro por dominio

# =========================================================
# FORMATO DE LOGS
# =========================================================

LOG_DIVIDER = "=" * 60
LOG_FORMAT = "[%(levelname)s] %(message)s"
LOG_LEVEL = "INFO"

# =========================================================
# REGLAS DE SANEAMIENTO
# =========================================================

FILTROS_SANEAMIENTO = {
    "eliminar_gendarmeria": True,
    "eliminar_regional_vacio": True,
    "eliminar_fiscalizador_vacio": True,
    "eliminar_transporte_invalido": True
}
