"""
Enhanced Instagram Auto-Unfollower
Script seguro y rápido para dejar de seguir usuarios que no te siguen
Optimizado para trabajar con el bookmarklet de Enhanced Instagram Unfollowers
"""

import asyncio
import random
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unfollower.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class InstagramAutoUnfollower:
    def __init__(self, headless: bool = False, speed: str = "balanced"):
        """
        Args:
            headless: Si True, ejecuta sin ventana visible (más rápido)
            speed: "fast", "balanced" o "safe"
        """
        self.headless = headless
        self.speed_config = {
            "fast": {"click_delay": 0.2, "scroll_delay": 0.1, "page_delay": 1, "action_delay": 0.5},
            "balanced": {"click_delay": 0.5, "scroll_delay": 0.3, "page_delay": 1.5, "action_delay": 1},
            "safe": {"click_delay": 1, "scroll_delay": 0.5, "page_delay": 2.5, "action_delay": 2}
        }
        self.delays = self.speed_config.get(speed, self.speed_config["balanced"])
        self.stats = {"total": 0, "unfollowed": 0, "failed": 0, "skipped": 0, "pages": 0}
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.context: Optional[BrowserContext] = None
        self.main_page_url: str = None  # URL de la página del bookmarklet

    async def get_current_page_info(self) -> tuple:
        """
        Obtiene información de la página actual
        Returns: (página actual, total páginas, total mostrados)
        """
        try:
            # Obtener el texto de paginación: "1 / 19"
            page_span = await self.page.query_selector('.sidebar-pagination span')
            if page_span:
                page_text = await page_span.text_content()
                parts = page_text.split('/')
                if len(parts) == 2:
                    current_page = int(parts[0].strip())
                    total_pages = int(parts[1].strip())
                    
                    # Obtener total mostrados
                    displayed_elem = await self.page.query_selector('.sidebar-stats p:first-of-type')
                    displayed_text = await displayed_elem.text_content() if displayed_elem else "0"
                    displayed_count = int(displayed_text.replace('Displayed: ', ''))
                    
                    return current_page, total_pages, displayed_count
        except Exception as e:
            logger.debug(f"Error obteniendo info de página: {e}")
        
        return None, None, None

    async def wait_for_page_load(self, timeout: int = 3000):
        """Espera a que la página cargue completamente"""
        try:
            await self.page.wait_for_selector('label.result-item', timeout=timeout)
            await self.random_delay(0.5)
        except:
            pass

    async def scroll_into_view(self, selector: str):
        """Scroll a un elemento y espera a que sea visible"""
        try:
            await self.page.locator(selector).scroll_into_view_if_needed()
            await self.random_delay(self.delays["scroll_delay"])
        except Exception as e:
            logger.warning(f"No se pudo hacer scroll a {selector}: {e}")

    async def init_browser(self):
        """Inicializa el navegador Playwright con optimizaciones"""
        self.playwright = await async_playwright().start()
        
        # Configuración de Chrome que simula comportamiento humano
        launch_args = {
            "headless": self.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",  # ← Desactivar imágenes para más velocidad
            ]
        }
        
        self.browser = await self.playwright.chromium.launch(**launch_args)
        
        # Contexto con headers reales
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        )
        
        self.page = await self.context.new_page()
        
        # Evitar que Instagram detecte automatización
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
        """)
        
        logger.info("✓ Navegador inicializado")

    async def wait_for_bookmarklet_page(self, timeout_seconds: int = 60):
        """
        Espera a que el usuario ejecute el bookmarklet
        Automáticamente detectará la página del bookmarklet
        """
        logger.info("\n" + "="*60)
        logger.info("⏳ ESPERANDO INSTRUCCIÓN...")
        logger.info("="*60)
        logger.info("\n1. Abre Instagram (www.instagram.com)")
        logger.info("2. Ve a tu perfil → Siguiendo")
        logger.info("3. Ejecuta el bookmarklet (Enhanced Instagram Unfollowers)")
        logger.info("4. El script detectará automáticamente la página\n")
        
        try:
            # Esperar a que haya un elemento de resultado
            await self.page.wait_for_selector('label.result-item', timeout=timeout_seconds * 1000)
            self.main_page_url = self.page.url
            logger.info(f"✓ Página del bookmarklet detectada!")
            logger.info(f"  URL: {self.main_page_url[:80]}...")
            return True
        except:
            logger.error("✗ Timeout - El bookmarklet no fue ejecutado en tiempo")
            return False

    async def get_unfollowers_from_page(self) -> List[str]:
        """
        Obtiene los unfollowers de la página del bookmarklet
        Extrae directamente del HTML: <a href="/username" ...>
        """
        try:
            # Esperar a que los elementos carguen
            await self.page.wait_for_selector('label.result-item', timeout=5000)
            
            # Obtener el contenedor principal de resultados
            results_list = await self.page.query_selector('.results-list')
            if not results_list:
                logger.warning("⚠ No se encontró .results-list")
                return []
            
            # Obtener todos los usuarios (labels dentro de .results-list)
            user_labels = await results_list.query_selector_all('label.result-item')
            unfollowers = []
            
            for label in user_labels:
                try:
                    # Obtener el link dentro del label
                    link = await label.query_selector('a[href^="/"]')
                    if link:
                        href = await link.get_attribute('href')
                        if href:
                            username = href.strip('/')
                            if username and not username.startswith('#'):
                                unfollowers.append(username)
                except Exception as e:
                    logger.debug(f"Error extrayendo usuario: {e}")
                    continue
            
            # Remover duplicados manteniendo orden
            unfollowers = list(dict.fromkeys(unfollowers))
            
            if unfollowers:
                logger.info(f"✓ Encontrados {len(unfollowers)} unfollowers en esta página")
            else:
                logger.warning("⚠ No se encontraron usuarios en esta página")
            
            return unfollowers
        
        except Exception as e:
            logger.error(f"✗ Error obteniendo unfollowers: {e}")
            return []

    async def unfollow_user(self, username: str) -> bool:
        """Dejar de seguir a un usuario - VERSIÓN OPTIMIZADA"""
        profile_page = None
        try:
            # Abrir perfil en nueva pestaña
            profile_page = await self.context.new_page()
            
            # Navegar al perfil
            await profile_page.goto(f"https://www.instagram.com/{username}/", wait_until="domcontentloaded", timeout=10000)
            await self.random_delay(self.delays["action_delay"], variance=0.3)
            
            # Buscar botón "Following"
            following_btn = profile_page.locator('button:has-text("Following"), button[aria-label*="Following"]').first
            
            if await following_btn.is_visible(timeout=3000):
                await following_btn.scroll_into_view_if_needed()
                await self.random_delay(self.delays["click_delay"], variance=0.3)
                await following_btn.click()
                await self.random_delay(self.delays["click_delay"], variance=0.2)
                
                # Confirmar en el pop-up (buscar botón "Unfollow")
                try:
                    unfollow_confirm = profile_page.locator('button:has-text("Unfollow")').first
                    if await unfollow_confirm.is_visible(timeout=2000):
                        await unfollow_confirm.click()
                        await self.random_delay(self.delays["click_delay"], variance=0.2)
                        logger.info(f"✓ @{username}")
                        return True
                except:
                    logger.warning(f"⚠ No se pudo confirmar unfollow de @{username}")
                    return False
            else:
                logger.warning(f"⚠ @{username} - Sin botón Following (posible ya no sigue)")
                return False
        
        except asyncio.TimeoutError:
            logger.warning(f"⏱ @{username} - Timeout")
            return False
        except Exception as e:
            logger.error(f"✗ @{username} - {str(e)[:50]}")
            return False
        finally:
            if profile_page:
                await profile_page.close()

    async def handle_pagination(self) -> bool:
        """
        Detecta y navega a la siguiente página en el bookmarklet
        Busca el botón "❯" (siguiente) en el aside de paginación
        """
        try:
            # Esperar a que el div de paginación sea visible
            await self.page.wait_for_selector('.sidebar-pagination', timeout=2000)
            
            # Obtener todos los enlaces de paginación (❮ y ❯)
            pagination_links = await self.page.query_selector_all('.sidebar-pagination .pagination-controls a.p-medium')
            
            if not pagination_links or len(pagination_links) < 2:
                logger.info("✓ No hay botones de paginación")
                return False
            
            # El último enlace es el botón "siguiente" (❯)
            next_btn = pagination_links[-1]
            
            # Verificar el texto para confirmar que es "siguiente"
            btn_text = await next_btn.text_content()
            
            if "❯" in btn_text or ">" in btn_text:
                await next_btn.scroll_into_view_if_needed()
                await self.random_delay(self.delays["click_delay"], variance=0.3)
                await next_btn.click()
                
                # Esperar a que cargue la nueva página
                await self.page.wait_for_load_state("domcontentloaded")
                await self.random_delay(self.delays["page_delay"], variance=0.5)
                
                logger.info("→ Siguiente página")
                return True
            else:
                logger.info("✓ Última página alcanzada")
                return False
        
        except Exception as e:
            logger.warning(f"Error en paginación: {e}")
            return False

    async def run(self, max_unfollows: int = None):
        """
        Ejecuta el script completo
        
        Args:
            max_unfollows: Número máximo de unfollows (None = sin límite)
        """
        try:
            await self.init_browser()
            
            # Navegar a Instagram (en blanco, esperará el bookmarklet)
            await self.page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            
            # Esperar a que el usuario ejecute el bookmarklet
            if not await self.wait_for_bookmarklet_page():
                return
            
            page_number = 1
            should_continue = True
            
            while should_continue and (max_unfollows is None or self.stats["unfollowed"] < max_unfollows):
                # Obtener información de la página
                current_page, total_pages, displayed = await self.get_current_page_info()
                
                logger.info(f"\n{'='*60}")
                if current_page and total_pages:
                    logger.info(f"📄 PÁGINA {current_page}/{total_pages}")
                else:
                    logger.info(f"📄 PÁGINA {page_number}")
                logger.info(f"{'='*60}")
                
                # Esperar a que carguen los usuarios
                await self.wait_for_page_load()
                
                # Obtener unfollowers de la página actual
                unfollowers = await self.get_unfollowers_from_page()
                
                if not unfollowers:
                    logger.info("⚠ No se encontraron usuarios en esta página")
                    break
                
                self.stats["pages"] += 1
                
                # Procesar cada usuario
                for i, username_to_unfollow in enumerate(unfollowers, 1):
                    if max_unfollows and self.stats["unfollowed"] >= max_unfollows:
                        logger.info(f"✓ Límite de {max_unfollows} unfollows alcanzado")
                        should_continue = False
                        break
                    
                    self.stats["total"] += 1
                    
                    # Mostrar progreso
                    logger.info(f"[{i}/{len(unfollowers)}] {username_to_unfollow}...", end=" ")
                    
                    success = await self.unfollow_user(username_to_unfollow)
                    if success:
                        self.stats["unfollowed"] += 1
                    else:
                        self.stats["failed"] += 1
                    
                    # Delay entre unfollows
                    await self.random_delay(self.delays["action_delay"], variance=0.8)
                
                # Intentar siguiente página
                if should_continue:
                    logger.info("")  # Salto de línea
                    should_continue = await self.handle_pagination()
                    page_number += 1
        
        except KeyboardInterrupt:
            logger.info("\n\n⊘ Script cancelado por el usuario")
        except Exception as e:
            logger.error(f"Error fatal: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await self.close()
            self.print_stats()

    async def close(self):
        """Cierra el navegador"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
            logger.info("Navegador cerrado")

    def print_stats(self):
        """Imprime estadísticas"""
        logger.info(f"\n{'='*60}")
        logger.info("📊 ESTADÍSTICAS FINALES")
        logger.info(f"{'='*60}")
        logger.info(f"Páginas procesadas: {self.stats['pages']}")
        logger.info(f"Total procesados: {self.stats['total']}")
        logger.info(f"✓ Dejados de seguir: {self.stats['unfollowed']}")
        logger.info(f"✗ Fallidos: {self.stats['failed']}")
        logger.info(f"⏱ Tiempo total: Revisa el log para detalles")
        logger.info(f"{'='*60}\n")


async def main():
    """Función principal"""
    # CONFIGURACIÓN
    SPEED = "balanced"  # "fast", "balanced" o "safe"
    HEADLESS = False    # True = sin ventana visible (más rápido)
    MAX_UNFOLLOWS = None  # None = sin límite, o número específico (ej: 50)
    
    unfollower = InstagramAutoUnfollower(headless=HEADLESS, speed=SPEED)
    
    try:
        await unfollower.run(max_unfollows=MAX_UNFOLLOWS)
    except KeyboardInterrupt:
        logger.info("\n⊘ Script cancelado")


if __name__ == "__main__":
    asyncio.run(main())
