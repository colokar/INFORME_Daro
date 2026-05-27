# =========================================================
# SANEAMIENTO.PY - ETAPA 2: LIMPIEZA Y VALIDACIÓN
# =========================================================
# Implementa el procedimiento operativo real de CNRT
# 
# REGLA FUNDAMENTAL:
# Estos registros se ELIMINAN FÍSICAMENTE del DataFrame
# ANTES de cualquier procesamiento, conteo o métrica:
#
# 1. REGIONAL == "GENDARMERIA"
# 2. REGIONAL vacío
# 3. FISCALIZADOR1 vacío
#
# Estos registros NO deben:
# - contarse
# - procesarse
# - generar métricas
# - generar actas
# - generar incidencias
# =========================================================

import pandas as pd
from utils import imprimir_titulo, imprimir_info, imprimir_warning, imprimir_ok


def limpiar_whitespace(df, columnas_texto):
    """Limpia espacios en blanco de columnas de texto."""
    df = df.copy()
    for col in columnas_texto:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
    return df


def saneamiento_base(df):
    """
    ETAPA 2: SANEAMIENTO OBLIGATORIO
    
    Elimina registros que NO cumplen con los criterios operativos.
    Retorna: (df_saneado, estadísticas_saneamiento)
    """
    
    imprimir_titulo("ETAPA 2: SANEAMIENTO DE BASE DE DATOS")
    
    # Tomar copia para no modificar original
    df = df.copy()
    
    # Registros iniciales
    total_original = len(df)
    imprimir_info(f"Registros originales: {total_original:,}")
    
    # =========================================================
    # PASO 1: Normalizar columnas críticas para saneamiento
    # =========================================================
    
    columnas_criticas = ["REGIONAL", "FISCALIZADOR1", "FISCALIZADOR"]
    df = limpiar_whitespace(df, columnas_criticas)
    
    # Crear columna normalizada si no existe
    if "REGIONAL" not in df.columns:
        df["REGIONAL"] = ""
    
    # =========================================================
    # PASO 2: ELIMINAR REGIONAL == "GENDARMERIA"
    # =========================================================
    
    gendarmeria_antes = len(df)
    df = df[df["REGIONAL"].str.upper() != "GENDARMERIA"]
    gendarmeria_eliminados = gendarmeria_antes - len(df)
    
    if gendarmeria_eliminados > 0:
        imprimir_warning(f"Registros eliminados (REGIONAL=GENDARMERIA): {gendarmeria_eliminados:,}")
    else:
        imprimir_ok("No hay registros de GENDARMERIA")
    
    # =========================================================
    # PASO 3: ELIMINAR REGIONAL VACÍO
    # =========================================================
    
    regional_vacio_antes = len(df)
    df = df[
        (df["REGIONAL"].notna()) & 
        (df["REGIONAL"].str.strip() != "") &
        (df["REGIONAL"].astype(str) != "nan")
    ]
    regional_vacio_eliminados = regional_vacio_antes - len(df)
    
    if regional_vacio_eliminados > 0:
        imprimir_warning(f"Registros eliminados (REGIONAL vacío): {regional_vacio_eliminados:,}")
    else:
        imprimir_ok("No hay REGIONAL vacío")
    
    # =========================================================
    # PASO 4: ELIMINAR FISCALIZADOR VACÍO
    # =========================================================
    
    # Buscar columna FISCALIZADOR (puede ser FISCALIZADOR1 o similar)
    fiscal_col = None
    for col in ["FISCALIZADOR1", "FISCALIZADOR", "FISCALIZADOR_1"]:
        if col in df.columns:
            fiscal_col = col
            break
    
    if fiscal_col:
        df = limpiar_whitespace(df, [fiscal_col])
        fiscal_vacio_antes = len(df)
        df = df[
            (df[fiscal_col].notna()) & 
            (df[fiscal_col].str.strip() != "") &
            (df[fiscal_col].astype(str) != "nan")
        ]
        fiscal_vacio_eliminados = fiscal_vacio_antes - len(df)
        
        if fiscal_vacio_eliminados > 0:
            imprimir_warning(f"Registros eliminados ({fiscal_col} vacío): {fiscal_vacio_eliminados:,}")
        else:
            imprimir_ok(f"No hay {fiscal_col} vacío")
    else:
        fiscal_vacio_eliminados = 0
        imprimir_info("Nota: No se encontró columna FISCALIZADOR")
    
    # =========================================================
    # PASO 5: ELIMINAR TRANSPORTE INVÁLIDO
    # =========================================================
    
    if "TRANSPORTE" in df.columns:
        df = limpiar_whitespace(df, ["TRANSPORTE"])
        transporte_vacio_antes = len(df)
        df = df[df["TRANSPORTE"].str.upper().isin(["CA", "PA"])]
        transporte_vacio_eliminados = transporte_vacio_antes - len(df)
        
        if transporte_vacio_eliminados > 0:
            imprimir_warning(f"Registros eliminados (TRANSPORTE inválido): {transporte_vacio_eliminados:,}")
    else:
        transporte_vacio_eliminados = 0
    
    # =========================================================
    # RESUMEN DE SANEAMIENTO
    # =========================================================
    
    total_saneado = len(df)
    total_eliminados = total_original - total_saneado
    
    print()
    imprimir_ok(f"Base saneada correctamente")
    print()
    imprimir_info(f"Registros originales:        {total_original:,}")
    imprimir_info(f"Registros eliminados:       {total_eliminados:,}")
    imprimir_info(f"Registros válidos:          {total_saneado:,}")
    print()
    
    if total_saneado == 0:
        imprimir_warning("⚠️  ADVERTENCIA CRÍTICA: Base de datos completamente vacía después del saneamiento")
    
    # =========================================================
    # ESTADÍSTICAS DE SANEAMIENTO
    # =========================================================
    
    estadisticas = {
        "total_original": total_original,
        "total_saneado": total_saneado,
        "total_eliminados": total_eliminados,
        "desglose": {
            "gendarmeria": gendarmeria_eliminados,
            "regional_vacio": regional_vacio_eliminados,
            "fiscalizador_vacio": fiscal_vacio_eliminados,
            "transporte_invalido": transporte_vacio_eliminados
        }
    }
    
    return df.reset_index(drop=True), estadisticas


