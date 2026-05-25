# =========================================================
# MÓDULO: CÁLCULO DE MÉTRICAS POR REGIÓN
# =========================================================
# 
# Responsable de:
# - Procesar registros de fiscalización
# - Calcular estadísticas por región
# - Detectar incidencias
# - Generar métricas de dashboard
# =========================================================

import pandas as pd
from typing import List, Dict, Tuple, Any
from collections import defaultdict

from config.settings import (
    REGIONES_ORDENADAS, MODO_PROCESAMIENTO,
    TIPOS_TRANSPORTE_VALIDOS
)
from utils import (
    setup_logger, detectar_incidencia, elegir_articulo,
    convertir_dms_a_decimal
)

logger = setup_logger(__name__)

class ProcesadorRegistros:
    """Procesa registros de fiscalización y calcula métricas."""
    
    def __init__(self, modo: str = MODO_PROCESAMIENTO):
        """
        Inicializa el procesador.
        
        Args:
            modo: "A" (1 reg/fila) o "B" (1 reg/dominio)
        """
        self.modo = modo
        self.registros = []
        self.incidencias = []
        self.metricas = {
            "total_cargas": 0,
            "total_pasajeros": 0,
            "total_retenciones": 0,
            "total_dominios": 0,
            "incidencias_alcoholemia": 0,
            "incidencias_sustancias": 0,
            "retenciones_alcoholemia": 0,
            "retenciones_sustancias": 0
        }
        self.regiones = {
            region: {
                "cargas": {"vc": 0, "actas": 0, "ret": 0},
                "pasajeros": {"vc": 0, "actas": 0, "ret": 0},
                "total": {"vc": 0, "actas": 0, "ret": 0}
            }
            for region in REGIONES_ORDENADAS
        }
    
    def procesar_fila(self, fila: pd.Series):
        """
        Procesa una fila del DataFrame.
        
        Args:
            fila: Fila del DataFrame
        """
        fecha = str(fila.get("FECHA", ""))[:10]
        hora = str(fila.get("HORA", ""))
        regional_original = str(fila.get("REGIONAL", "")).strip()
        lugar = str(fila.get("LUGAR", "")).strip()
        regional = str(fila.get("REGION_NORMALIZADA", "SIN_REGION")).upper().strip()
        
        acta_obs = str(fila.get("ACTA OBS", "")).strip()
        retiene = str(fila.get("RETIENE", "")).upper().strip()
        items_infraccion = str(fila.get("ITEMS INFRACCION", "")).strip()
        
        # Convertir coordenadas
        latitud = convertir_dms_a_decimal(fila.get("LATITUD"))
        longitud = convertir_dms_a_decimal(fila.get("LONGITUD"))
        
        # Normalizar transporte
        transporte = str(fila.get("TRANSPORTE", "")).strip().upper()
        
        # Elegir artículo
        articulo = elegir_articulo(transporte, items_infraccion)
        
        # Detectar incidencia
        tipo_incidencia, fuente_incidencia = detectar_incidencia(fila)
        
        # Procesar dominios
        dominios_lista = [
            str(fila.get("DOMINIO", "")).strip().upper(),
            str(fila.get("DOMINIO2", "")).strip().upper(),
            str(fila.get("DOMINIO3", "")).strip().upper(),
        ]
        
        dominios_validos = [
            d for d in dominios_lista if d and d not in ["", "NAN"]
        ]
        
        self.metricas["total_dominios"] += len(dominios_validos)
        
        es_retencion = retiene in ["SI", "SÍ"]
        if es_retencion:
            self.metricas["total_retenciones"] += 1
        
        # Contar cargas/pasajeros según modo
        if self.modo == "A":
            if transporte == "CA":
                self.metricas["total_cargas"] += 1
            elif transporte == "PA":
                self.metricas["total_pasajeros"] += 1
        elif self.modo == "B":
            if transporte == "CA":
                self.metricas["total_cargas"] += len(dominios_validos)
            elif transporte == "PA":
                self.metricas["total_pasajeros"] += len(dominios_validos)
        
        # Generar registros según modo
        if self.modo == "A":
            self._generar_registro_modo_a(
                fecha, hora, regional, lugar, dominios_validos,
                transporte, items_infraccion, articulo, retiene,
                tipo_incidencia, latitud, longitud, acta_obs, es_retencion
            )
        elif self.modo == "B":
            self._generar_registros_modo_b(
                fecha, hora, regional, lugar, dominios_validos,
                transporte, items_infraccion, articulo, retiene,
                tipo_incidencia, latitud, longitud, acta_obs, es_retencion
            )
        
        # Contar incidencias
        self._contar_incidencias(tipo_incidencia, es_retencion)
        
        # Actualizar métricas por región
        self._actualizar_region(regional, transporte, articulo, retiene)
    
    def _generar_registro_modo_a(self, fecha, hora, regional, lugar, dominios,
                                 transporte, items, articulo, retiene,
                                 incidencia, lat, lon, acta, es_ret):
        """Genera registro en modo A (1 por fila)."""
        self.registros.append({
            "fecha": fecha,
            "hora": hora,
            "regional": regional,
            "lugar": lugar,
            "dominios": dominios,
            "transporte": transporte,
            "items": items,
            "articulo": articulo,
            "retiene": retiene,
            "incidencia": incidencia,
            "lat": lat,
            "lon": lon
        })
        
        if incidencia:
            self.incidencias.append({
                "fecha": fecha,
                "regional": regional,
                "lugar": lugar,
                "dominios": dominios,
                "latitud": lat,
                "longitud": lon,
                "tipo": incidencia,
                "acta_obs": acta,
                "retiene": es_ret
            })
    
    def _generar_registros_modo_b(self, fecha, hora, regional, lugar, dominios,
                                  transporte, items, articulo, retiene,
                                  incidencia, lat, lon, acta, es_ret):
        """Genera registros en modo B (1 por dominio)."""
        for dominio in dominios:
            self.registros.append({
                "fecha": fecha,
                "hora": hora,
                "regional": regional,
                "lugar": lugar,
                "dominio": dominio,
                "transporte": transporte,
                "items": items,
                "articulo": articulo,
                "retiene": retiene,
                "incidencia": incidencia,
                "lat": lat,
                "lon": lon
            })
            
            if incidencia:
                self.incidencias.append({
                    "fecha": fecha,
                    "regional": regional,
                    "lugar": lugar,
                    "dominio": dominio,
                    "latitud": lat,
                    "longitud": lon,
                    "tipo": incidencia,
                    "acta_obs": acta,
                    "retiene": es_ret
                })
    
    def _contar_incidencias(self, tipo: str, es_ret: bool):
        """Actualiza contadores de incidencias."""
        if tipo == "ALCOHOLEMIA":
            self.metricas["incidencias_alcoholemia"] += 1
            if es_ret:
                self.metricas["retenciones_alcoholemia"] += 1
        elif tipo == "SUSTANCIA":
            self.metricas["incidencias_sustancias"] += 1
            if es_ret:
                self.metricas["retenciones_sustancias"] += 1
    
    def _actualizar_region(self, regional: str, transporte: str, 
                          articulo: str, retiene: str):
        """Actualiza métricas de región."""
        if not regional or regional not in REGIONES_ORDENADAS:
            return
        
        cat = "cargas" if transporte == "CA" else "pasajeros"
        if cat not in ["cargas", "pasajeros"]:
            return
        
        # Actualizar categoría y total
        for key in [cat, "total"]:
            self.regiones[regional][key]["vc"] += 1
            if articulo:
                self.regiones[regional][key]["actas"] += 1
            if retiene == "SI":
                self.regiones[regional][key]["ret"] += 1
    
    def procesar_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Procesa todo el DataFrame.
        
        Args:
            df: DataFrame con datos de fiscalización
            
        Returns:
            Diccionario con resultados del procesamiento
        """
        logger.info(f"Procesando {len(df):,} filas en modo {self.modo}...")
        
        for _, fila in df.iterrows():
            self.procesar_fila(fila)
        
        logger.info(f"Procesamiento completado: {len(self.registros):,} registros generados")
        
        return {
            "registros": self.registros,
            "incidencias": self.incidencias,
            "metricas": self.metricas,
            "regiones": self.regiones
        }

def procesar_datos(df: pd.DataFrame, modo: str = MODO_PROCESAMIENTO) -> Dict[str, Any]:
    """
    Función auxiliar para procesar datos.
    
    Args:
        df: DataFrame a procesar
        modo: Modo de procesamiento
        
    Returns:
        Resultados del procesamiento
    """
    procesador = ProcesadorRegistros(modo=modo)
    return procesador.procesar_dataframe(df)
