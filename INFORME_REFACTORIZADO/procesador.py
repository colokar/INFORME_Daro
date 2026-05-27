# =========================================================
# PROCESADOR.PY - ORQUESTADOR PRINCIPAL
# =========================================================
# Coordina todo el flujo de procesamiento:
#
# ETAPA 1: DESCARGA (archivos Excel)
# ETAPA 2: SANEAMIENTO (elimina registros inválidos)
# ETAPA 3: PROCESAMIENTO (normalizacion y cálculos)
# ETAPA 4: ACTAS/GLOSARIO (clasificación)
# ETAPA 5: EXPORTACIÓN (genera datos.json)
# =========================================================

import glob
import json
from pathlib import Path
import pandas as pd
import unicodedata
import re

from config import DATOS_JSON_PATH, EXCEL_FOLDER, DEFAULT_MODO, VALID_TRANSPORTES, REGIONES_ORDENADAS
from incidencias import detectar_incidencia, elegir_articulo
from normalizacion import convertir_dms_a_decimal, normalizar_region
from reportes import crear_resumen_regiones, crear_salida_json
from saneamiento import saneamiento_base, validar_saneamiento
from utils import imprimir_error, imprimir_info, imprimir_ok, imprimir_titulo, imprimir_warning


# =========================================================
# ETAPA 1: DESCARGA
# =========================================================

def leer_archivos_excel(carpeta_excels):
    """Lee todos los archivos Excel de la carpeta."""
    ruta = Path(carpeta_excels)
    archivos = [Path(path) for path in glob.glob(str(ruta / "*.xls*")) if "~$" not in Path(path).name]
    
    if not archivos:
        return [], 0

    imprimir_titulo("ETAPA 1: DESCARGA DE ARCHIVOS")
    
    dfs = []
    total_filas = 0

    for idx, archivo in enumerate(sorted(archivos), 1):
        nombre = archivo.name
        imprimir_info(f"[{idx}/{len(archivos)}] Procesando: {nombre}")
        try:
            if archivo.suffix.lower() == ".xls":
                df_temp = pd.read_excel(archivo, engine="xlrd")
            else:
                df_temp = pd.read_excel(archivo, engine="openpyxl", header=0)

            df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
            df_temp = df_temp.dropna(how="all")
            filas = df_temp.shape[0]
            total_filas += filas
            dfs.append(df_temp)
            imprimir_ok(f"{filas:,} filas")
        except Exception as err:
            imprimir_warning(f"ERROR al leer {nombre}: {err}")

    if dfs:
        imprimir_ok(f"Total descargado: {total_filas:,} filas en {len(dfs)} archivo(s)")
        print()
    
    return dfs, total_filas


# =========================================================
# Normalización de DataFrame
# =========================================================

def normalizar_dataframe(df):
    """Normaliza columnas y estructura del DataFrame."""
    df = df.copy()
    df.columns = df.columns.str.strip().str.upper()
    df = df.loc[:, ~df.columns.duplicated()]

    # Crear columnas faltantes
    columnas_esperadas = [
        "DOMINIO", "DOMINIO2", "DOMINIO3", "REGIONAL", "TRANSPORTE", "FECHA", "HORA",
        "ACTA OBS", "RETIENE", "ITEMS INFRACCION", "LATITUD", "LONGITUD", "LUGAR",
        "FISCALIZADOR1", "FISCALIZADOR"
    ]

    for col in columnas_esperadas:
        if col not in df.columns:
            df[col] = ""

    # Normalizar columnas de texto
    df["DOMINIO"] = df["DOMINIO"].fillna("").astype(str).str.strip().str.upper()
    df["DOMINIO2"] = df["DOMINIO2"].fillna("").astype(str).str.strip().str.upper()
    df["DOMINIO3"] = df["DOMINIO3"].fillna("").astype(str).str.strip().str.upper()
    df["REGIONAL"] = df["REGIONAL"].fillna("").astype(str).str.strip().str.upper()
    df["TRANSPORTE"] = df["TRANSPORTE"].fillna("").astype(str).str.strip().str.upper()
    df["FECHA"] = df["FECHA"].fillna("").astype(str).str.strip()
    df["HORA"] = df["HORA"].fillna("").astype(str).str.strip()
    df["ACTA OBS"] = df["ACTA OBS"].fillna("").astype(str).str.strip()
    df["RETIENE"] = df["RETIENE"].fillna("").astype(str).str.strip().str.upper()
    df["ITEMS INFRACCION"] = df["ITEMS INFRACCION"].fillna("").astype(str).str.strip()
    df["LUGAR"] = df["LUGAR"].fillna("").astype(str).str.strip()
    df["FISCALIZADOR1"] = df["FISCALIZADOR1"].fillna("").astype(str).str.strip()
    df["FISCALIZADOR"] = df["FISCALIZADOR"].fillna("").astype(str).str.strip()

    # Normalizar caracteres especiales en REGIONAL
    df["REGIONAL"] = df["REGIONAL"].apply(
        lambda x: ''.join(c for c in unicodedata.normalize('NFD', x) if unicodedata.category(c) != 'Mn')
    )
    df["REGIONAL"] = df["REGIONAL"].str.replace("–", "-", regex=False).str.replace("—", "-", regex=False)
    df["REGIONAL"] = df["REGIONAL"].str.replace("_", " ", regex=False)
    df["REGIONAL"] = df["REGIONAL"].str.replace(r"\s+", " ", regex=True).str.strip()

    # Normalizar región
    df["REGION_NORMALIZADA"] = df["REGIONAL"].apply(normalizar_region).str.strip().str.upper()

    return df


