# =========================================================
# MÓDULO: CÁLCULO DE MÉTRICAS POR REGIÓN (SANEADO)
# =========================================================
# 
# Responsable de:
# - Filtrar y aislar registros de Gendarmería / Confección
# - Eliminar filas corruptas sin nombre de Fiscalizador
# - Procesar registros de fiscalización válidos CNRT
# - Calcular estadísticas por región compatibles con HTML
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
    """Procesa registros de fiscalización y calcula métricas saneadas."""
    
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
            "retenciones_sustancias": 0,
            "gendarmeria_confeccion_apartados": 0  # <--- Guardamos el conteo aparte de auditoría
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
        """Procesa una fila del DataFrame saneado."""
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
        if not regional or regional not in REGIONES_ORDENADAS:
            return
        
        cat = "cargas" if transporte == "CA" else "pasajeros"
        if cat not in ["cargas", "pasajeros"]:
            return
        
        for key in [cat, "total"]:
            self.regiones[regional][key]["vc"] += 1
            if articulo:
                self.regiones[regional][key]["actas"] += 1
            if retiene in ["SI", "SÍ"]:
                self.regiones[regional][key]["ret"] += 1
    
    def procesar_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Aplica saneamiento estricto sobre el dataframe y procesa los datos limpios."""
        df_limpio = df.copy()
        
        # Homogeneizar nombres de columnas a mayúsculas
        df_limpio.columns = df_limpio.columns.str.strip().str.upper()
        
        # Rellenar vacíos para evitar que rompan los métodos string de Pandas
        for col in ["REGIONAL", "FISCALIZADOR", "TRANSPORTE"]:
            if col in df_limpio.columns:
                df_limpio[col] = df_limpio[col].fillna("").astype(str).str.strip()
            else:
                df_limpio[col] = ""

        # -----------------------------------------------------------------
        # FILTRO 1: Apartar filas de Gendarmería y Confección (Auditoría)
        # -----------------------------------------------------------------
        filtro_gendarmeria = df_limpio["REGIONAL"].str.upper().str.contains("GENDARMERIA|CONFECCION", na=False)
        df_gendarmeria_apartada = df_limpio[filtro_gendarmeria]
        df_final = df_limpio[~filtro_gendarmeria].copy()
        
        # Guardamos la métrica del bloque que apartamos
        self.metricas["gendarmeria_confeccion_apartados"] = len(df_gendarmeria_apartada)
        
        # -----------------------------------------------------------------
        # FILTRO 2: Eliminar Fiscalizadores vacíos / Datos Sucios
        # -----------------------------------------------------------------
        invalidos = ["", "NAN", "NULL", "SIN NOMBRE", "0", "N/A", "INDETERMINADO"]
        df_final = df_final[
            df_final["FISCALIZADOR"].apply(lambda x: x.upper() not in invalidos)
        ]
        
        # Logs de control en la consola
        logger.info(f"Saneamiento: {len(df_gendarmeria_apartada):,} filas de Gendamería apartadas.")
        logger.info(f"Saneamiento: {len(df) - len(df_gendarmeria_apartada) - len(df_final):,} filas sin fiscalizador eliminadas.")
        logger.info(f"Procesando {len(df_final):,} filas limpias en modo {self.modo}...")
        
        # Ejecutar ciclo de procesamiento sobre las filas netas e impecables
        for _, fila in df_final.iterrows():
            self.procesar_fila(fila)
        
        logger.info(f"Procesamiento completado: {len(self.registros):,} registros generados")
        
        return {
            "registros": self.registros,
            "incidencias": self.incidencias,
            "metricas": self.metricas,
            "regiones": self.regiones
        }

def procesar_datos(df: pd.DataFrame, modo: str = MODO_PROCESAMIENTO) -> Dict[str, Any]:
    procesador = ProcesadorRegistros(modo=modo)
    return procesador.procesar_dataframe(df)