"""
Módulo de utilidades
"""
from .logger import setup_logger, titulo, subtitulo
from .normalizaciones import (
    normalizar, normalizar_region, convertir_dms_a_decimal,
    detectar_incidencia, elegir_articulo, validar_fila
)

__all__ = [
    'setup_logger', 'titulo', 'subtitulo',
    'normalizar', 'normalizar_region', 'convertir_dms_a_decimal',
    'detectar_incidencia', 'elegir_articulo', 'validar_fila'
]
