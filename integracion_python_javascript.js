// ========================================================
// INTEGRACIÓN JAVASCRIPT ↔ PYTHON
// ========================================================
//
// Este archivo muestra cómo leer los resúmenes
// generados por Python desde JavaScript.
//
// Flujo:
// 1. Python ejecuta: gestor_fiscalizacion.py
// 2. Se actualiza: datos.json con resumen_general y resumen_por_region
// 3. JavaScript fetch: datos.json
// 4. HTML se actualiza automáticamente
// ========================================================

/**
 * Carga los resúmenes desde datos.json (generados por Python)
 * y actualiza la tabla HTML
 */
async function actualizarDesdeResumenesPython() {
    try {
        console.log("Cargando resúmenes calculados por Python...");
        
        const response = await fetch("datos.json");
        if (!response.ok) throw new Error("No se pudo cargar datos.json");
        
        const datos = await response.json();
        
        // Verificar que existen los resúmenes
        if (!datos.resumen_general || !datos.resumen_por_region) {
            console.warn("Advertencia: Los resúmenes no existen en datos.json");
            console.log("Ejecuta: python gestor_fiscalizacion.py");
            return;
        }
        
        console.log("Resúmenes encontrados:");
        
        // ====================================================
        // 1. ACTUALIZAR RESUMEN GENERAL
        // ====================================================
        
        const resumenGeneral = datos.resumen_general;
        
        // Total VC
        const totalVC = resumenGeneral.total.vc;
        console.log(`Total VC: ${totalVC}`);
        
        // Cargas vs Pasajeros
        const vcCargas = resumenGeneral.cargas.vc;
        const vcPasajeros = resumenGeneral.pasajeros.vc;
        const porcCargas = totalVC > 0 ? Math.round((vcCargas / totalVC) * 100) : 0;
        const porcPasajeros = totalVC > 0 ? Math.round((vcPasajeros / totalVC) * 100) : 0;
        
        // Actualizar elementos HTML (ejemplo)
        if (document.getElementById("vc_total")) {
            document.getElementById("vc_total").textContent = totalVC;
        }
        
        if (document.getElementById("barra_cargas_pct")) {
            document.getElementById("barra_cargas_pct").textContent = porcCargas + "%";
        }
        
        if (document.getElementById("barra_pasajeros_pct")) {
            document.getElementById("barra_pasajeros_pct").textContent = porcPasajeros + "%";
        }
        
        // ====================================================
        // 2. ACTUALIZAR TABLA POR REGIÓN
        // ====================================================
        
        const resumenPorRegion = datos.resumen_por_region;
        
        // Regiones e sus IDs en la tabla
        const regiones = ["AMBA", "COSTA", "BA", "CEN", "CUY", "NEA", "NOA", "PAT"];
        
        regiones.forEach(region => {
            
            const datosRegion = resumenPorRegion[region];
            
            // Para cada tipo (cargas, pasajeros, total)
            // y cada métrica (vc, actas, ret)
            
            // CARGAS
            actualizarCelda(`${region.toLowerCase()}_cargas_vc`, datosRegion.cargas.vc);
            actualizarCelda(`${region.toLowerCase()}_cargas_actas`, datosRegion.cargas.actas);
            actualizarCelda(`${region.toLowerCase()}_cargas_ret`, datosRegion.cargas.ret);
            
            // PASAJEROS
            actualizarCelda(`${region.toLowerCase()}_pasajeros_vc`, datosRegion.pasajeros.vc);
            actualizarCelda(`${region.toLowerCase()}_pasajeros_actas`, datosRegion.pasajeros.actas);
            actualizarCelda(`${region.toLowerCase()}_pasajeros_ret`, datosRegion.pasajeros.ret);
            
            // TOTALES
            actualizarCelda(`${region.toLowerCase()}_total_vc`, datosRegion.total.vc);
            actualizarCelda(`${region.toLowerCase()}_total_actas`, datosRegion.total.actas);
            actualizarCelda(`${region.toLowerCase()}_total_ret`, datosRegion.total.ret);
        });
        
        // ====================================================
        // 3. ACTUALIZAR TOTALES GENERALES EN TABLA
        // ====================================================
        
        actualizarCelda("total_cargas_vc", resumenGeneral.cargas.vc);
        actualizarCelda("total_cargas_actas", resumenGeneral.cargas.actas);
        actualizarCelda("total_cargas_ret", resumenGeneral.cargas.ret);
        
        actualizarCelda("total_pasajeros_vc", resumenGeneral.pasajeros.vc);
        actualizarCelda("total_pasajeros_actas", resumenGeneral.pasajeros.actas);
        actualizarCelda("total_pasajeros_ret", resumenGeneral.pasajeros.ret);
        
        actualizarCelda("total_vc", resumenGeneral.total.vc);
        actualizarCelda("total_actas", resumenGeneral.total.actas);
        actualizarCelda("total_ret", resumenGeneral.total.ret);
        
        console.log("Tabla actualizada exitosamente");
        
    } catch (error) {
        console.error("Error al cargar resúmenes:", error);
    }
}

/**
 * Helper: Actualiza una celda de la tabla por ID
 */
function actualizarCelda(elementId, valor) {
    const elemento = document.getElementById(elementId);
    if (elemento) {
        elemento.textContent = valor || 0;
    }
}

/**
 * Flujo: El usuario hace click en "Generar Informe"
 * 
 * OPCIÓN 1 - Solo JavaScript (lectura):
 *   - JavaScript lee datos.json
 *   - Usa los resúmenes ya calculados por Python
 * 
 * OPCIÓN 2 - Con Backend (recalcular):
 *   - JavaScript envía POST a endpoint Python
 *   - Python recalcula con nuevas fechas
 *   - Python actualiza datos.json
 *   - JavaScript lee los nuevos datos
 */

async function generarInformeModerno() {
    
    console.log("Generando informe...");
    
    // Obtener fechas del HTML
    const fechaDesde = document.getElementById("desde")?.value;
    const fechaHasta = document.getElementById("hasta")?.value;
    
    console.log(`Fechas: ${fechaDesde} a ${fechaHasta}`);
    
    // ====================================================
    // OPCIÓN 1: Solo leer datos.json (ya procesados)
    // ====================================================
    // Esto funciona si los datos ya fueron procesados
    // por: python gestor_fiscalizacion.py
    
    await actualizarDesdeResumenesPython();
    
    // ====================================================
    // OPCIÓN 2: Enviar al backend para recalcular
    // ====================================================
    // Descomentar esto si tienes un servidor Flask/Django
    
    /*
    try {
        const response = await fetch("/api/generar-informe", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                fecha_desde: fechaDesde,
                fecha_hasta: fechaHasta
            })
        });
        
        const resultado = await response.json();
        
        if (resultado.exito) {
            // Actualizar HTML con nuevos datos
            await actualizarDesdeResumenesPython();
        } else {
            console.error("Error en backend:", resultado.error);
        }
    } catch (error) {
        console.error("Error en request:", error);
    }
    */
}

// ========================================================
// EJECUTAR AL CARGAR LA PÁGINA
// ========================================================

document.addEventListener("DOMContentLoaded", function() {
    console.log("Página cargada. Actualizando con datos de Python...");
    actualizarDesdeResumenesPython();
});

// ========================================================
// INTEGRACIÓN CON BOTÓN "GENERAR INFORME"
// ========================================================
//
// En index.html, reemplaza:
//
//   <button onclick="generarInforme()">
//
// Por:
//
//   <button onclick="generarInformeModerno()">
//
// ========================================================
