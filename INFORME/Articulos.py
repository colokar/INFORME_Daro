import re

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

# ---------------------------------------------------------------------
# NORMALIZADOR DE MOTIVO DE INFRACCIONES 
# ---------------------------------------------------------------------
def normalizar_motivo_infraccion(texto_observacion, tipo_transporte):
   """
    Analiza el texto libre de observaciones o ítems de infracción
    y lo agrupa en categorías limpias y estandarizadas para el Top 10.
    """
   texto = str(texto_observacion).lower().strip()
   transporte = str(tipo_transporte).strip().upper()[:2] # 'CA' o 'PA'

    # ---------------------------------------------------------------------
    # CRITERIOS DE CATEGORIZACIÓN POR PALABRAS CLAVE
    # ---------------------------------------------------------------------
    
    # 1. Alcoholemia / Sustancias
   if re.search(r'(alcoh|substanc|sustanc|droga|positivo|pipeta|dosaj)', texto):
        return "Alcoholemia / Sustancias Positiva"

    # 2. Revisión Técnica (RTO / VTV)
   if re.search(r'(rto|vtv|revision tecnica|vencida|sin rto|sin vtv|vencido)', texto):
        return "Falta de Revisión Técnica (RTO / VTV)"

    # 3. Licencia de Conducir / LNH
   if re.search(r'(licencia|l\.n\.h|lnh|sin registro|conductor no habilitado|vencida|vencido)', texto) and 'chofer' in texto or 'lic' in texto:
        return "Licencia de Conducir Inexistente / Vencida"

    # 4. Tacógrafo / Limitador de velocidad
   if re.search(r'(tacograf|disco|sin disco|velocidad|limitador|registro de veloc)', texto):
        return "Tacógrafo Inoperante / Falta de Disco"

    # 5. Medidas de Seguridad Críticas (Mecánica, matafuegos, luces)
   if re.search(r'(matafuego|luces|neumat|cubiert|paragolp|cinturon|parabris|freno)', texto):
        return "Deficiencias en Medidas de Seguridad Críticas"

    # 6. Descanso de Choferes / Exceso de Jornada
   if re.search(r'(descanso|jornada|exceso horas|sin relebo|relevo|diagrama)', texto):
        return "Falta de Descanso Reglamentario de Choferes"

    # 7. Falta de Habilitación / Permiso del vehículo
   if re.search(r'(sin habilit|no habilit|permiso inexistente|sin cert|sin permiso)', texto):
        return "Falta de Habilitación / Permiso de Circulación"

    # 8. Seguros / Pólizas
   if re.search(r'(seguro|poliza|vencido|sin seguro|comprobante de seguro)', texto):
        return "Falta de Seguro Obligatorio / Póliza Vencida"

    # ---------------------------------------------------------------------
    # DIFERENCIACIÓN POR RAMAL (PASAJEROS vs CARGAS)
    # ---------------------------------------------------------------------
   if transporte == "PA":
        # 9. Higiene / Confort (Pasajeros)
        if re.search(r'(higiene|baño|limpiez|olor|asiento|aire|calefac)', texto):
            return "Deficiencias de Higiene / Confort en Pasajeros"
        # 10. Modalidad / Desvío de Tráfico (Pasajeros)
        if re.search(r'(modalidad|desvio|fuera de ruta|linea|turismo)', texto):
            return "Violación de Modalidad de Servicio Autorizado"
    
   elif transporte == "CA":
        # 9. Remito / Porte / Manifiesto de Carga (Cargas)
        if re.search(r'(remito|carta de porte|porte|manifiesto|guia|remit)', texto):
            return "Falta de Documentación de Carga (Carta de Porte/Remito)"
        # 10. Exceso de peso / Dimensiones (Cargas)
        if re.search(r'(peso|exceso|balanza|kilos|dimension|sobrepeso)', texto):
            return "Exceso de Peso / Dimensiones Permitidas"

    # Categoría de respaldo para lo que no se logre encuadrar automáticamente
   return "Otras Infracciones Operativas menores"