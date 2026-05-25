# 📊 TABLA RESUMEN POR REGIÓN - SISTEMA DINÁMICO

## 🎯 Descripción General

Sistema para actualizar **dinámicamente** la tabla "RESUMEN POR REGIÓN" del informe CNRT con valores calculados automáticamente a partir de los datos reales.

**Componentes:**
1. **calcular_resumen_regiones.py** - Módulo Python que procesa datos y calcula valores
2. **actualizar_tabla_regiones.js** - Script JavaScript que actualiza la tabla HTML
3. **index.html** - HTML con IDs dinámicos para cada celda

---

## 🚀 INSTALACIÓN Y USO

### 1. Preparar los datos (Python)

#### Opción A: Ejecutar desde línea de comandos

```bash
# Navegar a la carpeta del INFORME
cd "INFORME"

# Ejecutar el script
python calcular_resumen_regiones.py
```

**Resultado esperado:**
```
============================================================
RESUMEN POR REGIÓN
============================================================

AMBA:
  Cargas:    VC=100, ACTAS=20, RET=5
  Pasajeros: VC=150, ACTAS=30, RET=8
  Total:     VC=250, ACTAS=50, RET=13

...

✅ Resumen guardado en datos.json
```

#### Opción B: Integrar en generador.py

```python
# Al final de generador.py, agregar:

from calcular_resumen_regiones import calcular_resumen_por_region, guardar_resumen_en_json

# Después de procesar todos los datos:
resumen = calcular_resumen_por_region(registros_list)
guardar_resumen_en_json(resumen, "datos.json")
```

### 2. Actualizar el HTML

El HTML ya está configurado con los IDs necesarios. Si agregas nuevas regiones, asegúrate de incluir los IDs:

```html
<!-- Patrón para cada celda: {REGION}_{TIPO}_{METRICA} -->

<!-- Ejemplo: AMBA Cargas -->
<td id="amba_cargas_vc">0</td>      <!-- Vehículos controlados -->
<td id="amba_cargas_actas">0</td>   <!-- Actas -->
<td id="amba_cargas_ret">0</td>     <!-- Retenciones -->

<!-- Ejemplo: AMBA Pasajeros -->
<td id="amba_pasajeros_vc">0</td>
<td id="amba_pasajeros_actas">0</td>
<td id="amba_pasajeros_ret">0</td>

<!-- Ejemplo: AMBA Total -->
<td id="amba_total_vc">0</td>
<td id="amba_total_actas">0</td>
<td id="amba_total_ret">0</td>

<!-- Total General CNRT -->
<td id="total_cargas_vc">0</td>
<td id="total_cargas_actas">0</td>
<td id="total_cargas_ret">0</td>
<!-- ... más ... -->
```

### 3. Cargar la página

Una vez que `datos.json` contenga la sección `resumen_por_region`, al cargar `index.html`:

1. ✅ El script `actualizar_tabla_regiones.js` se ejecuta automáticamente
2. ✅ Lee los datos desde `datos.json`
3. ✅ Actualiza todas las celdas de la tabla

---

## 📋 ESTRUCTURA DE DATOS

El archivo `datos.json` debe incluir una nueva sección:

```json
{
  "registros": [...],
  "metadata": {...},
  "resumen_por_region": {
    "AMBA": {
      "cargas": {"vc": 100, "actas": 20, "ret": 5},
      "pasajeros": {"vc": 150, "actas": 30, "ret": 8},
      "total": {"vc": 250, "actas": 50, "ret": 13}
    },
    "COSTA": {...},
    "BA": {...},
    "CEN": {...},
    "CUY": {...},
    "NEA": {...},
    "NOA": {...},
    "PAT": {...},
    "TOTAL": {
      "cargas": {"vc": 1000, "actas": 200, "ret": 50},
      "pasajeros": {"vc": 1500, "actas": 300, "ret": 80},
      "total": {"vc": 2500, "actas": 500, "ret": 130}
    }
  }
}
```

---

## 🔧 FUNCIONES DISPONIBLES

### En Python: `calcular_resumen_regiones.py`

#### `calcular_resumen_por_region(registros, fecha_desde=None, fecha_hasta=None)`

Calcula el resumen de todas las regiones.

**Parámetros:**
- `registros` (list/DataFrame): Registros con estructura {fecha, regional, transporte, retiene, ...}
- `fecha_desde` (str, opcional): Formato "YYYY-MM-DD"
- `fecha_hasta` (str, opcional): Formato "YYYY-MM-DD"

**Retorna:**
- dict con estructura de resumen por región