def validar_saneamiento(df_original, df_saneado, estadisticas):
    """
    Valida que el saneamiento fue correctamente aplicado.
    """
    
    imprimir_titulo("VALIDACIÓN DE SANEAMIENTO")
    
    # Verificar que no hay GENDARMERIA
    if "REGIONAL" in df_saneado.columns:
        gendarmeria_count = (df_saneado["REGIONAL"].str.upper() == "GENDARMERIA").sum()
        if gendarmeria_count > 0:
            imprimir_warning(f"⚠️  ERROR: Encontrados {gendarmeria_count:,} registros GENDARMERIA después del saneamiento")
        else:
            imprimir_ok("✓ No hay GENDARMERIA")
    
    # Verificar que no hay REGIONAL vacío
    if "REGIONAL" in df_saneado.columns:
        regional_vacio = (df_saneado["REGIONAL"].astype(str) == "").sum()
        if regional_vacio > 0:
            imprimir_warning(f"⚠️  ERROR: Encontrados {regional_vacio:,} registros con REGIONAL vacío")
        else:
            imprimir_ok("✓ No hay REGIONAL vacío")
    
    # Verificación matemática
    suma_desglose = sum(estadisticas["desglose"].values())
    total_eliminados = estadisticas["total_eliminados"]
    
    if suma_desglose == total_eliminados:
        imprimir_ok(f"✓ Consistencia: suma de desglose ({suma_desglose:,}) = total eliminados ({total_eliminados:,})")
    else:
        imprimir_warning(f"⚠️  Inconsistencia: suma ({suma_desglose:,}) ≠ total ({total_eliminados:,})")
    
    print()
