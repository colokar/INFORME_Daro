# =========================================================
# MÓDULO: AUTOMATIZACIÓN DE DESCARGAS CNRT CON PLAYWRIGHT
# =========================================================
# 
# Responsable de:
# - Automatizar login en sistema CNRT
# - Navegar a reportes
# - Descargar reportes por delegación/región
# - Guardar archivos automáticamente
# - Manejar errores y timeouts
# =========================================================

import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
except ImportError:
    raise ImportError(
        "Playwright no está instalado. Ejecuta: pip install playwright\n"
        "Luego: playwright install"
    )

from config.settings import (
    CNRT_URL, CNRT_USERNAME, CNRT_PASSWORD,
    PLAYWRIGHT_HEADLESS, PLAYWRIGHT_TIMEOUT,
    EXCELS_DESCARGADOS
)
from utils import setup_logger

logger = setup_logger(__name__)

class DescargadorCNRT:
    """Automatiza la descarga de reportes desde el sistema CNRT."""
    
    def __init__(self, 
                 url: str = CNRT_URL,
                 username: str = CNRT_USERNAME,
                 password: str = CNRT_PASSWORD,
                 directorio_salida: Path = None,
                 headless: bool = PLAYWRIGHT_HEADLESS,
                 timeout: int = PLAYWRIGHT_TIMEOUT):
        """
        Inicializa el descargador.
        
        Args:
            url: URL del sistema CNRT
            username: Usuario para login
            password: Contraseña para login
            directorio_salida: Directorio donde guardar descargas
            headless: Si ejecutar en modo headless
            timeout: Timeout en milisegundos
        """
        self.url = url
        self.username = username
        self.password = password
        self.directorio_salida = directorio_salida or EXCELS_DESCARGADOS
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Crear directorio si no existe
        self.directorio_salida.mkdir(parents=True, exist_ok=True)
    
    async def iniciar(self):
        """Inicia el navegador Playwright."""
        logger.info("Iniciando navegador Playwright...")
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            # Simular comportamiento real de navegador
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(self.timeout)
        
        logger.info("✓ Navegador iniciado")
    
    async def cerrar(self):
        """Cierra el navegador."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("✓ Navegador cerrado")
        except Exception as e:
            logger.error(f"Error cerrando navegador: {e}")
    
    async def login(self) -> bool:
        """
        Realiza login en el sistema CNRT.
        
        Returns:
            True si el login fue exitoso
        """
        try:
            logger.info(f"Navegando a {self.url}...")
            await self.page.goto(self.url, wait_until="networkidle")
            
            logger.info("Realizando login...")
            
            # Rellenar credenciales (adaptar selectores según HTML real)
            # Estos son placeholders - necesitan ajustarse con los selectores reales
            await self.page.fill('input[name="usuario"]', self.username, timeout=self.timeout)
            await self.page.fill('input[name="password"]', self.password, timeout=self.timeout)
            
            # Hacer click en botón de login
            await self.page.click('button:has-text("Ingresar")', timeout=self.timeout)
            
            # Esperar a que cargue después del login
            await self.page.wait_for_load_state("networkidle", timeout=self.timeout)
            
            logger.info("✓ Login exitoso")
            return True
        
        except asyncio.TimeoutError:
            logger.error("Timeout durante login")
            return False
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return False
    
    async def navegar_a_reportes(self) -> bool:
        """
        Navega a la sección de reportes.
        
        Returns:
            True si fue exitoso
        """
        try:
            logger.info("Navegando a sección de reportes...")
            
            # Adaptar selectores según estructura real del sitio
            await self.page.click('a:has-text("Reportes")', timeout=self.timeout)
            await self.page.wait_for_load_state("networkidle")
            
            logger.info("✓ Navegación a reportes completada")
            return True
        
        except Exception as e:
            logger.error(f"Error navegando a reportes: {e}")
            return False
    
    async def descargar_reporte(self, 
                               delegacion: str,
                               fecha_desde: Optional[str] = None,
                               fecha_hasta: Optional[str] = None) -> bool:
        """
        Descarga un reporte para una delegación específica.
        
        Args:
            delegacion: Nombre de la delegación
            fecha_desde: Fecha desde (YYYY-MM-DD)
            fecha_hasta: Fecha hasta (YYYY-MM-DD)
            
        Returns:
            True si la descarga fue exitosa
        """
        try:
            logger.info(f"Descargando reporte para: {delegacion}")
            
            # Seleccionar delegación (adaptar selectores)
            await self.page.select_option(
                'select[name="delegacion"]',
                delegacion,
                timeout=self.timeout
            )
            
            # Seleccionar fechas si se proporcionan
            if fecha_desde:
                await self.page.fill('input[name="fecha_desde"]', fecha_desde)
            if fecha_hasta:
                await self.page.fill('input[name="fecha_hasta"]', fecha_hasta)
            
            # Hacer click en descargar
            async with self.page.expect_download() as download_info:
                await self.page.click('button:has-text("Descargar")', timeout=self.timeout)
            
            download = await download_info.value
            
            # Guardar archivo con nombre descriptivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"reporte_{delegacion}_{timestamp}.xlsx"
            ruta_destino = self.directorio_salida / nombre_archivo
            
            await download.save_as(ruta_destino)
            
            logger.info(f"✓ Reporte descargado: {nombre_archivo}")
            logger.info(f"  Ubicación: {ruta_destino}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error descargando reporte de {delegacion}: {e}")
            return False
    
    async def descargar_multiples_reportes(self, 
                                          delegaciones: List[str],
                                          fecha_desde: Optional[str] = None,
                                          fecha_hasta: Optional[str] = None) -> Dict[str, bool]:
        """
        Descarga múltiples reportes.
        
        Args:
            delegaciones: Lista de delegaciones
            fecha_desde: Fecha desde
            fecha_hasta: Fecha hasta
            
        Returns:
            Diccionario con resultados por delegación
        """
        resultados = {}
        
        for delegacion in delegaciones:
            logger.info(f"[{delegaciones.index(delegacion) + 1}/{len(delegaciones)}] Procesando...")
            
            exito = await self.descargar_reporte(delegacion, fecha_desde, fecha_hasta)
            resultados[delegacion] = exito
            
            # Esperar entre descargas para no sobrecargar
            await asyncio.sleep(2)
        
        return resultados
    
    async def obtener_listado_delegaciones(self) -> List[str]:
        """
        Obtiene lista de delegaciones disponibles.
        
        Returns:
            Lista de nombres de delegaciones
        """
        try:
            logger.info("Obteniendo listado de delegaciones...")
            
            # Adaptar selector según HTML real
            options = await self.page.locator(
                'select[name="delegacion"] option'
            ).all_text_contents()
            
            # Filtrar la opción "Seleccionar" o similar
            delegaciones = [opt.strip() for opt in options 
                           if opt.strip() and "seleccionar" not in opt.lower()]
            
            logger.info(f"✓ {len(delegaciones)} delegaciones encontradas")
            return delegaciones
        
        except Exception as e:
            logger.error(f"Error obteniendo delegaciones: {e}")
            return []

async def descargar_reportes_cnrt(
    delegaciones: List[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    username: str = CNRT_USERNAME,
    password: str = CNRT_PASSWORD
) -> Tuple[bool, Dict[str, bool]]:
    """
    Función auxiliar para descargar reportes.
    
    Args:
        delegaciones: Lista de delegaciones (None para todas)
        fecha_desde: Fecha desde
        fecha_hasta: Fecha hasta
        username: Usuario
        password: Contraseña
        
    Returns:
        Tupla (éxito_general, resultados_por_delegación)
    """
    descargador = DescargadorCNRT(username=username, password=password)
    
    try:
        await descargador.iniciar()
        
        # Login
        if not await descargador.login():
            return False, {}
        
        # Navegar a reportes
        if not await descargador.navegar_a_reportes():
            return False, {}
        
        # Obtener delegaciones si no se especifican
        if delegaciones is None:
            delegaciones = await descargador.obtener_listado_delegaciones()
        
        if not delegaciones:
            logger.error("No hay delegaciones para descargar")
            return False, {}
        
        # Descargar reportes
        resultados = await descargador.descargar_multiples_reportes(
            delegaciones, fecha_desde, fecha_hasta
        )
        
        # Verificar si todas fueron exitosas
        todas_ok = all(resultados.values())
        
        return todas_ok, resultados
    
    except Exception as e:
        logger.error(f"Error en descarga: {e}")
        return False, {}
    
    finally:
        await descargador.cerrar()