**Ejemplo:**
```python
from calcular_resumen_regiones import calcular_resumen_por_region

resumen = calcular_resumen_por_region(
    registros,
    fecha_desde="2026-03-01",
    fecha_hasta="2026-03-31"
)

print(resumen["AMBA"]["cargas"]["vc"])  # 100
```

#### `guardar_resumen_en_json(resumen, ruta_datos_json="datos.json")`

Agrega el resumen a `datos.json`.

**Parámetros:**
- `resumen`: dict retornado por `calcular_resumen_por_region()`
- `ruta_datos_json`: ruta al archivo (default: "datos.json")

**Retorna:**
- True si tuvo éxito, False si error

---

### En JavaScript: `actualizar_tabla_regiones.js`

#### `actualizarTablaRegiones()`

Carga automáticamente `datos.json` y actualiza la tabla. **Se ejecuta automáticamente** al cargar la página.

```javascript
// Ejecutar manualmente si es necesario
actualizarTablaRegiones();
```

#### `actualizarCelda(elementId, valor)`

Actualiza una celda individual.

```javascript
actualizarCelda("amba_cargas_vc", 250);
```

---

## ⚙️ FLUJO COMPLETO DE INTEGRACIÓN

### Paso 1: Python genera data
```
Ejecutar generador.py
  ↓
Lee Excel/CSV
  ↓
Procesa registros
  ↓
Calcula resumen por región
  ↓
Guarda en datos.json
```

### Paso 2: JavaScript actualiza tabla
```
Usuario abre index.html
  ↓
Carga actualizar_tabla_regiones.js
  ↓
Fetch datos.json
  ↓
Lee resumen_por_region
  ↓
Actualiza todas las celdas
```

---

## 🎯 FILTRO POR FECHAS (Modo Avanzado)

Si quieres que el usuario seleccione fechas y se recalcule el resumen:

### En HTML:
```html
<div class="container-filtro">
    <div class="campo">
        <label for="desde">Desde:</label>
        <input type="date" id="desde">
    </div>
    <div class="campo">
        <label for="hasta">Hasta:</label>
        <input type="date" id="hasta">
    </div>
    <button class="btn-informe" onclick="generarResumenConFechas()">
        Generar Resumen
    </button>
</div>
```

### En JavaScript:
```javascript
function generarResumenConFechas() {
    const desde = document.getElementById("desde").value;
    const hasta = document.getElementById("hasta").value;
    
    // Llamar a endpoint Python o enviar datos
    fetch("api/calcular-resumen", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fecha_desde: desde, fecha_hasta: hasta })
    })
    .then(r => r.json())
    .then(data => {
        // Actualizar tabla con nuevos datos
        actualizarTablaRegiones();
    });
}
```

**Nota:** Esto requiere un servidor Python (Flask, Django, etc.) para procesar en tiempo real.

---

## 🐛 TROUBLESHOOTING

### Problema: "⚠️ No se encontró resumen_por_region en datos.json"

**Solución:**
1. Ejecutar `python calcular_resumen_regiones.py` desde la carpeta INFORME
2. Verificar que `datos.json` contiene `"resumen_por_region": {...}`

### Problema: Los valores muestran "0" pero deberían mostrar números

**Solución:**
1. Verificar que el archivo `datos.json` tiene la estructura correcta
2. Abrir consola (F12) y buscar mensajes de error
3. Asegurar que los IDs HTML coincidan: `{region}_{tipo}_{metrica}`

### Problema: "Uncaught ReferenceError: Chart is not defined"

**Solución:**
Asegurar que Chart.js se carga antes del script:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="actualizar_tabla_regiones.js"></script>
```

---

## 📝 NOTAS IMPORTANTES

1. **Regiones soportadas:**
   - AMBA, COSTA, BA, CEN, CUY, NEA, NOA, PAT

2. **Tipo transporte:**
   - CA = CARGAS
   - PA = PASAJEROS

3. **Mapeo de "REGIONAL" a "REGION":**
   - El script intenta mapear automáticamente regional name a región CNRT
   - Si falta algún mapeo, edita `MAPEO_REGIONALES_REGIONES` en calcular_resumen_regiones.py

4. **Performance:**
   - Para datasets > 10,000 registros, usar pandas (ya está implementado)
   - Los cálculos se hacen en Python, no en JavaScript

---

## 📞 SOPORTE

Si hay errores o comportamiento inesperado:

1. Ejecutar con debug:
   ```bash
   python calcular_resumen_regiones.py  # Ver si hay errores
   ```

2. Revisar consola del navegador (F12 → Console)

3. Verificar estructura de datos.json

---

**¡Sistema listo! 🚀**
