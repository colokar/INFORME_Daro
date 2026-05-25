# =========================================================
# GENERADOR.PY - ORQUESTADOR PRINCIPAL
# =========================================================
# 
# Este archivo actúa como orquestador principal del proyecto.
# Coordina la ejecución de diferentes módulos sin mezclar lógica.
# 
# Flujo:
# 1. Descargar reportes (OPCIONAL)
# 2. Limpiar y leer Excel
# 3. Procesar datos y calcular métricas
# 4. Exportar a JSON
# 5. Iniciar servidor Flask
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

# Inicializar logger
logger = setup_logger("Generador")

class Orquestador:
    """Orquestador principal del procesamiento CNRT."""
    
    def __init__(self, descargar: bool = False, 
                 fecha_desde: Optional[str] = None,
                 fecha_hasta: Optional[str] = None):
        """
        Inicializa el orquestador.
        
        Args:
            descargar: Si descargar reportes antes de procesar
            fecha_desde: Fecha desde (YYYY-MM-DD)
            fecha_hasta: Fecha hasta (YYYY-MM-DD)
        """
        self.descargar = descargar
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.resultados = None
    
    async def ejecutar(self) -> bool:
        """
        Ejecuta el flujo completo de procesamiento.
        
        Returns:
            True si fue exitoso
        """
        try:
            titulo("PROCESAMIENTO CNRT - INICIO")
            
            # Paso 1: Descargar reportes (opcional)
            if self.descargar:
                await self._paso_descargar()
            
            # Paso 2: Limpiar y leer Excel
            df = await self._paso_limpiar_excel()
            if df is None:
                return False
            
            # Paso 3: Procesar datos
            self.resultados = self._paso_procesar_datos(df)
            
            # Paso 4: Exportar JSON
            exitoso = self._paso_exportar()
            
            if exitoso:
                titulo("PROCESAMIENTO COMPLETADO ✓")
            else:
                logger.error("Error en exportación")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error fatal: {e}", exc_info=True)
            return False
    
    async def _paso_descargar(self):
        """Descarga reportes del sistema CNRT."""
        try:
            subtitulo("PASO 1: DESCARGA DE REPORTES")
            logger.info("Iniciando descarga automática de reportes...")
            
            # Descargar todos los reportes disponibles
            exitoso, resultados = await descargar_reportes_cnrt(
                fecha_desde=self.fecha_desde,
                fecha_hasta=self.fecha_hasta
            )
            
            if exitoso:
                logger.info("✓ Descargas completadas")
                for delegacion, ok in resultados.items():
                    status = "✓" if ok else "✗"
                    logger.info(f"  {status} {delegacion}")
            else:
                logger.error("✗ Error en descargas")
        
        except Exception as e:
            logger.error(f"Error en descarga: {e}")
    
    def _paso_limpiar_excel(self):
        """Lee y limpia archivos Excel."""
        try:
            subtitulo("PASO 2: LECTURA Y LIMPIEZA DE EXCEL")
            
            # Obtener archivos
            archivos = obtener_archivos_excel(EXCEL_DIR)
            
            if not archivos:
                logger.error(f"No se encontraron archivos Excel en {EXCEL_DIR}")
                return None
            
            logger.info(f"Archivos encontrados: {len(archivos)}")
            for archivo in archivos:
                logger.info(f"  • {archivo.name}")
            
            # Combinar Excel
            df, total_filas = combinar_excels(archivos)
            
            # Aplicar filtro de fechas
            if self.fecha_desde or self.fecha_hasta:
                logger.info(f"Aplicando filtro de fechas...")
                df = aplicar_filtro_fechas(df, self.fecha_desde, self.fecha_hasta)
            
            # Validar integridad
            stats = validar_integridad(df)
            log_estadisticas_excel(df, stats)
            
            logger.info(f"✓ {len(df):,} registros listos para procesar")
            
            return df
        
        except Exception as e:
            logger.error(f"Error en limpieza de Excel: {e}")
            return None
    
    def _paso_procesar_datos(self, df) -> Optional[dict]:
        """Procesa datos y calcula métricas."""
        try:
            subtitulo("PASO 3: PROCESAMIENTO Y CÁLCULO DE MÉTRICAS")
            
            logger.info(f"Modo de procesamiento: {MODO_PROCESAMIENTO}")
            
            resultados = procesar_datos(df, modo=MODO_PROCESAMIENTO)
            
            # Mostrar resumen
            metricas = resultados.get("metricas", {})
            logger.info(f"\nResumen de procesamiento:")
            logger.info(f"  • Total cargas: {metricas.get('total_cargas', 0):,}")
            logger.info(f"  • Total pasajeros: {metricas.get('total_pasajeros', 0):,}")
            logger.info(f"  • Total retenciones: {metricas.get('total_retenciones', 0):,}")
            logger.info(f"  • Total incidencias: {metricas.get('incidencias_alcoholemia', 0) + metricas.get('incidencias_sustancias', 0):,}")
            logger.info(f"    - Alcoholemia: {metricas.get('incidencias_alcoholemia', 0):,}")
            logger.info(f"    - Sustancias: {metricas.get('incidencias_sustancias', 0):,}")
            
            return resultados
        
        except Exception as e:
            logger.error(f"Error en procesamiento: {e}")
            return None
    
    def _paso_exportar(self) -> bool:
        """Exporta resultados a JSON."""
        try:
            subtitulo("PASO 4: EXPORTACIÓN A JSON")
            
            if self.resultados is None:
                logger.error("No hay resultados para exportar")
                return False
            
            exitoso = exportar_json(self.resultados, JSON_SALIDA)
            
            if exitoso:
                logger.info("✓ Exportación completada")
                return True
            else:
                logger.error("✗ Error en exportación")
                return False
        
        except Exception as e:
            logger.error(f"Error en exportación: {e}")
            return False
    
    def iniciar_servidor(self):
        """Inicia el servidor Flask."""
        try:
            from app import app
            
            subtitulo("INICIANDO SERVIDOR WEB")
            logger.info(f"Servidor escuchando en http://{FLASK_HOST}:{FLASK_PORT}")
            logger.info("Presiona Ctrl+C para detener")
            
            app.run(
                host=FLASK_HOST,
                port=FLASK_PORT,
                debug=FLASK_DEBUG
            )
        
        except ImportError:
            logger.error("No se pudo importar app.py")
        except Exception as e:
            logger.error(f"Error iniciando servidor: {e}")

# =========================================================
# PUNTO DE ENTRADA
# =========================================================

async def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Orquestador del procesamiento CNRT"
    )
    parser.add_argument(
        "--descargar",
        action="store_true",
        help="Descargar reportes del sistema CNRT antes de procesar"
    )
    parser.add_argument(
        "--desde",
        type=str,
        help="Fecha desde (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--hasta",
        type=str,
        help="Fecha hasta (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--solo-procesar",
        action="store_true",
        help="Solo procesar Excel sin iniciar servidor"
    )
    
    args = parser.parse_args()
    
    # Crear orquestador
    orquestador = Orquestador(
        descargar=args.descargar,
        fecha_desde=args.desde,
        fecha_hasta=args.hasta
    )
    
    # Ejecutar procesamiento
    exitoso = await orquestador.ejecutar()
    
    if not exitoso:
        logger.error("Procesamiento fallido")
        sys.exit(1)
    
    # Iniciar servidor si no es modo solo-procesar
    if not args.solo_procesar:
        orquestador.iniciar_servidor()

if __name__ == "__main__":
    # Ejecutar con soporte para async si es necesario
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n✓ Proceso interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)