def aplicar_filtro_fechas(df, fecha_desde=None, fecha_hasta=None):
    """Aplica filtro de fechas opcional."""
    if not fecha_desde and not fecha_hasta:
        return df

    try:
        fecha_desde_dt = pd.to_datetime(fecha_desde, format="%Y-%m-%d", errors="coerce") if fecha_desde else pd.Timestamp("1900-01-01")
        fecha_hasta_dt = pd.to_datetime(fecha_hasta, format="%Y-%m-%d", errors="coerce") if fecha_hasta else pd.Timestamp("2099-12-31")

        if pd.isna(fecha_desde_dt) or pd.isna(fecha_hasta_dt):
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD.")

        df = df.copy()
        df["FECHA_TEMP"] = pd.to_datetime(df["FECHA"], format="%Y-%m-%d", errors="coerce")
        antes = df.shape[0]
        df = df[(df["FECHA_TEMP"] >= fecha_desde_dt) & (df["FECHA_TEMP"] <= fecha_hasta_dt)]
        df = df.drop(columns=["FECHA_TEMP"], errors="ignore")
        despues = df.shape[0]
        imprimir_info(f"Filtro de fechas aplicado: {antes:,} → {despues:,} registros")
        return df
    except Exception as err:
        imprimir_warning(f"No se aplicó filtro de fechas: {err}")
        return df


# =========================================================
# ETAPA 3: PROCESAMIENTO
# =========================================================

