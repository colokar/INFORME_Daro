# =========================================================
# BIBLIOTECA CENTRAL DE CONSULTAS DE ARTÍCULOS
# =========================================================

def contar_articulos_en_fila(texto_items):
    """
    Recibe el texto de 'ITEMS INFRACCION' de una fila.
    Busca de forma independiente cada artículo y devuelve un diccionario
    con cuáles sumaron en este control.
    """
    texto = str(texto_items).strip()
    
    # Armamos un diccionario con los contadores en 0 para esta fila
    conteo_fila = {
        "105": 0,
        "108": 0,
        "110": 0,
        "18": 0,
        "22": 0,
        # Podés seguir agregando acá abajo los artículos que quieras de la lista de tu compañero
    }
    
    # Si la celda está vacía, no buscamos nada
    if not texto or texto.lower() == "nan":
        return conteo_fila

    # Buscamos cada artículo por separado (para que si hay más de uno, sume ambos)
    if "105" in texto:
        conteo_fila["105"] = 1
        
    if "108" in texto:
        conteo_fila["108"] = 1
        
    if "110" in texto:
        conteo_fila["110"] = 1
        
    if "18" in texto:
        conteo_fila["18"] = 1
        
    if "22" in texto:
        conteo_fila["22"] = 1

    return conteo_fila