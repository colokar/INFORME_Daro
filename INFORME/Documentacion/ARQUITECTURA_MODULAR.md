# 📐 Arquitectura Modular del Proyecto CNRT

## 📋 Descripción General

El proyecto ha sido refactorizado de un archivo monolítico (`generador.py` de 753 líneas) a una **arquitectura modular, escalable y mantenible** basada en principios SOLID y separación de responsabilidades.

---

## 🏗️ Estructura del Proyecto

```
INFORME/
│
├── generador_nuevo.py          ⭐ ORQUESTADOR PRINCIPAL
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuración centralizada
│
├── utils/
│   ├── __init__.py
│   ├── logger.py               # Sistema de logging
│   └── normalizaciones.py      # Funciones de normalización
│
├── procesamiento/
│   ├── __init__.py
│   ├── limpiar_excel.py        # Lectura y limpieza de Excel
│   └── calcular_metricas.py    # Cálculo de métricas
│
├── exportacion/
│   ├── __init__.py
│   └── generar_json.py         # Generación de JSON
│
├── automatizacion/
│   ├── __init__.py
│   └── descarga_cnrt.py        # Automatización con Playwright
│
├── archivos/
│   ├── excels_descargados/     # Excel descargados automáticamente
│   └── procesados/             # Archivos procesados
│
├── logs/
│   └── procesamiento.log       # Registros de ejecución
│
└── Excel/                      # Carpeta con archivos fuente
    └── (archivos .xls/.xlsx)
```

---

## 🔧 Módulos Principales

### 1️⃣ **config/settings.py** - Configuración Centralizada

**Responsabilidad:** Centralizar TODAS las constantes, rutas y parámetros del proyecto.

```python
# Directorios
BASE_DIR = Path(__file__).parent.parent
EXCEL_DIR = BASE_DIR / "Excel"
LOGS_DIR = BASE_DIR / "logs"

# Mapeo de regiones
MAPA_REGIONES = {
    "AMBA": [...],
    "CEN": [...],
    # ...
}

# Configuración de Flask
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000

# Parámetros de Playwright
PLAYWRIGHT_HEADLESS = True
PLAYWRIGHT_TIMEOUT = 30000
```

**Ventajas:**
- 📝 Un único lugar para cambiar constantes
- 🔒 Fácil de securizar (usar `os.getenv()` para credenciales)
- 🎯 Configuración por ambiente (desarrollo/producción)

---

### 2️⃣ **utils/logger.py** - Sistema de Logging

**Responsabilidad:** Proporcionar logging consistente a consola y archivo.

```python
from utils import setup_logger, titulo, subtitulo

logger = setup_logger(__name__)
logger.info("Mensaje informativo")
logger.error("Mensaje de error")

titulo("TITULO GRANDE")
subtitulo("Subtítulo")
```

**Ventajas:**
- 📊 Logs a archivo y consola simultáneamente
- 🎨 Formato consistente
- 🔍 Fácil debugging

---

### 3️⃣ **utils/normalizaciones.py** - Funciones Reutilizables

**Responsabilidad:** Centralizar todas las funciones de normalización y validación.

```python
# Funciones disponibles:
normalizar(texto)                    # "MaÑana" → "manana"
normalizar_region(valor)             # "La PLATA" → "AMBA"
convertir_dms_a_decimal(coordenada)  # "34°12'45"S" → -34.2125
detectar_incidencia(fila)            # Detecta alcoholemia/sustancias
elegir_articulo(transporte, items)   # Elige Art. 108 o 110
validar_fila(fila)                   # Valida integridad de fila
```

**Ventajas:**
- ♻️ Funciones reutilizables desde cualquier módulo
- 🧪 Fáciles de testear
- 📚 Documentadas con docstrings

---

### 4️⃣ **procesamiento/limpiar_excel.py** - Lectura de Excel

**Responsabilidad:** Manejo completo de archivos Excel.

```python
from procesamiento import (
    obtener_archivos_excel,
    leer_excel,
    limpiar_dataframe,
    combinar_excels,
    aplicar_filtro_fechas,
    validar_integridad
)

# Ejemplo
archivos = obtener_archivos_excel()
df, total = combinar_excels(archivos)
df = aplicar_filtro_fechas(df, "2024-01-01", "2024-12-31")
stats = validar_integridad(df)
```

