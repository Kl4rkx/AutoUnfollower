"""
Enhanced Instagram Auto-Unfollower v2.1
Script ultra-rápido para dejar de seguir usuarios
Soporta 2FA - Comportamiento humanizado - Sin bloqueos
"""

import asyncio
import random
import sys
from typing import List, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import logging

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unfollower.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class InstagramAutoUnfollower:
    def __init__(self, headless: bool = False, speed: str = "balanced"):
        self.headless = headless
        # Delays más realistas para evitar bloqueos
        self.speed_config = {
            "fast": {"click": 0.8, "scroll": 0.3, "page": 2, "action": 1.5},
            "balanced": {"click": 1.2, "scroll": 0.5, "page": 3, "action": 2},
            "safe": {"click": 1.8, "scroll": 0.7, "page": 4, "action": 3}
        }
        self.delays = self.speed_config.get(speed, self.speed_config["balanced"])
        self.stats = {"total": 0, "unfollowed": 0, "failed": 0, "pages": 0}
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.context: Optional[BrowserContext] = None

    async def random_delay(self, base_delay: float, variance: float = 0.4):
        """Delay humanizado con varianza"""
        variation = base_delay * variance
        delay = base_delay + random.uniform(-variation, variation)
        await asyncio.sleep(max(delay, 0.1))

    async def init_browser(self):
        """Inicializa navegador con anti-detección de bots"""
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-plugins",
            ]
        )
        
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        self.page = await self.context.new_page()
        
        # Anti-detección de automatización
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
        """)
        
        logger.info("[OK] Navegador iniciado")

    async def handle_2fa(self):
        """Maneja autenticación de 2 factores si es necesaria"""
        try:
            # Buscar campo de autenticación
            auth_input = self.page.locator('input[aria-label*="code"], input[placeholder*="code"], input[placeholder*="Código"]').first
            
            if await auth_input.is_visible(timeout=2000):
                logger.info("[2FA] Codigo 2FA requerido")
                code = input("Ingresa el codigo de autenticacion: ").strip()
                
                await auth_input.click()
                await self.random_delay(self.delays["click"])
                await auth_input.fill(code)
                await self.random_delay(self.delays["click"])
                
                # Buscar botón de confirmación
                confirm_btn = self.page.locator('button:has-text("Siguiente"), button:has-text("Confirm"), button:has-text("Done")').first
                if await confirm_btn.is_visible(timeout=1000):
                    await confirm_btn.click()
                    await self.page.wait_for_load_state("domcontentloaded")
                    await self.random_delay(2)
                    logger.info("[OK] 2FA completado")
                    return True
        except:
            pass
        return False

    async def load_all_results(self, max_loops: int = 20, pause: float = 0.5) -> int:
        """Hace scroll en la lista para cargar todos los usuarios del bookmarklet."""
        container = await self.page.query_selector('.results-list')
        if not container:
            return 0

        last_count = 0
        stable_steps = 0

        for _ in range(max_loops):
            labels = await container.query_selector_all('label.result-item')
            count = len(labels)

            if count > last_count:
                last_count = count
                stable_steps = 0
            else:
                stable_steps += 1

            # Si no cambia en 3 iteraciones seguidas, asumimos que ya cargó todo
            if stable_steps >= 3:
                break

            # Scroll al fondo para forzar carga perezosa
            try:
                await container.evaluate("el => { el.scrollTop = el.scrollHeight; }")
            except:
                pass

            await asyncio.sleep(pause)

        return last_count

    async def get_unfollowers_from_page(self) -> List[str]:
        """Extrae usuarios de la página actual"""
        try:
            await self.page.wait_for_selector('label.result-item', timeout=3000)

            # Cargar todos los usuarios disponibles haciendo scroll en la lista
            await self.load_all_results()
            
            results_list = await self.page.query_selector('.results-list')
            if not results_list:
                return []
            
            user_labels = await results_list.query_selector_all('label.result-item')
            unfollowers = []
            
            for label in user_labels:
                try:
                    link = await label.query_selector('a[href^="/"]')
                    if link:
                        href = await link.get_attribute('href')
                        if href:
                            username = href.strip('/')
                            if username:
                                unfollowers.append(username)
                except:
                    continue
            
            unfollowers = list(dict.fromkeys(unfollowers))
            if unfollowers:
                logger.info(f"[OK] {len(unfollowers)} usuarios encontrados")
            return unfollowers
        
        except Exception as e:
            logger.error(f"Error extrayendo usuarios: {e}")
            return []

    async def unfollow_user(self, username: str) -> bool:
        """Dejar de seguir a un usuario"""
        profile_page = None
        try:
            profile_page = await self.context.new_page()
            await profile_page.goto(f"https://www.instagram.com/{username}/", wait_until="domcontentloaded", timeout=8000)
            await self.random_delay(self.delays["action"])
            
            # Buscar botón "Following" o "Siguiendo" (el texto está en un div interno)
            following_btn = profile_page.locator('button:has(div._ap3a:has-text("Siguiendo")), button:has(div:has-text("Following")), button:has-text("Siguiendo"), button:has-text("Following")').first
            
            if await following_btn.is_visible(timeout=2000):
                await following_btn.scroll_into_view_if_needed()
                await self.random_delay(self.delays["click"])
                await following_btn.click()
                await self.random_delay(self.delays["click"])
                
                # Hacer clic en "Dejar de seguir" del menú emergente
                try:
                    # Buscar el botón específico con el texto exacto "Dejar de seguir"
                    # Usar un selector más específico para evitar otros botones
                    unfollow_confirm = profile_page.locator(
                        'button:has-text("Dejar de seguir"), '
                        'button:has-text("Unfollow"), '
                        'span.x1lliihq:has-text("Dejar de seguir"), '
                        'span:text-is("Dejar de seguir"), '
                        'span:text-is("Unfollow")'
                    ).first
                    
                    if await unfollow_confirm.is_visible(timeout=2000):
                        await unfollow_confirm.click()
                        
                        # Dar tiempo para que Instagram procese el unfollow
                        await self.random_delay(2)
                        
                        # ESPERAR a que el botón cambie de "Siguiendo" a "Seguir"
                        # Esto confirma que realmente se dejó de seguir
                        try:
                            # Aumentar timeout a 8 segundos para darle tiempo a Instagram
                            await profile_page.wait_for_selector(
                                'button:has-text("Seguir"), button:has-text("Follow"), button:has(div._ap3a:has-text("Seguir")), button:has(div:has-text("Follow"))',
                                timeout=8000
                            )
                            logger.info(f"[OK] @{username}")
                            # Delay adicional antes de cerrar la página
                            await self.random_delay(1)
                            return True
                        except:
                            logger.warning(f"[SKIP] @{username} - No cambio a 'Seguir'")
                            return False
                except:
                    pass
            
            logger.warning(f"[SKIP] @{username}")
            return False
        
        except asyncio.TimeoutError:
            logger.warning(f"[TIMEOUT] @{username}")
            return False
        except Exception as e:
            logger.error(f"[FAIL] @{username}")
            return False
        finally:
            if profile_page:
                await profile_page.close()

    async def handle_pagination(self) -> bool:
        """Detecta y cambia a siguiente página leyendo el contador de páginas"""
        try:
            await self.page.wait_for_selector('.sidebar-pagination', timeout=1500)
            
            # Leer el texto del contador de páginas (ej: "1 / 5")
            page_counter = await self.page.query_selector('.pagination-controls span')
            if not page_counter:
                return False
            
            counter_text = await page_counter.text_content()
            # Formato: "X / Y" donde X es página actual, Y es total
            
            try:
                parts = counter_text.split('/')
                current_page = int(parts[0].strip())
                total_pages = int(parts[1].strip())
                
                # Si ya estamos en la última página, detener
                if current_page >= total_pages:
                    logger.info(f"[END] Pagina {current_page}/{total_pages} - Ultima pagina alcanzada")
                    return False
                
                logger.info(f"[PAGE] {current_page}/{total_pages}")
            except:
                pass
            
            # Buscar y hacer click en el botón siguiente
            pagination_links = await self.page.query_selector_all('.sidebar-pagination .pagination-controls a.p-medium')
            
            if not pagination_links or len(pagination_links) < 2:
                return False
            
            next_btn = pagination_links[-1]
            btn_text = await next_btn.text_content()
            
            # Verificar que sea el botón siguiente (❯)
            if "❯" not in btn_text and ">" not in btn_text:
                return False
            
            await next_btn.scroll_into_view_if_needed()
            await self.random_delay(self.delays["click"])
            await next_btn.click()
            await self.page.wait_for_load_state("domcontentloaded")
            await self.random_delay(self.delays["page"])
            
            logger.info("[NEXT] Siguiente pagina")
            return True
                
        except:
            pass
        
        return False

    async def wait_for_bookmarklet(self):
        """Espera a que ejecutes el bookmarklet"""
        logger.info("\n" + "="*60)
        logger.info("[ESPERANDO] BOOKMARKLET...")
        logger.info("="*60)
        logger.info("\nEN LA MISMA VENTANA DE CHROME:")
        logger.info("1. Ve a tu Perfil -> Siguiendo")
        logger.info("2. Ejecuta el bookmarklet 'Enhanced Instagram Unfollowers'")
        logger.info("3. El script continuara automaticamente\n")
        
        try:
            # Esperar hasta 3 minutos por el bookmarklet
            await self.page.wait_for_selector('label.result-item', timeout=180000)
            logger.info("[OK] Bookmarklet detectado!")
            
            # Esperar un momento para que cargue
            await self.random_delay(2)
            
            # Verificar si existe progressbar (solo aparece con muchos usuarios)
            progress = await self.page.query_selector('progress.progressbar')
            
            if not progress:
                # No hay progressbar = pocos usuarios, continuar inmediatamente
                logger.info("[OK] Cuenta pequena detectada (sin progressbar). Iniciando desfollow...\n")
                return True
            
            # Si hay progressbar, esperar a que termine
            logger.info("[LOADING] Esperando a que termine de cargar usuarios...")
            
            # Esperar hasta 5 minutos a que complete
            last_reported = -1  # Rastrear último porcentaje reportado
            for _ in range(300):  # 300 segundos = 5 minutos
                try:
                    progress = await self.page.query_selector('progress.progressbar')
                    if progress:
                        value = await progress.get_attribute('value')
                        max_val = await progress.get_attribute('max')
                        
                        if value and max_val:
                            current = float(value)
                            maximum = float(max_val)
                            percentage = int((current / maximum) * 100)
                            
                            # Mostrar progreso solo si cambió y es múltiplo de 5
                            if percentage % 5 == 0 and percentage != last_reported:
                                logger.info(f"[PROGRESS] Cargando... {percentage}%")
                                last_reported = percentage
                            
                            # Si llega a 100% o muy cerca (95%+), continuar
                            if percentage >= 95:
                                logger.info("[OK] Carga completa! Iniciando desfollow...\n")
                                await self.random_delay(2)
                                return True
                except:
                    pass
                
                await asyncio.sleep(1)
            
            # Si pasa el timeout, continuar de todas formas
            logger.warning("[TIMEOUT] Progreso no llego a 100%, continuando de todas formas...")
            return True
            
        except:
            logger.error("[ERROR] Timeout - Bookmarklet no detectado en 3 minutos")
            return False

    async def run(self, max_unfollows: int = None):
        """Ejecuta el script"""
        try:
            await self.init_browser()
            
            # Ir a Instagram y esperar login manual
            await self.page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            await self.random_delay(2)
            
            # Verificar si necesita 2FA
            await self.handle_2fa()
            
            # Ahora esperar a que el usuario navegue y ejecute el bookmarklet
            if not await self.wait_for_bookmarklet():
                return
            
            page_num = 1
            should_continue = True
            
            while should_continue and (max_unfollows is None or self.stats["unfollowed"] < max_unfollows):
                logger.info(f"\n{'='*60}")
                logger.info(f"[PAGINA {page_num}]")
                logger.info(f"{'='*60}")
                
                unfollowers = await self.get_unfollowers_from_page()
                
                if not unfollowers:
                    break
                
                self.stats["pages"] += 1
                
                for i, username in enumerate(unfollowers, 1):
                    if max_unfollows and self.stats["unfollowed"] >= max_unfollows:
                        should_continue = False
                        break
                    
                    self.stats["total"] += 1
                    print(f"[{i}/{len(unfollowers)}] Procesando @{username}...", end=" ", flush=True)
                    
                    success = await self.unfollow_user(username)
                    if success:
                        self.stats["unfollowed"] += 1
                        print("[OK]")
                    else:
                        self.stats["failed"] += 1
                        print("[FAIL]")
                    
                    await self.random_delay(self.delays["action"], variance=0.6)
                
                if should_continue:
                    logger.info("")
                    should_continue = await self.handle_pagination()
                    page_num += 1
        
        except KeyboardInterrupt:
            logger.info("\n[CANCEL] Cancelado por usuario")
        except Exception as e:
            logger.error(f"[ERROR] {e}")
        finally:
            await self.close()
            self.print_stats()

    async def close(self):
        """Cierra navegador"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
                await self.playwright.stop()
            logger.info("Navegador cerrado")
        except Exception as e:
            # Ignorar errores si el navegador ya fue cerrado manualmente
            logger.info("Navegador ya estaba cerrado")

    def print_stats(self):
        """Muestra estadisticas finales"""
        logger.info(f"\n{'='*60}")
        logger.info("[ESTADISTICAS]")
        logger.info(f"{'='*60}")
        logger.info(f"Paginas procesadas: {self.stats['pages']}")
        logger.info(f"Total usuarios: {self.stats['total']}")
        logger.info(f"Desfollowados: {self.stats['unfollowed']}")
        logger.info(f"Fallos: {self.stats['failed']}")
        logger.info(f"{'='*60}\n")


async def main():
    # CONFIGURACIÓN
    SPEED = "balanced"        # "fast", "balanced" o "safe"
    HEADLESS = False          # True = sin ventana visible
    MAX_UNFOLLOWS = None      # None = sin límite
    
    unfollower = InstagramAutoUnfollower(headless=HEADLESS, speed=SPEED)
    
    try:
        await unfollower.run(max_unfollows=MAX_UNFOLLOWS)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())
