# 📊 INTEGRACIÓN DINÁMICA - VEHÍCULOS CONTROLADOS

## 🎯 Resumen Ejecutivo

Se ha creado un sistema de **actualización dinámica** para el componente de Vehículos Controlados:

1. **vc-mejorado.html** - Componente HTML + CSS mejorado
2. **vc-actualizar.js** - Script que carga datos de `datos.json` y actualiza automáticamente todos los elementos

**Ventaja Principal:** Los gráficos, números y porcentajes se actualizan **automáticamente** cuando `datos.json` cambia.

---

## 📁 Archivos Creados

### 1. `vc-mejorado.html`
- Reemplazo mejorado del componente VC original
- Incluye HTML estructura limpia
- CSS responsivo con media queries
- Enlaza automáticamente el script vc-actualizar.js

**IDs HTML principales:**
```html
<span id="vc_cargas">2.951</span>        <!-- Número de cargas -->
<span id="vc_pasajeros">4.186</span>    <!-- Número de pasajeros -->
<span id="vc_total">9.349</span>        <!-- Total VC -->
<canvas id="grafico-vc"></canvas>      <!-- Gráfico donut -->
<span id="ret_count">13</span>          <!-- Retenciones -->
<span id="acta_count">130</span>        <!-- Actas -->
```

### 2. `vc-actualizar.js`
Script JavaScript que:
- ✅ Carga automáticamente `datos.json` al cargar la página
- ✅ Actualiza todos los números (cargas, pasajeros, total)
- ✅ Recrea el gráfico donut con Chart.js
- ✅ Actualiza callouts (retenciones, actas)
- ✅ Formatea números con separadores de miles (ej: 1.234.567)
- ✅ Calcula porcentajes automáticamente

---

## 🚀 Pasos de Integración

### OPCIÓN A: Usar vc-mejorado.html directamente

Si quieres reemplazar completamente tu index.html actual:

```bash
# 1. Reemplazar el componente VC en index.html
cp vc-mejorado.html index.html

# 2. IMPORTANTE: Asegurar que datos.json esté en el mismo directorio
# Debería estar en: /INFORME/datos.json
```

### OPCIÓN B: Integrar en tu index.html existente

Si ya tienes un index.html con otros componentes:

#### 1️⃣ Copiar CSS en `<head>`

Ve al archivo `vc-mejorado.html`, busca la sección `<style>` completa y cópiala completa en tu `index.html`:

```html
<head>
    <!-- ... otros estilos ... -->
    <style>
        /* Copiar TODA la sección <style> de vc-mejorado.html aquí */
    </style>
</head>
```

#### 2️⃣ Copiar HTML del componente VC

En `vc-mejorado.html`, busca:
```html
<div class="vc-bloque">
    <!-- ... contenido ... -->
</div>
```

Copia este bloque completo y pegalo en el lugar donde quieras que aparezca el componente en tu `index.html`.

#### 3️⃣ Incluir los scripts necesarios

En `<head>`, asegúrate de tener Chart.js:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

Antes de cerrar `</body>`, incluye el script de actualización:
```html
<script src="vc-actualizar.js"></script>
```

#### 4️⃣ Estructura final esperada

```html
<!DOCTYPE html>
<html>
<head>
    <!-- ... otros elementos ... -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* Estilos de vc-mejorado.html */
    </style>
</head>
<body>
    <!-- ... otros componentes ... -->
    
    <div class="vc-bloque">
        <!-- Componente VC importado -->
    </div>
    
    <!-- Script de actualización DEBE estar aquí -->
    <script src="vc-actualizar.js"></script>
</body>
</html>
```

---

## 📊 Estructura esperada de `datos.json`

El script espera que `datos.json` tenga esta estructura:

```json
{
    "metadata": {
        "total_cargas": 2951,
        "total_pasajeros": 4186,
        "total_registros": 9349,
        "total_retenciones": 13,
        "total_actas": 130
    },
    "incidencias": {
        "alcoholemia_positiva": 5,
        "sustancias_positivas": 3,
        "retenciones_alcoholemia": 2,
        "retenciones_sustancias": 1
    },
    "registros": [
        { /* datos de registros */ }
    ]
}
```

**Verificación:** Abre la consola del navegador (F12) y verás logs como:
```
📊 Cargando datos VC desde datos.json...
✅ Datos cargados: {...}
📈 Cargas: 2951 (55%)
📈 Pasajeros: 4186 (45%)
🔒 Retenciones: 13 (0.14%)
📋 Actas: 130 (1.39%)
✅ Gráfico VC actualizado
```

