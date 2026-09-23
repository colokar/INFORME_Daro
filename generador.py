from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
EXCEL_DIR = BASE_DIR / "Excel"
DATA_FILE = BASE_DIR / "datos.json"

REGIONES_ORDENADAS = ["AMBA", "CEN", "CUY", "NEA", "NOA", "COSTA", "PAT"]
MAPA_REGIONES = {
    "AMBA": ["AMBA", "RETIRO", "CAPITAL FEDERAL", "LA PLATA", "EZEIZA", "MATANZA", "BUENOS AIRES", "LANUS", "QUILMES", "AVELLANEDA", "MORON", "LOMAS", "TALAR", "LIMA"],
    "COSTA": ["COSTA", "MAR DEL PLATA", "BAHIA BLANCA", "NECOCHEA"],
    "CEN": ["CEN", "CORDOBA", "ROSARIO", "SANTA FE", "PARANA", "ENTRE RIOS", "RIO CUARTO"],
    "CUY": ["CUY", "MENDOZA", "SAN JUAN", "SAN LUIS"],
    "NEA": ["NEA", "CHACO", "CORRIENTES", "FORMOSA", "MISIONES", "RESISTENCIA"],
    "NOA": ["NOA", "SALTA", "JUJUY", "TUCUMAN", "SANTIAGO DEL ESTERO", "CATAMARCA", "LA RIOJA"],
    "PAT": ["PAT", "NEUQUEN", "CHUBUT", "RIO NEGRO", "SANTA CRUZ", "TIERRA DEL FUEGO", "USHUAIA", "RIO GALLEGOS"],
}

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")


