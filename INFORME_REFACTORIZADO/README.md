# 🚀 Sistema CNRT - Refactorización Modular Completa

## 📋 Descripción

Refactorización **completa y profesional** del sistema CNRT de fiscalización vial, implementando:

- ✅ **Saneamiento correcto**: Elimina registros inválidos ANTES de procesar
- ✅ **Arquitectura modular**: 8 módulos especializados, sin código duplicado
- ✅ **Sin ejecución duplicada**: Flask sin reloader, procesamiento centralizado
- ✅ **Logs profesionales**: Etapas claras, legibles e informativos
- ✅ **Flujo operativo real**: ETAPA 1 → 5 según procedimiento CNRT
- ✅ **Validaciones robustas**: Consistencia de datos garantizada
- ✅ **Mantiene funcionalidad**: Compatible 100% con datos.json y frontend

---

## 🏗️ Arquitectura

```
INFORME_REFACTORIZADO/
│
├── main.py                    ← PUNTO DE ENTRADA PRINCIPAL
├── app.py                     ← SOLO Flask (rutas, sin procesamiento)
├── procesador.py              ← ORQUESTADOR (coordina etapas)
├── saneamiento.py             ← ETAPA 2 (limpieza de datos)
├── normalizacion.py           ← Funciones de normalización
├── incidencias.py             ← Detección de incidencias
├── reportes.py                ← Generación de resúmenes
├── utils.py                   ← Funciones auxiliares (logs, etc)
├── config.py                  ← Configuración centralizada
├── requirements.txt           ← Dependencias Python
├── datos.json                 ← SALIDA (JSON procesado)
│
├── Excel/                     ← ENTRADA (archivos Excel)
├── templates/
│   └── index.html            ← Frontend sin cambios
├── static/                    ← Assets sin cambios
├── logs/                      ← Logs del sistema
│
└── README.md                  ← Este archivo
```

---

## 🔄 Flujo de Procesamiento (ETAPAS)

### **ETAPA 1: DESCARGA**
- Lee archivos Excel de carpeta `Excel/`
- Consolida múltiples archivos
- Normaliza estructura de columnas

### **ETAPA 2: SANEAMIENTO** ⭐ CRÍTICO
**Elimina FÍSICAMENTE estos registros ANTES de procesar:**

```python
# REGLA FUNDAMENTAL:
df = df[
    (df["REGIONAL"].notna()) &
    (df["REGIONAL"].str.strip() != "") &
    (df["REGIONAL"].str.upper() != "GENDARMERIA") &
    (df["FISCALIZADOR1"].notna()) &
    (df["FISCALIZADOR1"].str.strip() != "")
]
```

**Validaciones:**
- ❌ REGIONAL = "GENDARMERIA" → ELIMINAR
- ❌ REGIONAL vacío → ELIMINAR
- ❌ FISCALIZADOR1 vacío → ELIMINAR
- ❌ TRANSPORTE inválido (no CA/PA) → ELIMINAR

**Estas filas NO se cuentan ni procesan.**

### **ETAPA 3: PROCESAMIENTO**
- Normaliza datos (regiones, transportes, coordenadas)
- Genera registros JSON (Modo A o B)
- Calcula métricas por región
- Detecta incidencias (alcoholemia, sustancias)

### **ETAPA 4: ACTAS/GLOSARIO**
- Clasifica artículos (108/110)
- Agrupa por tipo de acta
- Genera detalles de incidencias

### **ETAPA 5: EXPORTACIÓN**
- Genera `datos.json` final
- Valida consistencia de datos
- Muestra resumen ejecutivo

---

## 🚀 Cómo Ejecutar

### **Opción 1: Procesamiento Completo (DEFAULT)**
```bash
cd INFORME_REFACTORIZADO
python main.py
```

**Esto hace:**
1. Procesa archivos Excel
2. Inicia servidor Flask en http://127.0.0.1:5000

### **Opción 2: Solo Procesar (sin servidor)**
```bash
python main.py --solo-procesar
```

### **Opción 3: Solo Servidor (datos ya procesados)**
```bash
python main.py --solo-servidor
```

### **Opción 4: Con Filtro de Fechas**
```bash
python main.py --desde 2024-01-01 --hasta 2024-06-30
```

### **Opción 5: Modo B (1 registro por dominio)**
```bash
python main.py --modo B
```

### **Ejemplo Combinado:**
```bash
python main.py --modo B --desde 2024-01-01 --hasta 2024-12-31 --solo-procesar
```

---

## 📊 Ejemplo de Logs Profesionales

