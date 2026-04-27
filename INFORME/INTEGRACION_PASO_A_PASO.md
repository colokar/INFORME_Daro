# INTEGRACIÓN: Reemplazar IndexedDB por Python

## Descripción

Este documento explica cómo modificar `index.html` para usar el nuevo sistema Python sin romper nada.

---

## PASO 1: Agregar script de integración

En `index.html`, en la sección `<head>` o antes del `</body>`, añade:

```html
<!-- INTEGRACIÓN PYTHON ↔ JAVASCRIPT -->
<script src="integracion_python_javascript.js"></script>
```

**Ubicación recomendada:**

```html
<head>
    <meta charset="UTF-8">
    ...
    <link rel="stylesheet" href="STYLE.css">
    <!-- AQUÍ: -->
    <script src="integracion_python_javascript.js"></script>
</head>
```

O al final del documento:

```html
    <script src="integracion_python_javascript.js"></script>
</body>
</html>
```

---

## PASO 2: Reemplazar función "Generar Informe"

### ANTES (Old way - IndexedDB)

```html
<button class="btn-informe" onclick="generarInforme()">
    Generar Informe
</button>

<script>
// Función antigua que usa IndexedDB
async function generarInforme() {
    console.log("Generando informe...");
    
    try {
        // Código viejo que accedía a IndexedDB
        const db = await openDB();
        // ... lógica complicada ...
    } catch (error) {
        console.error("Error:", error);
    }
}
</script>
```

### DESPUÉS (New way - Python + JSON)

```html
<button class="btn-informe" onclick="generarInformeModerno()">
    Generar Informe
</button>

<!-- NO NECESITAS SCRIPT ADICIONAL: ya está en integracion_python_javascript.js -->
```

**Eso es todo.** La función `generarInformeModerno()` está definida en `integracion_python_javascript.js`.

---

## PASO 3: Antes de usar (ejecutar Python)

**Cada vez que quieras actualizar los datos, ejecuta:**

```bash
cd INFORME
python gestor_fiscalizacion.py
```

Esto actualiza `datos.json` con los nuevos resúmenes calculados.

---

## SOLUCIÓN RÁPIDA (Copy-Paste)

Si quieres todo listo ahora mismo, reemplaza tu elemento `<body>` de index.html con esta estructura:

```html
<body>
<!-- === ESTE ID ENVUELVE TODO PARA EL BUTTON PDF (DESCARGA) === -->
<div id="informe">

    <!-- === HEADER === -->
    <div class="header">
        <!-- ... tu contenido actual ... -->
        <h1>Resumen Operativo</h1>
        
        <!-- === BLOQUE DE BOTONES === -->
        <div class="container-filtro">
            <div class="campo">
                <label for="desde">Desde:</label>
                <input type="date" id="desde">
            </div>

            <div class="campo">
                <label for="hasta">Hasta:</label>
                <input type="date" id="hasta">
            </div>

            <!-- BOTÓN IMPORTANTE: -->
            <button class="btn-informe" onclick="generarInformeModerno()">
                Generar Informe
            </button>

            <button class="btn-informe" onclick="descargarPDF()">
                Descargar PDF
            </button>
        </div>
    </div>

    <!-- === REST OF YOUR HTML === -->
    <!-- ... mantener todo lo demás igual ... -->

</div>

<!-- === SCRIPTS === -->

<!-- Chart.js (necesario para donut charts) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- PDF Export (necesario para descargarPDF) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>

<!-- INTEGRACIÓN PYTHON ↔ JAVASCRIPT (NUEVO) -->
<script src="integracion_python_javascript.js"></script>

<!-- TUS SCRIPTS EXISTENTES -->
<script src="actualizar_tabla_regiones.js"></script>

<!-- SCRIPTS INLINE (mantener) -->
<script>
// ... tu código JavaScript existente ...
// (funciones como descargarPDF, toggleMapa, etc.)
</script>

</body>
```

---

## VERIFICACIÓN

Para verificar que todo funciona:

### 1. Abre la consola del navegador (F12)

```
Ctrl + Shift + K  (Firefox)
F12 → Console tab  (Chrome)
```

