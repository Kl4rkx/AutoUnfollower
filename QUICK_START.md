## 🚀 GUÍA RÁPIDA - Enhanced Instagram Auto-Unfollower

### ⏱️ 30 SEGUNDOS PARA EMPEZAR

```bash
# 1. Abre terminal/PowerShell en la carpeta del proyecto
# 2. Instala dependencias (solo la primera vez)
pip install -r requirements.txt
playwright install chromium

# 3. Inicia el script
python auto_unfollower.py
```

### 📋 LO QUE HACE EL SCRIPT

1. Se abre un navegador Chrome
2. Espera a que ejecutes el bookmarklet en Instagram
3. Detecta automáticamente la lista de unfollowers
4. Va uno por uno desfollowando
5. Cambia de página automáticamente
6. Genera un log con todo lo que hizo

### ⚡ VELOCIDADES RÁPIDAS

**Si quieres ir MÁS RÁPIDO** (edita `auto_unfollower.py` línea ~318):
```python
SPEED = "fast"      # Muy rápido (~4-6 min para 100 usuarios)
HEADLESS = True     # Sin ver el navegador
```

**Si quieres ir MÁS LENTO** (más seguro):
```python
SPEED = "safe"      # Muy lento pero seguro (~15-20 min)
```

### 🛑 DETENER EN CUALQUIER MOMENTO

Presiona `Ctrl+C` en la terminal.

### 📊 VER RESULTADOS

```bash
# En PowerShell, ver el log en tiempo real
Get-Content unfollower.log -Wait

# En CMD
type unfollower.log
```

### ⚠️ SI INSTAGRAM BLOQUEA

1. Cambia `SPEED = "safe"`
2. Espera 1-2 horas
3. Intenta de nuevo con velocidad "safe"

### ✅ CHECKLIST

- [ ] Instalé `pip install -r requirements.txt`
- [ ] Instalé `playwright install chromium`
- [ ] Estoy logueado en Instagram
- [ ] Tengo lista la URL del bookmarklet
- [ ] Ejecuté `python auto_unfollower.py`
- [ ] Ejecuté el bookmarklet cuando el script lo pidió
- [ ] ¡Relájate y espera!

---

**¿Problemas?** Ver README.md para troubleshooting completo.
