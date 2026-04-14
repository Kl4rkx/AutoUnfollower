"""
Enhanced Instagram Auto-Unfollower v3.0
Script ultra-rápido para dejar de seguir usuarios
Incluye: Unfollow normal + Cancelar solicitudes pendientes
Soporta 2FA - Comportamiento humanizado - Sin bloqueos
"""

import asyncio
import random
import sys
import os
import re
from pathlib import Path
from typing import List, Optional, Set, Tuple
from playwright.async_api import async_playwright, Page, BrowserContext
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


# ============================================================
# UTILIDADES PARA PARSEAR HTML DE SOLICITUDES PENDIENTES
# ============================================================

def parse_pending_requests_html(html_path: Path) -> List[str]:
    """
    Parsea el archivo HTML exportado de Instagram para extraer
    los enlaces de perfiles con solicitudes pendientes.
    No requiere BeautifulSoup - usa regex simple.
    """
    if not html_path.exists():
        logger.error(f"[ERROR] No se encontró el archivo: {html_path}")
        return []
    
    try:
        content = html_path.read_text(encoding='utf-8')
        
        # Buscar todos los enlaces de Instagram
        # Patrón: href="https://www.instagram.com/username" o similar
        pattern = r'href="(https?://(?:www\.)?instagram\.com/([^/"]+))"'
        matches = re.findall(pattern, content)
        
        # Extraer usernames únicos (evitar duplicados)
        usernames = []
        seen = set()
        
        for full_url, username in matches:
            # Filtrar enlaces que no son perfiles (como /p/, /reel/, etc.)
            if username and username not in seen:
                # Excluir rutas especiales de Instagram
                if username not in ['p', 'reel', 'stories', 'explore', 'accounts', 'direct', 'tv']:
                    usernames.append(username)
                    seen.add(username)
        
        return usernames
    
    except Exception as e:
        logger.error(f"[ERROR] Error al parsear HTML: {e}")
        return []


