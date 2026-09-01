# =========================================================
# EJEMPLO: USO AVANZADO DE MÓDULOS
# =========================================================
# 
# Este archivo muestra cómo usar los módulos de forma
# programática en tus propios scripts.
# =========================================================

"""
EJEMPLO 1: Procesamiento simple
"""

from pathlib import Path
from procesamiento import obtener_archivos_excel, combinar_excels, procesar_datos
from exportacion import exportar_json
from utils import setup_logger, titulo, subtitulo

logger = setup_logger(__name__)

def ejemplo_1_procesamiento_simple():
    """Procesa archivos Excel y genera JSON."""
    titulo("EJEMPLO 1: Procesamiento Simple")
    
    # Obtener archivos
    archivos = obtener_archivos_excel()
    logger.info(f"Archivos encontrados: {len(archivos)}")
    
    # Combinar
    df, total = combinar_excels(archivos)
    
    # Procesar
    resultados = procesar_datos(df, modo="A")
    
    # Exportar
    exportar_json(resultados, Path("ejemplo1_salida.json"))
    
    logger.info("✓ Ejemplo 1 completado")

# =========================================================

"""
EJEMPLO 2: Procesamiento con filtro de fechas
"""

from procesamiento import aplicar_filtro_fechas, validar_integridad

def ejemplo_2_con_filtro_fechas():
    """Procesa solo datos de un período específico."""
    titulo("EJEMPLO 2: Procesamiento con Filtro de Fechas")
    
    # Obtener y combinar
    archivos = obtener_archivos_excel()
    df, _ = combinar_excels(archivos)
    
    # Aplicar filtro
    df_filtrado = aplicar_filtro_fechas(
        df,
        fecha_desde="2024-01-01",
        fecha_hasta="2024-06-30"
    )
    
    # Validar
    stats = validar_integridad(df_filtrado)
    logger.info(f"Registros válidos: {stats['filas_validas']:,}")
    
    # Procesar
    resultados = procesar_datos(df_filtrado)
    
    # Exportar
    exportar_json(resultados, Path("ejemplo2_h1_2024.json"))
    
    logger.info("✓ Ejemplo 2 completado")

# =========================================================

"""
EJEMPLO 3: Análisis personalizado
"""

import pandas as pd
from collections import Counter
from utils import normalizar_region

def ejemplo_3_analisis_personalizado():
    """Análisis personalizado de los datos."""
    titulo("EJEMPLO 3: Análisis Personalizado")
    
    # Obtener datos
    archivos = obtener_archivos_excel()
    df, _ = combinar_excels(archivos)
    
    # Análisis 1: Distribución de regiones
    subtitulo("Distribución por región")
    regiones = df["REGION_NORMALIZADA"].value_counts()
    for region, count in regiones.items():
        porcentaje = (count / len(df)) * 100
        logger.info(f"{region}: {count:,} registros ({porcentaje:.1f}%)")
    
    # Análisis 2: Transportes por región
    subtitulo("Transportes por región")
    for region in regiones.index:
        df_region = df[df["REGION_NORMALIZADA"] == region]
        cargas = (df_region["TRANSPORTE"] == "CA").sum()
        pasajeros = (df_region["TRANSPORTE"] == "PA").sum()
        logger.info(f"{region}: Cargas={cargas}, Pasajeros={pasajeros}")
    
    # Análisis 3: Retenciones
    subtitulo("Análisis de retenciones")
    total_ret = (df["RETIENE"].isin(["SI", "SÍ"])).sum()
    pct_ret = (total_ret / len(df)) * 100
    logger.info(f"Total retenciones: {total_ret:,} ({pct_ret:.1f}%)")
    
    logger.info("✓ Ejemplo 3 completado")

# =========================================================

"""
EJEMPLO 4: Uso de automatización Playwright
"""

import asyncio
from automatizacion import descargar_reportes_cnrt

