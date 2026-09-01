# 🚀 Proyecto CNRT - Arquitectura Modular

## ⚡ Inicio Rápido

```bash
# 1. Entrar al directorio
cd INFORME

# 2. Activar entorno virtual
.venv\Scripts\activate

# 3. Instalar Playwright (nuevo)
pip install playwright
playwright install

# 4. Procesar Excel
python generador_nuevo.py --solo-procesar

# 5. O iniciar servidor
python generador_nuevo.py
```

## 📁 Estructura Nueva

```
INFORME/
├── config/              ← Configuración centralizada
├── utils/               ← Funciones reutilizables  
├── procesamiento/       ← Lectura y cálculos de Excel
├── exportacion/         ← Generación de JSON
├── automatizacion/      ← Descarga automática (Playwright)
├── generador_nuevo.py   ← Orquestador (renombrar a generador.py)
├── ARQUITECTURA_MODULAR.md ← Documentación completa
└── MIGRACION.md         ← Guía de migración
```

## 📚 Documentación

- **[ARQUITECTURA_MODULAR.md](ARQUITECTURA_MODULAR.md)** - Descripción de cada módulo
- **[MIGRACION.md](MIGRACION.md)** - Guía paso a paso para migrar
- **[RESUMEN_REFACTORIZACION.md](RESUMEN_REFACTORIZACION.md)** - Qué cambió y por qué
- **[ejemplos_uso.py](ejemplos_uso.py)** - 9 ejemplos de uso

## 🎯 Opciones de Comando

```bash
# Procesar sin iniciar servidor
python generador_nuevo.py --solo-procesar

# Con filtro de fechas
python generador_nuevo.py --desde 2024-01-01 --hasta 2024-12-31

# Descargar reportes (requiere credenciales)
python generador_nuevo.py --descargar

# Iniciar servidor
python generador_nuevo.py

# Ayuda
python generador_nuevo.py --help
```

## 🤖 Automatización Playwright

```bash
# Configurar credenciales
export CNRT_USERNAME="tu_usuario"
export CNRT_PASSWORD="tu_contraseña"

# Descargar y procesar
python generador_nuevo.py --descargar --desde 2024-01-01
```

Los archivos se descargan en: `archivos/excels_descargados/`

## 💻 Uso Programático

```python
from procesamiento import procesar_datos
from exportacion import exportar_json
import pandas as pd

df = pd.read_excel("archivo.xlsx")
resultados = procesar_datos(df)
exportar_json(resultados)
```

Ver **[ejemplos_uso.py](ejemplos_uso.py)** para 9 ejemplos detallados.

## 📊 Logs

Los logs se guardan automáticamente en:
```
logs/procesamiento.log
```

Ver en tiempo real:
```bash
tail -f logs/procesamiento.log
```

## ✅ Cambios Clave

| Aspecto | Antes | Ahora |
|--------|-------|-------|
| Organización | 1 archivo (753 líneas) | 8 módulos especializados |
| Configuración | Esparcida | `config/settings.py` |
| Reutilización | Difícil | Fácil con imports |
| Logging | Ad-hoc | Centralizado y profesional |
| Automatización | No existía | Playwright integrado |
| Credenciales | Hardcodeadas | Variables de entorno |
| Documentación | Nula | Completa |

## 🔧 Migración (Cuando Esté Listo)

```bash
# 1. Backup del antiguo
mv generador.py generador_backup.py

# 2. Reemplazar con el nuevo
mv generador_nuevo.py generador.py

# 3. Probar
python generador.py --solo-procesar
```

## 📞 Troubleshooting

**Error: `ModuleNotFoundError: No module named 'config'`**
```bash
cd INFORME  # Estar en la carpeta correcta
```

**Error de Playwright**
```bash
pip install --upgrade playwright
playwright install
```

**¿Los datos no se actualizan?**
```bash
# Ver si hay archivos en Excel/
ls Excel/

# Revisar logs
tail -50 logs/procesamiento.log
```

## 🎁 Características Nuevas

✅ Descarga automática desde CNRT con Playwright  
✅ Configuración centralizada  
✅ Logging profesional a archivo  
✅ Validación automática de datos  
✅ Interfaz CLI mejorada  
✅ Código reutilizable  
✅ Fácil de mantener y extender  

## 🚀 Próximos Pasos

1. Leer [ARQUITECTURA_MODULAR.md](ARQUITECTURA_MODULAR.md)
2. Ejecutar ejemplos en [ejemplos_uso.py](ejemplos_uso.py)
3. Migrar cuando estés seguro
4. Extender con nuevas funcionalidades

---

**Para documentación completa:** Ver [ARQUITECTURA_MODULAR.md](ARQUITECTURA_MODULAR.md)

**Para guía de migración:** Ver [MIGRACION.md](MIGRACION.md)
