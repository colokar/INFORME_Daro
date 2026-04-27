# =========================================================
# MÓDULO: GESTOR DE DATOS DE FISCALIZACIÓN
# =========================================================
# 
# Propósito: Reemplazar IndexedDB de JavaScript
# Centraliza la lógica de datos de fiscalizaciones en Python
# 
# Funciones disponibles:
# - cargar_datos()
# - filtrar_por_fecha()
# - calcular_resumen()
# - calcular_por_region()
# =========================================================

import json
import os
from datetime import datetime

# =========================================================
# CONFIGURACIÓN
# =========================================================

ARCHIVO_JSON = "datos_fiscalizacion.json"

REGIONES_ORDEN = ["AMBA", "COSTA", "BA", "CEN", "CUY", "NEA", "NOA", "PAT"]

TIPOS_VALIDOS = ["CARGAS", "PASAJEROS"]


# =========================================================
# FUNCIÓN: CARGAR DATOS
# =========================================================
# Lee el archivo JSON y devuelve la lista de registros
# Maneja errores si el archivo no existe o está corrupto
# =========================================================

def cargar_datos(ruta=ARCHIVO_JSON):
    """
    Carga los datos de fiscalización desde el archivo JSON.
    
    Args:
        ruta (str): Ruta al archivo JSON. Default: datos_fiscalizacion.json
        
    Returns:
        list: Lista de diccionarios con los registros
        list: Lista vacía si hay error
        
    Ejemplos:
        >>> registros = cargar_datos()
        >>> print(len(registros))  # Cantidad de registros
    """
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta):
            print(f"⚠️  ADVERTENCIA: Archivo '{ruta}' no encontrado.")
            return []
        
        # Leer el JSON
        with open(ruta, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
        
        # Extraer la lista de registros
        registros = datos.get('registros', [])
        
        print(f"✓ Datos cargados: {len(registros)} registros")
        
        return registros
    
    except json.JSONDecodeError:
        print(f"❌ ERROR: El archivo '{ruta}' no es JSON válido.")
        return []
    
    except Exception as e:
        print(f"❌ ERROR al cargar datos: {e}")
        return []


# =========================================================
# FUNCIÓN: VALIDAR FECHA
# =========================================================
# Convierte string a datetime y valida formato
# =========================================================

def _validar_fecha(fecha_str):
    """
    Convierte string "YYYY-MM-DD" a datetime.
    
    Args:
        fecha_str (str): Fecha en formato "YYYY-MM-DD"
        
    Returns:
        datetime: Objeto datetime o None si es inválida
    """
    
    if not fecha_str:
        return None
    
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d")
    except ValueError:
        print(f"⚠️  ADVERTENCIA: Fecha inválida '{fecha_str}'. Formato esperado: YYYY-MM-DD")
        return None


# =========================================================
# FUNCIÓN: FILTRAR POR FECHA
# =========================================================
# Filtra registros dentro del rango de fechas (inclusive)
# =========================================================

def filtrar_por_fecha(registros, fecha_desde=None, fecha_hasta=None):
    """
    Filtra registros dentro de un rango de fechas.
    
    Args:
        registros (list): Lista de diccionarios con registros
        fecha_desde (str): Fecha inicio en formato "YYYY-MM-DD"
        fecha_hasta (str): Fecha fin en formato "YYYY-MM-DD"
        
    Returns:
        list: Registros filtrados
        
    Nota:
        - Si ambas fechas son None, devuelve todos los registros
        - Si fecha_desde > fecha_hasta, las intercambia
        
    Ejemplos:
        >>> filtrados = filtrar_por_fecha(registros, "2026-03-01", "2026-03-05")
    """
    
    # Si no hay fechas, devolver todos
    if not fecha_desde and not fecha_hasta:
        return registros
    
    # Validar fechas
    dt_desde = _validar_fecha(fecha_desde) if fecha_desde else None
    dt_hasta = _validar_fecha(fecha_hasta) if fecha_hasta else None
    
    # Si no hay fechas válidas, devolver todos
    if not dt_desde and not dt_hasta:
        return registros
    
    # Si solo hay una fecha válida
    if dt_desde and not dt_hasta:
        return [r for r in registros if _validar_fecha(r.get('fecha')) >= dt_desde]
    
    if dt_hasta and not dt_desde:
        return [r for r in registros if _validar_fecha(r.get('fecha')) <= dt_hasta]
    
    # Asegurar que desde <= hasta
    if dt_desde > dt_hasta:
        dt_desde, dt_hasta = dt_hasta, dt_desde
    
    # Filtrar
    filtrados = []
    for r in registros:
        dt_registro = _validar_fecha(r.get('fecha'))
        if dt_registro and dt_desde <= dt_registro <= dt_hasta:
            filtrados.append(r)
    
    return filtrados


# =========================================================
# FUNCIÓN: CREAR ESTRUCTURA VACÍA
# =========================================================
# Genera una estructura de resumen con todos los valores en 0
# =========================================================

def _crear_resumen_vacio():
    """
    Crea una estructura de resumen inicializada en ceros.
    
    Returns:
        dict: Estructura con cargas, pasajeros y totales
    """
    
    return {
        "cargas": {
            "vc": 0,
            "actas": 0,
            "ret": 0
        },
        "pasajeros": {
            "vc": 0,
            "actas": 0,
            "ret": 0
        },
        "total": {
            "vc": 0,
            "actas": 0,
            "ret": 0
        }
    }


# =========================================================
# FUNCIÓN: CALCULAR RESUMEN
# =========================================================
# Separa por tipo y suma totales
# =========================================================

def calcular_resumen(registros):
    """
    Calcula resumen agrupado por tipo (CARGAS/PASAJEROS).
    
    Args:
        registros (list): Lista de diccionarios con registros
        
    Returns:
        dict: Estructura con sumas por tipo:
            {
                "cargas": {"vc": int, "actas": int, "ret": int},
                "pasajeros": {"vc": int, "actas": int, "ret": int},
                "total": {"vc": int, "actas": int, "ret": int}
            }
        
    Ejemplos:
        >>> resumen = calcular_resumen(registros)
        >>> print(resumen["cargas"]["vc"])  # Total VC de cargas
    """
    
    # Si no hay registros, devolver estructura vacía
    if not registros:
        return _crear_resumen_vacio()
    
    resumen = _crear_resumen_vacio()
    
    # Iterar registros
    for registro in registros:
        
        tipo = (registro.get('tipo') or "").upper()
        
        # Validar que sea un tipo conocido
        if tipo not in TIPOS_VALIDOS:
            continue
        
        # Obtener valores (default 0 si no existen)
        vc = int(registro.get('vc') or 0)
        actas = int(registro.get('actas') or 0)
        ret = int(registro.get('ret') or 0)
        
        # Sumar al tipo correspondiente
        if tipo == "CARGAS":
            resumen["cargas"]["vc"] += vc
            resumen["cargas"]["actas"] += actas
            resumen["cargas"]["ret"] += ret
        
        elif tipo == "PASAJEROS":
            resumen["pasajeros"]["vc"] += vc
            resumen["pasajeros"]["actas"] += actas
            resumen["pasajeros"]["ret"] += ret
    
    # Calcular totales
    resumen["total"]["vc"] = resumen["cargas"]["vc"] + resumen["pasajeros"]["vc"]
    resumen["total"]["actas"] = resumen["cargas"]["actas"] + resumen["pasajeros"]["actas"]
    resumen["total"]["ret"] = resumen["cargas"]["ret"] + resumen["pasajeros"]["ret"]
    
    return resumen


# =========================================================
# FUNCIÓN: CALCULAR POR REGIÓN
# =========================================================
# Agrupa por región manteniendo orden específico
# =========================================================

def calcular_por_region(registros):
    """
    Calcula resumen agrupado por región.
    
    Args:
        registros (list): Lista de diccionarios con registros
        
    Returns:
        dict: Estructura con datos por región:
            {
                "AMBA": {"cargas": {...}, "pasajeros": {...}, "total": {...}},
                "COSTA": {...},
                ...
            }
        
    Nota:
        - Mantiene el orden: AMBA, COSTA, BA, CEN, CUY, NEA, NOA, PAT
        - Si una región no tiene datos, devuelve estructura en ceros
        
    Ejemplos:
        >>> por_region = calcular_por_region(registros)
        >>> print(por_region["AMBA"]["cargas"]["vc"])
    """
    
    # Inicializar estructura por región
    resultado = {}
    for region in REGIONES_ORDEN:
        resultado[region] = _crear_resumen_vacio()
    
    # Si no hay registros, devolver estructura vacía
    if not registros:
        return resultado
    
    # Agrupar y sumar por región
    for registro in registros:
        
        region = (registro.get('region') or "").upper()
        tipo = (registro.get('tipo') or "").upper()
        
        # Validar región y tipo
        if region not in REGIONES_ORDEN or tipo not in TIPOS_VALIDOS:
            continue
        
        # Obtener valores
        vc = int(registro.get('vc') or 0)
        actas = int(registro.get('actas') or 0)
        ret = int(registro.get('ret') or 0)
        
        # Sumar al tipo correspondiente
        if tipo == "CARGAS":
            resultado[region]["cargas"]["vc"] += vc
            resultado[region]["cargas"]["actas"] += actas
            resultado[region]["cargas"]["ret"] += ret
        
        elif tipo == "PASAJEROS":
            resultado[region]["pasajeros"]["vc"] += vc
            resultado[region]["pasajeros"]["actas"] += actas
            resultado[region]["pasajeros"]["ret"] += ret
    
    # Calcular totales por región
    for region in REGIONES_ORDEN:
        resultado[region]["total"]["vc"] = (
            resultado[region]["cargas"]["vc"] + 
            resultado[region]["pasajeros"]["vc"]
        )
        resultado[region]["total"]["actas"] = (
            resultado[region]["cargas"]["actas"] + 
            resultado[region]["pasajeros"]["actas"]
        )
        resultado[region]["total"]["ret"] = (
            resultado[region]["cargas"]["ret"] + 
            resultado[region]["pasajeros"]["ret"]
        )
    
    return resultado


# =========================================================
# FUNCIÓN: GUARDAR RESUMEN EN JSON
# =========================================================
# Guarda el resumen calculado en el archivo datos.json
# para que JavaScript pueda leerlo fácilmente
# =========================================================

def guardar_resumen_en_datos(resumen_general, resumen_por_region, ruta="datos.json"):
    """
    Guarda los resúmenes calculados en el archivo datos.json.
    
    Args:
        resumen_general (dict): Resumen general de calcular_resumen()
        resumen_por_region (dict): Resumen por región de calcular_por_region()
        ruta (str): Ruta al archivo datos.json
        
    Returns:
        bool: True si se guardó correctamente, False si hay error
        
    Nota:
        - Si datos.json no existe, lo crea
        - Mantiene los datos existentes, solo actualiza los resúmenes
    """
    
    try:
        # Cargar datos existentes o crear estructura nueva
        datos = {}
        if os.path.exists(ruta):
            with open(ruta, 'r', encoding='utf-8') as f:
                datos = json.load(f)
        
        # Actualizar con nuevos resúmenes
        datos['resumen_general'] = resumen_general
        datos['resumen_por_region'] = resumen_por_region
        datos['metadata'] = datos.get('metadata', {})
        datos['metadata']['ultima_actualizacion'] = datetime.now().isoformat()
        
        # Guardar
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Resumen guardado en '{ruta}'")
        return True
    
    except Exception as e:
        print(f"❌ ERROR al guardar resumen: {e}")
        return False


# =========================================================
# FUNCIÓN: GENERAR INFORME COMPLETO
# =========================================================
# Flujo completo: cargar, filtrar, calcular, guardar
# =========================================================

def generar_informe_completo(fecha_desde=None, fecha_hasta=None):
    """
    Genera un informe completo con un flujo integrado.
    
    Args:
        fecha_desde (str): Fecha inicio "YYYY-MM-DD" (opcional)
        fecha_hasta (str): Fecha fin "YYYY-MM-DD" (opcional)
        
    Returns:
        dict: Estructura con resúmenes generales y por región
        
    Ejemplos:
        >>> informe = generar_informe_completo("2026-03-01", "2026-03-05")
        >>> print(informe['resumen_general']['total']['vc'])
    """
    
    print("\n" + "="*60)
    print("GENERANDO INFORME DE FISCALIZACIÓN")
    print("="*60)
    
    # 1. Cargar datos
    registros = cargar_datos()
    
    # 2. Filtrar por fecha
    registros_filtrados = filtrar_por_fecha(registros, fecha_desde, fecha_hasta)
    print(f"✓ Registros después de filtrado: {len(registros_filtrados)}")
    
    # 3. Calcular resúmenes
    resumen_general = calcular_resumen(registros_filtrados)
    resumen_por_region = calcular_por_region(registros_filtrados)
    
    print(f"✓ Total VC: {resumen_general['total']['vc']}")
    print(f"✓ Total Actas: {resumen_general['total']['actas']}")
    print(f"✓ Total Retenciones: {resumen_general['total']['ret']}")
    
    # 4. Guardar en datos.json
    guardar_resumen_en_datos(resumen_general, resumen_por_region)
    
    print("="*60 + "\n")
    
    return {
        'resumen_general': resumen_general,
        'resumen_por_region': resumen_por_region
    }


# =========================================================
# EJEMPLOS DE USO (ejecutar si se llama directamente)
# =========================================================

if __name__ == "__main__":
    
    print("\n" + "#"*60)
    print("# PRUEBAS: GESTOR DE DATOS DE FISCALIZACIÓN")
    print("#"*60)
    
    # Generar informe sin filtro de fechas
    print("\n--- PRUEBA 1: Informe general ---")
    informe = generar_informe_completo()
    
    print("\nResumen General:")
    print(f"  Cargas VC: {informe['resumen_general']['cargas']['vc']}")
    print(f"  Cargas Actas: {informe['resumen_general']['cargas']['actas']}")
    print(f"  Pasajeros VC: {informe['resumen_general']['pasajeros']['vc']}")
    print(f"  Pasajeros Actas: {informe['resumen_general']['pasajeros']['actas']}")
    
    # Generar informe con filtro de fechas
    print("\n--- PRUEBA 2: Informe con rango de fechas ---")
    informe_filtrado = generar_informe_completo("2026-03-01", "2026-03-03")
    
    print("\nResumen por Región (primeras 3):")
    for region in ["AMBA", "COSTA", "BA"]:
        print(f"\n{region}:")
        print(f"  Cargas VC: {informe_filtrado['resumen_por_region'][region]['cargas']['vc']}")
        print(f"  Pass. VC: {informe_filtrado['resumen_por_region'][region]['pasajeros']['vc']}")

