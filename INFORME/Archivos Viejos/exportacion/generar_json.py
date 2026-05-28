# =========================================================
# MÓDULO: EXPORTACIÓN DE DATOS A JSON
# =========================================================
# 
# Responsable de:
# - Generar estructura JSON para el frontend
# - Guardar datos procesados
# - Crear archivos de salida formateados
# =========================================================

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from config.settings import JSON_SALIDA, REGIONES_ORDENADAS
from utils import setup_logger

logger = setup_logger(__name__)

class ExportadorJSON:
    """Genera y exporta datos a JSON."""
    
    def __init__(self, archivo_salida: Path = None):
        """
        Inicializa el exportador.
        
        Args:
            archivo_salida: Ruta del archivo JSON (usa default si no se especifica)
        """
        self.archivo_salida = archivo_salida or JSON_SALIDA
    
    def generar_estructura_dashboard(self, resultados: Dict[str, Any]) -> Dict:
        """
        Genera la estructura JSON para el dashboard frontend.
        
        Args:
            resultados: Resultados del procesamiento
            
        Returns:
            Estructura JSON para frontend
        """
        metricas = resultados.get("metricas", {})
        regiones = resultados.get("regiones", {})
        registros = resultados.get("registros", [])
        incidencias = resultados.get("incidencias", [])
        
        # Calcular totales de actas
        total_actas_cargas = sum(
            regiones[r]["cargas"]["actas"] 
            for r in REGIONES_ORDENADAS if r in regiones
        )
        total_actas_pasajeros = sum(
            regiones[r]["pasajeros"]["actas"] 
            for r in REGIONES_ORDENADAS if r in regiones
        )
        total_actas = total_actas_cargas + total_actas_pasajeros
        
        # Estructura principal
        salida = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_registros": len(registros),
                "total_incidencias": len(incidencias),
                "modo_procesamiento": "A" if len(registros) < len(registros) else "B"
            },
            "resumen": {
                "total_cargas": metricas.get("total_cargas", 0),
                "total_pasajeros": metricas.get("total_pasajeros", 0),
                "total_retenciones": metricas.get("total_retenciones", 0),
                "total_actas": total_actas,
                "actas_articulo_108": 0,  # Se calcula por región
                "actas_articulo_110": 0,  # Se calcula por región
                "incidencias_alcoholemia": metricas.get("incidencias_alcoholemia", 0),
                "incidencias_sustancias": metricas.get("incidencias_sustancias", 0),
                "retenciones_alcoholemia": metricas.get("retenciones_alcoholemia", 0),
                "retenciones_sustancias": metricas.get("retenciones_sustancias", 0)
            },
            "regiones": regiones,
            "registros": registros,
            "incidencias": incidencias
        }
        
        # Calcular principales motivos de infracción por transportes
        salida["principal_infracciones"] = self._calcular_principales_motivos(
            registros, total_actas_cargas, total_actas_pasajeros
        )
        
        return salida
    
    def _calcular_principales_motivos(self, registros: list, 
                                     total_cargas: int, 
                                     total_pasajeros: int) -> Dict:
        """
        Calcula los principales motivos de infracción.
        
        Args:
            registros: Lista de registros procesados
            total_cargas: Total de actas de cargas
            total_pasajeros: Total de actas de pasajeros
            
        Returns:
            Estructura con principales motivos
        """
        motivos_cargas = {}
        motivos_pasajeros = {}
        
        for reg in registros:
            if not reg.get("articulo"):
                continue
            
            transporte = reg.get("transporte", "")
            articulo = reg.get("articulo", "")
            items = reg.get("items", "")
            
            key = f"Art. {articulo}" if articulo else "Sin artículo"
            
            if transporte == "CA":
                motivos_cargas[key] = motivos_cargas.get(key, 0) + 1
            elif transporte == "PA":
                motivos_pasajeros[key] = motivos_pasajeros.get(key, 0) + 1
        
        # Ordenar por cantidad descendente y tomar top 10
        top_cargas = dict(sorted(motivos_cargas.items(), key=lambda x: x[1], 
                                reverse=True)[:10])
        top_pasajeros = dict(sorted(motivos_pasajeros.items(), key=lambda x: x[1], 
                                   reverse=True)[:10])
        
        # Convertir a porcentajes
        return {
            "cargas": {
                "motivos": [
                    {
                        "nombre": k,
                        "cantidad": v,
                        "porcentaje": round((v / total_cargas * 100) if total_cargas > 0 else 0, 1)
                    }
                    for k, v in top_cargas.items()
                ],
                "totalActas": total_cargas,
                "totalPercent": 100
            },
            "pasajeros": {
                "motivos": [
                    {
                        "nombre": k,
                        "cantidad": v,
                        "porcentaje": round((v / total_pasajeros * 100) if total_pasajeros > 0 else 0, 1)
                    }
                    for k, v in top_pasajeros.items()
                ],
                "totalActas": total_pasajeros,
                "totalPercent": 100
            }
        }
    
    def guardar_json(self, datos: Dict) -> bool:
        """
        Guarda datos en archivo JSON.
        
        Args:
            datos: Estructura de datos a guardar
            
        Returns:
            True si se guardó correctamente, False si hay error
        """
        try:
            self.archivo_salida.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ JSON guardado: {self.archivo_salida}")
            logger.info(f"  Tamaño: {self.archivo_salida.stat().st_size / 1024:.1f} KB")
            
            return True
        except Exception as e:
            logger.error(f"Error guardando JSON: {e}")
            return False
    
    def exportar(self, resultados: Dict[str, Any]) -> bool:
        """
        Exporta resultados a JSON.
        
        Args:
            resultados: Resultados del procesamiento
            
        Returns:
            True si fue exitoso
        """
        logger.info("Generando estructura JSON para dashboard...")
        
        datos = self.generar_estructura_dashboard(resultados)
        
        return self.guardar_json(datos)

def exportar_json(resultados: Dict[str, Any], 
                 archivo: Path = None) -> bool:
    """
    Función auxiliar para exportar datos.
    
    Args:
        resultados: Resultados del procesamiento
        archivo: Archivo de salida (opcional)
        
    Returns:
        True si fue exitoso
    """
    exportador = ExportadorJSON(archivo_salida=archivo)
    return exportador.exportar(resultados)
