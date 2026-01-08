# 🚀 Enhanced Instagram Auto-Unfollower v2.0

Script ultra-optimizado para dejar de seguir automáticamente a usuarios que no te siguen en Instagram.

**Funciona directamente con el bookmarklet de Enhanced Instagram Unfollowers**

## ⚡ Características

✅ **Super rápido** - Optimizado para velocidad máxima  
✅ **Automático** - Detecta y procesa el bookmarklet automáticamente  
✅ **Seguro** - Simula comportamiento humano  
✅ **Paginación automática** - Cambia de página sin intervención  
✅ **Logging completo** - Seguimiento detallado en consola y archivo  
✅ **Robusto** - Manejo inteligente de errores  

## 📦 Instalación

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Listo para usar
No necesitas configurar credenciales. El script funciona directamente con el bookmarklet.

## 🎯 Cómo usar

### Paso 1: Inicia el script
```bash
python auto_unfollower.py
```

### Paso 2: El script te guiará
```
============================================================
⏳ ESPERANDO INSTRUCCIÓN...
============================================================

1. Abre Instagram (www.instagram.com)
2. Ve a tu perfil → Siguiendo
3. Ejecuta el bookmarklet (Enhanced Instagram Unfollowers)
4. El script detectará automáticamente la página
```

### Paso 3: Relájate
El script:
- ✓ Detecta automáticamente la página del bookmarklet
- ✓ Extrae la lista de unfollowers
- ✓ Va usuario por usuario desfollowando
- ✓ Cambia de página automáticamente
- ✓ Maneja errores sin fallar

## ⚙️ Configuración

Abre `auto_unfollower.py` y edita estas líneas (aprox. línea 315):

```python
SPEED = "balanced"    # "fast", "balanced" o "safe"
HEADLESS = False      # True = sin ventana visible (más rápido)
MAX_UNFOLLOWS = None  # None = sin límite, o número (ej: 50)
```

## 🏃 Niveles de velocidad

| Nivel | Delay | Uso |
|-------|-------|-----|
| **fast** | 0.2-1s | Máxima velocidad (riesgo de bloqueo) |
| **balanced** | 0.5-1.5s | ⭐ Recomendado - Balance perfecto |
| **safe** | 1-2.5s | Muy lento pero muy seguro |

```python
SPEED = "fast"      # Para ir rápido
SPEED = "balanced"  # Recomendado
SPEED = "safe"      # Si Instagram bloquea
```

## 👁️ Modos de ejecución

### Modo visible (ver el navegador)
```python
HEADLESS = False
```
Más lento pero puedes ver qué está pasando.

### Modo oculto (background)
```python
HEADLESS = True
```
50% más rápido pero sin ventana visible.

## 🎛️ Límites de unfollows

```python
MAX_UNFOLLOWS = None    # Sin límite
MAX_UNFOLLOWS = 50      # Máximo 50 unfollows
MAX_UNFOLLOWS = 100     # Máximo 100 unfollows
```

## 📊 Logging

El script registra TODO:
- **Consola**: Progreso en tiempo real
- **unfollower.log**: Historial completo (se crea automáticamente)

```bash
# Ver el log en tiempo real
tail -f unfollower.log

# En Windows (PowerShell)
Get-Content unfollower.log -Wait
```

## ⚠️ Consideraciones importantes

### Instagram puede bloquear si:
- Haces demasiadas acciones muy rápido (usa "balanced" o "safe")
- Haces múltiples unfollows en poco tiempo
- Tienes patrones sospechosos

### Recomendaciones:
1. **Primera vez**: Usa "balanced" (velocidad intermedia)
2. **Si Instagram bloquea**: Cambia a "safe"
3. **Si es muy lento**: Cambia a "fast"
4. **Haz pausas**: Si vas a dejar de seguir 1000 usuarios, divide en sesiones
5. **Activa 2FA**: Es una buena práctica de seguridad

## 🚨 Solución de problemas

### Script no detecta la página
- Asegúrate de que ejecutaste el bookmarklet
- Espera a que la página cargue completamente
- Verifica que estés en la página correcta (debe tener usuarios listados)

### Muy lento
- Usa `SPEED = "fast"`
- Usa `HEADLESS = True`

### Instagram está bloqueando
- Usa `SPEED = "safe"`
- Aumenta los delays manualmente
- Haz sesiones más cortas con pausas

### Error: "Element not found"
- Instagram cambió su estructura HTML
- Reporta el error en el log
- Puede requerir actualización del script

## 🔒 Seguridad

✅ **No necesita credenciales** - Funciona con tu sesión ya activa  
✅ **No instala extensiones** - Solo abre un navegador normal  
✅ **No modifica tu cuenta** - Solo hace clicks como un humano  
✅ **Logs locales** - Todo se guarda en tu computadora  

## 📈 Velocidad esperada

| Scenario | Velocidad |
|----------|-----------|
| 100 unfollows (balanced) | ~8-12 minutos |
| 100 unfollows (fast) | ~4-6 minutos |
| 100 unfollows (safe) | ~15-20 minutos |
| 500+ unfollows | Recomendado en sesiones |

*La velocidad depende de tu conexión y de Instagram*

## 🛑 Detener el script

Presiona `Ctrl+C` en la terminal en cualquier momento. El script mostrará estadísticas finales.

## 📞 Troubleshooting avanzado

### Ver detalles de ejecución
En `auto_unfollower.py`, línea 17:
```python
logging.basicConfig(
    level=logging.DEBUG  # Cambia a DEBUG para más detalles
)
```

### Ajustar delays manualmente
En `auto_unfollower.py`, línea 34-39:
```python
self.speed_config = {
    "fast": {"click_delay": 0.2, "scroll_delay": 0.1, "page_delay": 1, "action_delay": 0.5},
    "mi_velocidad": {"click_delay": 1.0, "scroll_delay": 0.5, "page_delay": 2, "action_delay": 1.5},
}
```

## 📝 Notas

- El script respeta los checkboxes del bookmarklet (si seleccionas usuarios específicos)
- Funciona con perfiles privados y públicos
- Detecta automáticamente múltiples páginas
- Compatible con Windows, macOS y Linux

---

**Versión**: 2.0  
**Última actualización**: Enero 2026  
**Estado**: Estable ✓
