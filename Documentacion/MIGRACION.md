# 🔄 Guía de Migración a Arquitectura Modular

## 🎯 Resumen de Cambios

Tu proyecto ha sido transformado de:
- ❌ **1 archivo gigante** (`generador.py` 753 líneas)
- ✅ **Arquitectura modular** con 8+ módulos especializados

---

## 📋 Pasos para Migración

### Paso 1: Backup del código anterior

```bash
# Renombrar archivo antiguo
mv INFORME/generador.py INFORME/generador_antiguo.py

# Guardar en git
git add .
git commit -m "Backup: generador.py antiguo antes de refactorización"
```

### Paso 2: Probar nuevo orquestador

```bash
# Navegar al proyecto
cd INFORME

# Activar entorno virtual
.venv\Scripts\activate

# Instalar nuevas dependencias (si es necesario)
pip install playwright

# Ejecutar nuevo generador
python generador_nuevo.py --solo-procesar
```

### Paso 3: Reemplazar generador.py

Una vez que `generador_nuevo.py` funciona correctamente:

```bash
# Backup del antiguo
mv generador_antiguo.py generador_backup_$(date +%Y%m%d).py

# Renombrar el nuevo
mv generador_nuevo.py generador.py

# Commit de cambios
git add .
git commit -m "Refactorización: arquitectura modular"
```

### Paso 4: Probar todo el flujo

```bash
# Procesar archivos Excel
python generador.py --solo-procesar

# Si tienes credenciales CNRT (opcional)
export CNRT_USERNAME="tu_usuario"
export CNRT_PASSWORD="tu_contraseña"
python generador.py --descargar --desde 2024-01-01

# Iniciar servidor
python generador.py
```

---

## 🔗 Relación entre código antiguo y nuevo

### ✅ Lo que se movió (sin cambios funcionales)

| Código Antiguo | Nuevo Módulo | Ubicación |
|---|---|---|
| `titulo()`, `subtitulo()` | `utils/logger.py` | `from utils import titulo, subtitulo` |
| `normalizar()` | `utils/normalizaciones.py` | `from utils import normalizar` |
| `normalizar_region()` | `utils/normalizaciones.py` | `from utils import normalizar_region` |
| `convertir_dms_a_decimal()` | `utils/normalizaciones.py` | `from utils import convertir_dms_a_decimal` |
| `detectar_incidencia()` | `utils/normalizaciones.py` | `from utils import detectar_incidencia` |
| `elegir_articulo()` | `utils/normalizaciones.py` | `from utils import elegir_articulo` |
| `mapa_regiones` | `config/settings.py` | `from config import MAPA_REGIONES` |
| Lectura de Excel | `procesamiento/limpiar_excel.py` | `from procesamiento import combinar_excels` |
| Cálculo de regiones | `procesamiento/calcular_metricas.py` | `from procesamiento import procesar_datos` |
| Generación JSON | `exportacion/generar_json.py` | `from exportacion import exportar_json` |
| Rutas Flask | `app.py` | Sin cambios |

### 🆕 Lo que es nuevo

| Funcionalidad | Módulo | Beneficio |
|---|---|---|
| Descarga automática CNRT | `automatizacion/descarga_cnrt.py` | Automatización Playwright |
| Configuración centralizada | `config/settings.py` | Fácil de cambiar parámetros |
| Logging profesional | `utils/logger.py` | Logs a archivo + consola |
| Orquestador limpio | `generador.py` | Flujo visible y mantenible |
| Validaciones | `procesamiento/limpiar_excel.py` | Mejor calidad de datos |

---

## 💻 Ejemplos de Uso

### Ejemplo 1: Procesamiento simple

**Antes (antiguo):**
```python
# Todo mezclado en generador.py
python generador.py
```

**Ahora (modular):**
```python
python generador.py --solo-procesar
```

### Ejemplo 2: Con filtro de fechas

**Antes:**
```python
# Era un argumento sys.argv[1]
python generador.py 2024-01-01 2024-12-31
```

**Ahora:**
```python
python generador.py --desde 2024-01-01 --hasta 2024-12-31
```

### Ejemplo 3: Usar modules en tu código

**Antes (importar desde generador.py era difícil):**
```python
# No había estructura clara
```

**Ahora:**
```python
# En tu script personalizado
from procesamiento import procesar_datos
from exportacion import exportar_json
from utils import setup_logger

logger = setup_logger(__name__)
logger.info("Mi procesamiento personalizado")

df = pd.read_excel("mi_archivo.xlsx")
resultados = procesar_datos(df)
exportar_json(resultados)
```

### Ejemplo 4: Automatización Playwright

**Antes:**
```python
# No existía
```