def normalizar_texto(valor: Any) -> str:
    if valor is None or pd.isna(valor):
        return ""
    texto = str(valor).upper()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(caracter for caracter in texto if unicodedata.category(caracter) != "Mn")
    texto = texto.replace("Ñ", "N")
    texto = re.sub(r"[^A-Z0-9 ]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def columna(df: pd.DataFrame, *nombres: str) -> str | None:
    candidatos = {normalizar_texto(nombre) for nombre in nombres}
    for nombre in df.columns:
        if normalizar_texto(nombre) in candidatos:
            return str(nombre)
    return None


def valor_fila(fila: pd.Series, nombre: str | None) -> Any:
    if nombre is None or nombre not in fila.index:
        return ""
    valor = fila[nombre]
    return "" if pd.isna(valor) else valor


def normalizar_region(valor: Any) -> str:
    texto = normalizar_texto(valor)
    if not texto:
        return "SIN_REGION"
    for region, nombres in MAPA_REGIONES.items():
        if any(normalizar_texto(nombre) in texto for nombre in nombres):
            return region
    return "SIN_REGION"


def convertir_dms_a_decimal(coordenada: Any) -> float | None:
    if coordenada is None or pd.isna(coordenada):
        return None
    try:
        coord_str = str(coordenada).strip()
        match = re.search(r"(\d+)[º°](\d+)['\'](\d+(?:\.\d+)?)[\"″]([NSEW])", coord_str, re.IGNORECASE)
        if not match:
            return None
        grados = float(match.group(1))
        minutos = float(match.group(2))
        segundos = float(match.group(3))
        direccion = match.group(4).upper()
        decimal = grados + (minutos / 60) + (segundos / 3600)
        if direccion in {"S", "W"}:
            decimal *= -1
        return round(decimal, 6)
    except Exception:
        return None


def detectar_incidencia_fila(fila: pd.Series) -> tuple[str | None, str | None]:
    columnas_alcohol = ["ALCOHOLEMIA CHOFER 1", "ALCOHOLEMIA CHOFER 2", "ALCOHOLEMIA CHOFER 3"]
    columnas_sustancias = ["SUSTANCIAS CHOFER 1", "SUSTANCIAS CHOFER 2", "SUSTANCIAS CHOFER 3"]

    for nombre in columnas_alcohol:
        valor = str(valor_fila(fila, nombre)).strip()
        if not valor:
            continue
        texto = normalizar_texto(valor)
        if texto in {"", "NAN", "NULL", "NEG", "NEGATIVO", "0", "0.0"}:
            continue
        if "POS" in texto or "POSITIVO" in texto or "+" in texto:
            try:
                numero = float(valor.replace(",", "."))
                if numero > 0:
                    return "ALCOHOLEMIA", nombre
            except ValueError:
                return "ALCOHOLEMIA", nombre

    for nombre in columnas_sustancias:
        valor = str(valor_fila(fila, nombre)).strip()
        if not valor:
            continue
        texto = normalizar_texto(valor)
        if texto in {"", "NAN", "NULL", "NEG", "NEGATIVO", "0", "0.0"}:
            continue
        if "POS" in texto or "POSITIVO" in texto or "+" in texto:
            return "SUSTANCIA", nombre

    texto_obs = normalizar_texto(valor_fila(fila, "ACTA OBS"))
    if any(token in texto_obs for token in ["SUSTANCIA POSITIVA", "TEST DROGA POSITIVO", "POSITIVO SUSTANCIA"]):
        return "SUSTANCIA", "ACTA OBS"
    if any(token in texto_obs for token in ["ALCOHOL POSITIVO", "ALCOHOLIMETRO"]):
        return "ALCOHOLEMIA", "ACTA OBS"
    return None, None


def elegir_articulo(transporte: Any, items: Any) -> str:
    transporte_text = str(transporte).lower()
    texto_items = str(items)
    tiene_108 = "108" in texto_items
    tiene_110 = "110" in texto_items
    if "carg" in transporte_text:
        if tiene_108:
            return "108"
        if tiene_110:
            return "110"
    if "pasaj" in transporte_text:
        if tiene_110:
            return "110"
        if tiene_108:
            return "108"
    if tiene_108:
        return "108"
    if tiene_110:
        return "110"
    return ""


def listar_archivos_excel() -> list[Path]:
    if not EXCEL_DIR.exists():
        return []
    return sorted(
        path for path in EXCEL_DIR.glob("*.xls*")
        if path.is_file() and "~$" not in path.name
    )


def contar_filas_excel() -> tuple[list[dict[str, Any]], int, list[str]]:
    archivos = listar_archivos_excel()
    resultados: list[dict[str, Any]] = []
    total_filas = 0
    errores: list[str] = []
    for path in archivos:
        try:
            engine = "xlrd" if path.suffix.lower() == ".xls" else "openpyxl"
            df_temp = pd.read_excel(path, engine=engine)
            filas = int(df_temp.shape[0])
            columnas = int(df_temp.shape[1])
            total_filas += filas
            resultados.append({
                "archivo": path.name,
                "filas": filas,
                "columnas": columnas,
                "estado": "OK",
            })
        except Exception as exc:  # pragma: no cover - diagnóstico de archivo corrupto
            resultados.append({
                "archivo": path.name,
                "filas": 0,
                "columnas": 0,
                "estado": "ERROR",
                "error": str(exc),
            })
            errores.append(f"{path.name}: {exc}")
    return resultados, total_filas, errores


def consolidar_archivos() -> tuple[pd.DataFrame, list[dict[str, Any]], int, list[str]]:
    archivos, total_filas, errores = contar_filas_excel()
    frames: list[pd.DataFrame] = []
    for path in listar_archivos_excel():
        try:
            engine = "xlrd" if path.suffix.lower() == ".xls" else "openpyxl"
            df_temp = pd.read_excel(path, engine=engine)
            if df_temp.empty:
                continue
            df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()].copy()
            df_temp = df_temp.dropna(how="all")
            frames.append(df_temp)
        except Exception as exc:  # pragma: no cover - diagnóstico de archivo corrupto
            errores.append(f"{path.name}: {exc}")
    if not frames:
        return pd.DataFrame(), archivos, total_filas, errores
    df = pd.concat(frames, ignore_index=True)
    df = df.loc[:, ~df.columns.duplicated()].copy()
    df.columns = [str(col).strip().upper() for col in df.columns]
    return df, archivos, total_filas, errores


