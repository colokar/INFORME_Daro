"""Servidor y generador de datos del informe operativo CNRT."""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
EXCEL_DIR, DATA_FILE = BASE_DIR / "Excel", BASE_DIR / "datos.json"
REGIONES = ("AMBA", "CEN", "CUY", "NEA", "NOA", "COSTA", "PAT")
MAPA_REGIONES = {
    "AMBA": ("AMBA", "RETIRO", "CAPITAL FEDERAL", "LA PLATA", "EZEIZA", "MATANZA", "BUENOS AIRES", "LANUS", "QUILMES", "AVELLANEDA", "MORON", "LOMAS", "TALAR", "LIMA"),
    "COSTA": ("COSTA", "MAR DEL PLATA", "BAHIA BLANCA", "NECOCHEA"),
    "CEN": ("CEN", "CORDOBA", "ROSARIO", "SANTA FE", "PARANA", "ENTRE RIOS", "RIO CUARTO"),
    "CUY": ("CUY", "MENDOZA", "SAN JUAN", "SAN LUIS"),
    "NEA": ("NEA", "CHACO", "CORRIENTES", "FORMOSA", "MISIONES", "RESISTENCIA"),
    "NOA": ("NOA", "SALTA", "JUJUY", "TUCUMAN", "SANTIAGO DEL ESTERO", "CATAMARCA", "LA RIOJA"),
    "PAT": ("PAT", "NEUQUEN", "CHUBUT", "RIO NEGRO", "SANTA CRUZ", "TIERRA DEL FUEGO", "USHUAIA", "RIO GALLEGOS"),
}
app = Flask(__name__)


def normalizar(valor: Any) -> str:
    if pd.isna(valor): return ""
    texto = unicodedata.normalize("NFD", str(valor).upper())
    return re.sub(r"\s+", " ", "".join(c for c in texto if unicodedata.category(c) != "Mn")).strip()


def columna(df: pd.DataFrame, *nombres: str) -> str | None:
    buscadas = {normalizar(nombre) for nombre in nombres}
    return next((nombre for nombre in df.columns if normalizar(nombre) in buscadas), None)


def valor(fila: pd.Series, nombre: str | None) -> Any:
    return fila[nombre] if nombre and nombre in fila.index and not pd.isna(fila[nombre]) else ""


def agentes_de_fila(fila: pd.Series, columnas: list[str | None]) -> list[str]:
    agentes: list[str] = []
    for nombre in columnas:
        if not nombre:
            continue
        agente = normalizar(valor(fila, nombre))
        if agente and agente not in {"NAN", "NULL"} and agente not in agentes:
            agentes.append(agente)
    return agentes


def region_de(regional: Any, lugar: Any) -> str:
    texto = f"{normalizar(regional)} {normalizar(lugar)}"
    return next((region for region, nombres in MAPA_REGIONES.items() if any(nombre in texto for nombre in nombres)), "SIN_REGION")


def estructura_region() -> dict[str, dict[str, dict[str, int]]]:
    return {r: {g: {m: 0 for m in ("vc", "actas", "ret")} for g in ("total", "cargas", "pasajeros")} for r in REGIONES}


def es_positivo(fila: pd.Series, prefijo: str) -> bool:
    for nombre in fila.index:
        if prefijo not in normalizar(nombre): continue
        texto = normalizar(fila[nombre])
        if not texto or texto in {"NAN", "NULL", "NO", "NEG", "NEGATIVO", "0", "0.0"}: continue
        if "POSIT" in texto or "+" in texto: return True
        try:
            if float(texto.replace(",", ".")) > 0: return True
        except ValueError: pass
    return False


def leer_excels() -> pd.DataFrame:
    archivos = sorted(p for p in EXCEL_DIR.glob("*.xls*") if not p.name.startswith("~$"))
    if not archivos: raise FileNotFoundError(f"No hay archivos Excel en {EXCEL_DIR}")
    tablas = []
    for archivo in archivos:
        if archivo.suffix.lower() == ".xls":
            inicio = archivo.read_bytes()[:512].lstrip().lower()
            if inicio.startswith(b"<html") or b"<table" in inicio:
                tablas.extend(pd.read_html(archivo))
                continue
        tablas.append(pd.read_excel(archivo, engine="xlrd" if archivo.suffix.lower() == ".xls" else "openpyxl"))
    return pd.concat(tablas, ignore_index=True).dropna(how="all")


