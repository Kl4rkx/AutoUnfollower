# ⚡ INICIO RÁPIDO

## 3 Pasos

```bash
# 1. Instalar
pip install -r requirements.txt
playwright install chromium

# 2. Ejecutar
python auto_unfollower.py

# 3. Seguir instrucciones
```

## Configuración

Edita `auto_unfollower.py` línea 250:

```python
SPEED = "balanced"      # fast, balanced, safe
HEADLESS = False        # True = sin ventana
MAX_UNFOLLOWS = None    # Número o None
```

## Velocidades

- **fast**: 4-6 min (riesgoso)
- **balanced**: 8-12 min (recomendado)
- **safe**: 15-20 min (conservador)

## Con 2FA

Si Instagram pide código:
1. El script te lo pedirá
2. Ingresa el código recibido
3. Continuará automáticamente

---

**Listo para usar**: `python auto_unfollower.py`