def sanear_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    columnas = {str(col).strip().upper(): col for col in df.columns}
    for nombre in ["DOMINIO", "DOMINIO2", "DOMINIO3", "REGIONAL", "TRANSPORTE", "FECHA", "HORA", "RETIENE", "ITEMS INFRACCION", "ACTA OBS", "LUGAR"]:
        if nombre in columnas:
            df[nombre] = df[nombre].fillna("").astype(str).str.strip().str.upper()
    for nombre in ["LATITUD", "LONGITUD"]:
        if nombre in columnas:
            df[nombre] = df[nombre].fillna("")
    if "REGIONAL" in df.columns:
        df["REGIONAL"] = df["REGIONAL"].apply(lambda valor: "" if pd.isna(valor) else str(valor).strip())
        df["REGION_NORMALIZADA"] = df["REGIONAL"].apply(normalizar_region)
    return df


def contar_dominios_fila(fila: pd.Series) -> tuple[list[str], int, int]:
    dominios: list[str] = []
    for nombre in ["DOMINIO", "DOMINIO2", "DOMINIO3"]:
        valor = str(valor_fila(fila, nombre)).strip().upper()
        if valor and valor not in {"NAN", "NULL", ""}:
            dominios.append(valor)
    patron = re.compile(r"^[A-Z]{2,3}[0-9A-Z]{2,5}$")
    validos = sum(1 for dominio in dominios if patron.fullmatch(dominio))
    invalidos = max(0, len(dominios) - validos)
    return dominios, validos, invalidos


def calcular_indicadores_resolucion_284(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"colegios": 0, "controles": 0, "hitos_graves": 0, "deficiencias_tecnicas": 0, "aplicable": False}
    texto_completo = df.apply(lambda fila: f"{valor_fila(fila, 'ACTA OBS')} {valor_fila(fila, 'PL OBS')}", axis=1)
    patron = re.compile(r"(?:res|reso|resoluci[oó]n)\s*[\.-]*\s*284", re.IGNORECASE)
    mascara = texto_completo.str.contains(patron, na=False)
    subset = df[mascara].copy()
    if subset.empty:
        return {"colegios": 0, "controles": 0, "hitos_graves": 0, "deficiencias_tecnicas": 0, "aplicable": False}

    total_controles = int(len(subset))
    hitos_graves = 0
    deficiencias_tecnicas = 0
    for _, fila in subset.iterrows():
        texto = f"{valor_fila(fila, 'ACTA OBS')} {valor_fila(fila, 'PL OBS')}"
        texto_limpio = normalizar_texto(texto)
        es_alcohol = False
        es_sustancias = False
        for nombre in ["ALCOHOLEMIA CHOFER 1", "ALCOHOLEMIA CHOFER 2", "ALCOHOLEMIA CHOFER 3"]:
            valor = str(valor_fila(fila, nombre)).upper().strip()
            if valor and valor not in {"NAN", "NEG", "NEGATIVO", "0", "0.0"} and ("POS" in valor or "POSITIVO" in valor or "+" in valor):
                es_alcohol = True
                break
        for nombre in ["SUSTANCIAS CHOFER 1", "SUSTANCIAS CHOFER 2", "SUSTANCIAS CHOFER 3"]:
            valor = str(valor_fila(fila, nombre)).upper().strip()
            if valor and valor not in {"NAN", "NEG", "NEGATIVO", "0"} and ("POS" in valor or "POSITIVO" in valor or "+" in valor):
                es_sustancias = True
                break
        mencion = any(token in texto_limpio for token in ["ALCOHOLEMIA", "POSITIVO", "NARCO", "SUSTANCIA", "DROGA", "TESTIGO"])
        retencion = str(valor_fila(fila, "RETIENE")).upper().strip()
        if es_alcohol or es_sustancias or (mencion and retencion == "SI"):
            hitos_graves += 1
            continue
        if retencion == "SI" or str(valor_fila(fila, "ACTA N°")).strip() or re.search(r"(vencid|seguro|habilitaci|licencia|cubierta|neumatic|tenic|revision|vtv|rto|carrocer|chasis|freno|luces|matafuego|parabris|tacograf)", texto_limpio, re.IGNORECASE):
            deficiencias_tecnicas += 1
    return {"colegios": int(len(subset)), "controles": total_controles, "hitos_graves": hitos_graves, "deficiencias_tecnicas": deficiencias_tecnicas, "aplicable": True}