### 2. Deberías ver mensajes como:

```
Página cargada. Actualizando con datos de Python...
Cargando resúmenes calculados por Python...
Resúmenes encontrados:
Total VC: 360
Tabla actualizada exitosamente
```

### 3. Si ves errores:

```
⚠️ Error: El archivo 'datos_fiscalizacion.json' no encontrado.
```

**Solución:** Ejecuta `python gestor_fiscalizacion.py`

---

## TROUBLESHOOTING

### Problema 1: "generarInformeModerno is not defined"

**Causa:** `integracion_python_javascript.js` no se cargó.

**Solución:**
1. Verifica que el archivo existe: `INFORME/integracion_python_javascript.js`
2. Verifica la ruta en el HTML: `<script src="integracion_python_javascript.js"></script>`
3. Recarga la página (Ctrl + Shift + R para limpiar caché)

### Problema 2: "datos.json no encontrado"

**Causa:** No ejecutaste Python.

**Solución:**
```bash
cd INFORME
python gestor_fiscalizacion.py
```

### Problema 3: Tabla no se actualiza

**Causa:** Los IDs en HTML no coinciden con los de JavaScript.

**Verificar:**
- En HTML: `<td id="amba_cargas_vc">0</td>`
- En JS: `actualizarCelda("amba_cargas_vc", valor)`

Deben ser **exactamente iguales**.

### Problema 4: Botón "Generar Informe" no funciona

**Solución:**
1. Abre consola (F12)
2. Escribe: `generarInformeModerno()`
3. Presiona Enter
4. Revisa si hay errores impresos

---

## FLUJO COMPLETO

```
1. Usuario abre index.html en navegador
   ↓
2. JavaScript ejecuta DOMContentLoaded
   ↓
3. Carga integracion_python_javascript.js
   ↓
4. Fetch datos.json (generado por Python)
   ↓
5. Actualiza tabla HTML automáticamente
   ↓
6. Usuario ve datos calculados
   ↓
7. (Opcional) Usuario cambia fechas y hace click en "Generar Informe"
   ↓
8. generarInformeModerno() lee datos.json actualizado
   ↓
9. Tabla se actualiza con nuevos valores
```

---

## MANTENER FUNCIONALIDAD ANTIGUA

Si tu código JavaScript actual tiene funciones que necesitas mantener, **SÍ se pueden mezclar:**

```html
<script>
// Funciones antiguas (mantén las que necesites)
function descargarPDF() {
    // ... código existente ...
}

function toggleMapa() {
    // ... código existente ...
}

// Nuevas funciones (en integracion_python_javascript.js)
// generarInformeModerno() 
// actualizarDesdeResumenesPython()
// etc.
</script>
```

No hay conflicto. Ambos sistemas pueden coexistir.

---

## PRÓXIMAS MEJORAS (Opcional)

### 1. Server-side (Flask/Django)

Si quieres que Python recalcule en tiempo real:

**Backend (app.py):**
```python
from flask import Flask, request, jsonify
from gestor_fiscalizacion import generar_informe_completo

@app.route("/api/informe", methods=["POST"])
def get_informe():
    datos = request.json
    informe = generar_informe_completo(
        datos.get('fecha_desde'),
        datos.get('fecha_hasta')
    )
    return jsonify(informe)
```

**Frontend (integracion_python_javascript.js):**
```javascript
async function generarInformeConFechas() {
    const fechaDesde = document.getElementById("desde").value;
    const fechaHasta = document.getElementById("hasta").value;
    
    const response = await fetch("/api/informe", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({fecha_desde: fechaDesde, fecha_hasta: fechaHasta})
    });
    
    const informe = await response.json();
    // Actualizar HTML...
}
```

### 2. Base de datos

Almacenar `datos_fiscalizacion.json` en PostgreSQL/MySQL para mejor escalabilidad.

---

## CONCLUSIÓN

**Cambio mínimo, máximo beneficio:**

- Solo 2 líneas: agregar script + cambiar onclick
- No rompes nada existente
- Sistema completamente funcional
- Listo para escalabilidad futura

¡Listo para usar! 🎉

