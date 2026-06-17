import re

# =========================================================================
# CNRT - BIBLIOTECA SANEADA DE ARTÍCULOS PARA DASHBOARD
# Basado en Decretos Estatales 1395/1998 (Pasajeros) y 1035/2002 (Cargas)
# =========================================================================

def agrupar_y_sanear_articulos(articulo_crudo, tipo_transporte):
    """
    Toma el artículo de la planilla (ej: 18, 105, '105') y el ramal (PA o CA).
    Devuelve la categoría limpia y unificada para las 11 barras del Dashboard.
    """
    # Limpiamos los datos de entrada para evitar fallas por formatos
    art = str(articulo_crudo).strip()
    transporte = str(tipo_transporte).strip().upper()[:2]

    # ==========================================
    # RAMAL PASAJEROS (PA) - Top de Infracciones
    # ==========================================
    if transporte == "PA":
        if art == "105":
            return "Deficiencias mecánicas, de carrocería o instrumental"
        elif art == "91":
            return "Falta de documentación de servicio - DUT / LP"
        elif art == "96":
            return "Conductores sin descanso mínimo"
        elif art == "112":
            return "Libreta de trabajo / Control horario irregular"
        elif art in ["136", "126"]:
            return "Prestar servicios con vehículos o personal desafectados"
        elif art in ["82", "83"]:
            return "Incumplimiento de horarios y frecuencias"
        elif art == "111":
            return "Falta de documentos obligatorios a bordo"
        else:
            return "Otros"

    # ==========================================
    # RAMAL CARGAS (CA) - Top de Infracciones
    # ==========================================
    elif transporte == "CA":
        if art == "18":
            return "Falta de Revisión Técnica Obligatoria (RTO)"
        elif art == "22":
            return "Conductor sin Licencia Nacional Habilitante (LNH)"
        elif art == "26":
            return "Falta de documentación de la carga (Carta de Porte / Remito)"
        elif art in ["42", "34", "45", "49", "23", "24"]:
            # Unifica todo el bloque operativo y de cargas peligrosas
            return "Irregularidades en Transporte de Cargas"
        elif art == "27":
            return "Desobediencia a las órdenes de la Autoridad de Aplicación"
        else:
            return "Otros"

    return "Otros"