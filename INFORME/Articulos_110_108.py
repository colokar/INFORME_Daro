# =========================================================================
# CNRT - BIBLIOTECA DE CONSULTAS ESPECÍFICA DE ARTÍCULOS (PASAJEROS Y CARGAS)
# Basado en los Decretos Estatales 1395/1998 y 1035/2002
# =========================================================================

def contar_articulos_en_fila(texto_items, tipo_transporte):
    """
    Analiza el texto de 'ITEMS INFRACCION' cruzándolo con el tipo de transporte.
    Devuelve un diccionario indicando qué artículos específicos se configuraron.
    
    tipo_transporte: Espera 'PA' (Pasajeros) o 'CA' (Cargas).
    """
    # Normalizamos los textos para evitar fallos por espacios o minúsculas
    texto = str(texto_items).strip()
    transporte = str(tipo_transporte).strip().upper()[:2]
    
    # Glosario inicializado en 0 para esta fila
    conteo_fila = {
        "105": 0,  # Dec 1395/98 - Pasajeros: Seguridad / Carrocería
        "108": 0,  # Dec 1395/98 - Pasajeros: Higiene
        "110": 0,  # Dec 1395/98 - Pasajeros: Falta RTO / VTV
        "18": 0,   # Dec 1035/02 - Cargas: Falta RTO / VTV
        "22": 0    # Dec 1035/02 - Cargas: Conductor sin LNH
    }
    
    # Si la celda está vacía, no hay nada que buscar
    if not texto or texto.lower() == "nan" or texto == "":
        return conteo_fila

    # ---------------------------------------------------------------------
    # 🚍 RAMAL PASAJEROS (PA) - Aplicación estricta Decreto 1395/98
    # ---------------------------------------------------------------------
    if transporte == "PA":
        if "105" in texto:
            conteo_fila["105"] = 1
            
        if "108" in texto:
            conteo_fila["108"] = 1
            
        if "110" in texto:
            conteo_fila["110"] = 1

    # ---------------------------------------------------------------------
    # 🚚 RAMAL CARGAS (CA) - Aplicación estricta Decreto 1035/02 (Anexo II)
    # ---------------------------------------------------------------------
    elif transporte == "CA":
        if "18" in texto:
            conteo_fila["18"] = 1
            
        if "22" in texto:
            conteo_fila["22"] = 1
            
    # ---------------------------------------------------------------------
    # CASO DE CONTINGENCIA (Si el transporte no está claro en la celda)
    # ---------------------------------------------------------------------
    else:
        # Si por error el sistema no cargó 'PA' o 'CA', busca por texto puro
        if "105" in texto: conteo_fila["105"] = 1
        if "108" in texto: conteo_fila["108"] = 1
        if "110" in texto: conteo_fila["110"] = 1
        if "18" in texto:  conteo_fila["18"] = 1
        if "22" in texto:  conteo_fila["22"] = 1

    return conteo_fila