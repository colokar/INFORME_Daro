import os
import glob
import re
import unicodedata
import pandas as pd
import json
import sys
from datetime import datetime
from flask import Flask, jsonify, send_from_directory

# =========================================================
# CONFIGURACIÓN DE RUTAS Y FLASK
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")

try:
    from flask_cors import CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
except ImportError:
    print("⚠️ Flask-CORS no instalado. Ejecuta: pip install flask-cors")

# =========================================================
# FUNCIONES AUXILIARES (Títulos y Normalización)
# =========================================================
def titulo(texto):
    print(f"\n{'='*60}\n{texto.center(60)}\n{'='*60}")

def subtitulo(texto):
    print(f"\n--- {texto} ---")

mapa_regiones = {
    "AMBA": ["RETIRO", "CAPITAL FEDERAL", "LA PLATA", "EZEIZA", "MATANZA", "BUENOS AIRES", "LANUS", "QUILMES", "AVELLANEDA", "MORON", "LOMAS"],
    "COSTA": ["MAR DEL PLATA", "BAHIA BLANCA", "NECOCHEA"],
    "CEN": ["CORDOBA", "ROSARIO", "SANTA FE", "PARANA", "ENTRE RIOS", "RIO CUARTO"],
    "CUY": ["MENDOZA", "SAN JUAN", "SAN LUIS"],
    "NEA": ["CHACO", "CORRIENTES", "FORMOSA", "MISIONES"],
    "NOA": ["SALTA", "JUJUY", "TUCUMAN", "SANTIAGO DEL ESTERO", "CATAMARCA", "LA RIOJA"],
    "PAT": ["NEUQUEN", "CHUBUT", "RIO NEGRO", "SANTA CRUZ", "TIERRA DEL FUEGO", "USHUAIA", "RIO GALLEGOS"]
}

REGIONES_ORDENADAS = ["AMBA", "CEN", "CUY", "NEA", "NOA", "COSTA", "PAT"]