def procesar_datos(desde: str | None = None, hasta: str | None = None) -> dict[str, Any]:
    df = leer_excels()
    fecha_col = columna(df, "FECHA")
    if fecha_col and (desde or hasta):
        fechas = pd.to_datetime(df[fecha_col], errors="coerce")
        if desde: df = df[fechas >= pd.Timestamp(desde)]
        if hasta: df = df[fechas <= pd.Timestamp(hasta)]
    regiones, registros = estructura_region(), []
    metricas = {"total_vehiculos": 0, "total_cargas": 0, "total_pasajeros": 0, "total_actas": 0, "total_retenciones": 0, "incidencias_alcoholemia": 0, "incidencias_sustancias": 0, "gendarmeria_confeccion_apartados": 0, "sin_region": 0}
    regional_col, transporte_col, lugar_col = columna(df, "REGIONAL"), columna(df, "TRANSPORTE"), columna(df, "LUGAR")
    retiene_col, acta_col, items_col = columna(df, "RETIENE"), columna(df, "ACTA N°", "ACTA Nº", "ACTA N�"), columna(df, "ITEMS INFRACCION")
    fiscalizador_cols = [columna(df, f"FISCALIZADOR{i}", f"FISCALIZADOR {i}") for i in range(1, 4)]
    ranking_delegaciones: dict[str, dict[str, int | str]] = {}
    ranking_agentes: dict[str, dict[str, int | str]] = {}
    for _, fila in df.iterrows():
        regional = normalizar(valor(fila, regional_col))
        if "GENDARMERIA" in regional or "CONFECCION" in regional:
            metricas["gendarmeria_confeccion_apartados"] += 1; continue
        raw = normalizar(valor(fila, transporte_col))
        if raw in {"CA", "CARGAS", "CARGA"}: clave, tipo = "cargas", "CA"
        elif raw in {"PA", "PASAJEROS", "PASAJERO"}: clave, tipo = "pasajeros", "PA"
        else: continue
        region = region_de(regional, valor(fila, lugar_col))
        retiene = normalizar(valor(fila, retiene_col)) in {"SI", "SÍ"}
        acta = normalizar(valor(fila, acta_col)); items = normalizar(valor(fila, items_col))
        tiene_acta = bool(items) or acta not in {"", "NAN", "NULL", "0"}
        alco, sustancias = es_positivo(fila, "ALCOHOLEMIA"), es_positivo(fila, "SUSTANCIAS")
        fecha = valor(fila, fecha_col)
        fecha_texto = pd.Timestamp(fecha).date().isoformat() if not pd.isna(fecha) else ""
        agentes = agentes_de_fila(fila, fiscalizador_cols)
        registros.append({"fecha": fecha_texto, "regional": region, "transporte": tipo, "retiene": "SI" if retiene else "NO", "incidencia": "ALCOHOLEMIA" if alco else ("SUSTANCIA" if sustancias else None), "agentes": agentes})
        metricas["total_vehiculos"] += 1; metricas[f"total_{clave}"] += 1; metricas["total_actas"] += int(tiene_acta); metricas["total_retenciones"] += int(retiene); metricas["incidencias_alcoholemia"] += int(alco); metricas["incidencias_sustancias"] += int(sustancias)
        if region not in regiones: metricas["sin_region"] += 1; continue
        for grupo in ("total", clave):
            regiones[region][grupo]["vc"] += 1; regiones[region][grupo]["actas"] += int(tiene_acta); regiones[region][grupo]["ret"] += int(retiene)
        if region not in ranking_delegaciones:
            ranking_delegaciones[region] = {"delegacion": region, "controles": 0, "actas": 0, "retenciones": 0}
        ranking_delegaciones[region]["controles"] += 1
        ranking_delegaciones[region]["actas"] += int(tiene_acta)
        ranking_delegaciones[region]["retenciones"] += int(retiene)
        for agente in agentes:
            if agente not in ranking_agentes:
                ranking_agentes[agente] = {"agente": agente, "delegacion": region, "controles": 0, "actas": 0, "retenciones": 0}
            ranking_agentes[agente]["controles"] += 1
            ranking_agentes[agente]["actas"] += int(tiene_acta)
            ranking_agentes[agente]["retenciones"] += int(retiene)
    ranking = {
        "delegaciones": sorted(ranking_delegaciones.values(), key=lambda item: (-int(item["controles"]), -int(item["actas"]), -int(item["retenciones"]), str(item["delegacion"]))),
        "agentes": sorted(ranking_agentes.values(), key=lambda item: (-int(item["controles"]), -int(item["actas"]), -int(item["retenciones"]), str(item["agente"]))),
    }
    resultado = {"metadata": {"generado_en": datetime.now().isoformat(timespec="seconds"), "total_registros": len(registros), "filtro_desde": desde, "filtro_hasta": hasta}, "metricas": metricas, "regiones": regiones, "registros": registros, "ranking": ranking}
    DATA_FILE.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    return resultado


@app.get("/")
def inicio(): return send_from_directory(BASE_DIR, "informe-operativo.html")

@app.get("/datos.json")
def datos(): return send_from_directory(BASE_DIR, "datos.json")

@app.post("/api/procesar")
def api_procesar():
    payload = request.get_json(silent=True) or {}
    try: return jsonify(procesar_datos(payload.get("desde"), payload.get("hasta")))
    except (FileNotFoundError, ValueError) as error: return jsonify({"status": "error", "message": str(error)}), 400
    except Exception:
        app.logger.exception("No se pudo procesar el informe")
        return jsonify({"status": "error", "message": "No se pudo procesar el archivo Excel."}), 500


if __name__ == "__main__":
    procesar_datos()
    app.run(host="127.0.0.1", port=5001, debug=False)
