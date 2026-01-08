# Auto Unfollower - Instagram

Script automatizado para dejar de seguir usuarios que no te siguen, usando el bookmarklet "Enhanced Instagram Unfollowers".

**Bookmarklet oficial**: https://instagram.dcastillo.dev/

## Características

- ✅ Automatiza desfollow de no-seguidores
- ✅ Soporte 2FA (autenticación de dos factores)
- ✅ Comportamiento humanizado (evita bloqueos)
- ✅ 3 velocidades configurables (fast/balanced/safe)
- ✅ Detección automática de páginas
- ✅ Compatible con cuentas pequeñas y grandes
- ✅ Soporte español/inglés

## Instalación

```bash
pip install playwright
python -m playwright install chromium
```

## Uso Rápido

```bash
python auto_unfollower.py
```

1. Inicia sesión en Instagram (si es necesario)
2. Ve a Perfil → Siguiendo
3. Ejecuta el bookmarklet "Enhanced Instagram Unfollowers" desde https://instagram.dcastillo.dev/
4. El script comienza automáticamente

Ver [USAGE.md](USAGE.md) para guía completa.

## Configuración

Edita `auto_unfollower.py` línea ~380:

```python
SPEED = "balanced"        # fast, balanced, safe
HEADLESS = False          # True = sin ventana, False = con ventana
MAX_UNFOLLOWS = None      # None = sin límite
```

| Modo | Delay | Tiempo |
|------|-------|--------|
| fast | 0.8s | 4-6 min |
| balanced | 1.2s | 8-12 min |
| safe | 1.8s | 15-20 min |

**Recomendado**: "balanced" para evitar bloqueos.

## 2FA

Si tienes autenticación de dos factores:
1. El script pausará automáticamente
2. Ingresa el código que recibas
3. Presiona Enter para continuar

## Documentación

- [SETUP.md](SETUP.md) - Instalación y troubleshooting
- [USAGE.md](USAGE.md) - Guía de uso detallada

## Advertencia

Instagram puede limitar tu cuenta si desigues muchos usuarios muy rápido. Usa "balanced" o "safe" mode.

---

**Versión**: 2.1 | **Estado**: Estable ✅
