# 🎯 INSTRUCCIONES DE USO - Sistema CNRT Refactorizado

## ⚡ Quick Start (30 segundos)

```bash
cd c:\Users\dmolina\Desktop\INFORME\INFORME_REFACTORIZADO
python main.py
# Ir a http://127.0.0.1:5000
```

---

## 📦 Preparación Inicial

### 1. Activar entorno virtual (si existe)
```bash
cd c:\Users\dmolina\Desktop\INFORME\INFORME_REFACTORIZADO
.venv\Scripts\activate
```

### 2. Instalar dependencias (primera vez)
```bash
pip install -r requirements.txt
```

---

## 🚀 FORMAS DE EJECUTAR

### **FORMA 1: Procesamiento + Servidor (RECOMENDADO)**
```bash
python main.py
```
**Hace:**
1. Lee Excel desde `Excel/`
2. Aplica saneamiento (ETAPA 2)
3. Procesa datos (ETAPA 3)
4. Genera `datos.json`
5. Inicia servidor en http://127.0.0.1:5000

**Tiempo:** 2-5 segundos + servidor activo

---

### **FORMA 2: Solo Procesar (sin servidor)**
```bash
python main.py --solo-procesar
```
**Hace:**
1. Procesa datos
2. Genera `datos.json`
3. Termina

**Útil para:** Validar procesamiento, generar reportes

---

### **FORMA 3: Solo Servidor (datos ya procesados)**
```bash
python main.py --solo-servidor
```
**Hace:**
1. Inicia servidor
2. Lee `datos.json` existente

**Útil para:** Explorar datos ya procesados

---

### **FORMA 4: Con filtro de fechas**
```bash
python main.py --desde 2024-01-01 --hasta 2024-06-30
```
**Procesa solo datos de enero a junio 2024**

---

### **FORMA 5: Modo B (1 registro por dominio)**
```bash
python main.py --modo B
```
**Expande dominios en múltiples registros**

---

### **FORMA 6: Combinaciones**
```bash
# Modo B + Fechas + Solo procesar
python main.py --modo B --desde 2024-01-01 --hasta 2024-12-31 --solo-procesar

# Solo servidor con modo B
python main.py --modo B --solo-servidor
```

---

## 📁 Estructura de Carpetas

```
c:\Users\dmolina\Desktop\INFORME\INFORME_REFACTORIZADO\
│
├── Excel/                      ← AQUÍ PONES LOS ARCHIVOS .xls o .xlsx
│   └── (vacío inicialmente)
│
├── templates/
│   └── index.html             ← Frontend (igual que antes)
│
├── static/                    ← Assets (igual que antes)
│
├── logs/
│   └── procesamiento.log      ← Se genera automáticamente
│
├── datos.json                 ← SALIDA (se genera automáticamente)
│
├── CAMBIOS.md                 ← Explicación de cambios
├── README.md                  ← Documentación completa
└── main.py                    ← EJECUTAR ESTE
```

---

## 🔧 Copiar Archivos Excel

### Desde carpeta INFORME original:
```bash
# Copiar archivos de INFORME/Excel a INFORME_REFACTORIZADO/Excel
copy "c:\Users\dmolina\Desktop\INFORME\INFORME\Excel\*.xls" ^
      "c:\Users\dmolina\Desktop\INFORME\INFORME_REFACTORIZADO\Excel\"

copy "c:\Users\dmolina\Desktop\INFORME\INFORME\Excel\*.xlsx" ^
      "c:\Users\dmolina\Desktop\INFORME\INFORME_REFACTORIZADO\Excel\"
```

---

## 📊 Interpretación de Logs

### Cuando ejecutas `python main.py --solo-procesar`

```
============================================================
ETAPA 1: DESCARGA DE ARCHIVOS
============================================================
```
→ Leyendo archivos Excel

```
[INFO] [1/2] Procesando: Enero.xlsx
[OK] 5,432 filas
```
→ 1 de 2 archivos, 5,432 filas leídas ✓

```
============================================================
ETAPA 2: SANEAMIENTO DE BASE DE DATOS
============================================================
[INFO] Registros originales: 10,864
[WARNING] Registros eliminados (REGIONAL=GENDARMERIA): 1,945
[WARNING] Registros eliminados (REGIONAL vacío): 121
[WARNING] Registros eliminados (FISCALIZADOR vacío): 336
```
→ Se eliminaron registros inválidos
- 1,945 de GENDARMERIA (basura)
- 121 con REGIONAL vacío
- 336 sin FISCALIZADOR

```
[OK] Base saneada correctamente
[INFO] Registros originales:        10,864
[INFO] Registros eliminados:        2,402
[INFO] Registros válidos:           8,462
```
→ Quedaron 8,462 registros válidos

```
============================================================
ETAPA 3: PROCESAMIENTO DE REGISTROS
============================================================
[OK] Registros generados: 8,462
```
→ Se generaron 8,462 registros JSON

```
============================================================
ETAPA 5: EXPORTACIÓN
============================================================
[OK] JSON guardado: datos.json

[INFO] VEHÍCULOS CONTROLADOS:
    • Total VC:    8,462
    • Cargas:      5,100 (60.2%)
    • Pasajeros:   3,362 (39.8%)
```
→ Resumen final ✓

---

## ❌ Solución de Problemas