def normalizar(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = texto.replace("ñ", "n")
    texto = re.sub(r"[^a-z0-9 ]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()

def normalizar_region(valor):
    if not valor or pd.isna(valor): return "SIN_REGION"
    texto_norm = normalizar(valor)
    for region, nombres in mapa_regiones.items():
        for nombre in nombres:
            if normalizar(nombre) in texto_norm:
                return region
    return "SIN_REGION"

def convertir_dms_a_decimal(coordenada):
    if not coordenada or pd.isna(coordenada): return None
    try:
        coord_str = str(coordenada).strip()
        patron = r"(\d+)[º°](\d+)['\'](\d+(?:\.\d+)?)[\"″]([NSEW])"
        match = re.search(patron, coord_str)
        if not match: return None
        decimal = float(match.group(1)) + (float(match.group(2)) / 60) + (float(match.group(3)) / 3600)
        if match.group(4).upper() in ['S', 'W']: decimal = -decimal
        return round(decimal, 6)
    except: return None

def detectar_incidencia(fila):
    for col in ["ALCOHOLEMIA CHOFER 1", "ALCOHOLEMIA CHOFER 2", "ALCOHOLEMIA CHOFER 3"]:
        if col in fila and any(x in str(fila[col]).upper() for x in ["POS", "POSITIVO", "+"]):
            return "ALCOHOLEMIA", col
    for col in ["SUSTANCIAS CHOFER 1", "SUSTANCIAS CHOFER 2", "SUSTANCIAS CHOFER 3"]:
        if col in fila and any(x in str(fila[col]).upper() for x in ["POS", "POSITIVO", "+"]):
            return "SUSTANCIA", col
    return None, None

def elegir_articulo(transporte, items):
    t = str(transporte).lower()
    infr = str(items)
    if "carg" in t: return "108" if "108" in infr else ("110" if "110" in infr else "")
    if "pasaj" in t: return "110" if "110" in infr else ("108" if "108" in infr else "")
    return "108" if "108" in infr else ("110" if "110" in infr else "")

# =========================================================
# RUTAS DE FLASK
# =========================================================
@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/resumen')
def get_resumen():
    try:
        with open(os.path.join(BASE_DIR, "datos.json"), "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except:
        return jsonify({"error": "No se pudo leer datos.json. ¿Ejecutaste el script completo?"}), 500

# =========================================================
# LÓGICA DE PROCESAMIENTO (Se ejecuta al iniciar)
# =========================================================
if __name__ == "__main__":
    titulo("INICIO DE PROCESAMIENTO CNRT")
    
    carpeta_excels = os.path.join(BASE_DIR, "Excel")
    archivos_excel = [f for f in glob.glob(os.path.join(carpeta_excels, "*.xls*")) if "~$" not in os.path.basename(f)]

    if not archivos_excel:
        print(f"✗ No se encontraron archivos Excel en {carpeta_excels}")
    else:
        print(f"📁 Archivos detectados: {len(archivos_excel)}")
        
        dfs = []
        for archivo in archivos_excel:
            try:
                engine = "xlrd" if archivo.lower().endswith(".xls") else "openpyxl"
                df_temp = pd.read_excel(archivo, engine=engine)
                dfs.append(df_temp)
                print(f"   ✓ Leído: {os.path.basename(archivo)}")
            except Exception as e:
                print(f"   ✗ Error en {os.path.basename(archivo)}: {e}")

        if dfs:
            df = pd.concat(dfs, ignore_index=True)
            df.columns = df.columns.str.strip().str.upper()
            
            # Normalización
            df["REGION_NORMALIZADA"] = df["REGIONAL"].apply(normalizar_region)
            
            registros = []
            total_retenciones = 0
            
            for _, fila in df.iterrows():
                transporte = str(fila.get("TRANSPORTE", "")).strip().upper()
                if transporte not in ('CA', 'PA'): continue
                
                retiene = str(fila.get("RETIENE", "")).upper().strip()
                es_ret = retiene in ["SI", "SÍ"]
                if es_ret: total_retenciones += 1
                
                tipo_inc, fuente = detectar_incidencia(fila)
                
                dominios = [str(fila.get(d, "")).strip().upper() for d in ["DOMINIO", "DOMINIO2", "DOMINIO3"]]
                dominios = [d for d in dominios if d and d != "NAN"]

                registros.append({
                    "fecha": str(fila.get("FECHA", ""))[:10],
                    "regional": fila.get("REGION_NORMALIZADA"),
                    "transporte": transporte,
                    "retiene": "SI" if es_ret else "NO",
                    "articulo": elegir_articulo(transporte, fila.get("ITEMS INFRACCION", "")),
                    "incidencia": tipo_inc,
                    "dominios": dominios
                })

            # Cálculo por Regiones para Dashboard
            reg_stats = {r: {"total": {"vc":0, "actas":0, "ret":0}, "cargas":{"vc":0,"actas":0,"ret":0}, "pasajeros":{"vc":0,"actas":0,"ret":0}} for r in REGIONES_ORDENADAS}
            
            for r in registros:
                reg = r["regional"]
                if reg in reg_stats:
                    cat = "cargas" if r["transporte"] == "CA" else "pasajeros"
                    for k in [cat, "total"]:
                        reg_stats[reg][k]["vc"] += 1
                        if r["articulo"]: reg_stats[reg][k]["actas"] += 1
                        if r["retiene"] == "SI": reg_stats[reg][k]["ret"] += 1

            # Guardar JSON
            salida = {
                "metadata": {"total_registros": len(registros), "total_retenciones": total_retenciones},
                "regiones": reg_stats,
                "registros": registros
            }
            
            with open(os.path.join(BASE_DIR, "datos.json"), "w", encoding="utf-8") as f:
                json.dump(salida, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Proceso completado. {len(registros)} registros guardados en datos.json")

    # Iniciar Servidor
    subtitulo("INICIANDO SERVIDOR WEB")
    app.run(debug=True, port=5000)


# =========================================================
# FUNCION: CONVERTIR COORDENADAS DMS → DECIMAL
# Convierte coordenadas tipo:
# 34°12'45"S  → -34.2125
# =========================================================


def convertir_dms_a_decimal(coordenada):

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


# =========================================================
# FUNCION: DETECTAR INCIDENCIAS
# Busca alcoholemia positiva o sustancias
# =========================================================

def detectar_incidencia(fila):

    # ---- ALCOHOLEMIA ----

    for col in ["ALCOHOLEMIA CHOFER 1",
                "ALCOHOLEMIA CHOFER 2",
                "ALCOHOLEMIA CHOFER 3"]:

        if col not in fila:
            continue

        v = str(fila[col]).upper().strip()

        if v and any(x in v for x in ["POS", "POSITIVO", "+"]):

            try:
                val = float(v.replace(",", "."))

                if val > 0:
                    return "ALCOHOLEMIA", col

            except:
                return "ALCOHOLEMIA", col

    # ---- SUSTANCIAS ----

    for col in ["SUSTANCIAS CHOFER 1",
                "SUSTANCIAS CHOFER 2",
                "SUSTANCIAS CHOFER 3"]:

        if col not in fila:
            continue

        v = str(fila[col]).upper().strip()

        if v and any(x in v for x in ["POS", "POSITIVO", "+"]):
            return "SUSTANCIA", col

    # ---- BUSQUEDA EN OBSERVACIONES ----

    obs = str(fila.get("ACTA OBS", "")).upper()

    t = normalizar(obs)

    if any(x in t for x in [
        "sustancia positiva",
        "test droga positivo",
        "positivo sustancia"
    ]):
        return "SUSTANCIA", "ACTA OBS"

    if any(x in t for x in [
        "alcohol positivo",
        "alcoholimetro"
    ]):
        return "ALCOHOLEMIA", "ACTA OBS"

    return None, None

# =========================================================
# FILTRO ARTICULOS 108 / 110 SEGUN TRANSPORTE
# =========================================================

def elegir_articulo(transporte, items):

    t = str(transporte).lower()
    infr = str(items)

    tiene108 = "108" in infr
    tiene110 = "110" in infr

    if "carg" in t:
        if tiene108:
            return "108"
        if tiene110:
            return "110"

    if "pasaj" in t:
        if tiene110:
            return "110"
        if tiene108:
            return "108"

    if tiene108:
        return "108"

    if tiene110:
        return "110"

    return ""


# =========================================================
# BUSQUEDA AUTOMATICA DE ARCHIVOS EXCEL Carpeta /Excel
# =========================================================

carpeta_excels = os.path.join(os.path.dirname(__file__), "Excel")

archivos_excel = [
    f for f in glob.glob(os.path.join(carpeta_excels, "*.xls*"))
    if "~$" not in os.path.basename(f)
]

if not archivos_excel:
    print("✗ No se encontraron archivos Excel en /Excel")
    exit()

titulo("DETECCIÓN DE ARCHIVOS FUENTE")
print(f"📁 Archivos detectados: {len(archivos_excel)}\n")
for idx, archivo in enumerate(archivos_excel, 1):
    print(f"   [{idx}] {os.path.basename(archivo)}")
print()



# =========================================================
# PARÁMETROS DE FILTRADO (FECHAS)
# =========================================================

import sys
from datetime import datetime

fecha_desde = None
fecha_hasta = None

# Leer parámetros de línea de comando
if len(sys.argv) > 1:
    fecha_desde = sys.argv[1]
if len(sys.argv) > 2:
    fecha_hasta = sys.argv[2]

# =========================================================
# MODO DE PROCESAMIENTO DE DOMINIOS
# "A": 1 registro por fila (dominios en lista)
# "B": 1 registro por dominio (expansión)
# =========================================================

modo = "A"  # Cambiar a "B" para el modo expansión

subtitulo("CONFIGURACIÓN INICIAL")
print(f"⚙️  MODO DE PROCESAMIENTO: {modo}")
print(f"    [A] = 1 registro por fila (dominios en lista)")
print(f"    [B] = 1 registro por dominio (expansión)\n")

if fecha_desde or fecha_hasta:
    print("📅 FILTRO DE FECHAS:")
    if fecha_desde:
        print(f"    Desde: {fecha_desde}")
    if fecha_hasta:
        print(f"    Hasta: {fecha_hasta}")
else:
    print("📅 FILTRO DE FECHAS: ✗ SIN FILTRO (se procesarán TODOS los datos)")
print()


# =========================================================
# LECTURA DE ARCHIVOS EXCEL
# =========================================================

titulo("LECTURA DE ARCHIVOS FUENTE")

dfs = []
total_filas = 0

for idx, archivo in enumerate(archivos_excel, 1):
    if "~$" in archivo:
        continue

    nombre_archivo = os.path.basename(archivo)
    print(f"   [{idx}] Procesando: {nombre_archivo}")

    try:
        if archivo.lower().endswith(".xls"):
            df_temp = pd.read_excel(archivo, engine="xlrd")
        else:
            df_temp = pd.read_excel(archivo, engine="openpyxl", header=0)

        df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
        df_temp = df_temp.dropna(how="all")

        filas = df_temp.shape[0]
        print(f"       ✓ {filas:,} filas leídas")

        total_filas += filas
        dfs.append(df_temp)

    except Exception as e:
        print(f"       ✗ ERROR: {str(e)[:80]}")

if not dfs:
    print("\n✗ No se pudo leer ningún archivo. Abortando...")
    exit()

df = pd.concat(dfs, ignore_index=True)
print(f"\n   📊 TOTAL ACUMULADO: {total_filas:,} filas")
print(f"   📊 TOTAL CONSOLIDADO: {df.shape[0]:,} filas\n")


# =========================================================
# NORMALIZACIÓN DE COLUMNAS Y ESTRUCTURA
# =========================================================

df.columns = df.columns.str.strip().str.upper()
df = df.loc[:, ~df.columns.duplicated()]

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

df["REGIONAL"] = df["REGIONAL"].apply(lambda x: ''.join(c for c in unicodedata.normalize('NFD', x) if unicodedata.category(c) != 'Mn'))

# Limpieza adicional: reemplazar guiones raros y normalizar espacios
df["REGIONAL"] = df["REGIONAL"].str.replace("–", "-").str.replace("—", "-").str.replace("_", " ")
df["REGIONAL"] = df["REGIONAL"].apply(lambda x: re.sub(r"\s+", " ", x).strip())

df["REGION_NORMALIZADA"] = df["REGIONAL"].apply(normalizar_region)

# Limpiar REGION_NORMALIZADA
df["REGION_NORMALIZADA"] = df["REGION_NORMALIZADA"].str.strip().str.upper()

sin_region_count = int((df["REGION_NORMALIZADA"] == "SIN_REGION").sum())
print(f"🔎 Registros sin región mapeada: {sin_region_count:,}")
if sin_region_count > 0:
    print("    Ejemplos de regionales no mapeadas:")
    for reg in sorted(set(df.loc[df["REGION_NORMALIZADA"] == "SIN_REGION", "REGIONAL"]))[:20]:
        print(f"      • {reg}")

# Validación de consistencia en agrupamiento
df_valid = df[df["REGION_NORMALIZADA"] != "SIN_REGION"]
total_valid = len(df_valid)
total_groupby = df_valid.groupby("REGION_NORMALIZADA").size().sum()

print(f"✅ Validación de agrupamiento:")
print(f"    Registros válidos: {total_valid:,}")
print(f"    Suma del groupby: {total_groupby:,}")

if total_valid == total_groupby:
    print("    ✓ Consistencia perfecta: la suma coincide.")
else:
    print("    ✗ Inconsistencia detectada!")
    print(f"    Diferencia: {abs(total_valid - total_groupby)}")
    
    # Mostrar valores únicos problemáticos
    print("    Valores únicos problemáticos en REGION_NORMALIZADA:")
    problematicos = df_valid["REGION_NORMALIZADA"].unique()
    for val in sorted(problematicos):
        count = (df_valid["REGION_NORMALIZADA"] == val).sum()
        print(f"      • {val}: {count} registros")
    
    # Detectar registros que no entran en el groupby (si hay NaN o algo)
    print("    Registros que no entran en groupby:")
    groupby_keys = set(df_valid.groupby("REGION_NORMALIZADA").groups.keys())
    all_keys = set(df_valid["REGION_NORMALIZADA"].dropna().unique())
    missing = all_keys - groupby_keys
    if missing:
        for key in sorted(missing):
            count = (df_valid["REGION_NORMALIZADA"] == key).sum()
            print(f"      • {key}: {count} registros")
    else:
        print("      Ninguno detectado.")

print("Valores únicos en REGION_NORMALIZADA:")
for val in sorted(df["REGION_NORMALIZADA"].unique()):
    count = (df["REGION_NORMALIZADA"] == val).sum()
    print(f"  {val}: {count}")

subtitulo("ESTRUCTURA DE DATOS")
print(f"📋 COLUMNAS DISPONIBLES ({len(df.columns)}):\n")
for col in df.columns:
    print(f"    • {col}")
print()


# =========================================================
# APLICAR FILTRO DE FECHAS (OPCIONAL)
# =========================================================

if fecha_desde or fecha_hasta:
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

        df_original_rows = df.shape[0]
        df = df[(df["FECHA_TEMP"] >= fecha_desde_dt) & (df["FECHA_TEMP"] <= fecha_hasta_dt)]
        df = df.drop("FECHA_TEMP", axis=1)

        print(f"🔍 Filtro de fechas aplicado: {df_original_rows:,} → {df.shape[0]:,} registros\n")

    except Exception as e:
        print(f"⚠️  Error al aplicar filtro de fechas: {e}\n")

print(f"✓ DF listo para procesamiento: {df.shape[0]:,} filas\n")


# =========================================================
# LISTA DE REGIONES VÁLIDAS
# =========================================================
regiones_validas = list(mapa_regiones.keys())

# =========================================================
# PROCESAMIENTO DE REGISTROS
# =========================================================

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

    regional_original = str(fila.get("REGIONAL", "")).strip()
    lugar = str(fila.get("LUGAR", "")).strip()

    # NORMALIZACIÓN DE REGIONAL
    regional = str(fila.get("REGION_NORMALIZADA", "SIN_REGION")).upper().strip()
    if regional == "SIN_REGION":
        # Mantener el valor original para debug si la región no se pudo mapear
        regional = "SIN_REGION"
    # Nota: No se ignora aquí, se procesan todas las filas para generar registros

    acta = str(fila.get("ACTA OBS", "")).strip()
    retiene = str(fila.get("RETIENE", "")).upper().strip()
    items_infraccion = str(fila.get("ITEMS INFRACCION", "")).strip()

    latitud = convertir_dms_a_decimal(fila.get("LATITUD"))
    longitud = convertir_dms_a_decimal(fila.get("LONGITUD"))

    # NORMALIZACIÓN CLAVE
    transporte = str(fila.get("TRANSPORTE", "")).strip().upper()

    articulo_filtrado = elegir_articulo(transporte, items_infraccion)

    tipo_incidencia, fuente = detectar_incidencia(fila)

    # PROCESAMIENTO DE DOMINIOS: Mantener como lista, orden y posibles duplicados
    dominios_lista = [
        str(fila.get("DOMINIO", "")).strip().upper(),
        str(fila.get("DOMINIO2", "")).strip().upper(),
        str(fila.get("DOMINIO3", "")).strip().upper(),
    ]

    # Filtrar valores vacíos, NaN y strings "nan"
    dominios_validos = [
        d for d in dominios_lista
        if d and d not in ["", "NAN"]
    ]

    total_dominios += len(dominios_validos)

    es_retencion = retiene in ["SI", "SÍ"]

    # CONTADOR DE RETENCIONES (una vez por fila)
    if es_retencion:
        total_retenciones += 1

    # CONTADOR DE CARGAS Y PASAJEROS (depende del modo)
    if modo == "A":
        # Modo A: 1 por fila
        if transporte == "CA":
            total_cargas += 1
        elif transporte == "PA":
            total_pasajeros += 1
    elif modo == "B":
        # Modo B: por cantidad de dominios
        if transporte == "CA":
            total_cargas += len(dominios_validos)
        elif transporte == "PA":
            total_pasajeros += len(dominios_validos)

    # =========================
    # GENERACIÓN DE REGISTROS SEGÚN MODO
    # =========================

    if modo == "A":
        # Modo A: 1 registro por fila, dominios en lista
        registros.append({
            "fecha": fecha,
            "hora": hora,
            "regional": regional,
            "lugar": lugar,
            "dominios": dominios_validos,  # Lista de dominios
            "transporte": transporte,
            "items": items_infraccion,
            "articulo": articulo_filtrado,
            "retiene": retiene,
            "incidencia": tipo_incidencia,
            "lat": latitud,
            "lon": longitud
        })

        # INCIDENCIAS (una por fila en modo A)
        if tipo_incidencia:
            detalles_incidencias.append({
                "fecha": fecha,
                "regional": regional,
                "lugar": lugar,
                "dominios": dominios_validos,  # Lista de dominios
                "latitud": latitud,
                "longitud": longitud,
                "tipo": tipo_incidencia,
                "fuente": fuente,
                "acta_obs": acta,
                "retiene": es_retencion
            })

    elif modo == "B":
        # Modo B: 1 registro por dominio (como antes, pero sin set)
        for dominio in dominios_validos:
            registros.append({
                "fecha": fecha,
                "hora": hora,
                "regional": regional,
                "lugar": lugar,
                "dominio": dominio,  # Un dominio por registro
                "transporte": transporte,
                "items": items_infraccion,
                "articulo": articulo_filtrado,
                "retiene": retiene,
                "incidencia": tipo_incidencia,
                "lat": latitud,
                "lon": longitud
            })

            # INCIDENCIAS (una por dominio en modo B)
            if tipo_incidencia:
                detalles_incidencias.append({
                    "fecha": fecha,
                    "regional": regional,
                    "lugar": lugar,
                    "dominio": dominio,  # Un dominio por incidencia
                    "latitud": latitud,
                    "longitud": longitud,
                    "tipo": tipo_incidencia,
                    "fuente": fuente,
                    "acta_obs": acta,
                    "retiene": es_retencion
                })

    # CONTADORES DE INCIDENCIAS (fuera del loop de dominios, una vez por fila)
    if tipo_incidencia:
        if tipo_incidencia == "ALCOHOLEMIA":
            incidencias_alcoholemia += 1
            if es_retencion:
                retenciones_alcoholemia += 1
        elif tipo_incidencia == "SUSTANCIA":
            incidencias_sustancias += 1
            if es_retencion:
                retenciones_sustancias += 1


# =========================================================
# CALCULO DE MÉTRICAS POR REGIÓN
# =========================================================

from collections import defaultdict

regiones_detectadas = set()
regiones_no_mapeadas = set()

regiones = {region: {
    "cargas": {"vc": 0, "actas": 0, "ret": 0},
    "pasajeros": {"vc": 0, "actas": 0, "ret": 0},
    "total": {"vc": 0, "actas": 0, "ret": 0}
} for region in regiones_validas}

for r in registros:
    reg = r.get("regional", "").strip().upper()
    if not reg:
        continue

    if reg not in regiones_validas:
        regiones_no_mapeadas.add(reg)
        continue

    regiones_detectadas.add(reg)

    transporte = r.get("transporte", "").strip().upper()
    articulo = r.get("articulo", "").strip()
    retiene = r.get("retiene", "").strip().upper()

    if transporte == "CA":
        t = "cargas"
    elif transporte == "PA":
        t = "pasajeros"
    else:
        continue

    regiones[reg][t]["vc"] += 1
    if articulo:
        regiones[reg][t]["actas"] += 1
    if retiene == "SI":
        regiones[reg][t]["ret"] += 1

    regiones[reg]["total"]["vc"] += 1
    if articulo:
        regiones[reg]["total"]["actas"] += 1
    if retiene == "SI":
        regiones[reg]["total"]["ret"] += 1


# =========================================================
# CALCULO TOTALES Y PORCENTAJES
# =========================================================

total_vehiculos = len(registros)

porc_cargas = 0
porc_pasajeros = 0

if total_vehiculos > 0:
    porc_cargas = round(total_cargas / total_vehiculos * 100, 2)
    porc_pasajeros = round(total_pasajeros / total_vehiculos * 100, 2)

# =========================================================
# GENERACION DEL ARCHIVO JSON
# =========================================================

salida = {
    "registros": registros,
    "incidencias": {
        "alcoholemia_positiva": incidencias_alcoholemia,
        "sustancias_positivas": incidencias_sustancias,
        "retenciones_alcoholemia": retenciones_alcoholemia,
        "retenciones_sustancias": retenciones_sustancias
    },
    "detalle_incidencias": detalles_incidencias,
    "metadata": {
        "total_registros": len(registros),
        "total_cargas": total_cargas,
        "total_pasajeros": total_pasajeros,
        "total_retenciones": total_retenciones,
        "registros_con_incidencia": len(detalles_incidencias),
        "fecha_generacion": pd.Timestamp.now().isoformat()
    },
    "actas": {
        "total": sum(1 for r in registros if r.get("articulo")),
        "cargas": sum(1 for r in registros if r.get("transporte") == "CA" and r.get("articulo")),
        "pasajeros": sum(1 for r in registros if r.get("transporte") == "PA" and r.get("articulo"))
    },
    "retenciones": {
        "total": total_retenciones,
        "cargas": sum(1 for r in registros if r.get("transporte") == "CA" and r.get("retiene") == "SI"),
        "pasajeros": sum(1 for r in registros if r.get("transporte") == "PA" and r.get("retiene") == "SI")
    },
    "regiones": regiones
}

# =========================================================
# GUARDAR datos.json
# =========================================================

datos_json_path = os.path.join(os.path.dirname(__file__), "datos.json")

with open(datos_json_path, "w", encoding="utf-8") as f:
    json.dump(salida, f, indent=2, ensure_ascii=False)

# =========================================================
# BLOQUE A: RESUMEN GENERAL
# =========================================================

titulo("RESUMEN GENERAL DE PROCESAMIENTO")

print(f"⚙️  MODO DE PROCESAMIENTO: {modo}\n")
print(f"📊 DATOS PROCESADOS:")
print(f"    • Filas Excel: {df.shape[0]:,}")
print(f"    • Registros generados: {len(registros):,}")
print(f"    • Dominios válidos totales: {total_dominios:,}\n")

print(f"🚗 VEHÍCULOS CONTROLADOS:")
print(f"    • Total VC: {total_vehiculos:,}")
print(f"    • Cargas: {total_cargas:,} ({porc_cargas}%)")
print(f"    • Pasajeros: {total_pasajeros:,} ({porc_pasajeros}%)\n")

print(f"📝 ACTAS:")
print(f"    • Total actas: {salida['actas']['total']}")
print(f"    • Cargas: {salida['actas']['cargas']}")
print(f"    • Pasajeros: {salida['actas']['pasajeros']}\n")

print(f"🛑 RETENCIONES:")
print(f"    • Total retenciones: {total_retenciones}")
print(f"    • Cargas: {salida['retenciones']['cargas']}")
print(f"    • Pasajeros: {salida['retenciones']['pasajeros']}\n")

print(f"⚠️  INCIDENCIAS CRÍTICAS:")
print(f"    • Alcoholemia positiva: {incidencias_alcoholemia}")
print(f"    • Sustancias positivas: {incidencias_sustancias}")
print(f"    • Registros con incidencia: {len(detalles_incidencias)}\n")

# =========================================================
# BLOQUE B: DEBUG PROCESAMIENTO
# =========================================================

subtitulo("DEBUG PROCESAMIENTO")

regionales_en_registros = sorted(set(r.get('regional', '') for r in registros if r.get('regional')))
transportes_en_registros = sorted(set(r.get('transporte', '') for r in registros if r.get('transporte')))

print(f"📍 Regionales presentes:")
if regionales_en_registros:
    for reg in regionales_en_registros:
        count = sum(1 for r in registros if r.get('regional') == reg)
        print(f"    • {reg:5} → {count:,} registros")
else:
    print("    ✗ Ninguna región detectada")

print(f"\n🚗 Tipos de transporte presentes:")
if transportes_en_registros:
    for transp in transportes_en_registros:
        count = sum(1 for r in registros if r.get('transporte') == transp)
        print(f"    • {transp:5} → {count:,} registros")
else:
    print("    ✗ Ningún tipo de transporte detectado")
print()

# =========================================================
# BLOQUE C: RESUMEN POR REGIÓN
# =========================================================

titulo("RESUMEN POR REGIÓN")

for region in sorted(regiones_detectadas):
    r = regiones[region]
    total_vc = r["total"]["vc"]
    total_actas = r["total"]["actas"]
    total_ret = r["total"]["ret"]
    
    print(f"📍 {region.upper()}")
    print(f"    Total    → VC: {total_vc:,} | Actas: {total_actas:,} | Ret: {total_ret:,}")
    print(f"    Cargas   → VC: {r['cargas']['vc']:,} | Actas: {r['cargas']['actas']:,} | Ret: {r['cargas']['ret']:,}")
    print(f"    Pasajeros→ VC: {r['pasajeros']['vc']:,} | Actas: {r['pasajeros']['actas']:,} | Ret: {r['pasajeros']['ret']:,}\n")

# =========================================================
# BLOQUE D: CONTROL DE CONSISTENCIA
# =========================================================

subtitulo("CONTROL DE CONSISTENCIA")

suma_vc_regiones = sum(regiones[r]["total"]["vc"] for r in regiones_detectadas)
total_registros_validos = len([r for r in registros if r.get('regional') in regiones_validas])

print(f"Validación de registros:")
print(f"    • Total registros con regional válida: {total_registros_validos:,}")
print(f"    • Suma VC por regiones: {suma_vc_regiones:,}")

if suma_vc_regiones == total_registros_validos:
    print(f"    ✅ OK - Los datos son consistentes\n")
else:
    print(f"    ⚠️  ERROR - Discrepancia detectada ({total_registros_validos:,} vs {suma_vc_regiones:,})\n")

# =========================================================
# BLOQUE E: REGIONES NO MAPEADAS
# =========================================================

if regiones_no_mapeadas:
    subtitulo("REGIONES NO MAPEADAS (POSIBLES VALORES INVÁLIDOS)")
    print("⚠️  Las siguientes regiones fueron encontradas pero no están en el mapa de normalización:\n")
    for reg in sorted(regiones_no_mapeadas):
        count = len([r for r in registros if r.get('regional') == reg])
        print(f"    ⊘ {reg:20} → {count:,} registros ignorados")
    print()

# =========================================================
# RESUMEN FINAL
# =========================================================

titulo("RESUMEN FINAL")

print(f"✅ Archivo generado exitosamente\n")
print(f"📁 Ubicación: {datos_json_path}\n")

if fecha_desde or fecha_hasta:
    print(f"🕐 Período de datos:")
    if fecha_desde:
        print(f"    Desde: {fecha_desde}")
    if fecha_hasta:
        print(f"    Hasta: {fecha_hasta}\n")

print(f"📊 RESUMEN CONSOLIDADO:")
print(f"    • Vehículos Controlados: {total_vehiculos:,}")
print(f"      - Cargas: {total_cargas:,} ({porc_cargas}%)")
print(f"      - Pasajeros: {total_pasajeros:,} ({porc_pasajeros}%)")
print(f"    • Actas: {salida['actas']['total']}")
print(f"    • Retenciones: {total_retenciones}")
print(f"    • Incidencias Alcoholemia: {incidencias_alcoholemia}")
print(f"    • Incidencias Sustancias: {incidencias_sustancias}")
print(f"    • Registros Generados: {len(registros):,}\n")
print(f"🕐 Timestamp: {salida['metadata']['fecha_generacion']}\n")