"""
Módulo de procesamiento de datos CNRT
"""
from .limpiar_excel import (
    obtener_archivos_excel, leer_excel, limpiar_dataframe,
    combinar_excels, aplicar_filtro_fechas, validar_integridad,
    log_estadisticas_excel
)
from .calcular_metricas import ProcesadorRegistros, procesar_datos

__all__ = [
    'obtener_archivos_excel', 'leer_excel', 'limpiar_dataframe',
    'combinar_excels', 'aplicar_filtro_fechas', 'validar_integridad',
    'log_estadisticas_excel', 'ProcesadorRegistros', 'procesar_datos'
]
