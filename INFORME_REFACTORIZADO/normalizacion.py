import re
import unicodedata
import pandas as pd
from config import REGION_MAP


def normalizar_texto(texto):
    if pd.isna(texto) or texto is None:
        return ""

    texto = str(texto).strip().lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = texto.replace('ñ', 'n')
    texto = re.sub(r'[^a-z0-9 ]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def normalizar_region(valor):
    if valor is None or pd.isna(valor) or str(valor).strip() == "":
        return "SIN_REGION"

    texto_norm = normalizar_texto(valor)
    for region, nombres in REGION_MAP.items():
        for nombre in nombres:
            if normalizar_texto(nombre) in texto_norm:
                return region

    return "SIN_REGION"


def convertir_dms_a_decimal(coordenada):
    if coordenada is None or pd.isna(coordenada):
        return None

    try:
        coord_str = str(coordenada).strip()
        patron = r"(\d+)[º°](\d+)[\''](\d+(?:\.\d+)?)[\"″]([NSEW])"
        match = re.search(patron, coord_str)
        if not match:
            return None

        grados = float(match.group(1))
        minutos = float(match.group(2))
        segundos = float(match.group(3))
        direccion = match.group(4).upper()

        decimal = grados + minutos / 60 + segundos / 3600
        if direccion in {"S", "W"}:
            decimal = -decimal

        return round(decimal, 6)
    except Exception:
        return None