---

## 🔄 Llamadas Manuales al Script

El script se ejecuta automáticamente cuando carga la página, pero puedes llamarlo manualmente:

### Desde la consola del navegador (F12):
```javascript
// Recarga datos y actualiza todo
actualizarDatosVC();

// Actualizar solo gráfico (uso avanzado)
actualizarGraficoVehiculosControlados(55, 45);
```

### Desde otro script JavaScript:
```javascript
// Después de generar datos.json
async function generarInformeCompleto() {
    // ... generar datos.json ...
    
    // Actualizar componente VC
    await actualizarDatosVC();
    
    console.log('✅ Informe generado y componente actualizado');
}

generarInformeCompleto();
```

---

## 🎨 Personalización

### Cambiar colores

En `vc-actualizar.js`, función `actualizarGraficoVC()`:

```javascript
backgroundColor: [
    '#1a3a5c',      // Cambiar azul
    '#e8e8e8'       // Cambiar gris
]
```

### Cambiar formato de números

En `vc-actualizar.js`, función `actualizarElemento()`:

```javascript
// Sin separadores: 1234567
const valorFormateado = valor;

// Con separadores: 1.234.567 (hispano)
const valorFormateado = valor.toLocaleString('es-AR');

// Con separadores: 1,234,567 (inglés)
const valorFormateado = valor.toLocaleString('en-US');
```

### Cambiar textos de etiquetas

En `vc-mejorado.html`, busca y modifica:

```html
<div class="vc-numero-label">Cargas</div>      <!-- Cambiar este texto -->
<span class="vc-callout-titulo">Retenciones</span>  <!-- O este -->
```

---

## 🔍 Troubleshooting

### ❌ "Error: datos.json no encontrado"

**Solución:**
- Asegúrate de que `datos.json` esté en la misma carpeta que `index.html`
- Verifica que `generador.py` haya ejecutado correctamente
- Abre la consola del navegador (F12) para ver el error exacto

### ❌ "Gráfico no aparece"

**Solución:**
- Verifica que Chart.js esté cargado: abre consola (F12) y escribe `Chart`
- Si completa con un objeto azul, está bien; si no, falta incluir: `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`

### ❌ "Los números no se actualizan"

**Solución:**
- Verifica que `vc-actualizar.js` esté incluido
- Abre consola (F12) y llama manualmente: `actualizarDatosVC()`
- Si hay error, revisa que los IDs HTML coincidan exactamente

### ❌ "percentajes incorrectos"

**Solución:**
- Verifica que `total_cargas + total_pasajeros = total_registros`
- Si no es exacto, el porcentaje será impreciso
- Los porcentajes se redondean: `Math.round((cargas / total) * 100)`

---

## 📋 Checklist de Implementación

- [ ] `vc-actualizar.js` copiado a `/INFORME/`
- [ ] `vc-mejorado.html` disponible como referencia
- [ ] Chart.js incluido en `<head>`
- [ ] CSS de vc-mejorado.html copiado a index.html
- [ ] HTML del componente VC copiado a index.html
- [ ] `vc-actualizar.js` enlazado antes de `</body>`
- [ ] `datos.json` generado correctamente por generador.py
- [ ] Abierto en navegador, consola sin errores ✓
- [ ] Números actualizados correctamente ✓
- [ ] Gráfico mostrado en vivo ✓

---

## 🚀 Próximos Pasos

### 1. Ejecutar generador.py
```bash
cd /INFORME
python generador.py
```

### 2. Abrir en navegador
```bash
# Opción A: Doble clic en index.html (si tiene el componente integrado)
# Opción B: Servidor local
python -m http.server 8000
# Luego abre http://localhost:8000/INFORME/index.html
```

### 3. Verificar consola
Presiona F12, ve a la pestaña **Console** y verifica que no haya errores rojos.

### 4. Validar datos
Presiona F12, escribe en consola:
```javascript
fetch('datos.json').then(r => r.json()).then(d => console.log(d.metadata))
```

---

## 📞 Soporte

**Errores frecuentes:**

| Problema | Causa | Solución |
|----------|-------|----------|
| Canvas blanco | Chart.js no cargado | Incluir `<script src="...chart.js"></script>` |
| Números no cambian | vc-actualizar.js falta | Incluir `<script src="vc-actualizar.js"></script>` |
| 404 datos.json | Archivo no existe | Ejecutar generador.py |
| Gráfico antiguos | Cache del navegador | Ctrl+F5 para limpiar cache |

---

*Última actualización: 2024*
*Versión: 2.0 (Con script dinámico)*
