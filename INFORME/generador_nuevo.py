# =========================================================
# GENERADOR_NUEVO.PY - ORQUESTADOR PRINCIPAL RECONSTRUIDO
# =========================================================

import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

from config.settings import (
    EXCEL_DIR, MODO_PROCESAMIENTO, JSON_SALIDA,
    FLASK_DEBUG, FLASK_PORT, FLASK_HOST
)
from utils import setup_logger, titulo, subtitulo
from procesamiento import (
    obtener_archivos_excel, combinar_excels, aplicar_filtro_fechas,
    validar_integridad, log_estadisticas_excel, procesar_datos
)
from exportacion import exportar_json
from automatizacion import descargar_reportes_cnrt

# Inicializar logger oficial
logger = setup_logger("Generador")

class Orquestador:
    """Orquestador principal del procesamiento CNRT."""
    
    def __init__(self, descargar: bool = False, 
                 fecha_desde: Optional[str] = None,
                 fecha_hasta: Optional[str] = None):
        self.descargar = descargar
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.resultados = None
    
    async def ejecutar(self) -> bool:
        """Ejecuta el flujo de procesamiento controlado."""
        try:
            titulo("PROCESAMIENTO OPERATIVO CNRT - INICIO")
            
            # Paso 1: Descargar reportes (Opcional)
            if self.descargar:
                subtitulo("PASO 1: DESCARGA AUTOMÁTICA DE REPORTES")
                logger.info("Iniciando descarga por Playwright...")
                exitoso, descargas = await descargar_reportes_cnrt(
                    fecha_desde=self.fecha_desde,
                    fecha_hasta=self.fecha_hasta
                )
                if exitoso:
                    logger.info("✓ Descargas de red finalizadas.")
                else:
                    logger.warning("✗ Problemas en la descarga automatizada.")
            
            # Paso 2: Limpiar y leer Excel Local
            subtitulo("PASO 2: LECTURA Y LIMPIEZA SINCRO DE EXCEL")
            archivos = obtener_archivos_excel(EXCEL_DIR)
            
            if not archivos:
                logger.error(f"No se detectaron archivos Excel en la ruta: {EXCEL_DIR}")
                return False
                
            logger.info(f"Archivos en proceso ({len(archivos)}):")
            for arc in archivos:
                logger.info(f"   • {arc.name}")
                
            # Combinación de las tablas Excel
            df, _ = combinar_excels(archivos)
            
            if self.fecha_desde or self.fecha_hasta:
                logger.info(f"Filtrando rango temporal solicitado...")
                df = aplicar_filtro_fechas(df, self.fecha_desde, self.fecha_hasta)
                
            # Estadísticas de lectura en bruto
            stats_integridad = validar_integridad(df)
            log_estadisticas_excel(df, stats_integridad)
            
            # Paso 3: Procesamiento Core y Saneamiento Estricto
            subtitulo("PASO 3: SANEAMIENTO ESPECÍFICO Y MÉTRICAS")
            logger.info(f"Modo operativo seleccionado: {MODO_PROCESAMIENTO}")
            
            # Llamada al procesador orientado a objetos que modificamos en calculos.py
            self.resultados = procesar_datos(df, modo=MODO_PROCESAMIENTO)
            
            if not self.resultados:
                logger.error("El motor de procesamiento retornó un set vacío.")
                return False
                
            # =========================================================
            # IMPRESIÓN REVISADA DE RESULTADOS EN CONSOLA
            # =========================================================
            metricas = self.resultados.get("metricas", {})
            regiones_stats = self.resultados.get("regiones", {})
            
            total_vc = metricas.get('total_vehiculos', 0)
            total_cargas = metricas.get('total_cargas', 0)
            total_pasajeros = metricas.get('total_pasajeros', 0)
            
            porc_cargas = round((total_cargas / total_vc) * 100, 1) if total_vc > 0 else 0
            porc_pasajeros = round((total_pasajeros / total_vc) * 100, 1) if total_vc > 0 else 0

            titulo("RESUMEN CONSOLIDADO FINAL (DATOS SANEADOS)")
            print(f" • Vehículos Controlados Fiscales netos: {total_vc:,}")
            print(f"   - Transporte de Cargas:  {total_cargas:,} ({porc_cargas}%)")
            print(f"   - Transporte Pasajeros:  {total_pasajeros:,} ({porc_pasajeros}%)")
            print(f" • Actas de Infracción Labradas:  {metricas.get('total_actas', 0):,}")
            print(f" • Unidades con Retención Física: {metricas.get('total_retenciones', 0):,}")
            print(f" • Controles de Conducción Positivos (Alcoholemia/Sustancias): {metricas.get('incidencias_alcoholemia', 0) + metricas.get('incidencias_sustancias', 0):,}")
            
            print(f"\n  SECCIÓN INCUMPLIMIENTOS / AUDITORÍA:")
            print(f"   - Registros de Gendarmería / Confección aislados: {metricas.get('gendarmeria_confeccion_apartados', 0):,}")
            
            if regiones_stats:
                subtitulo("TABLA DE REGIONES COMPATIBLE CON DASHBOARD HTML")
                print(f"{'REGIÓN':<12} | {'CARGAS (VC/ACTAS/RET)':<22} | {'PASAJEROS (VC/ACTAS/RET)':<25}")
                print("-" * 65)
                for reg in ["AMBA", "CEN", "CUY", "NEA", "NOA", "COSTA", "PAT"]:
                    if reg in regiones_stats:
                        c = regiones_stats[reg].get('cargas', {'vc':0,'actas':0,'ret':0})
                        p = regiones_stats[reg].get('pasajeros', {'vc':0,'actas':0,'ret':0})
                        print(f"{reg:<12} | {c['vc']}/{c['actas']}/{c['ret']:<16} | {p['vc']}/{p['actas']}/{p['ret']}")
                print("=" * 65 + "\n")
            # =========================================================
            
            # Paso 4: Exportación de Datos Directa al JSON
            subtitulo("PASO 4: EXPORTACIÓN DE ESTRUCTURA COMPATIBLE")
            exitoso = exportar_json(self.resultados, JSON_SALIDA)
            
            if exitoso:
                titulo("PROCESAMIENTO COMPLETADO EXITOSAMENTE ✓")
                return True
            else:
                logger.error("Falló la escritura del archivo JSON de salida.")
                return False
                
        except Exception as e:
            logger.error(f"Error crítico en la ejecución del flujo: {e}", exc_info=True)
            return False
            
    def iniciar_servidor(self):
        """Inicializa la interfaz del Dashboard en Flask."""
        try:
            from app import app
            subtitulo("INICIANDO SERVIDOR DE VISUALIZACIÓN WEB")
            logger.info(f"Dashboard disponible en: http://{FLASK_HOST}:{FLASK_PORT}")
            logger.info("Para apagar el servidor presiona de forma continua: Ctrl + C")
            
            app.run(
                host=FLASK_HOST,
                port=FLASK_PORT,
                debug=FLASK_DEBUG
            )
        except ImportError:
            logger.error("No se pudo cargar el archivo app.py del servidor Flask.")
        except Exception as e:
            logger.error(f"Error al levantar el servicio web: {e}")

# =========================================================
# ENTRADA DEL PROGRAMA
# =========================================================
async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Orquestador del procesamiento CNRT")
    parser.add_argument("--descargar", action="store_true", help="Descarga web vía Playwright")
    parser.add_argument("--desde", type=str, help="Filtro Fecha Inicial (YYYY-MM-DD)")
    parser.add_argument("--hasta", type=str, help="Filtro Fecha Final (YYYY-MM-DD)")
    parser.add_argument("--solo-procesar", action="store_true", help="Evita levantar Flask")
    
    args = parser.parse_args()
    
    orquestador = Orquestador(
        descargar=args.descargar,
        fecha_desde=args.desde,
        fecha_hasta=args.hasta
    )
    
    exitoso = await orquestador.ejecutar()
    
    if not exitoso:
        logger.error("El proceso se detuvo por errores internos previos.")
        sys.exit(1)
        
    if not args.solo_procesar:
        orquestador.iniciar_servidor()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n✓ Sistema cerrado a solicitud del operador.")
        sys.exit(0)