class InstagramAutoUnfollower:
    def __init__(self, headless: bool = False, speed: str = "balanced", user_data_dir: Optional[str] = None, whitelist_path: Optional[str] = None):
        self.headless = headless
        self.window_width = 1920
        self.window_height = 1080
        # Delays más realistas para evitar bloqueos
        self.speed_config = {
            "fast": {"click": 0.8, "scroll": 0.3, "page": 2, "action": 1.5},
            "balanced": {"click": 1.2, "scroll": 0.5, "page": 3, "action": 2},
            "safe": {"click": 1.8, "scroll": 0.7, "page": 4, "action": 3}
        }
        self.delays = self.speed_config.get(speed, self.speed_config["balanced"])
        self.stats = {"total": 0, "unfollowed": 0, "failed": 0, "pages": 0, "pending_cancelled": 0}
        self.page: Optional[Page] = None
        self.worker_page: Optional[Page] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
        # Directorio de perfil persistente (evita re-login)
        base_dir = Path(user_data_dir) if user_data_dir else Path.cwd() / "user_data"
        self.user_data_dir: Path = base_dir
        # Ruta de whitelist
        self.whitelist_path: Path = Path(whitelist_path) if whitelist_path else (Path.cwd() / "whitelist.txt")
        # Ruta del archivo de solicitudes pendientes
        self.pending_requests_path: Path = Path.cwd() / "pending_follow_requests.html"
        self.whitelist: Set[str] = set()
        self._ensure_dirs()
        self._load_whitelist()

    async def random_delay(self, base_delay: float, variance: float = 0.4):
        """Delay humanizado con varianza"""
        variation = base_delay * variance
        delay = base_delay + random.uniform(-variation, variation)
        await asyncio.sleep(max(delay, 0.1))

    async def init_browser(self):
        """Inicializa navegador con perfil persistente y anti-detección de bots"""
        self.playwright = await async_playwright().start()

        # Usar contexto persistente para guardar sesión (cookies/localStorage)
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
            args=[
                f"--window-size={self.window_width},{self.window_height}",
                "--force-device-scale-factor=1",
                "--high-dpi-support=1",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-notifications",
            ],
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        self.page = await self.context.new_page()

        # Anti-detección de automatización
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
        """)

        logger.info(f"[OK] Navegador iniciado (perfil: {self.user_data_dir})")

    async def _get_worker_page(self) -> Page:
        """Reutiliza una sola pestaña para acciones de perfil y evita abrir/cerrar pestañas por usuario."""
        if self.worker_page and not self.worker_page.is_closed():
            return self.worker_page

        self.worker_page = await self.context.new_page()
        await self.worker_page.goto("about:blank", wait_until="domcontentloaded")
        return self.worker_page

    def _ensure_dirs(self):
        try:
            self.user_data_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def _load_whitelist(self):
        """Carga/crea whitelist.txt y guarda en memoria (en minúsculas)."""
        wl: Set[str] = set()
        if not self.whitelist_path.exists():
            try:
                default = (
                    "# Lista blanca de usuarios (uno por línea)\n"
                    "# Cualquier nombre aquí NO será desfolloweado.\n"
                    "# Ejemplo:\n"
                    "# elonmusk\n# nasa\n"
                )
                self.whitelist_path.write_text(default, encoding="utf-8")
                logger.info(f"[OK] Creada whitelist en {self.whitelist_path}")
            except Exception:
                pass
        else:
            try:
                for line in self.whitelist_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    wl.add(line.lower())
            except Exception:
                pass
        self.whitelist = wl

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
        try:
            profile_page = await self._get_worker_page()
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

    async def cancel_pending_request(self, username: str) -> bool:
        """Cancela una solicitud de seguimiento pendiente"""
        try:
            profile_page = await self._get_worker_page()
            await profile_page.goto(f"https://www.instagram.com/{username}/", wait_until="domcontentloaded", timeout=10000)
            await self.random_delay(self.delays["action"])
            
            # Buscar botón "Solicitado", "Pendiente", "Requested" o "Cancel Request"
            # El botón puede tener diferentes textos dependiendo del idioma
            pending_btn = profile_page.locator(
                'button:has-text("Solicitado"), '
                'button:has-text("Pendiente"), '
                'button:has-text("Requested"), '
                'button:has-text("Solicitud enviada"), '
                'button:has(div:has-text("Solicitado")), '
                'button:has(div:has-text("Requested")), '
                'button:has(div:has-text("Pendiente"))'
            ).first
            
            if await pending_btn.is_visible(timeout=3000):
                await pending_btn.scroll_into_view_if_needed()
                await self.random_delay(self.delays["click"])
                await pending_btn.click()
                await self.random_delay(self.delays["click"])
                
                # Buscar opción "Dejar de seguir" o "Cancel request" en el menú
                try:
                    cancel_confirm = profile_page.locator(
                        'button:has-text("Dejar de seguir"), '
                        'button:has-text("Unfollow"), '
                        'button:has-text("Cancelar"), '
                        'button:has-text("Cancel"), '
                        'span:text-is("Dejar de seguir"), '
                        'span:text-is("Unfollow"), '
                        'span:text-is("Cancelar")'
                    ).first
                    
                    if await cancel_confirm.is_visible(timeout=2000):
                        await cancel_confirm.click()
                        await self.random_delay(2)
                        
                        # Verificar que el botón cambió a "Seguir" o "Follow"
                        try:
                            await profile_page.wait_for_selector(
                                'button:has-text("Seguir"), button:has-text("Follow"), '
                                'button:has(div:has-text("Seguir")), button:has(div:has-text("Follow"))',
                                timeout=8000
                            )
                            logger.info(f"[CANCELADA] @{username}")
                            await self.random_delay(1)
                            return True
                        except:
                            logger.warning(f"[SKIP] @{username} - No cambió a 'Seguir'")
                            return False
                except:
                    pass
            
            # Verificar si el usuario ya no tiene solicitud pendiente (ya sigue o fue rechazado)
            follow_btn = profile_page.locator(
                'button:has-text("Seguir"), button:has-text("Follow")'
            ).first
            
            if await follow_btn.is_visible(timeout=1000):
                logger.info(f"[YA CANCELADA] @{username} - No había solicitud pendiente")
                return True
            
            # Verificar si ya lo sigues (botón "Siguiendo")
            following_btn = profile_page.locator(
                'button:has-text("Siguiendo"), button:has-text("Following")'
            ).first
            
            if await following_btn.is_visible(timeout=1000):
                logger.info(f"[YA SIGUE] @{username} - La solicitud fue aceptada")
                return True
            
            logger.warning(f"[SKIP] @{username} - No se encontró botón pendiente")
            return False
        
        except asyncio.TimeoutError:
            logger.warning(f"[TIMEOUT] @{username}")
            return False
        except Exception as e:
            logger.error(f"[FAIL] @{username}: {e}")
            return False

    async def run_cancel_pending_requests(self, max_cancels: int = None):
        """Ejecuta la cancelación de solicitudes pendientes desde el archivo HTML"""
        try:
            await self.init_browser()
            
            # Verificar que existe el archivo HTML
            if not self.pending_requests_path.exists():
                logger.error(f"\n[ERROR] No se encontró el archivo: {self.pending_requests_path}")
                logger.info("\nPara usar esta opción:")
                logger.info("1. Ve a Instagram > Configuración > Tu actividad > Datos de Instagram")
                logger.info("2. Descarga tus datos en formato HTML")
                logger.info("3. Busca el archivo 'pending_follow_requests.html'")
                logger.info("4. Cópialo a la carpeta del script")
                return
            
            # Parsear el archivo HTML
            usernames = parse_pending_requests_html(self.pending_requests_path)
            
            if not usernames:
                logger.error("[ERROR] No se encontraron solicitudes pendientes en el archivo HTML")
                return
            
            logger.info(f"\n[OK] Se encontraron {len(usernames)} solicitudes pendientes")
            
            # Aplicar whitelist
            if self.whitelist:
                before = len(usernames)
                usernames = [u for u in usernames if u.lower() not in self.whitelist]
                skipped = before - len(usernames)
                if skipped > 0:
                    logger.info(f"[WHITELIST] {skipped} usuarios omitidos por whitelist")
            
            # Ir a Instagram y esperar login manual
            await self.page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            await self.random_delay(2)
            
            # Verificar si necesita 2FA
            await self.handle_2fa()
            
            # Verificar si está logueado
            logger.info("\n" + "="*60)
            logger.info("[VERIFICANDO LOGIN]")
            logger.info("="*60)
            logger.info("\nAsegúrate de estar logueado en Instagram.")
            logger.info("Presiona Enter cuando estés listo para continuar...")
            input()
            
            logger.info(f"\n[INICIANDO] Cancelando {len(usernames)} solicitudes pendientes...\n")
            
            for i, username in enumerate(usernames, 1):
                if max_cancels and self.stats["pending_cancelled"] >= max_cancels:
                    logger.info(f"\n[LIMITE] Alcanzado el límite de {max_cancels} cancelaciones")
                    break
                
                self.stats["total"] += 1
                print(f"[{i}/{len(usernames)}] Procesando @{username}...", end=" ", flush=True)
                
                success = await self.cancel_pending_request(username)
                if success:
                    self.stats["pending_cancelled"] += 1
                    print("[OK]")
                else:
                    self.stats["failed"] += 1
                    print("[FAIL]")
                
                await self.random_delay(self.delays["action"], variance=0.6)
        
        except KeyboardInterrupt:
            logger.info("\n[CANCEL] Cancelado por usuario")
        except Exception as e:
            logger.error(f"[ERROR] {e}")
        finally:
            await self.close()
            self.print_stats_pending()

    def print_stats_pending(self):
        """Muestra estadísticas de cancelación de solicitudes pendientes"""
        logger.info(f"\n{'='*60}")
        logger.info("[ESTADÍSTICAS - SOLICITUDES PENDIENTES]")
        logger.info(f"{'='*60}")
        logger.info(f"Total procesadas: {self.stats['total']}")
        logger.info(f"Canceladas: {self.stats['pending_cancelled']}")
        logger.info(f"Fallos: {self.stats['failed']}")
        logger.info(f"{'='*60}\n")

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
                # Aplicar whitelist si existe
                if self.whitelist:
                    before = len(unfollowers)
                    unfollowers = [u for u in unfollowers if u.lower() not in self.whitelist]
                    skipped = before - len(unfollowers)
                    if skipped > 0:
                        logger.info(f"[WHITELIST] {skipped} usuarios omitidos por whitelist")
                
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
            if self.worker_page and not self.worker_page.is_closed():
                await self.worker_page.close()
            if self.context:
                await self.context.close()
            if self.playwright:
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


def show_menu() -> int:
    """Muestra el menú principal y retorna la opción seleccionada"""
    print("\n" + "="*60)
    print("   INSTAGRAM AUTO-UNFOLLOWER v3.0")
    print("="*60)
    print("\n¿Qué deseas hacer?\n")
    print("  [1] Dejar de seguir usuarios (con bookmarklet)")
    print("      → Usa el bookmarklet para detectar quién no te sigue")
    print()
    print("  [2] Cancelar solicitudes de seguimiento pendientes")
    print("      → Cancela solicitudes enviadas desde archivo HTML")
    print()
    print("  [3] Salir")
    print()
    print("="*60)
    
    while True:
        try:
            choice = input("\nSelecciona una opción (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return int(choice)
            print("[ERROR] Por favor, ingresa 1, 2 o 3")
        except ValueError:
            print("[ERROR] Por favor, ingresa un número válido")
        except KeyboardInterrupt:
            return 3


def get_speed_config() -> str:
    """Permite al usuario seleccionar la velocidad"""
    print("\n" + "-"*40)
    print("Selecciona la velocidad:\n")
    print("  [1] Fast    - Rápido (más riesgo de bloqueo)")
    print("  [2] Balanced - Equilibrado (recomendado)")
    print("  [3] Safe    - Seguro (más lento, menos riesgo)")
    print("-"*40)
    
    speed_map = {'1': 'fast', '2': 'balanced', '3': 'safe'}
    
    while True:
        try:
            choice = input("\nSelecciona velocidad (1-3) [2]: ").strip() or '2'
            if choice in speed_map:
                return speed_map[choice]
            print("[ERROR] Por favor, ingresa 1, 2 o 3")
        except KeyboardInterrupt:
            return 'balanced'


def get_max_count(action_type: str) -> Optional[int]:
    """Permite al usuario establecer un límite máximo"""
    print(f"\n¿Cuántos usuarios quieres {action_type}?")
    print("  - Escribe un número para establecer un límite")
    print("  - Presiona Enter para sin límite")
    
    while True:
        try:
            value = input("\nMáximo [sin límite]: ").strip()
            if not value:
                return None
            num = int(value)
            if num > 0:
                return num
            print("[ERROR] El número debe ser mayor a 0")
        except ValueError:
            print("[ERROR] Por favor, ingresa un número válido")
        except KeyboardInterrupt:
            return None


async def main():
    """Función principal con menú interactivo"""
    
    choice = show_menu()
    
    if choice == 3:
        print("\n¡Hasta luego!")
        return
    
    # Configuración común
    speed = get_speed_config()
    headless = False  # Siempre visible para poder hacer login
    
    unfollower = InstagramAutoUnfollower(headless=headless, speed=speed)
    
    try:
        if choice == 1:
            # Opción 1: Unfollow normal con bookmarklet
            max_unfollows = get_max_count("dejar de seguir")
            print(f"\n[CONFIG] Velocidad: {speed}")
            print(f"[CONFIG] Límite: {max_unfollows if max_unfollows else 'Sin límite'}")
            print("\nIniciando...\n")
            await unfollower.run(max_unfollows=max_unfollows)
            
        elif choice == 2:
            # Opción 2: Cancelar solicitudes pendientes
            max_cancels = get_max_count("cancelar")
            print(f"\n[CONFIG] Velocidad: {speed}")
            print(f"[CONFIG] Límite: {max_cancels if max_cancels else 'Sin límite'}")
            print("\nIniciando...\n")
            await unfollower.run_cancel_pending_requests(max_cancels=max_cancels)
            
    except KeyboardInterrupt:
        print("\n\n[CANCEL] Operación cancelada por el usuario")


if __name__ == "__main__":
    asyncio.run(main())