def procesar_registros(df, modo=DEFAULT_MODO):
    """
    Etapa 3: PROCESAMIENTO
    Convierte filas de DataFrame en registros JSON
    """
    
    imprimir_titulo("ETAPA 3: PROCESAMIENTO DE REGISTROS")
    
    registros = []
    detalles_incidencias = []

    total_cargas = 0
    total_pasajeros = 0
    total_retenciones = 0
    total_dominios = 0
    incidencias_alcoholemia = 0
    incidencias_sustancias = 0
    retenciones_alcoholemia = 0
    retenciones_sustancias = 0

    for _, fila in df.iterrows():
        fecha = str(fila.get("FECHA", ""))[:10]
        hora = str(fila.get("HORA", ""))
        lugar = str(fila.get("LUGAR", "")).strip()
        regional = str(fila.get("REGION_NORMALIZADA", "SIN_REGION")).upper().strip() or "SIN_REGION"
        retiene = str(fila.get("RETIENE", "")).upper().strip()
        items_infraccion = str(fila.get("ITEMS INFRACCION", "")).strip()
        transporte = str(fila.get("TRANSPORTE", "")).strip().upper()
        acta_obs = str(fila.get("ACTA OBS", "")).strip()

        latitud = convertir_dms_a_decimal(fila.get("LATITUD"))
        longitud = convertir_dms_a_decimal(fila.get("LONGITUD"))
        articulo_filtrado = elegir_articulo(transporte, items_infraccion)
        tipo_incidencia, fuente = detectar_incidencia(fila)

        dominios_lista = [
            str(fila.get("DOMINIO", "")).strip().upper(),
            str(fila.get("DOMINIO2", "")).strip().upper(),
            str(fila.get("DOMINIO3", "")).strip().upper(),
        ]
        dominios_validos = [d for d in dominios_lista if d and d != "NAN"]
        total_dominios += len(dominios_validos)

        es_retencion = retiene in {"SI", "SÍ"}
        if es_retencion:
            total_retenciones += 1

        # MODO A: 1 registro por fila
        if modo == "A":
            if transporte == "CA":
                total_cargas += 1
            elif transporte == "PA":
                total_pasajeros += 1

            registros.append({
                "fecha": fecha,
                "hora": hora,
                "regional": regional,
                "lugar": lugar,
                "dominios": dominios_validos,
                "transporte": transporte,
                "items": items_infraccion,
                "articulo": articulo_filtrado,
                "retiene": retiene,
                "incidencia": tipo_incidencia,
                "lat": latitud,
                "lon": longitud,
                "acta_obs": acta_obs
            })

            if tipo_incidencia:
                detalles_incidencias.append({
                    "fecha": fecha,
                    "regional": regional,
                    "lugar": lugar,
                    "dominios": dominios_validos,
                    "latitud": latitud,
                    "longitud": longitud,
                    "tipo": tipo_incidencia,
                    "fuente": fuente,
                    "acta_obs": acta_obs,
                    "retiene": es_retencion
                })

        # MODO B: 1 registro por dominio
        else:
            for dominio in dominios_validos:
                if transporte == "CA":
                    total_cargas += 1
                elif transporte == "PA":
                    total_pasajeros += 1

                registros.append({
                    "fecha": fecha,
                    "hora": hora,
                    "regional": regional,
                    "lugar": lugar,
                    "dominio": dominio,
                    "transporte": transporte,
                    "items": items_infraccion,
                    "articulo": articulo_filtrado,
                    "retiene": retiene,
                    "incidencia": tipo_incidencia,
                    "lat": latitud,
                    "lon": longitud,
                    "acta_obs": acta_obs
                })

                if tipo_incidencia:
                    detalles_incidencias.append({
                        "fecha": fecha,
                        "regional": regional,
                        "lugar": lugar,
                        "dominio": dominio,
                        "latitud": latitud,
                        "longitud": longitud,
                        "tipo": tipo_incidencia,
                        "fuente": fuente,
                        "acta_obs": acta_obs,
                        "retiene": es_retencion
                    })

        # Contadores de incidencias
        if tipo_incidencia:
            if tipo_incidencia == "ALCOHOLEMIA":
                incidencias_alcoholemia += 1
                if es_retencion:
                    retenciones_alcoholemia += 1
            elif tipo_incidencia == "SUSTANCIA":
                incidencias_sustancias += 1
                if es_retencion:
                    retenciones_sustancias += 1

    imprimir_ok(f"Registros generados: {len(registros):,}")
    print()
    
    inc_summary = {
        "alcoholemia_positiva": incidencias_alcoholemia,
        "sustancias_positivas": incidencias_sustancias,
        "retenciones_alcoholemia": retenciones_alcoholemia,
        "retenciones_sustancias": retenciones_sustancias
    }

    metadata = {
        "total_registros": len(registros),
        "total_cargas": total_cargas,
        "total_pasajeros": total_pasajeros,
        "total_retenciones": total_retenciones,
        "registros_con_incidencia": len(detalles_incidencias),
        "fecha_generacion": pd.Timestamp.now().isoformat()
    }

    regiones = crear_resumen_regiones(registros)
    salida = crear_salida_json(registros, detalles_incidencias, metadata, inc_summary, regiones)

    return salida, {
        "total_cargas": total_cargas,
        "total_pasajeros": total_pasajeros,
        "total_retenciones": total_retenciones,
        "total_dominios": total_dominios,
        "incidencias_alcoholemia": incidencias_alcoholemia,
        "incidencias_sustancias": incidencias_sustancias,
        "retenciones_alcoholemia": retenciones_alcoholemia,
        "retenciones_sustancias": retenciones_sustancias
    }


# =========================================================
# ETAPA 5: EXPORTACIÓN
# =========================================================

