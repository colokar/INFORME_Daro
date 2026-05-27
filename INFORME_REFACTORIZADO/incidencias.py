import pandas as pd
from normalizacion import normalizar_texto


def detectar_incidencia(fila):
    for col in ["ALCOHOLEMIA CHOFER 1", "ALCOHOLEMIA CHOFER 2", "ALCOHOLEMIA CHOFER 3"]:
        if col not in fila:
            continue

        valor = str(fila[col]).upper().strip()
        if not valor:
            continue

        if any(token in valor for token in ["POS", "POSITIVO", "+"]):
            try:
                valor_num = float(valor.replace(',', '.'))
                if valor_num > 0:
                    return "ALCOHOLEMIA", col
            except ValueError:
                return "ALCOHOLEMIA", col

    for col in ["SUSTANCIAS CHOFER 1", "SUSTANCIAS CHOFER 2", "SUSTANCIAS CHOFER 3"]:
        if col not in fila:
            continue

        valor = str(fila[col]).upper().strip()
        if not valor:
            continue

        if any(token in valor for token in ["POS", "POSITIVO", "+"]):
            return "SUSTANCIA", col

    observaciones = normalizar_texto(fila.get("ACTA OBS", ""))
    if any(token in observaciones for token in ["sustancia positiva", "test droga positivo", "positivo sustancia"]):
        return "SUSTANCIA", "ACTA OBS"

    if any(token in observaciones for token in ["alcohol positivo", "alcoholimetro"]):
        return "ALCOHOLEMIA", "ACTA OBS"

    return None, None


def elegir_articulo(transporte, items):
    transporte_text = str(transporte).lower()
    infraccion_text = str(items)
    tiene108 = "108" in infraccion_text
    tiene110 = "110" in infraccion_text

    if "carg" in transporte_text:
        if tiene108:
            return "108"
        if tiene110:
            return "110"

    if "pasaj" in transporte_text:
        if tiene110:
            return "110"
        if tiene108:
            return "108"

    if tiene108:
        return "108"

    if tiene110:
        return "110"

    return ""
