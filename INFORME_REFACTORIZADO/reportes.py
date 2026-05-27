from collections import defaultdict
from config import REGIONES_ORDENADAS


def crear_resumen_regiones(registros):
    regiones = {
        region: {
            "cargas": {"vc": 0, "actas": 0, "ret": 0},
            "pasajeros": {"vc": 0, "actas": 0, "ret": 0},
            "total": {"vc": 0, "actas": 0, "ret": 0}
        }
        for region in REGIONES_ORDENADAS
    }

    for registro in registros:
        region = str(registro.get("regional", "")).strip().upper()
        transporte = str(registro.get("transporte", "")).strip().upper()
        articulo = str(registro.get("articulo", "")).strip()
        retiene = str(registro.get("retiene", "")).strip().upper()

        if region not in regiones:
            continue

        tipo = None
        if transporte == "CA":
            tipo = "cargas"
        elif transporte == "PA":
            tipo = "pasajeros"

        if tipo is None:
            continue

        regiones[region][tipo]["vc"] += 1
        regiones[region]["total"]["vc"] += 1

        if articulo:
            regiones[region][tipo]["actas"] += 1
            regiones[region]["total"]["actas"] += 1

        if retiene == "SI":
            regiones[region][tipo]["ret"] += 1
            regiones[region]["total"]["ret"] += 1

    return regiones


def crear_salida_json(registros, detalles_incidencias, metadata, inc_summary, regiones):
    return {
        "registros": registros,
        "incidencias": inc_summary,
        "detalle_incidencias": detalles_incidencias,
        "metadata": metadata,
        "actas": {
            "total": sum(1 for registro in registros if registro.get("articulo")),
            "cargas": sum(1 for registro in registros if registro.get("transporte") == "CA" and registro.get("articulo")),
            "pasajeros": sum(1 for registro in registros if registro.get("transporte") == "PA" and registro.get("articulo"))
        },
        "retenciones": {
            "total": metadata.get("total_retenciones", 0),
            "cargas": sum(1 for registro in registros if registro.get("transporte") == "CA" and registro.get("retiene") == "SI"),
            "pasajeros": sum(1 for registro in registros if registro.get("transporte") == "PA" and registro.get("retiene") == "SI")
        },
        "regiones": regiones
    }