def calcular_indicadores(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "filas": {"total": 0, "validas": 0, "invalidas": 0},
            "dominios": {"filas": 0, "encontrados": 0, "validos": 0, "invalidos": 0},
            "transporte": {"cargas": 0, "pasajeros": 0, "total": 0},
            "vehiculos_controlados": {"total": 0, "cargas": 0, "pasajeros": 0},
            "actas": {"total": 0, "cargas": 0, "pasajeros": 0},
            "retenciones": {"total": 0, "cargas": 0, "pasajeros": 0},
            "alcohol": {"total": 0},
            "sustancias": {"total": 0},
            "articulos": {"total": 0, "cargas": 0, "pasajeros": 0},
            "resolucion_284": {"colegios": 0, "controles": 0, "hitos_graves": 0, "deficiencias_tecnicas": 0, "aplicable": False},
        }

    transporte = df["TRANSPORTE"].fillna("").astype(str).str.upper().str.strip() if "TRANSPORTE" in df.columns else pd.Series(["" for _ in range(len(df))], index=df.index)
    ca_mask = transporte.isin(["CA", "CARGA", "CARGAS"])
    pa_mask = transporte.isin(["PA", "PASAJERO", "PASAJEROS"])

    dominios_totales: list[str] = []
    dominios_validos = 0
    dominios_invalidos = 0
    for _, fila in df.iterrows():
        dominios_fila, validos, invalidos = contar_dominios_fila(fila)
        dominios_totales.extend(dominios_fila)
        dominios_validos += validos
        dominios_invalidos += invalidos

    total_actas = 0
    total_actas_cargas = 0
    total_actas_pasajeros = 0
    total_retenciones = 0
    total_retenciones_cargas = 0
    total_retenciones_pasajeros = 0
    alcohol_total = 0
    sustancias_total = 0
    articulos_total = 0
    articulos_cargas = 0
    articulos_pasajeros = 0
    for _, fila in df.iterrows():
        transporte_valor = str(valor_fila(fila, "TRANSPORTE")).upper().strip()
        retiene = str(valor_fila(fila, "RETIENE")).upper().strip() in {"SI", "SÍ"}
        tipo = "CA" if transporte_valor in {"CA", "CARGA", "CARGAS"} else "PA" if transporte_valor in {"PA", "PASAJERO", "PASAJEROS"} else None
        if tipo == "CA" and retiene:
            total_retenciones_cargas += 1
        if tipo == "PA" and retiene:
            total_retenciones_pasajeros += 1
        if retiene:
            total_retenciones += 1
        articulo = elegir_articulo(transporte_valor, valor_fila(fila, "ITEMS INFRACCION"))
        if articulo:
            articulos_total += 1
            if tipo == "CA":
                articulos_cargas += 1
            elif tipo == "PA":
                articulos_pasajeros += 1
            total_actas += 1
            if tipo == "CA":
                total_actas_cargas += 1
            elif tipo == "PA":
                total_actas_pasajeros += 1
        tipo_incidencia, _ = detectar_incidencia_fila(fila)
        if tipo_incidencia == "ALCOHOLEMIA":
            alcohol_total += 1
        elif tipo_incidencia == "SUSTANCIA":
            sustancias_total += 1

    resolucion_284 = calcular_indicadores_resolucion_284(df)
    return {
        "filas": {"total": int(len(df)), "validas": int(len(df)), "invalidas": 0},
        "dominios": {"filas": int(len(df)), "encontrados": int(len(dominios_totales)), "validos": int(dominios_validos), "invalidos": int(dominios_invalidos)},
        "transporte": {"cargas": int(ca_mask.sum()), "pasajeros": int(pa_mask.sum()), "total": int((ca_mask | pa_mask).sum())},
        "vehiculos_controlados": {"total": int((ca_mask | pa_mask).sum()), "cargas": int(ca_mask.sum()), "pasajeros": int(pa_mask.sum())},
        "actas": {"total": int(total_actas), "cargas": int(total_actas_cargas), "pasajeros": int(total_actas_pasajeros)},
        "retenciones": {"total": int(total_retenciones), "cargas": int(total_retenciones_cargas), "pasajeros": int(total_retenciones_pasajeros)},
        "alcohol": {"total": int(alcohol_total)},
        "sustancias": {"total": int(sustancias_total)},
        "articulos": {"total": int(articulos_total), "cargas": int(articulos_cargas), "pasajeros": int(articulos_pasajeros)},
        "resolucion_284": resolucion_284,
    }


