# =========================================================
# SISTEMA DE LOGGING CENTRALIZADO
# =========================================================
# 
# Proporciona logging a consola y archivo
# con distintos niveles y formatos.
# =========================================================

import logging
import sys
from pathlib import Path
from config.settings import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT, LOG_FILE

def setup_logger(name: str, log_file: Path = None) -> logging.Logger:
    """
    Configura un logger con manejo a consola y archivo.
    
    Args:
        name: Nombre del módulo/logger
        log_file: Ruta del archivo de log (usa default si no se especifica)
        
    Returns:
        Logger configurado
    """
    if log_file is None:
        log_file = LOG_FILE
    
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Evitar duplicar handlers
    if logger.hasHandlers():
        return logger
    
    # Formato
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    # Handler: Consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler: Archivo
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"No se pudo crear archivo de log: {e}")
    
    return logger

def titulo(texto: str):
    """Imprime un título formateado."""
    logger = logging.getLogger("CNRT")
    line = "=" * 60
    logger.info(f"\n{line}\n{texto.center(60)}\n{line}")

def subtitulo(texto: str):
    """Imprime un subtítulo formateado."""
    logger = logging.getLogger("CNRT")
    logger.info(f"\n--- {texto} ---")
