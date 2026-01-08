# Instalación y Configuración

## Instalación Rápida (30 segundos)

```bash
pip install playwright
python -m playwright install chromium
python auto_unfollower.py
```

## Instalación Paso a Paso

### 1. Requisitos
- Python 3.8+
- Pip (gestor de paquetes de Python)

### 2. Instalar dependencias
```bash
pip install playwright
```

### 3. Instalar navegador Chromium
```bash
python -m playwright install chromium
```

### 4. Ejecutar
```bash
python auto_unfollower.py
```

## Configuración

Abre `auto_unfollower.py` y busca la línea ~380:

```python
SPEED = "balanced"        # Velocidad: "fast", "balanced", "safe"
HEADLESS = False          # Mostrar ventana: False (sí), True (no)
MAX_UNFOLLOWS = None      # Límite: None (sin límite), o número (ej: 50)
```

## Velocidades

- **fast**: 0.8s entre clicks → 4-6 min por 100 usuarios (⚠️ riesgo)
- **balanced**: 1.2s entre clicks → 8-12 min por 100 usuarios (✅ recomendado)
- **safe**: 1.8s entre clicks → 15-20 min por 100 usuarios (🛡️ seguro)

## Problemas de Instalación

### Error: "Microsoft Visual C++ 14.0 or greater required"
**Solución**: Usa pip directamente en lugar de requirements.txt:
```bash
pip install playwright
```

### Error: "playwright: command not found"
**Solución**: Instala Chromium:
```bash
python -m playwright install chromium
```

### Puerto ocupado
**Solución**: El script usa puertos internos de Playwright, normalmente sin conflictos.

## Verificar Instalación

```bash
python -m py_compile auto_unfollower.py
```

Si no hay errores, está listo.
