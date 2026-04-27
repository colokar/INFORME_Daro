# =========================================================
# MÓDULO: CALCULAR RESUMEN POR REGIÓN
# =========================================================
# Procesa datos y calcula valores por región para la tabla
# "RESUMEN POR REGIÓN" del informe CNRT
# =========================================================

import json
import pandas as pd
from datetime import datetime

# =========================================================
# MAPEO: REGIONAL → REGIÓN CNRT
# =========================================================

MAPEO_REGIONALES_REGIONES = {
    # AMBA
    "CNRT-RETIRO": "AMBA",
    "EZEIZA": "AMBA",
    "LA MATANZA": "AMBA",
    "LANUS": "AMBA",
    "PILAR": "AMBA",
    "SAN ISIDRO": "AMBA",
    "CAMPANA": "AMBA",
    "CAPITAL FEDERAL": "AMBA",
    "BUENOS AIRES CAPITAL": "AMBA",
    "RETIRO": "AMBA",
    
    # COSTA ATLÁNTICA
    "MAR DEL PLATA": "COSTA",
    "COSTA": "COSTA",
    "ATLANTICA": "COSTA",
    "NECOCHEA": "COSTA",
    "BAHIA BLANCA": "COSTA",
    
    # BUENOS AIRES
    "LA PLATA": "BA",
    "BUENOS AIRES": "BA",
    "LOMAS": "BA",
    "MORENO": "BA",
    "JUNIN": "BA",
    
    # CENTRO
    "CORDOBA": "CEN",
    "ROSARIO": "CEN",
    "ENTRE RIOS": "CEN",
    "SANTA FE": "CEN",
    "CENTRO": "CEN",
    "PARANÁ": "CEN",
    "GENDARMERIA": "CEN",  # Por defecto va a Centro
    
    # CUYO
    "MENDOZA": "CUY",
    "SAN JUAN": "CUY",
    "SAN LUIS": "CUY",
    "CUYO": "CUY",
    "LA RIOJA": "CUY",
    
    # NEA
    "MISIONES": "NEA",
    "CORRIENTES": "NEA",
    "FORMOSA": "NEA",
    "NEA": "NEA",
    
    # NOA
    "SALTA": "NOA",
    "JUJUY": "NOA",
    "TUCUMAN": "NOA",
    "CATAMARCA": "NOA",
    "SANTIAGO": "NOA",
    "NOA": "NOA",
    
    # PATAGONIA
    "NEUQUEN": "PAT",
    "RIO NEGRO": "PAT",
    "CHUBUT": "PAT",
    "SANTA CRUZ": "PAT",
    "TIERRA": "PAT",
    "PATAGONIA": "PAT",
}

# =========================================================
# FUNCIÓN: MAPEAR REGIONAL A REGIÓN
# =========================================================

def mapear_region(regional_str):
    """
    Convierte nombre de REGIONAL a REGIÓN CNRT.
    Si no encuentra coincidencia, retorna la regional normalizada.
    """
    if not regional_str:
        return None
    
    regional = str(regional_str).upper().strip()
    
    # Buscar coincidencia exacta
    if regional in MAPEO_REGIONALES_REGIONES:
        return MAPEO_REGIONALES_REGIONES[regional]
    
    # Buscar coincidencia parcial (contains)
    for key, value in MAPEO_REGIONALES_REGIONES.items():
        if key in regional:
            return value
    
    # Si no encuentra, retorna None
    return None


# =========================================================
# FUNCIÓN: CALCULAR RESUMEN POR REGIÓN
# =========================================================