def guardar_json(salida, stats):
    """Guarda el JSON y muestra resumen."""
    
    imprimir_titulo("ETAPA 5: EXPORTACIÓN")
    
    try:
        with open(DATOS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(salida, f, indent=2, ensure_ascii=False)
        imprimir_ok(f"JSON guardado: {DATOS_JSON_PATH}")
    except Exception as e:
        imprimir_error(f"Error al guardar JSON: {e}")
        return False

    print()
    imprimir_titulo("RESUMEN FINAL DEL PROCESAMIENTO")
    
    print()
    imprimir_info("VEHÍCULOS CONTROLADOS:")
    total_vc = stats["total_cargas"] + stats["total_pasajeros"]
    if total_vc > 0:
        prc_ca = (stats["total_cargas"] / total_vc * 100)
        prc_pa = (stats["total_pasajeros"] / total_vc * 100)
    else:
        prc_ca = prc_pa = 0
    
    print(f"    • Total VC:    {total_vc:,}")
    print(f"    • Cargas:      {stats['total_cargas']:,} ({prc_ca:.1f}%)")
    print(f"    • Pasajeros:   {stats['total_pasajeros']:,} ({prc_pa:.1f}%)")
    
    print()
    imprimir_info("ACTAS:")
    print(f"    • Total actas: {salida['actas']['total']}")
    print(f"    • Cargas:      {salida['actas']['cargas']}")
    print(f"    • Pasajeros:   {salida['actas']['pasajeros']}")
    
    print()
    imprimir_info("RETENCIONES:")
    print(f"    • Total:       {stats['total_retenciones']}")
    print(f"    • Cargas:      {salida['retenciones']['cargas']}")
    print(f"    • Pasajeros:   {salida['retenciones']['pasajeros']}")
    
    print()
    imprimir_info("INCIDENCIAS CRÍTICAS:")
    print(f"    • Alcoholemia: {stats['incidencias_alcoholemia']}")
    print(f"    • Sustancias:  {stats['incidencias_sustancias']}")
    
    print()
    imprimir_info("REGIONES:")
    for region in REGIONES_ORDENADAS:
        r = salida['regiones'][region]
        print(f"    • {region:5} → VC: {r['total']['vc']:,} | Actas: {r['total']['actas']:,} | Ret: {r['total']['ret']:,}")
    
    print()
    return True


# =========================================================
# ORQUESTADOR PRINCIPAL
# =========================================================

def procesar_completo(modo="A", fecha_desde=None, fecha_hasta=None):
    """
    Ejecuta el flujo completo de procesamiento.
    """
    
    imprimir_titulo("SISTEMA CNRT - PROCESAMIENTO COMPLETO")
    imprimir_info(f"Modo procesamiento: {modo}")
    if fecha_desde or fecha_hasta:
        print(f"    Desde: {fecha_desde or 'inicio'}")
        print(f"    Hasta: {fecha_hasta or 'fin'}")
    print()

    # ETAPA 1: Descargar archivos
    dfs, total_filas = leer_archivos_excel(EXCEL_FOLDER)
    if not dfs:
        imprimir_error("No se encontraron archivos Excel para procesar")
        return False

    # Consolidar DataFrames
    df = pd.concat(dfs, ignore_index=True)
    imprimir_info(f"Archivos consolidados: {len(df):,} filas")
    print()

    # Normalizar estructura
    df = normalizar_dataframe(df)

    # Aplicar filtro de fechas
    df = aplicar_filtro_fechas(df, fecha_desde, fecha_hasta)
    print()

    # ETAPA 2: SANEAMIENTO
    df_saneado, stats_saneamiento = saneamiento_base(df)
    validar_saneamiento(df, df_saneado, stats_saneamiento)
    print()

    if len(df_saneado) == 0:
        imprimir_error("Base de datos vacía después del saneamiento. No hay registros para procesar.")
        return False

    # ETAPA 3: PROCESAMIENTO
    salida, stats_procesamiento = procesar_registros(df_saneado, modo=modo)

    # ETAPA 5: EXPORTACIÓN
    if not guardar_json(salida, stats_procesamiento):
        return False

    print()
    imprimir_ok("✓ PROCESAMIENTO COMPLETADO EXITOSAMENTE")
    print()
    
    return True


if __name__ == "__main__":
    procesar_completo()