async def ejemplo_4_automatizacion():
    """Descarga reportes y luego procesa."""
    titulo("EJEMPLO 4: Automatización Playwright")
    
    # Nota: Requiere CNRT_USERNAME y CNRT_PASSWORD en variables de entorno
    
    try:
        logger.info("Iniciando descarga de reportes...")
        
        exitoso, resultados = await descargar_reportes_cnrt(
            delegaciones=["AMBA", "CEN"],  # Especificar delegaciones
            fecha_desde="2024-01-01",
            fecha_hasta="2024-12-31"
        )
        
        if exitoso:
            logger.info("✓ Descargas completadas")
            
            # Los archivos están en archivos/excels_descargados/
            # Ahora procesar
            archivos = obtener_archivos_excel()
            df, _ = combinar_excels(archivos)
            resultados = procesar_datos(df)
            exportar_json(resultados, Path("ejemplo4_con_descargas.json"))
            
            logger.info("✓ Ejemplo 4 completado")
        else:
            logger.error("✗ Error en descargas")
    
    except Exception as e:
        logger.error(f"Error: {e}")

# =========================================================

"""
EJEMPLO 5: Exportar a múltiples formatos
"""

import json
from exportacion import ExportadorJSON

def ejemplo_5_multiples_formatos():
    """Exporta a múltiples formatos."""
    titulo("EJEMPLO 5: Múltiples Formatos de Exportación")
    
    # Procesar
    archivos = obtener_archivos_excel()
    df, _ = combinar_excels(archivos)
    resultados = procesar_datos(df)
    
    # Exportar JSON
    exportador = ExportadorJSON(Path("ejemplo5_formato1.json"))
    datos_json = exportador.generar_estructura_dashboard(resultados)
    exportador.guardar_json(datos_json)
    
    # Exportar JSON limpio (solo registros)
    registros_limpios = [
        {k: v for k, v in r.items() if k != "dominios"}
        for r in resultados["registros"]
    ]
    
    with open("ejemplo5_registros.json", "w", encoding="utf-8") as f:
        json.dump(registros_limpios, f, indent=2, ensure_ascii=False)
    
    # Exportar CSV
    df_registros = pd.DataFrame(resultados["registros"])
    df_registros.to_csv("ejemplo5_registros.csv", index=False, encoding="utf-8")
    
    logger.info("✓ Ejemplo 5 completado - 3 formatos exportados")

# =========================================================

"""
EJEMPLO 6: Validaciones personalizadas
"""

from utils import elegir_articulo, detectar_incidencia

def ejemplo_6_validaciones():
    """Valida y filtra datos con reglas personalizadas."""
    titulo("EJEMPLO 6: Validaciones Personalizadas")
    
    # Procesar
    archivos = obtener_archivos_excel()
    df, _ = combinar_excels(archivos)
    
    # Filtro 1: Solo cargas con artículo 108
    df_cargas_108 = df[df["TRANSPORTE"] == "CA"]
    df_cargas_108["ARTICULO"] = df_cargas_108.apply(
        lambda row: elegir_articulo(row["TRANSPORTE"], row.get("ITEMS INFRACCION", "")),
        axis=1
    )
    df_cargas_108 = df_cargas_108[df_cargas_108["ARTICULO"] == "108"]
    
    logger.info(f"Cargas con artículo 108: {len(df_cargas_108):,}")
    
    # Filtro 2: Registros con incidencias
    df_con_incidencias = df[
        df.apply(lambda row: detectar_incidencia(row)[0] is not None, axis=1)
    ]
    
    logger.info(f"Registros con incidencias: {len(df_con_incidencias):,}")
    
    # Filtro 3: Retenciones sin artículo
    df_ret_sin_art = df[
        (df["RETIENE"].isin(["SI", "SÍ"])) & 
        (df.get("ITEMS INFRACCION", "").astype(str) == "")
    ]
    
    logger.info(f"Retenciones sin artículo: {len(df_ret_sin_art):,}")
    
    logger.info("✓ Ejemplo 6 completado")

# =========================================================

"""
EJEMPLO 7: Generar reportes por región
"""

def ejemplo_7_reportes_por_region():
    """Genera reportes independientes por región."""
    titulo("EJEMPLO 7: Reportes por Región")
    
    # Procesar
    archivos = obtener_archivos_excel()
    df, _ = combinar_excels(archivos)
    
    # Generar reporte para cada región
    for region in ["AMBA", "CEN", "CUY", "NEA", "NOA", "COSTA", "PAT"]:
        df_region = df[df["REGION_NORMALIZADA"] == region]
        
        if df_region.empty:
            logger.info(f"❌ {region}: Sin datos")
            continue
        
        # Procesar región
        resultados = procesar_datos(df_region)
        
        # Exportar
        archivo_salida = Path(f"reporte_{region}_detallado.json")
        exportar_json(resultados, archivo_salida)
        
        # Estadísticas
        metricas = resultados["metricas"]
        logger.info(f"✓ {region}: {metricas['total_cargas']} cargas, "
                   f"{metricas['total_pasajeros']} pasajeros")
    
    logger.info("✓ Ejemplo 7 completado")