```
============================================================
SISTEMA CNRT - PROCESAMIENTO COMPLETO
============================================================
[INFO] Modo procesamiento: A
[INFO] Desde: 2024-01-01
[INFO] Hasta: 2024-12-31

============================================================
ETAPA 1: DESCARGA DE ARCHIVOS
============================================================
[INFO] [1/2] Procesando: Enero.xlsx
[OK] 5,432 filas
[INFO] [2/2] Procesando: Febrero.xlsx
[OK] 6,189 filas
[OK] Total descargado: 11,621 filas en 2 archivo(s)

============================================================
ETAPA 2: SANEAMIENTO DE BASE DE DATOS
============================================================
[INFO] Registros originales: 11,621
[WARNING] Registros eliminados (REGIONAL=GENDARMERIA): 1,945
[WARNING] Registros eliminados (REGIONAL vacío): 121
[WARNING] Registros eliminados (FISCALIZADOR vacío): 336

[OK] Base saneada correctamente

[INFO] Registros originales:        11,621
[INFO] Registros eliminados:        2,402
[INFO] Registros válidos:           9,219

============================================================
VALIDACIÓN DE SANEAMIENTO
============================================================
[OK] ✓ No hay GENDARMERIA
[OK] ✓ No hay REGIONAL vacío
[OK] ✓ Consistencia: suma de desglose (2,402) = total eliminados (2,402)

============================================================
ETAPA 3: PROCESAMIENTO DE REGISTROS
============================================================
[OK] Registros generados: 9,219

============================================================
ETAPA 5: EXPORTACIÓN
============================================================
[OK] JSON guardado: datos.json

============================================================
RESUMEN FINAL DEL PROCESAMIENTO
============================================================

[INFO] VEHÍCULOS CONTROLADOS:
    • Total VC:    9,219
    • Cargas:      5,634 (61.1%)
    • Pasajeros:   3,585 (38.9%)

[INFO] ACTAS:
    • Total actas: 186
    • Cargas:      112
    • Pasajeros:   74

[INFO] RETENCIONES:
    • Total:       115
    • Cargas:      68
    • Pasajeros:   47

[INFO] INCIDENCIAS CRÍTICAS:
    • Alcoholemia: 34
    • Sustancias:  12

[INFO] REGIONES:
    • AMBA  → VC: 3,456 | Actas: 52 | Ret: 38
    • CEN   → VC: 1,890 | Actas: 31 | Ret: 22
    • CUY   → VC: 856 | Actas: 18 | Ret: 14
    • NEA   → VC: 643 | Actas: 12 | Ret: 8
    • NOA   → VC: 1,123 | Actas: 45 | Ret: 20
    • COSTA → VC: 456 | Actas: 15 | Ret: 9
    • PAT   → VC: 795 | Actas: 13 | Ret: 4

[OK] ✓ PROCESAMIENTO COMPLETADO EXITOSAMENTE
```

---

## 📦 Dependencias

```bash
pip install -r requirements.txt
```

Contenido de `requirements.txt`:
```
Flask==2.3.0
Flask-CORS==4.0.0
pandas==2.0.0
openpyxl==3.1.0
xlrd==2.0.1
```

---

## 🛠️ Troubleshooting

### Error: "datos.json no encontrado"
```bash
python main.py --solo-procesar
```
Ejecuta procesamiento primero.

### Error: "Puerto 5000 en uso"
```bash
python main.py --solo-procesar  # O cambiar puerto en config.py
```

### Error: "Módulo no encontrado"
```bash
cd INFORME_REFACTORIZADO
python main.py  # Estar en la carpeta correcta
```

### Datos no se actualizan
```bash
# Ver logs
cat logs/procesamiento.log

# Forzar reprocesamiento
python main.py --solo-procesar
```

---

## ✅ Validación Final

```bash
# 1. Procesar
python main.py --solo-procesar

# 2. Verificar datos.json existe
ls -lh datos.json

# 3. Iniciar servidor
python main.py --solo-servidor

# 4. Abrir navegador
# http://127.0.0.1:5000
```

---

**Refactorización completada ✓**

```bash
cd INFORME_REFACTORIZADO
python -m venv .venv
.venv\Scripts\activate
```

2. Instala dependencias:

```bash
pip install -r requirements.txt
```

3. Copia tus archivos Excel a `INFORME_REFACTORIZADO/Excel`.

4. Genera `datos.json`:

```bash
python procesador.py --modo A
```

5. Inicia el servidor Flask:

```bash
python app.py
```

6. Abre el navegador en:

```text
http://127.0.0.1:5000
```

## Notas importantes

- `app.py` solo contiene Flask y rutas.
- `procesador.py` no ejecuta nada al importar.
- Se usa `app.run(debug=True, use_reloader=False)` para evitar doble ejecución.
- La ruta `/resumen` devuelve el mismo formato de JSON esperado por el frontend actual.
- Se mantuvo la lógica del negocio sin eliminar funciones existentes.