### Problema: "No se encontraron archivos Excel"
```bash
# Solución: Copiar archivos a Excel/
copy "INFORME\Excel\*.xls" "INFORME_REFACTORIZADO\Excel\"
```

### Problema: "datos.json no encontrado" (al abrir servidor)
```bash
# Solución: Procesar primero
python main.py --solo-procesar

# Luego iniciar servidor
python main.py --solo-servidor
```

### Problema: "Puerto 5000 en uso"
```bash
# Opción 1: Cambiar puerto en config.py
FLASK_PORT = 5001

# Opción 2: Solo procesar (sin servidor)
python main.py --solo-procesar
```

### Problema: "ModuleNotFoundError: No module named 'pandas'"
```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Problema: CTRL+C no termina servidor
```bash
# Presiona CTRL+C nuevamente
# El servidor debe terminar limpiamente
```

---

## ✅ Verificación Post-Ejecución

### 1. Verificar que se procesó correctamente
```bash
# Debe existir datos.json
ls -la datos.json

# Debe tener contenido
wc -l datos.json
```

### 2. Verificar estructura del JSON
```bash
# Ver estructura (primeras líneas)
python -c "import json; f=open('datos.json'); d=json.load(f); print(list(d.keys()))"

# Salida esperada:
# ['registros', 'incidencias', 'metadata', 'actas', 'retenciones', 'regiones']
```

### 3. Verificar totales
```bash
# Python interactivo
python
>>> import json
>>> d = json.load(open('datos.json'))
>>> print(f"Total registros: {len(d['registros']):,}")
>>> print(f"Total actas: {d['actas']['total']}")
>>> print(f"Total retenciones: {d['retenciones']['total']}")
```

### 4. Verificar en navegador
```
http://127.0.0.1:5000
# Dashboard debe cargar correctamente
```

---

## 🔄 Flujo Típico de Uso

### DÍA 1: Configuración inicial
```bash
# 1. Copiar archivos Excel
copy "INFORME\Excel\*.xlsx" "INFORME_REFACTORIZADO\Excel\"

# 2. Procesar datos
cd INFORME_REFACTORIZADO
python main.py --solo-procesar

# 3. Validar datos.json se creó
ls -la datos.json
```

### DÍA 2+: Usar normalmente
```bash
# Opción A: Procesamiento + servidor
python main.py

# Opción B: Solo procesar datos nuevos
python main.py --solo-procesar

# Opción C: Solo servir datos existentes
python main.py --solo-servidor
```

---

## 📈 Parámetros de Línea de Comando

```bash
python main.py [OPCIONES]

OPCIONES:
  --modo {A,B}           Modo procesamiento (default: A)
                         A = 1 registro por fila
                         B = 1 registro por dominio (expansión)
  
  --desde YYYY-MM-DD     Fecha desde (optional)
  
  --hasta YYYY-MM-DD     Fecha hasta (optional)
  
  --solo-procesar        Solo procesar, sin servidor
  
  --solo-servidor        Solo servidor, sin procesamiento
```

### Ejemplos:
```bash
python main.py
# Procesamiento completo + servidor

python main.py --modo B
# Modo B + servidor

python main.py --desde 2024-01-01 --hasta 2024-06-30 --solo-procesar
# Procesar solo H1 2024, modo A

python main.py --modo B --desde 2024-01-01 --solo-servidor
# Nota: --solo-servidor ignora fecha, usa datos.json existente
```

---

## 💡 Tips Profesionales

### Tip 1: Guardar outputs de diferentes períodos
```bash
# Procesar enero
python main.py --desde 2024-01-01 --hasta 2024-01-31 --solo-procesar
cp datos.json datos_enero.json

# Procesar febrero
python main.py --desde 2024-02-01 --hasta 2024-02-29 --solo-procesar
cp datos.json datos_febrero.json
```

### Tip 2: Ver logs en tiempo real
```bash
# En otra terminal
tail -f logs/procesamiento.log
```

### Tip 3: Validar sintaxis antes de ejecutar
```bash
python -m py_compile procesador.py saneamiento.py app.py main.py
# Si no hay error, está todo bien
```

### Tip 4: Crear alias para comando frecuente
```bash
# En PowerShell
Set-Alias cnrt "python c:\Users\dmolina\Desktop\INFORME\INFORME_REFACTORIZADO\main.py"

# Ahora puedes
cnrt --solo-procesar
```

---

## 🚨 IMPORTANTE: Diferencias de Números

**Números han cambiado respecto al sistema original porque:**

1. **Se aplica saneamiento correcto (ETAPA 2)**
   - Se eliminan registros de GENDARMERIA
   - Se eliminan REGIONAL vacío
   - Se eliminan FISCALIZADOR vacío

2. **Estos registros NO se procesaban antes correctamente**

3. **Los números NEW son más precisos y auditables**

**Ejemplo:**
```
Antes:  24,238 registros (incluye basura)
Después: 21,836 registros (válidos únicamente)

Diferencia: 2,402 registros inválidos eliminados
```

---

## 📞 Contacto / Soporte

1. **Revisar logs:** `logs/procesamiento.log`
2. **Ejecutar test:** `python main.py --solo-procesar`
3. **Verificar estructura:** Ver `CAMBIOS.md` y `README.md`

---

**¡Sistema listo para usar! 🎉**