# =========================================================

"""
EJEMPLO 8: Monitoreo y alertas
"""

def ejemplo_8_monitoreo():
    """Genera alertas basadas en umbrales."""
    titulo("EJEMPLO 8: Monitoreo y Alertas")
    
    # Procesar
    archivos = obtener_archivos_excel()
    df, _ = combinar_excels(archivos)
    resultados = procesar_datos(df)
    
    metricas = resultados["metricas"]
    
    # Alertas
    ALERTAS = {
        "retenciones_altas": (metricas["total_retenciones"], 200, ">"),
        "incidencias_alcoholemia_altas": (metricas["incidencias_alcoholemia"], 50, ">"),
        "incidencias_sustancias_altas": (metricas["incidencias_sustancias"], 30, ">"),
        "cargas_bajas": (metricas["total_cargas"], 100, "<"),
    }
    
    logger.info("\n📊 ALERTAS:")
    for nombre, (valor, umbral, operador) in ALERTAS.items():
        condicion = (valor > umbral) if operador == ">" else (valor < umbral)
        
        if condicion:
            logger.warning(f"⚠️  {nombre}: {valor} {operador} {umbral}")
        else:
            logger.info(f"✓ {nombre}: {valor} (normal)")
    
    logger.info("✓ Ejemplo 8 completado")

# =========================================================

"""
EJEMPLO 9: Uso combinado - Workflow completo
"""

async def ejemplo_9_workflow_completo():
    """Combina descargas, procesamiento y análisis."""
    titulo("EJEMPLO 9: Workflow Completo")
    
    # Paso 1: Descargar (opcional)
    # await ejemplo_4_automatizacion()
    
    # Paso 2: Procesar
    subtitulo("Paso 1: Procesamiento")
    archivos = obtener_archivos_excel()
    df, _ = combinar_excels(archivos)
    resultados = procesar_datos(df)
    
    # Paso 3: Validar
    subtitulo("Paso 2: Validación")
    stats = validar_integridad(df)
    logger.info(f"Datos válidos: {stats['filas_validas']:,}/{stats['total_filas']:,}")
    
    # Paso 4: Exportar múltiples formatos
    subtitulo("Paso 3: Exportación")
    exportar_json(resultados, Path("workflow_salida.json"))
    
    # Paso 5: Análisis
    subtitulo("Paso 4: Análisis")
    metricas = resultados["metricas"]
    logger.info(f"Total cargas: {metricas['total_cargas']:,}")
    logger.info(f"Total pasajeros: {metricas['total_pasajeros']:,}")
    logger.info(f"Total retenciones: {metricas['total_retenciones']:,}")
    
    logger.info("✓ Ejemplo 9 completado")

# =========================================================

if __name__ == "__main__":
    # Ejecutar ejemplos
    try:
        # Ejemplos síncronos
        print("\n" + "="*60)
        print("EJECUTANDO EJEMPLOS")
        print("="*60 + "\n")
        
        # Descomenta los ejemplos que quieras ejecutar
        
        # ejemplo_1_procesamiento_simple()
        # ejemplo_2_con_filtro_fechas()
        # ejemplo_3_analisis_personalizado()
        # await ejemplo_4_automatizacion()
        # ejemplo_5_multiples_formatos()
        # ejemplo_6_validaciones()
        # ejemplo_7_reportes_por_region()
        # ejemplo_8_monitoreo()
        # await ejemplo_9_workflow_completo()
        
        logger.info("\n¡Ejemplos listos para ejecutar!")
        logger.info("Descomenta el ejemplo que quieras usar en la sección '__main__'")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

# =========================================================
# NOTAS DE USO:
# 
# 1. Para ejecutar ejemplos síncronos:
#    python ejemplos_uso.py
#
# 2. Para ejecutar ejemplos con async:
#    Descomenta en __main__ y usa asyncio.run()
#
# 3. Para usar en tu script personalizado:
#    from procesamiento import *
#    from exportacion import *
#    from utils import *
#    # Tu código aquí
#
# 4. Ver documentación:
#    - ARQUITECTURA_MODULAR.md
#    - MIGRACION.md
#    - Docstrings en código
# =========================================================