**Funciones:**
- `obtener_archivos_excel()` - Busca .xls y .xlsx
- `leer_excel()` - Lee con engine automático
- `limpiar_dataframe()` - Normaliza columnas y datos
- `combinar_excels()` - Une múltiples archivos
- `aplicar_filtro_fechas()` - Filtra por rango de fechas
- `validar_integridad()` - Retorna estadísticas

---

### 5️⃣ **procesamiento/calcular_metricas.py** - Cálculos

**Responsabilidad:** Procesar registros y calcular métricas.

```python
from procesamiento import procesar_datos

resultados = procesar_datos(df, modo="A")

# Retorna:
{
    "registros": [...],
    "incidencias": [...],
    "metricas": {
        "total_cargas": 500,
        "total_pasajeros": 300,
        "total_retenciones": 120,
        "incidencias_alcoholemia": 15,
        # ...
    },
    "regiones": {
        "AMBA": {...},
        "CEN": {...},
        # ...
    }
}
```

**Características:**
- 🎯 Clase `ProcesadorRegistros` para fácil extensión
- 📊 Modo A (1 registro/fila) o Modo B (1 registro/dominio)
- 🔢 Cálculos de métricas por región
- 🚨 Detección de incidencias

---

### 6️⃣ **exportacion/generar_json.py** - Exportación

**Responsabilidad:** Generar JSON para el frontend.

```python
from exportacion import exportar_json

exitoso = exportar_json(resultados, archivo="datos.json")
```

**Genera:**
- Estructura JSON para dashboard
- Cálculo de principales motivos de infracción
- Estadísticas por región
- Compatibilidad con frontend existente

---

### 7️⃣ **automatizacion/descarga_cnrt.py** - Playwright

**Responsabilidad:** Automatizar descargas del sistema CNRT.

```python
from automatizacion import descargar_reportes_cnrt
import asyncio

async def descargar():
    exitoso, resultados = await descargar_reportes_cnrt(
        delegaciones=["AMBA", "CEN"],
        fecha_desde="2024-01-01",
        fecha_hasta="2024-12-31"
    )

asyncio.run(descargar())
```

**Características:**
- 🤖 Automatización completa del login
- 📥 Descarga de reportes por delegación
- ⏱️ Manejo de timeouts y reintentos
- 📁 Guardado automático en `archivos/excels_descargados/`

**Nota:** Incluye placeholders para selectores reales del sitio CNRT.

---

### 8️⃣ **generador_nuevo.py** - Orquestador

**Responsabilidad:** Coordinar el flujo completo sin mezclar lógica.

```bash
# Ejecutar con todas las opciones
python generador_nuevo.py \
    --descargar \
    --desde 2024-01-01 \
    --hasta 2024-12-31

# Solo procesar Excel
python generador_nuevo.py --solo-procesar

# Ayuda
python generador_nuevo.py --help
```

**Flujo:**
```
1. Descargar reportes (opcional) ← Playwright
2. Limpiar Excel ← Pandas
3. Procesar datos ← Cálculos
4. Exportar JSON ← Frontend
5. Iniciar servidor Flask
```

---

## 🚀 Cómo Usar

### Instalación Inicial

```bash
# Navegar al directorio
cd INFORME

# Crear entorno virtual
python -m venv .venv

# Activar entorno
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Para Playwright
pip install playwright
playwright install
```

### Uso Básico

```bash
# Procesar archivos Excel y iniciar servidor
python generador_nuevo.py

# Procesar con filtro de fechas
python generador_nuevo.py --desde 2024-01-01 --hasta 2024-12-31

# Solo procesar (sin servidor)
python generador_nuevo.py --solo-procesar
```

### Con Automatización

```bash
# Descargar reportes y procesar
python generador_nuevo.py --descargar --desde 2024-01-01

# Nota: Requiere credenciales en variables de entorno
# export CNRT_USERNAME="usuario"
# export CNRT_PASSWORD="contraseña"
```

---

## 📊 Flujo de Datos

