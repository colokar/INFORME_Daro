import pandas as pd
from typing import Dict, Any
from utils import setup_logger

logger = setup_logger("ProcesadorMetricas")

def procesar_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Aplica saneamiento estricto sobre el dataframe y procesa los datos limpios."""
        df_limpio = df.copy()
        
        # Homogeneizar nombres de columnas a mayúsculas
        df_limpio.columns = df_limpio.columns.str.strip().str.upper()
        
        # Rellenar vacíos para evitar que rompan los métodos string de Pandas
        for col in ["REGIONAL", "FISCALIZADOR", "TRANSPORTE"]:
            if col in df_limpio.columns:
                df_limpio[col] = df_limpio[col].fillna("").astype(str).str.strip().str.upper()
            else:
                df_limpio[col] = ""

        # -----------------------------------------------------------------
        # FILTRO 1: Apartar filas de Gendarmería y Confección (Auditoría)
        # -----------------------------------------------------------------
        filtro_gendarmeria = df_limpio["REGIONAL"].str.contains("GENDARMERIA|CONFECCION", na=False)
        df_gendarmeria_apartada = df_limpio[filtro_gendarmeria]
        df_final = df_limpio[~filtro_gendarmeria].copy()
        
        self.metricas["gendarmeria_confeccion_apartados"] = len(df_gendarmeria_apartada)
        
        # -----------------------------------------------------------------
        # FILTRO 2: Eliminar Fiscalizadores vacíos / Datos Sucios
        # -----------------------------------------------------------------
        invalidos = ["", "NAN", "NULL", "SIN NOMBRE", "0", "N/A", "INDETERMINADO"]
        df_final = df_final[
            df_final["FISCALIZADOR"].apply(lambda x: x.upper() not in invalidos)
        ]
        
        logger.info(f"Saneamiento: {len(df_gendarmeria_apartada):,} filas de Gendarmería apartadas.")
        logger.info(f"Procesando {len(df_final):,} filas netas para el Dashboard...")
        
        # -----------------------------------------------------------------
        # BUCLE DE PROCESAMIENTO CON MAPEO FLEXIBLE
        # -----------------------------------------------------------------
        for _, fila in df_final.iterrows():
            transporte_raw = str(fila.get("TRANSPORTE", "")).upper()
            
            # Mapeo inteligente: Si dice 'CARGA' o 'CA' va a cargas. Si dice 'PASAJ' o 'PA' va a pasajeros.
            if "CARG" in transporte_raw or transporte_raw == "CA":
                transporte = "CA"
            elif "PASAJ" in transporte_raw or transporte_raw == "PA":
                transporte = "PA"
            else:
                continue # Si es otra categoría inválida, salta la fila
                
            # Sobrescribimos temporalmente en la fila para que los submétodos de Copilot no se rompan
            fila["TRANSPORTE"] = transporte 
            
            # Ejecutar el procesamiento de la fila
            self.procesar_fila(fila)
        
        logger.info(f"Procesamiento completado: {len(self.registros):,} registros generados con éxito.")
        
        return {
            "registros": self.registros,
            "incidencias": self.incidencias,
            "metricas": self.metricas,
            "regiones": self.regiones
        }