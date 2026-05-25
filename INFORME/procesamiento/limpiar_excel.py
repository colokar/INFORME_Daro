# =========================================================
# MÓDULO: LIMPIEZA Y LECTURA DE ARCHIVOS EXCEL
# =========================================================
# 
# Responsable de:
# - Buscar archivos Excel en la carpeta de descargas
# - Limpiar datos
# - Normalizar columnas
# - Aplicar filtros de fecha
# =========================================================

import os
import glob
import pandas as pd
import unicodedata
import re
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

from config.settings import EXCEL_DIR, MODO_PROCESAMIENTO
from utils import setup_logger, validar_fila, normalizar_region

logger = setup_logger(__name__)

def obtener_archivos_excel(directorio: Path = None) -> List[Path]:
    """
    Obtiene lista de archivos Excel válidos en un directorio.
    
    Args:
        directorio: Directorio donde buscar (usa EXCEL_DIR si no se especifica)
        
    Returns:
        Lista de rutas de archivos Excel
    """
    if directorio is None:
        directorio = EXCEL_DIR
    
    archivos = []
    for ext in ["*.xls", "*.xlsx"]:
        for archivo in glob.glob(os.path.join(directorio, ext)):
            # Evitar archivos temporales
            if "~$" not in os.path.basename(archivo):
                archivos.append(Path(archivo))
    
    return sorted(archivos)

def leer_excel(archivo: Path) -> Optional[pd.DataFrame]:
    """
    Lee un archivo Excel detectando automáticamente el engine.
    
    Args:
        archivo: Ruta del archivo Excel
        
    Returns:
        DataFrame leído o None si hay error
    """
    try:
        engine = "xlrd" if str(archivo).lower().endswith(".xls") else "openpyxl"
        df = pd.read_excel(archivo, engine=engine, header=0)
        
        # Remover filas completamente vacías
        df = df.dropna(how="all")
        
        # Remover columnas duplicadas
        df = df.loc[:, ~df.columns.duplicated()]
        
        return df
    except Exception as e:
        logger.error(f"Error leyendo {archivo.name}: {e}")
        return None

def limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y normaliza un DataFrame.
    
    Args:
        df: DataFrame a limpiar
        
    Returns:
        DataFrame limpio
    """
    # Normalizar nombres de columnas
    df.columns = df.columns.str.strip().str.upper()
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Limpiar columnas de texto
    columnas_texto = [
        "DOMINIO", "DOMINIO2", "DOMINIO3",
        "REGIONAL", "TRANSPORTE", "FECHA", "HORA",
        "ACTA OBS", "RETIENE", "ITEMS INFRACCION", "LUGAR"
    ]
    
    for col in columnas_texto:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip().str.upper()
    
    # Normalizar REGIONAL (remover acentos)
    if "REGIONAL" in df.columns:
        df["REGIONAL"] = df["REGIONAL"].apply(
            lambda x: ''.join(c for c in unicodedata.normalize('NFD', x) 
                            if unicodedata.category(c) != 'Mn')
        )
        # Remover guiones raros y normalizar espacios
        df["REGIONAL"] = (
            df["REGIONAL"]
            .str.replace("–", "-")
            .str.replace("—", "-")
            .str.replace("_", " ")
            .apply(lambda x: re.sub(r"\s+", " ", x).strip())
        )
    
    # Mapear región
    if "REGIONAL" in df.columns:
        df["REGION_NORMALIZADA"] = df["REGIONAL"].apply(normalizar_region)
    
    return df

def combinar_excels(archivos: List[Path]) -> Tuple[pd.DataFrame, int]:
    """
    Combina múltiples archivos Excel en un solo DataFrame.
    
    Args:
        archivos: Lista de rutas de archivos
        
    Returns:
        Tupla (DataFrame combinado, total de filas)
    """
    dfs = []
    total_filas = 0
    
    logger.info(f"Leyendo {len(archivos)} archivo(s) Excel...")
    
    for idx, archivo in enumerate(archivos, 1):
        logger.info(f"  [{idx}] {archivo.name}")
        
        df = leer_excel(archivo)
        if df is None:
            continue
        
        filas = len(df)
        total_filas += filas
        dfs.append(df)
        logger.info(f"      ✓ {filas:,} filas leídas")
    
    if not dfs:
        logger.error("No se pudo leer ningún archivo Excel")
        raise ValueError("No hay datos para procesar")
    
    df_combinado = pd.concat(dfs, ignore_index=True)
    df_combinado = limpiar_dataframe(df_combinado)
    
    logger.info(f"Total combinado: {total_filas:,} filas")
    logger.info(f"Total después de limpieza: {len(df_combinado):,} filas")
    
    return df_combinado, total_filas

def aplicar_filtro_fechas(
    df: pd.DataFrame,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None
) -> pd.DataFrame:
    """
    Aplica filtro de fechas a un DataFrame.
    
    Args:
        df: DataFrame con columna FECHA
        fecha_desde: Fecha inicio (formato YYYY-MM-DD)
        fecha_hasta: Fecha fin (formato YYYY-MM-DD)
        
    Returns:
        DataFrame filtrado
    """
    if not fecha_desde and not fecha_hasta:
        return df
    
    try:
        if fecha_desde:
            fecha_desde_dt = pd.to_datetime(fecha_desde, format="%Y-%m-%d")
        else:
            fecha_desde_dt = pd.to_datetime("1900-01-01")
        
        if fecha_hasta:
            fecha_hasta_dt = pd.to_datetime(fecha_hasta, format="%Y-%m-%d")
        else:
            fecha_hasta_dt = pd.to_datetime("2099-12-31")
        
        df["FECHA_TEMP"] = pd.to_datetime(df["FECHA"], format="%Y-%m-%d", errors="coerce")
        
        rows_antes = len(df)
        df = df[(df["FECHA_TEMP"] >= fecha_desde_dt) & (df["FECHA_TEMP"] <= fecha_hasta_dt)]
        df = df.drop("FECHA_TEMP", axis=1)
        
        logger.info(f"Filtro de fechas: {rows_antes:,} → {len(df):,} registros")
        
        return df
    except Exception as e:
        logger.error(f"Error aplicando filtro de fechas: {e}")
        return df

def validar_integridad(df: pd.DataFrame) -> dict:
    """
    Valida la integridad de los datos y retorna estadísticas.
    
    Args:
        df: DataFrame a validar
        
    Returns:
        Diccionario con estadísticas de validación
    """
    stats = {
        "total_filas": len(df),
        "filas_validas": 0,
        "filas_invalidas": 0,
        "regiones_sin_mapear": 0,
        "regiones_mapeadas": {}
    }
    
    for _, fila in df.iterrows():
        if validar_fila(fila):
            stats["filas_validas"] += 1
        else:
            stats["filas_invalidas"] += 1
    
    # Estadísticas por región
    if "REGION_NORMALIZADA" in df.columns:
        region_counts = df["REGION_NORMALIZADA"].value_counts()
        stats["regiones_sin_mapear"] = region_counts.get("SIN_REGION", 0)
        stats["regiones_mapeadas"] = region_counts[region_counts.index != "SIN_REGION"].to_dict()
    
    return stats

def log_estadisticas_excel(df: pd.DataFrame, stats: dict):
    """
    Registra estadísticas de los datos leídos.
    
    Args:
        df: DataFrame procesado
        stats: Diccionario de estadísticas
    """
    logger.info(f"\n{'='*60}")
    logger.info("ESTADÍSTICAS DE INTEGRIDAD")
    logger.info(f"{'='*60}")
    logger.info(f"Total de filas: {stats['total_filas']:,}")
    logger.info(f"Filas válidas: {stats['filas_validas']:,}")
    logger.info(f"Filas inválidas: {stats['filas_invalidas']:,}")
    logger.info(f"Regiones sin mapear: {stats['regiones_sin_mapear']:,}")
    
    if stats['regiones_mapeadas']:
        logger.info(f"\nDistribución por región:")
        for region, count in sorted(stats['regiones_mapeadas'].items()):
            logger.info(f"  {region}: {count:,}")
