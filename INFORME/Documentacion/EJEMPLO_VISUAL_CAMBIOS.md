# EJEMPLO VISUAL: Qué modificar en index.html

## Cambio 1: Agregar script de integración

### UBICACIÓN: En la sección `<head>` o antes de `</body>`

**ANTES:**
```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>imagen</title>
    <meta name="author" content="Darío David Molina">
    <link rel="stylesheet" href="style.css">
    <!-- ← AQUÍ AGREGAR -->
</head>
```

**DESPUÉS:**
```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>imagen</title>
    <meta name="author" content="Darío David Molina">
    <link rel="stylesheet" href="style.css">
    <!-- INTEGRACIÓN PYTHON ↔ JAVASCRIPT -->
    <script src="integracion_python_javascript.js"></script>
</head>
```

---

## Cambio 2: Reemplazar función generarInforme()

### UBICACIÓN: En los scripts al final del documento (antes de `</body>`)

**BÚSQUEDA:** Encontrar la función `generarInforme()`

En tu `index.html` actual, busca algo como:

```javascript
async function generarInforme() {
    console.log("Generando informe...");
    try {
        // Leer datos.json
        const response = await fetch("datos.json");
        const data = await response.json();
        // ...más código...
    } catch (error) {
        console.error("Error:", error);
    }
}
```

### OPCIÓN A: Simplemente cambiar el nombre

Si tu función `generarInforme()` actual ya lee de `datos.json`, simplemente:

**DE:**
```html
<button class="btn-informe" onclick="generarInforme()">
    Generar Informe
</button>
```

**A:**
```html
<button class="btn-informe" onclick="generarInformeModerno()">
    Generar Informe
</button>
```

Y elimina la función antigua `generarInforme()` del script.

---

### OPCIÓN B: Mantener función antigua + agregar nueva

Si tienes código importante en `generarInforme()`, puedes mantenerlo:

```javascript
// FUNCIÓN ANTIGUA (mantener)
async function generarInforme() {
    // ... tu código ...
}

// FUNCIÓN NUEVA (usa la de integracion_python_javascript.js)
// No necesitas hacer nada, ya está agregada
```

Y cambiar el botón:

```html
<button class="btn-informe" onclick="generarInformeModerno()">
    Generar Informe
</button>
```

---

## Cambio 3: Mantener los demás scripts

**IMPORTANTE:** No elimines estos scripts existentes:

```html
<!-- ✓ MANTENER ESTOS -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="actualizar_tabla_regiones.js"></script>

<!-- ✓ AGREGAR NUEVO -->
<script src="integracion_python_javascript.js"></script>
```

---

## EJEMPLO COMPLETO

Aquí te muestro cómo debería verse la sección de scripts de tu `index.html`:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>imagen</title>
    <meta name="author" content="Darío David Molina">
    <link rel="stylesheet" href="style.css">
    <!-- ← AGREGAR AQUÍ (NUEVO) -->
    <script src="integracion_python_javascript.js"></script>
</head>

<body>
    <!-- === CONTENIDO PRINCIPAL === -->
    <div id="informe">
        
        <!-- === HEADER === -->
        <div class="header">
            <h1>Resumen Operativo</h1>
            <p>Análisis de Resultado</p>
            
            <!-- === BOTONES === -->
            <div class="container-filtro">
                <div class="campo">
                    <label for="desde">Desde:</label>
                    <input type="date" id="desde">
                </div>
                <div class="campo">
                    <label for="hasta">Hasta:</label>
                    <input type="date" id="hasta">
                </div>
                
                <!-- ← CAMBIAR AQUI: generarInforme() → generarInformeModerno() -->
                <button class="btn-informe" onclick="generarInformeModerno()">
                    Generar Informe
                </button>
                
                <button class="btn-informe" onclick="descargarPDF()">
                    Descargar PDF
                </button>
            </div>
        </div>
        
        <!-- === REST DE TU HTML === -->
        <!-- (Mantener igual) -->
        
    </div>

    <!-- === SCRIPTS === -->
    
    <!-- LIBRERÍAS EXTERNAS (MANTENER) -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    
    <!-- TUS SCRIPTS (MANTENER) -->
    <script src="actualizar_tabla_regiones.js"></script>
    
    <!-- NUEVO: Integración Python ↔ JavaScript -->
    <script src="integracion_python_javascript.js"></script>

    <!-- TUS SCRIPTS INLINE (MANTENER, pero cambiar onclick) -->
    <script>
        // ... mantener funciones como descargarPDF(), toggleMapa(), etc. ...
        
        // ELIMINAR: Función generarInforme() antigua
        // (Porque ahora usamos generarInformeModerno() del nuevo script)
        
        // Si necesitas más lógica después de actualizar, agrégala aquí
        // pero usa generarInformeModerno() como punto de entrada
    </script>

</body>
</html>
```

---

## CAMBIOS RESUMIDOS

| Elemento | Cambio | Nuevo Valor |
|----------|--------|-------------|
| `<head>` | Agregar script | `<script src="integracion_python_javascript.js"></script>` |
| Botón | Cambiar onclick | `onclick="generarInformeModerno()"` |
| Función | Eliminar o renombrar | Eliminar `generarInforme()` antigua |
| Scripts | Agregar | `<script src="integracion_python_javascript.js"></script>` |

---

## CHECKLIST VISUAL

- [ ] 1. Abrir `index.html` en editor
- [ ] 2. Encontrar `<head>`
- [ ] 3. Después de `<link rel="stylesheet"...>`, agregar:
  ```html
  <script src="integracion_python_javascript.js"></script>
  ```
- [ ] 4. Encontrar `<button...onclick="generarInforme()">`
- [ ] 5. Cambiar a `onclick="generarInformeModerno()"`
- [ ] 6. Buscar función `function generarInforme() { ... }`
- [ ] 7. Eliminar esa función (o comentarla)
- [ ] 8. Guardar archivo
- [ ] 9. Ejecutar: `python gestor_fiscalizacion.py`
- [ ] 10. Recargar página en navegador

---

## VERIFICACIÓN FINAL

### Abre la consola del navegador (F12 > Console)

**Deberías ver:**

```
Página cargada. Actualizando con datos de Python...
Cargando resúmenes calculados por Python...
Resúmenes encontrados:
Total VC: 360
Tabla actualizada exitosamente
```

**Si ves errores, revisa:**

1. ¿Ejecutaste `python gestor_fiscalizacion.py`?
2. ¿El archivo `integracion_python_javascript.js` existe?
3. ¿La ruta es correcta en el `<script>` tag?
4. ¿Hace falta punto y coma o comilla en algún lado?

---

## AYUDA RÁPIDA

Si no sabes por dónde empezar:

### 1. Abre index.html con un editor (VSCode, Sublime, etc.)

### 2. Presiona `Ctrl + H` para "Find and Replace"

### 3. Busca: `onclick="generarInforme"`

### 4. Reemplaza con: `onclick="generarInformeModerno"`

### 5. Busca: `</head>`

### 6. Agrega antes (si no existe):
```html
<script src="integracion_python_javascript.js"></script>
```

### 7. Guarda archivo

### 8. Abre terminal y ejecuta:
```bash
cd INFORME
python gestor_fiscalizacion.py
```

### 9. Abre index.html en navegador

### 10. ¡Listo! 🎉

---

Cualquier duda, revisa:
- `GUIA_GESTOR_FISCALIZACION.md` - Documentación completa
- `RESUMEN_SISTEMA_FISCALIZACION.md` - Resumen arquitectura
- `INTEGRACION_PASO_A_PASO.md` - Instrucciones paso a paso