def calcular_resumen_por_region(registros, fecha_desde=None, fecha_hasta=None):
    """
    Calcula VC, ACTAS y RET por región y tipo (CARGAS/PASAJEROS).
    
    Parámetros:
    -----------
    registros : list o DataFrame
        Lista/DataFrame de registros con estructura:
        {
            "fecha": "2026-03-20",
            "regional": "ROSARIO",
            "transporte": "CA" o "PA",  # CA=Cargas, PA=Pasajeros
            "retiene": "SI" o "NO"
        }
    
    fecha_desde : str (opcional)
        Fecha mínima en formato "YYYY-MM-DD"
    
    fecha_hasta : str (opcional)
        Fecha máxima en formato "YYYY-MM-DD"
    
    Retorna:
    --------
    dict : {
        "AMBA": {
            "cargas": {"vc": 100, "actas": 20, "ret": 5},
            "pasajeros": {"vc": 150, "actas": 30, "ret": 8},
            "total": {"vc": 250, "actas": 50, "ret": 13}
        },
        ...
        "TOTAL": {...}
    }
    """
    
    # Convertir a DataFrame si es necesario
    if isinstance(registros, list):
        df = pd.DataFrame(registros)
    else:
        df = registros.copy()
    
    # Manejo de datos vacíos
    if df.empty:
        return _crear_resumen_vacio()
    
    # Asegurar que existan las columnas necesarias
    df.columns = df.columns.str.upper()
    
    # ---- FILTRO POR FECHA ----
    if fecha_desde or fecha_hasta:
        try:
            df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")
            
            if fecha_desde:
                fecha_desde_dt = pd.to_datetime(fecha_desde)
                df = df[df["FECHA"] >= fecha_desde_dt]
            
            if fecha_hasta:
                fecha_hasta_dt = pd.to_datetime(fecha_hasta)
                df = df[df["FECHA"] <= fecha_hasta_dt]
        except Exception as e:
            print(f"⚠️  Error en filtro de fechas: {e}")
    
    # ---- MAPEAR REGIONALES A REGIONES ----
    df["REGION"] = df["REGIONAL"].apply(mapear_region)
    
    # Eliminar registros sin región mapeada
    df = df[df["REGION"].notna()]
    
    # ---- NORMALIZAR TRANSPORTE ----
    df["TIPO"] = df["TRANSPORTE"].str.upper().str.strip()
    df["TIPO"] = df["TIPO"].map({
        "CA": "CARGAS",
        "PA": "PASAJEROS"
    })
    
    # Eliminar registros sin tipo válido
    df = df[df["TIPO"].notna()]
    
    # ---- CONTAR RETENCIONES ----
    df["ES_RETENCION"] = df["RETIENE"].str.upper().str.strip() == "SI"
    
    # ---- INICIALIZAR RESULTADO ----
    regiones = ["AMBA", "COSTA", "BA", "CEN", "CUY", "NEA", "NOA", "PAT"]
    resumen = {region: _crear_vacio_region() for region in regiones}
    
    # ---- AGRUPAR Y CONTAR ----
    for region in regiones:
        df_region = df[df["REGION"] == region]
        
        for tipo in ["CARGAS", "PASAJEROS"]:
            df_tipo = df_region[df_region["TIPO"] == tipo]
            
            if not df_tipo.empty:
                vc_count = len(df_tipo)
                actas_count = len(df_tipo[df_tipo["ACTA OBS"].notna() & (df_tipo["ACTA OBS"] != "")])
                ret_count = len(df_tipo[df_tipo["ES_RETENCION"] == True])
                
                resumen[region][tipo.lower()] = {
                    "vc": vc_count,
                    "actas": actas_count,
                    "ret": ret_count
                }
    
    # ---- CALCULAR TOTALES POR REGIÓN ----
    for region in regiones:
        cargas = resumen[region]["cargas"]
        pasajeros = resumen[region]["pasajeros"]
        
        resumen[region]["total"] = {
            "vc": cargas["vc"] + pasajeros["vc"],
            "actas": cargas["actas"] + pasajeros["actas"],
            "ret": cargas["ret"] + pasajeros["ret"]
        }
    
    # ---- TOTAL GENERAL ----
    total_general = {
        "cargas": {"vc": 0, "actas": 0, "ret": 0},
        "pasajeros": {"vc": 0, "actas": 0, "ret": 0},
        "total": {"vc": 0, "actas": 0, "ret": 0}
    }
    
    for region in regiones:
        for tipo in ["cargas", "pasajeros", "total"]:
            for metrica in ["vc", "actas", "ret"]:
                total_general[tipo][metrica] += resumen[region][tipo][metrica]
    
    resumen["TOTAL"] = total_general
    
    return resumen


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def _crear_resumen_vacio():
    """Crea estructura vacía de resumen."""
    regiones = ["AMBA", "COSTA", "BA", "CEN", "CUY", "NEA", "NOA", "PAT"]
    resumen = {region: _crear_vacio_region() for region in regiones}
    resumen["TOTAL"] = {
        "cargas": {"vc": 0, "actas": 0, "ret": 0},
        "pasajeros": {"vc": 0, "actas": 0, "ret": 0},
        "total": {"vc": 0, "actas": 0, "ret": 0}
    }
    return resumen


def _crear_vacio_region():
    """Crea estructura vacía para una región."""
    return {
        "cargas": {"vc": 0, "actas": 0, "ret": 0},
        "pasajeros": {"vc": 0, "actas": 0, "ret": 0},
        "total": {"vc": 0, "actas": 0, "ret": 0}
    }


# =========================================================
# FUNCIÓN: AGREGAR RESUMEN A datos.json
# =========================================================

def guardar_resumen_en_json(resumen, ruta_datos_json="datos.json"):
    """
    Lee datos.json actual, calcula el resumen y lo guarda.
    
    Parámetros:
    -----------
    resumen : dict
        Resultado de calcular_resumen_por_region()
    
    ruta_datos_json : str
        Ruta del archivo datos.json
    """
    try:
        # Leer datos.json existente
        with open(ruta_datos_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
        
        # Agregar resumen
        datos["resumen_por_region"] = resumen
        
        # Guardar actualizado
        with open(ruta_datos_json, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Resumen guardado en {ruta_datos_json}")
        return True
    
    except Exception as e:
        print(f"❌ Error guardando resumen: {e}")
        return False


# =========================================================
# EJEMPLO DE USO
# =========================================================

if __name__ == "__main__":
    
    # Cargar datos.json
    try:
        with open("datos.json", "r", encoding="utf-8") as f:
            datos = json.load(f)
        
        registros = datos.get("registros", [])
        
        # Calcular resumen (sin filtro de fechas)
        resumen = calcular_resumen_por_region(registros)
        
        # Mostrar resultado
        print("\n" + "="*60)
        print("RESUMEN POR REGIÓN")
        print("="*60)
        for region, datos_region in resumen.items():
            print(f"\n{region}:")
            print(f"  Cargas:    VC={datos_region['cargas']['vc']}, "
                  f"ACTAS={datos_region['cargas']['actas']}, "
                  f"RET={datos_region['cargas']['ret']}")
            print(f"  Pasajeros: VC={datos_region['pasajeros']['vc']}, "
                  f"ACTAS={datos_region['pasajeros']['actas']}, "
                  f"RET={datos_region['pasajeros']['ret']}")
            print(f"  Total:     VC={datos_region['total']['vc']}, "
                  f"ACTAS={datos_region['total']['actas']}, "
                  f"RET={datos_region['total']['ret']}")
        
        # Guardar en datos.json
        guardar_resumen_en_json(resumen)
    
    except FileNotFoundError:
        print("❌ No se encontró datos.json")
    except Exception as e:
        print(f"❌ Error: {e}")
