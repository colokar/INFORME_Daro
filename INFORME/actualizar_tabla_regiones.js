// =========================================================
// SCRIPT: ACTUALIZAR TABLA RESUMEN POR REGIÓN
// =========================================================
// Este script consume datos en tiempo real desde /resumen.
// No usa archivos estáticos como datos.json.
// =========================================================

async function actualizarTablaRegiones() {
    try {
        const response = await fetch('/resumen');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status} - ${response.statusText}`);
        }

        const datos = await response.json();
        const resumenGeneral = datos.resumen_general || {};
        const resumenPorRegion = datos.resumen_por_region || {};

        actualizarResumenGeneral(resumenGeneral, resumenPorRegion);
        actualizarTablaResumenRegion(resumenPorRegion);
        actualizarTotalesTabla(resumenPorRegion);

        console.log('✅ Tabla RESUMEN POR REGIÓN actualizada con datos de la API');
    } catch (error) {
        console.error('❌ Error actualizando tabla regiones:', error);
    }
}

function actualizarResumenGeneral(resumenGeneral, resumenPorRegion) {
    const totalVC = Number(resumenGeneral.total_vc || 0);
    const totalCargas = Number(resumenGeneral.cargas_vc || 0);
    const totalPasajeros = Number(resumenGeneral.pasajeros_vc || 0);
    const totalRetenciones = Number(resumenGeneral.retenciones || 0);
    const totalActas = calcularTotalActas(resumenPorRegion);

    const pctCargas = totalVC > 0 ? Math.round((totalCargas / totalVC) * 100) : 0;
    const pctPasajeros = totalVC > 0 ? Math.round((totalPasajeros / totalVC) * 100) : 0;

    setTexto('vc_total', totalVC);
    setTexto('vc_cargas_un', totalCargas);
    setTexto('vc_pasajeros_un', totalPasajeros);
    setTexto('vc_ret_valor', totalRetenciones);
    setTexto('vc_actas_valor', totalActas);
    setTexto('vc_cargas_pct', `${pctCargas}%`);
    setTexto('vc_pasajeros_pct', `${pctPasajeros}%`);

    const barraCargas = document.getElementById('vc_cargas_pct');
    const barraPasajeros = document.getElementById('vc_pasajeros_pct');
    if (barraCargas) barraCargas.style.flexBasis = `${pctCargas}%`;
    if (barraPasajeros) barraPasajeros.style.flexBasis = `${pctPasajeros}%`;
}

function actualizarTablaResumenRegion(resumenPorRegion) {
    const regiones = ['AMBA', 'CEN', 'CUY', 'NEA', 'NOA', 'COSTA', 'PAT'];

    regiones.forEach(region => {
        const datosRegion = resumenPorRegion[region] || {
            cargas: {vc: 0, actas: 0, ret: 0},
            pasajeros: {vc: 0, actas: 0, ret: 0},
            total: {vc: 0, actas: 0, ret: 0}
        };

        setTexto(`${region.toLowerCase()}_cargas_vc`, datosRegion.cargas.vc);
        setTexto(`${region.toLowerCase()}_cargas_actas`, datosRegion.cargas.actas);
        setTexto(`${region.toLowerCase()}_cargas_ret`, datosRegion.cargas.ret);

        setTexto(`${region.toLowerCase()}_pasajeros_vc`, datosRegion.pasajeros.vc);
        setTexto(`${region.toLowerCase()}_pasajeros_actas`, datosRegion.pasajeros.actas);
        setTexto(`${region.toLowerCase()}_pasajeros_ret`, datosRegion.pasajeros.ret);

        setTexto(`${region.toLowerCase()}_total_vc`, datosRegion.total.vc);
        setTexto(`${region.toLowerCase()}_total_actas`, datosRegion.total.actas);
        setTexto(`${region.toLowerCase()}_total_ret`, datosRegion.total.ret);
    });
}

function actualizarTotalesTabla(resumenPorRegion) {
    const totales = {
        cargas_vc: 0,
        cargas_actas: 0,
        cargas_ret: 0,
        pasajeros_vc: 0,
        pasajeros_actas: 0,
        pasajeros_ret: 0,
        total_vc: 0,
        total_actas: 0,
        total_ret: 0
    };

    Object.values(resumenPorRegion).forEach(region => {
        totales.cargas_vc += Number(region.cargas.vc || 0);
        totales.cargas_actas += Number(region.cargas.actas || 0);
        totales.cargas_ret += Number(region.cargas.ret || 0);
        totales.pasajeros_vc += Number(region.pasajeros.vc || 0);
        totales.pasajeros_actas += Number(region.pasajeros.actas || 0);
        totales.pasajeros_ret += Number(region.pasajeros.ret || 0);
        totales.total_vc += Number(region.total.vc || 0);
        totales.total_actas += Number(region.total.actas || 0);
        totales.total_ret += Number(region.total.ret || 0);
    });

    setTexto('total_cargas_vc', totales.cargas_vc);
    setTexto('total_cargas_actas', totales.cargas_actas);
    setTexto('total_cargas_ret', totales.cargas_ret);
    setTexto('total_pasajeros_vc', totales.pasajeros_vc);
    setTexto('total_pasajeros_actas', totales.pasajeros_actas);
    setTexto('total_pasajeros_ret', totales.pasajeros_ret);
    setTexto('total_vc', totales.total_vc);
    setTexto('total_actas', totales.total_actas);
    setTexto('total_ret', totales.total_ret);
}

function calcularTotalActas(resumenPorRegion) {
    return Object.values(resumenPorRegion).reduce((sum, region) => sum + Number(region.total.actas || 0), 0);
}

function setTexto(id, valor) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = Number(valor || 0).toLocaleString('es-AR');
}

async function actualizarTablaConFechas(fechaDesde, fechaHasta) {
    console.warn('⚠️ El filtro por fechas requiere un endpoint backend adicional para filtrar el Excel.');
}

// Ejecutar directamente cuando la página esté cargada.
document.addEventListener('DOMContentLoaded', () => {
    actualizarTablaRegiones();
});