**Ahora:**
```python
import asyncio
from automatizacion import descargar_reportes_cnrt

async def descargar_y_procesar():
    # Descargar reportes
    exitoso, resultados = await descargar_reportes_cnrt(
        delegaciones=["AMBA", "CEN"],
        fecha_desde="2024-01-01"
    )
    
    # Los archivos están en archivos/excels_descargados/
    # Luego procesar normalmente
    
asyncio.run(descargar_y_procesar())
```

---

## ✅ Verificación de Funcionalidad

### Checklist post-migración

```bash
# 1. ¿Se lee correctamente el Excel?
python generador.py --solo-procesar
# Revisar: logs/procesamiento.log

# 2. ¿Se genera datos.json?
ls -la datos.json

# 3. ¿Los datos son correctos?
python -c "import json; print(json.load(open('datos.json'))['resumen'])"

# 4. ¿Funciona el servidor?
python generador.py
# Ir a: http://127.0.0.1:5000

# 5. ¿Los logs se guardan?
tail -f logs/procesamiento.log
```

---

## 🐛 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'config'`

**Solución:**
```bash
# Asegúrate de estar en la carpeta correcta
cd INFORME

# O agrega INFORME al PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Error: `PlaywrightException: ...`

**Solución:**
```bash
# Instalar navegadores de Playwright
playwright install

# Reinstalar Playwright
pip install --upgrade playwright
```

### Los datos.json no se actualiza

**Solución:**
```bash
# Asegúrate de que hay archivos en Excel/
ls -la Excel/*.xls*

# Revisa los logs
tail -50 logs/procesamiento.log

# Prueba con --solo-procesar
python generador.py --solo-procesar -v
```

---

## 🚀 Próximos Pasos Recomendados

### 1. Tests Automatizados

```bash
# Crear tests/
mkdir -p tests

# Crear test_normalizaciones.py
# Crear test_procesamiento.py
# Crear test_exportacion.py
```

### 2. CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/
```

### 3. Docker (Opcional)

```dockerfile
# Dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY INFORME .
CMD ["python", "generador.py"]
```

### 4. Documentación de API

```python
# Agregar docstrings más detallados
# Generar docs con: sphinx-build -b html docs docs/_build
```

---

## 📞 Comparación: Antes vs Después

### Legibilidad del Código

**Antes:**
```
generador.py: 753 líneas
- Función 1 (líneas 1-50)
- Función 2 (líneas 51-150)
- Función 3 (líneas 151-300)
- Lógica principal (líneas 301-753)
📌 Difícil de navegar
```

**Después:**
```
generador.py: 180 líneas (limpio, solo orquestación)
↓ importa de ↓
config/settings.py (65 líneas)
utils/logger.py (55 líneas)
utils/normalizaciones.py (150 líneas)
procesamiento/limpiar_excel.py (200 líneas)
procesamiento/calcular_metricas.py (250 líneas)
exportacion/generar_json.py (180 líneas)
automatizacion/descarga_cnrt.py (350 líneas)

📌 Fácil de navegar, cada módulo con una responsabilidad clara
```

### Mantenibilidad

| Tarea | Antes | Después |
|---|---|---|
| Cambiar configuración | Editar línea XYZ en generador.py | Editar config/settings.py |
| Agregar validación | Editar función compleja | Agregar en procesamiento/ |
| Debuggear error | Revisar 753 líneas | Revisar módulo específico |
| Reutilizar código | Copiar-pegar | Importar módulo |
| Testear función | Difícil de aislar | Fácil, módulo independiente |

---

## 🎓 Principios Aplicados

✅ **SOLID:**
- **S** (Single Responsibility): Cada módulo tiene una responsabilidad
- **O** (Open/Closed): Fácil de extender, difícil de romper
- **L** (Liskov Substitution): Módulos intercambiables
- **I** (Interface Segregation): Interfaces claras
- **D** (Dependency Inversion): Depende de abstracciones

✅ **DRY (Don't Repeat Yourself):**
- Las funciones comunes están en `utils/`
- Configuración centralizada en `config/`

✅ **Separated Concerns:**
- Excel → procesamiento/
- Cálculos → procesamiento/
- Exportación → exportacion/
- Descargas → automatizacion/
- Configuración → config/
- Utilidades → utils/

---

## ✨ Beneficios de la Nueva Arquitectura

1. **📈 Escalabilidad**: Agregar nuevas funciones es simple
2. **🔧 Mantenibilidad**: Cambios localizados no rompen todo
3. **🧪 Testabilidad**: Cada módulo puede probarse aisladamente
4. **📚 Documentación**: Código autodocumentado con docstrings
5. **🤝 Colaboración**: Otros desarrolladores entienden rápido
6. **🚀 Rendimiento**: Módulos optimizados sin lógica mezclada
7. **🔒 Seguridad**: Credenciales en variables de entorno
8. **♻️ Reutilización**: Módulos usables en otros proyectos

---

**¡Migración completada! 🎉**

Si tienes dudas, consulta `ARQUITECTURA_MODULAR.md`
