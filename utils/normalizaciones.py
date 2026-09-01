# =========================================================
# UTILIDADES DE NORMALIZACIÓN Y VALIDACIÓN
# =========================================================
# 
# Funciones para normalizar texto, regiones, coordenadas
# y detectar incidencias en los datos.
# =========================================================

import re
import unicodedata
import pandas as pd
from typing import Tuple, Optional, List
from config.settings import MAPA_REGIONES, KEYWORDS_ALCOHOLEMIA, KEYWORDS_SUSTANCIAS

def normalizar(texto: str) -> str:
    """
    Normaliza texto: minúsculas, sin acentos, caracteres especiales.
    
    Args:
        texto: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    if pd.isna(texto):
        return ""
    
    texto = str(texto).lower()
    # Remover acentos
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) 
                   if unicodedata.category(c) != 'Mn')
    texto = texto.replace("ñ", "n")
    # Remover caracteres especiales
    texto = re.sub(r"[^a-z0-9 ]", " ", texto)
    # Limpiar espacios múltiples
    return re.sub(r"\s+", " ", texto).strip()

def normalizar_region(valor: str) -> str:
    """
    Mapea un texto de región a su código normalizado (AMBA, CEN, etc).
    
    Args:
        valor: Texto de región a mapear
        
    Returns:
        Código de región o "SIN_REGION" si no se encuentra
    """
    if not valor or pd.isna(valor):
        return "SIN_REGION"
    
    texto_norm = normalizar(valor)
    
    for region, nombres in MAPA_REGIONES.items():
        for nombre in nombres:
            if normalizar(nombre) in texto_norm:
                return region
    
    return "SIN_REGION"

def convertir_dms_a_decimal(coordenada: str) -> Optional[float]:
    """
    Convierte coordenadas DMS (grados/minutos/segundos) a decimal.
    
    Ejemplo: 34°12'45"S  →  -34.2125
    
    Args:
        coordenada: Coordenada en formato DMS
        
    Returns:
        Coordenada decimal o None si no se puede convertir
    """
    if not coordenada or pd.isna(coordenada):
        return None
    
    try:
        coord_str = str(coordenada).strip()
        patron = r"(\d+)[º°](\d+)['\'](\d+(?:\.\d+)?)[\"″]([NSEW])"
        match = re.search(patron, coord_str)
        
        if not match:
            return None
        
        grados = float(match.group(1))
        minutos = float(match.group(2))
        segundos = float(match.group(3))
        direccion = match.group(4).upper()
        
        decimal = grados + (minutos / 60) + (segundos / 3600)
        
        if direccion in ['S', 'W']:
            decimal = -decimal
        
        return round(decimal, 6)
    except:
        return None

def detectar_incidencia(fila: pd.Series) -> Tuple[Optional[str], Optional[str]]:
    """
    Detecta incidencias de alcoholemia o sustancias en una fila.
    
    Args:
        fila: Fila del DataFrame con datos de fiscalización
        
    Returns:
        Tupla (tipo_incidencia, columna_fuente) o (None, None)
    """
    # ---- ALCOHOLEMIA ----
    for col in ["ALCOHOLEMIA CHOFER 1", "ALCOHOLEMIA CHOFER 2", "ALCOHOLEMIA CHOFER 3"]:
        if col not in fila:
            continue
        
        valor = str(fila[col]).upper().strip()
        
        if valor and any(x in valor for x in KEYWORDS_ALCOHOLEMIA):
            try:
                # Intentar convertir a número (para validar si es positivo)
                val = float(valor.replace(",", "."))
                if val > 0:
                    return "ALCOHOLEMIA", col
            except:
                # Si no es número pero contiene keyword, asumir positivo
                return "ALCOHOLEMIA", col
    
    # ---- SUSTANCIAS ----
    for col in ["SUSTANCIAS CHOFER 1", "SUSTANCIAS CHOFER 2", "SUSTANCIAS CHOFER 3"]:
        if col not in fila:
            continue
        
        valor = str(fila[col]).upper().strip()
        
        if valor and any(x in valor for x in KEYWORDS_SUSTANCIAS):
            return "SUSTANCIA", col
    
    # ---- BÚSQUEDA EN OBSERVACIONES ----
    obs = str(fila.get("ACTA OBS", "")).upper()
    texto_obs = normalizar(obs)
    
    if any(x in texto_obs for x in [
        "sustancia positiva",
        "test droga positivo",
        "positivo sustancia"
    ]):
        return "SUSTANCIA", "ACTA OBS"
    
    if any(x in texto_obs for x in [
        "alcohol positivo",
        "alcoholimetro"
    ]):
        return "ALCOHOLEMIA", "ACTA OBS"
    
    return None, None

def elegir_articulo(transporte: str, items: str) -> str:
    """
    Selecciona el artículo correspondiente según transporte e items de infracción.
    
    Art. 108: Cargas
    Art. 110: Pasajeros
    
    Args:
        transporte: Tipo de transporte (CA=Cargas, PA=Pasajeros)
        items: Items de infracción
        
    Returns:
        Código de artículo ("108", "110", o "")
    """
    t = str(transporte).lower()
    infr = str(items)
    
    tiene108 = "108" in infr
    tiene110 = "110" in infr
    
    if "carg" in t:
        return "108" if tiene108 else ("110" if tiene110 else "")
    
    if "pasaj" in t:
        return "110" if tiene110 else ("108" if tiene108 else "")
    
    return "108" if tiene108 else ("110" if tiene110 else "")

def validar_fila(fila: pd.Series) -> bool:
    """
    Valida si una fila tiene los datos mínimos requeridos.
    
    Args:
        fila: Fila del DataFrame
        
    Returns:
        True si es válida, False en caso contrario
    """
    transporte = str(fila.get("TRANSPORTE", "")).strip().upper()
    return transporte in ["CA", "PA"]