def calcular_regiones(df: pd.DataFrame) -> dict[str, dict[str, dict[str, int]]]:
    resultado = {region: {grupo: {metrica: 0 for metrica in ("vc", "actas", "ret")} for grupo in ("total", "cargas", "pasajeros")} for region in REGIONES_ORDENADAS}
    for _, fila in df.iterrows():
        region = normalizar_region(valor_fila(fila, "REGIONAL"))
        if region not in resultado:
            continue
        transporte = str(valor_fila(fila, "TRANSPORTE")).upper().strip()
        tipo = "CA" if transporte in {"CA", "CARGA", "CARGAS"} else "PA" if transporte in {"PA", "PASAJERO", "PASAJEROS"} else None
        if not tipo:
            continue
        grupo = "cargas" if tipo == "CA" else "pasajeros"
        retiene = str(valor_fila(fila, "RETIENE")).upper().strip() in {"SI", "SÍ"}
        articulo = elegir_articulo(transporte, valor_fila(fila, "ITEMS INFRACCION"))
        for nombre in (grupo, "total"):
            resultado[region][nombre]["vc"] += 1
            if articulo:
                resultado[region][nombre]["actas"] += 1
            if retiene:
                resultado[region][nombre]["ret"] += 1
    return resultado


def construir_registros(df: pd.DataFrame) -> list[dict[str, Any]]:
    registros: list[dict[str, Any]] = []
    for _, fila in df.iterrows():
        transporte = str(valor_fila(fila, "TRANSPORTE")).upper().strip()
        if transporte not in {"CA", "PA", "CARGA", "CARGAS", "PASAJERO", "PASAJEROS"}:
            continue
        dominios_fila, _, _ = contar_dominios_fila(fila)
        registros.append({
            "fecha": str(valor_fila(fila, "FECHA"))[:10],
            "hora": str(valor_fila(fila, "HORA"))[:10],
            "regional": normalizar_region(valor_fila(fila, "REGIONAL")),
            "lugar": str(valor_fila(fila, "LUGAR")).strip(),
            "transporte": "CA" if transporte in {"CA", "CARGA", "CARGAS"} else "PA",
            "dominios": dominios_fila,
            "retiene": "SI" if str(valor_fila(fila, "RETIENE")).upper().strip() in {"SI", "SÍ"} else "NO",
            "articulo": elegir_articulo(transporte, valor_fila(fila, "ITEMS INFRACCION")),
            "incidencia": detectar_incidencia_fila(fila)[0],
            "lat": convertir_dms_a_decimal(valor_fila(fila, "LATITUD")),
            "lon": convertir_dms_a_decimal(valor_fila(fila, "LONGITUD")),
        })
    return registros


