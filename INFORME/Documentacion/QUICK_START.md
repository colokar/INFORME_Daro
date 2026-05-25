# QUICK START (5 minutos)

## Archivos Creados

✓ `datos_fiscalizacion.json` - Datos de ejemplo (20 registros)
✓ `gestor_fiscalizacion.py` - Módulo Python (6 funciones)
✓ `integracion_python_javascript.js` - Script JS para leer datos
✓ Documentación completa (4 archivos)

---

## 3 PASOS PARA EMPEZAR

### 1️⃣ Ejecutar Python

```bash
cd INFORME
python gestor_fiscalizacion.py
```

**Resultado:** `datos.json` se actualiza con resúmenes calculados

### 2️⃣ Modificar HTML (2 cambios)

En `index.html`:

**Cambio A:** En `<head>`, después de `<link...>`

```html
<script src="integracion_python_javascript.js"></script>
```

**Cambio B:** En el botón "Generar Informe"

```html
<!-- DE ESTO: -->
<button onclick="generarInforme()">

<!-- A ESTO: -->
<button onclick="generarInformeModerno()">
```

### 3️⃣ Abrir navegador y probar

1. Abre `index.html`
2. Mira la consola (F12 > Console)
3. Deberías ver "Tabla actualizada exitosamente"
4. Los valores en la tabla HTML están actualizados

---

## VERIFICACIÓN

**Consola debería mostrar:**
```
Página cargada. Actualizando con datos de Python...
Cargando resúmenes calculados por Python...
Resúmenes encontrados:
Total VC: 360
Tabla actualizada exitosamente
```

---

## ¿QUÉ HACE?

```
datos_fiscalizacion.json
    ↓ (Python lee)
gestor_fiscalizacion.py
    ↓ (Calcula y guarda)
datos.json
    ↓ (JavaScript fetch)
integracion_python_javascript.js
    ↓ (Actualiza HTML)
index.html (tabla)
```

---

## FUNCIONES DISPONIBLES

### Python
- `cargar_datos()` - Lee JSON
- `filtrar_por_fecha()` - Filtra fechas
- `calcular_resumen()` - Suma por tipo
- `calcular_por_region()` - Agrupa por región
- `generar_informe_completo()` - Todo junto

### JavaScript
- `generarInformeModerno()` - Botón "Generar Informe"
- `actualizarDesdeResumenesPython()` - Lee datos.json

---

## EJEMPLO: Usar en tu código

```python
from gestor_fiscalizacion import generar_informe_completo

# Generar informe de todo
informe = generar_informe_completo()

# Acceder datos
total_vc = informe['resumen_general']['total']['vc']
amba_vc = informe['resumen_por_region']['AMBA']['total']['vc']

print(f"Total: {total_vc}, AMBA: {amba_vc}")
```

---

## ARCHIVOS DE REFERENCIA

- **`GUIA_GESTOR_FISCALIZACION.md`** - Doc técnica completa
- **`RESUMEN_SISTEMA_FISCALIZACION.md`** - Arquitectura general
- **`INTEGRACION_PASO_A_PASO.md`** - Pasos detallados
- **`EJEMPLO_VISUAL_CAMBIOS.md`** - Cambios HTML visuales

---

## DATOS DE PRUEBA

El archivo `datos_fiscalizacion.json` tiene 20 registros de ejemplo:

| Región | Fecha | Tipo | VC | Actas | Ret |
|--------|-------|------|----|----|-----|
| AMBA | 2026-03-01 | CARGAS | 45 | 8 | 2 |
| AMBA | 2026-03-01 | PASAJEROS | 32 | 5 | 1 |
| ... | ... | ... | ... | ... | ... |

**Para usar tus datos:** Reemplaza el contenido de `datos_fiscalizacion.json` con tus registros.

---

## TROUBLESHOOTING

| Problema | Solución |
|----------|----------|
| "generarInformeModerno is not defined" | Agrega `<script src="integracion_python_javascript.js"></script>` al HTML |
| "datos.json not found" | Ejecuta `python gestor_fiscalizacion.py` |
| Tabla no cambia | Abre consola (F12), busca errores |
| Valores siguen en 0 | Espera a que Python termine, recarga página |

---

## PRÓXIMO PASO

1. Ejecuta Python
2. Modifica HTML (2 cambios)
3. ¡Hecho! Tabla se actualiza mágicamente

Para más detalles, lee la documentación. ¡Buena suerte! 🚀

