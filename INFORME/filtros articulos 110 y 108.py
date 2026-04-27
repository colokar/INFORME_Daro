import pandas as pd
import json
from pathlib import Path


# =========================
# FILTRO ARTICULOS 108 / 110
# =========================

def elegir_articulo(row):

    tipo = str(row.get("TRANSP DISP", "")).strip()[:2]
    infr = str(row.get("ITEMS INFRACCION", ""))

    tiene108 = "108" in infr
    tiene110 = "110" in infr

    if tipo == "CA":
        if tiene108:
            return "108"
        if tiene110:
            return "110"

    if tipo == "PA":
        if tiene110:
            return "110"
        if tiene108:
            return "108"

    if tiene108:
        return "108"

    if tiene110:
        return "110"

    return ""


# =========================
# DETECTAR INCIDENCIAS
# =========================

def detectar_incidencia(texto):

    if not texto:
        return None

    t = texto.upper()

    if "ALCO" in t:
        return "alcoholemia"

    if "SUST" in t:
        return "sustancias"

    if "RTO" in t:
        return "rto"

    if "LIC" in t:
        return "licencia"

    if "PASAJ" in t:
        return "exceso_pasajeros"

    if "PELIG" in t:
        return "cargas_peligrosas"

    return None


# =========================
# LEER EXCEL
# =========================

def leer_excel(ruta):

    tablas = pd.read_html(ruta)
    df = tablas[0]

    df["TRANSP DISP"] = df.get("TRANSP DISP", "").astype(str).str[:2]
    df["RETIENE"] = df.get("RETIENE", "").astype(str)

    if "ITEMS INFRACCION" not in df.columns:
        df["ITEMS INFRACCION"] = ""

    df["ART"] = df.apply(elegir_articulo, axis=1)

    return df


# =========================
# PROCESAR
# =========================

def procesar(directorio="Excel"):

    total_vc = 0
    total_actas = 0
    total_ret = 0

    total_pa = 0
    total_ca = 0

    incidencias = {}
    detalle = []

    for archivo in Path(directorio).glob("*.xls"):

        region = archivo.stem

        df = leer_excel(archivo)

        for _, row in df.iterrows():

            total_vc += 1

            tipo = str(row["TRANSP DISP"])[:2]

            if tipo == "PA":
                total_pa += 1
            elif tipo == "CA":
                total_ca += 1

            art = row["ART"]

            if art:
                total_actas += 1

            ret = str(row["RETIENE"]).strip()

            if ret and ret != "nan":
                total_ret += 1

            texto = str(row.get("ITEMS INFRACCION", ""))

            inc = detectar_incidencia(texto)

            if inc:

                incidencias[inc] = incidencias.get(inc, 0) + 1

                detalle.append({

                    "regional": region,
                    "tipo": inc,
                    "texto": texto

                })


    salida = {

        "metadata": {

            "total_registros": total_vc,
            "total_actas": total_actas,
            "total_retenciones": total_ret,
            "total_pasajeros": total_pa,
            "total_cargas": total_ca

        },

        "incidencias": incidencias,

        "detalle_incidencias": detalle

    }

    with open("datos.json", "w", encoding="utf-8") as f:
        json.dump(salida, f, indent=4, ensure_ascii=False)

    print("OK datos.json generado")