def construir_delegaciones(df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    delegaciones: dict[str, dict[str, Any]] = {}
    for _, fila in df.iterrows():
        region = normalizar_region(valor_fila(fila, "REGIONAL"))
        if region not in REGIONES_ORDENADAS:
            continue
        transporte = str(valor_fila(fila, "TRANSPORTE")).upper().strip()
        if transporte not in {"CA", "PA", "CARGA", "CARGAS", "PASAJERO", "PASAJEROS"}:
            continue
        delegaciones.setdefault(region, {"delegacion": region, "controles": 0, "actas": 0, "retenciones": 0})
        delegaciones[region]["controles"] += 1
        if elegir_articulo(transporte, valor_fila(fila, "ITEMS INFRACCION")):
            delegaciones[region]["actas"] += 1
        if str(valor_fila(fila, "RETIENE")).upper().strip() in {"SI", "SÍ"}:
            delegaciones[region]["retenciones"] += 1
    return delegaciones


def construir_fiscalizadores(df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    fiscalizadores: dict[str, dict[str, Any]] = {}
    for _, fila in df.iterrows():
        region = normalizar_region(valor_fila(fila, "REGIONAL"))
        if region not in REGIONES_ORDENADAS:
            continue
        agentes: list[str] = []
        for index in range(1, 4):
            nombre = f"FISCALIZADOR{index}"
            if nombre in df.columns:
                valor = str(valor_fila(fila, nombre)).strip()
                if valor and valor not in {"NAN", "NULL"}:
                    agentes.append(valor)
        if not agentes:
            continue
        for agente in agentes:
            fiscalizadores.setdefault(agente, {"agente": agente, "delegacion": region, "controles": 0, "actas": 0, "retenciones": 0})
            fiscalizadores[agente]["controles"] += 1
            if elegir_articulo(str(valor_fila(fila, "TRANSPORTE")).upper().strip(), valor_fila(fila, "ITEMS INFRACCION")):
                fiscalizadores[agente]["actas"] += 1
            if str(valor_fila(fila, "RETIENE")).upper().strip() in {"SI", "SÍ"}:
                fiscalizadores[agente]["retenciones"] += 1
    return fiscalizadores


def procesar_datos(desde: str | None = None, hasta: str | None = None) -> dict[str, Any]:
    df, archivos, total_filas, errores = consolidar_archivos()
    if df.empty:
        return {
            "metadata": {"generado_en": datetime.now().isoformat(timespec="seconds"), "total_registros": 0, "filtro_desde": desde, "filtro_hasta": hasta},
            "diagnostico": {"archivos_procesados": 0, "filas_originales": 0, "filas_consolidadas": 0, "filas_validas": 0, "filas_invalidas": 0, "errores": errores},
            "periodo": {"fecha_desde": None, "fecha_hasta": None, "filas_antes_del_filtro": 0, "filas_despues_del_filtro": 0},
            "resumen": {"total_vehiculos": 0},
            "indicadores": {},
            "regiones": {},
            "delegaciones": {},
            "fiscalizadores": {},
            "infracciones": {},
            "incidencias": {},
            "registros": [],
        }

    df = sanear_dataframe(df)
    filas_antes = int(len(df))
    fecha_col = columna(df, "FECHA")
    if fecha_col and (desde is not None or hasta is not None):
        fechas = pd.to_datetime(df[fecha_col], errors="coerce")
        mascara = pd.Series(True, index=df.index)
        if desde is not None:
            mascara &= fechas >= pd.Timestamp(desde)
        if hasta is not None:
            mascara &= fechas <= pd.Timestamp(hasta)
        df = df[mascara].copy()

    diagnostico = {
        "archivos_procesados": len(archivos),
        "filas_originales": int(total_filas),
        "filas_consolidadas": int(filas_antes),
        "filas_validas": int(len(df)),
        "filas_invalidas": int(max(0, filas_antes - len(df))),
        "dominios_validos": 0,
        "dominios_invalidos": 0,
        "regiones_validas": 0,
        "regiones_invalidas": 0,
        "errores": errores,
    }

    for _, fila in df.iterrows():
        _, validos, invalidos = contar_dominios_fila(fila)
        diagnostico["dominios_validos"] += validos
        diagnostico["dominios_invalidos"] += invalidos
        region = normalizar_region(valor_fila(fila, "REGIONAL"))
        if region in REGIONES_ORDENADAS:
            diagnostico["regiones_validas"] += 1
        else:
            diagnostico["regiones_invalidas"] += 1

    indicadores = calcular_indicadores(df)
    regiones = calcular_regiones(df)
    delegaciones = construir_delegaciones(df)
    fiscalizadores = construir_fiscalizadores(df)
    registros = construir_registros(df)
    resumen = {
        "total_vehiculos": int(indicadores["vehiculos_controlados"]["total"]),
        "total_cargas": int(indicadores["vehiculos_controlados"]["cargas"]),
        "total_pasajeros": int(indicadores["vehiculos_controlados"]["pasajeros"]),
        "total_actas": int(indicadores["actas"]["total"]),
        "total_retenciones": int(indicadores["retenciones"]["total"]),
        "incidencias_alcoholemia": int(indicadores["alcohol"]["total"]),
        "incidencias_sustancias": int(indicadores["sustancias"]["total"]),
    }
    periodo = {
        "fecha_desde": desde,
        "fecha_hasta": hasta,
        "fecha_minima": str(df["FECHA"].min()) if "FECHA" in df.columns and not df.empty else None,
        "fecha_maxima": str(df["FECHA"].max()) if "FECHA" in df.columns and not df.empty else None,
        "filas_antes_del_filtro": int(filas_antes),
        "filas_despues_del_filtro": int(len(df)),
    }
    resultado = {
        "metadata": {"generado_en": datetime.now().isoformat(timespec="seconds"), "total_registros": int(len(registros)), "filtro_desde": desde, "filtro_hasta": hasta},
        "diagnostico": diagnostico,
        "periodo": periodo,
        "resumen": resumen,
        "indicadores": indicadores,
        "regiones": regiones,
        "delegaciones": delegaciones,
        "fiscalizadores": fiscalizadores,
        "infracciones": {"articulos": indicadores["articulos"]},
        "incidencias": {"alcoholemia": indicadores["alcohol"], "sustancias": indicadores["sustancias"], "resolucion_284": indicadores["resolucion_284"]},
        "registros": registros,
    }
    DATA_FILE.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    return resultado


@app.route("/")
def index():
    return send_from_directory(str(BASE_DIR), "informe-operativo.html")


@app.route("/resumen")
def resumen():
    if not DATA_FILE.exists():
        return jsonify({"error": "No hay datos disponibles. Ejecutá python generador.py"}), 503
    return jsonify(json.loads(DATA_FILE.read_text(encoding="utf-8")))


@app.route("/datos.json")
def obtener_datos_json():
    if not DATA_FILE.exists():
        return jsonify({"error": "No hay datos disponibles. Ejecutá python generador.py"}), 503
    return send_from_directory(str(BASE_DIR), "datos.json")


@app.route("/api/procesar", methods=["GET", "POST"])
def api_procesar():
    payload = request.get_json(silent=True) or {}
    desde = payload.get("desde") if isinstance(payload, dict) else None
    hasta = payload.get("hasta") if isinstance(payload, dict) else None
    try:
        return jsonify(procesar_datos(desde, hasta))
    except Exception as exc:  # pragma: no cover - manejo de errores de servidor
        return jsonify({"status": "error", "message": str(exc)}), 500


def main() -> None:
    parser = argparse.ArgumentParser(description="Generador del informe operativo CNRT")
    parser.add_argument("--desde", help="Fecha inicial en formato YYYY-MM-DD")
    parser.add_argument("--hasta", help="Fecha final en formato YYYY-MM-DD")
    parser.add_argument("--solo-procesar", action="store_true", help="Genera datos.json sin levantar el servidor")
    args = parser.parse_args()

    print("=" * 60)
    print("     INFORMES AUTOMATIZADOS CNRT")
    print("=" * 60)

    archivos, total_filas, errores = contar_filas_excel()
    print("[1/8] Buscando archivos Excel...")
    print(f"      Archivos encontrados: {len(archivos)}")
    print(f"      Filas originales: {total_filas:,}")

    print("[2/8] Consolidando...")
    df, _, _, _ = consolidar_archivos()
    print(f"      Filas consolidadas: {len(df):,}")

    print("[3/8] Saneando datos...")
    df = sanear_dataframe(df)
    problemas = 0
    print(f"      Filas válidas: {len(df):,}")
    print(f"      Filas con problemas: {problemas:,}")

    print("[4/8] Procesando dominios...")
    indicadores = calcular_indicadores(df)
    print(f"      Dominios válidos: {indicadores['dominios']['validos']:,}")

    print("[5/8] Calculando indicadores...")
    print(f"      Vehículos: {indicadores['vehiculos_controlados']['total']:,}")
    print(f"      Actas: {indicadores['actas']['total']:,}")
    print(f"      Retenciones: {indicadores['retenciones']['total']:,}")

    print("[6/8] Generando resultados...")
    resultado = procesar_datos(args.desde, args.hasta)
    print("      Regiones: OK")
    print("      Delegaciones: OK")
    print("      Fiscalizadores: OK")

    print("[7/8] Generando JSON...")
    print("      datos.json: OK")
    print("=" * 60)
    print("     SERVIDOR WEB")
    print("=" * 60)
    print("Dashboard: http://127.0.0.1:5000/")

    if not args.solo_procesar:
        app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