```
┌─────────────────┐
│  CNRT Website   │
│  (Playwright)   │
└────────┬────────┘
         │ ↓
    📥 Descargar
         │
┌────────▼────────────┐
│ Excel Files         │
│ /excels_descargados/│
└────────┬────────────┘
         │ ↓
    🧹 Limpiar
         │
┌────────▼────────────┐
│ DataFrame Limpio    │
│ (Normalizado)       │
└────────┬────────────┘
         │ ↓
    🔢 Procesar
         │
┌────────▼────────────┐
│ Registros           │
│ + Métricas          │
│ + Incidencias       │
└────────┬────────────┘
         │ ↓
    📤 Exportar JSON
         │
┌────────▼────────────┐
│ datos.json          │
│ (Frontend)          │
└────────┬────────────┘
         │ ↓
    🌐 Servidor Flask
         │
       ✅ Dashboard
```

---

## 🧪 Testing

Cada módulo puede testearse independientemente:

```python
# Test de normalización
from utils import normalizar, normalizar_region

assert normalizar("MaÑANA") == "manana"
assert normalizar_region("LA PLATA") == "AMBA"

# Test de procesamiento
from procesamiento import procesar_datos

resultados = procesar_datos(df, modo="A")
assert len(resultados["registros"]) > 0

# Test de exportación
from exportacion import exportar_json

exitoso = exportar_json(resultados, Path("test.json"))
assert exitoso
```

---

## 🔐 Seguridad

### Credenciales

**NUNCA** hardcodees credenciales. Usa variables de entorno:

```python
# config/settings.py
import os

CNRT_USERNAME = os.getenv("CNRT_USERNAME", "")
CNRT_PASSWORD = os.getenv("CNRT_PASSWORD", "")
```

```bash
# Comando (no commitearlo)
export CNRT_USERNAME="tu_usuario"
export CNRT_PASSWORD="tu_contraseña"
```

---

## 📈 Escalabilidad

### Agregar Nueva Funcionalidad

Ejemplo: Generar reportes en PDF con Typst

```python
# Crear: exportacion/generar_typst.py
class GeneradorTypst:
    def generar(self, resultados):
        # Lógica para generar PDF
        pass

# En generador_nuevo.py
from exportacion import GeneradorTypst

# En orquestador...
```

### Agregar Nuevo Procesamiento

```python
# Crear: procesamiento/nuevo_procesamiento.py
def procesar_algo_nuevo(df):
    # Tu lógica
    pass

# Importar y usar en generador_nuevo.py
```

---

## 📝 Estructura de Logs

```
2024-05-25 10:30:45 - INFO - ============================================================
2024-05-25 10:30:45 - INFO - PROCESAMIENTO CNRT - INICIO
2024-05-25 10:30:45 - INFO - ============================================================
2024-05-25 10:30:46 - INFO - --- PASO 1: DESCARGA DE REPORTES ---
2024-05-25 10:30:46 - INFO - Iniciando descarga automática de reportes...
2024-05-25 10:31:00 - INFO - ✓ Descargas completadas
2024-05-25 10:31:00 - INFO -   ✓ AMBA
2024-05-25 10:31:15 - INFO -   ✓ CEN
...
```

---

## ✅ Checklist de Implementación

- [x] Separar configuración en `config/settings.py`
- [x] Crear sistema de logging centralizado
- [x] Extraer funciones de normalización
- [x] Modularizar lectura de Excel
- [x] Modularizar cálculos de métricas
- [x] Crear exportador JSON
- [x] Implementar Playwright para descargas
- [x] Crear orquestador limpio
- [x] Documentar arquitectura
- [ ] Crear suite de tests (próximo paso)
- [ ] Agregar autenticación Flask (opcional)
- [ ] Crear dashboard mejorado (opcional)

---

## 🤝 Contribución

Cuando agregues funcionalidad:

1. ✅ Crea archivo en el módulo correspondiente
2. ✅ Exporta en `__init__.py` del módulo
3. ✅ Agrega docstrings a funciones
4. ✅ Usa logging para debugging
5. ✅ Actualiza esta documentación

---

## 📞 Soporte

Para preguntas o problemas:
1. Revisa los logs en `logs/procesamiento.log`
2. Verifica la configuración en `config/settings.py`
3. Consulta docstrings de funciones con `python -c "import modulo; help(modulo.funcion)"`

---

**Última actualización:** 25 de mayo de 2024
