# 📱 Auto Unfollower para Instagram

Script automatizado ultra-rápido para dejar de seguir usuarios que no te siguen y cancelar solicitudes de seguimiento pendientes. Incluye soporte para 2FA, comportamiento humanizado y velocidades configurables.

---

## ✨ Características Principales

- ✅ **Dejar de seguir automáticamente** usuarios no-seguidores mediante bookmarklet
- ✅ **Cancelar solicitudes pendientes** desde archivo HTML exportado
- ✅ **Soporte 2FA** (autenticación de dos factores)
- ✅ **3 velocidades configurables** (Fast/Balanced/Safe) para evitar bloqueos
- ✅ **Comportamiento humanizado** con delays variables y anti-detección
- ✅ **Sesión persistente** - no necesita re-login cada vez
- ✅ **Whitelist personalizada** - protege usuarios específicos de dejar de seguir
- ✅ **Menú interactivo** - fácil de usar, solo 3 opciones
- ✅ **Registro detallado** - guarda todos los eventos en log
- ✅ **Interfaz en español/inglés**
- ✅ **Compatible con cuentas pequeñas y grandes**

**Bookmarklet oficial**: https://instagram.dcastillo.dev/

---

## 📋 Requisitos Previos

- **Windows 10 o 11** (64-bit)
- **Python 3.8 o superior** (descargable desde python.org)
- **Git** (opcional, pero recomendado)
- **Conexión a Internet**
- **Cuenta de Instagram activa**

---

## 🚀 Guía Completa de Instalación (Desde Cero)

### Paso 1: Descargar e Instalar Python

1. Abre navegador y ve a https://www.python.org/downloads/
2. Descarga **Python 3.12** (o la versión más reciente)
3. Ejecuta el instalador `.exe`
4. **⚠️ IMPORTANTE**: En la primera pantalla, marca la casilla **"Add Python to PATH"**
5. Haz clic en **"Install Now"**
6. Espera a que termine la instalación

**Verificar instalación:**
```bash
python --version
```

### Paso 2: Descargar el Proyecto

#### Opción A: Con Git (recomendado)
```bash
git clone https://github.com/tu-usuario/AutoUnfollower.git
cd AutoUnfollower
```

#### Opción B: Descarga manual (sin Git)
1. Ve a https://github.com/tu-usuario/AutoUnfollower
2. Haz clic en **"Code"** → **"Download ZIP"**
3. Extrae el archivo ZIP
4. Abre una terminal en la carpeta extraída

### Paso 3: Instalar Dependencias

Abre una terminal (PowerShell o CMD) en la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

**Esto instalará:**
- Playwright 1.40.0 (navegador automatizado)
- Chromium (navegador para automatización)

**La instalación puede tomar 2-5 minutos.**

---

## 💻 Cómo Usar el Script

### Ejecución Básica

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
python auto_unfollower.py
```

Se abrirá un menú interactivo con 3 opciones:

```
============================================================
   INSTAGRAM AUTO-UNFOLLOWER v3.0
============================================================

¿Qué deseas hacer?

  [1] Dejar de seguir usuarios (con bookmarklet)
      → Usa el bookmarklet para detectar quién no te sigue

  [2] Cancelar solicitudes de seguimiento pendientes
      → Cancela solicitudes enviadas desde archivo HTML

  [3] Salir

============================================================
```

---

## 📌 Opción 1: Dejar de Seguir Usuarios (Recomendado para Limpieza Rápida)

### ¿Qué hace?
Automatiza dejar de seguir a usuarios que **no te siguen**. Requiere usar un bookmarklet para detectarlos.

### Pasos:

1. **Ejecuta el script**:
   ```bash
   python auto_unfollower.py
   ```
   Selecciona **opción 1**

2. **Selecciona velocidad** (recomendado: **2 - Balanced**):
   ```
   [1] Fast    - Rápido (más riesgo de bloqueo)
   [2] Balanced - Equilibrado (RECOMENDADO) ✓
   [3] Safe    - Seguro (más lento, menos riesgo)
   ```

3. **Inicia sesión en Instagram** (si es la primera vez):
   - Se abrirá un navegador Chrome automáticamente
   - Inicia sesión con tu usuario y contraseña
   - Si tienes 2FA, ingresa el código que recibas

4. **Navega a tu perfil**:
   - En Instagram, ve a **Perfil** → **Siguiendo**

5. **Ejecuta el bookmarklet**:
   - Abre tu navegador y ve a: https://instagram.dcastillo.dev/
   - Haz clic en "**Enhanced Instagram Unfollowers**"
   - Espera a que procese (verás una lista roja de usuarios que no te siguen)

6. **Vuelve a la terminal**:
   - El script se activará automáticamente
   - Verás el progreso en tiempo real:
   ```
   [1/150] Procesando @usuario1... [OK]
   [2/150] Procesando @usuario2... [OK]
   ...
   ```

7. **Al terminar**, verás un resumen:
   ```
   ============================================================
   [ESTADÍSTICAS]
   ============================================================
   Paginas procesadas: 2
   Total usuarios: 150
   Desfollowados: 148
   Fallos: 2
   ============================================================
   ```

### Velocidades Disponibles

| Modo | Delay | Uso | Riesgo |
|------|-------|-----|--------|
| **Fast** | 0.8s | Cuentas pequeñas | ⚠️ Alto |
| **Balanced** | 1.2s | Mayoría de casos | ✓ Bajo |
| **Safe** | 1.8s | Cuentas grandes (5K+) | ✓ Muy bajo |

**Recomendación**: Usa "Balanced" para la mayoría de casos.

---

## 📬 Opción 2: Cancelar Solicitudes de Seguimiento Pendientes

### ¿Qué hace?
Cancela todas las solicitudes de seguimiento que hayas enviado y aún estén pendientes.

### Pasos:

#### Paso A: Descargar datos de Instagram

1. Ve a **Instagram.com** → **Menú** (☰) → **Configuración y privacidad** → **Centro de descargas**
   
   O ve directamente a: https://instagram.com/accounts/login/?next=/download/request/

2. Haz clic en **"Solicitar descarga"**

3. Selecciona:
   - Formato: **HTML** ✓
   - Rango de fechas: **Todos los datos** ✓

4. Haz clic en **"Siguiente"**

5. Instagram te enviará un email cuando los datos estén listos (puede tardar horas o días)

6. **Una vez recibas el email**:
   - Descarga el archivo ZIP
   - Extráelo
   - Busca la carpeta: `instagram-account-klark-20XX-XX-XX/`
   - Dentro, busca: `requests_sent.html` o `pending_follow_requests.html`

#### Paso B: Preparar el archivo

1. Copia el archivo HTML a la carpeta del script
2. Renómbralo como: **`pending_follow_requests.html`** (importante el nombre exacto)

#### Paso C: Ejecutar el script

1. Abre terminal en la carpeta del proyecto:
   ```bash
   python auto_unfollower.py
   ```

2. Selecciona **opción 2**

3. Elige velocidad (recomendado: **Balanced**)

4. Inicia sesión en Instagram (si es necesario)

5. **Presiona Enter** cuando estés listo

6. El script comenzará a cancelar solicitudes automáticamente:
   ```
   [OK] Se encontraron 47 solicitudes pendientes
   
   [1/47] Procesando @usuario1... [OK]
   [2/47] Procesando @usuario2... [OK]
   ...
   
   ============================================================
   [ESTADÍSTICAS - SOLICITUDES PENDIENTES]
   ============================================================
   Total procesadas: 47
   Canceladas: 45
   Fallos: 2
   ============================================================
   ```

---

## 🛡️ Whitelist: Protege Tus Cuentas Favoritas

Crea un archivo `whitelist.txt` en la carpeta del script para proteger ciertas cuentas de dejar de seguir.

### Cómo hacerlo:

1. En la carpeta del script, abre (o crea) el archivo: **`whitelist.txt`**

2. Añade los usuarios que quieres proteger, uno por línea:

```
# Lista blanca - estos usuarios NO serán desfolloveados
# (Las líneas que empiezan con # son comentarios)

elonmusk
nasa
instagram
cristiano
```

3. Guarda el archivo

4. **Listo**: Los usuarios en la whitelist nunca serán desfolloveados

**Nota**: Al ejecutar el script por primera vez, se crea automáticamente `whitelist.txt` con ejemplos.

---

## 🔐 Autenticación de Dos Factores (2FA)

Si tienes 2FA activado en tu cuenta de Instagram:

1. El script pausará automáticamente
2. Se abrirá un navegador Chrome
3. Instagram te pedirá el código (SMS, app, etc.)
4. Ingresa el código en la **terminal** cuando se te pida:
   ```
   Ingresa el codigo de autenticacion: 123456
   ```
5. Presiona **Enter**
6. El script continuará automáticamente

---

## 💾 Sesión Persistente (Sin re-login cada vez)

Cuando ejecutas el script por primera vez:
- Se crea una carpeta `user_data/` automáticamente
- Tus cookies y sesión de Instagram se guardan ahí
- **En ejecutiones futuras, NO necesitas iniciar sesión de nuevo**
- La sesión persiste hasta que Instagram cierre tu sesión (por seguridad)

### Para limpiar la sesión:
```bash
# En Windows PowerShell o CMD:
rmdir /s user_data
```

---

## 📊 Archivos del Proyecto

| Archivo | Descripción |
|---------|-------------|
| `auto_unfollower.py` | Script principal (no editar) |
| `whitelist.txt` | ✏️ Lista de usuarios protegidos (edita este) |
| `pending_follow_requests.html` | Archivo HTML con solicitudes (descarga desde Instagram) |
| `requirements.txt` | Dependencias de Python |
| `user_data/` | Carpeta con sesión guardada (auto-generada) |
| `unfollower.log` | Registro detallado de todas las acciones |

---

## 🐛 Solución de Problemas

### "Python no se reconoce"
```bash
# Asegúrate de haber marcado "Add Python to PATH" en la instalación
# Si ya instalaste, desinstala y vuelve a instalar marcando esa casilla
```

### "No se encuentra playwright"
```bash
pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
```

### "El script se abre pero no hace nada"
- Comprueba que tienes sesión iniciada en Instagram
- Intenta con velocidad "Safe" en lugar de "Fast"
- Revisa el archivo `unfollower.log` para ver errores

### "Instagram me bloqueó temporalmente"
- Esto significa que hiciste demasiadas acciones muy rápido
- Espera 24-48 horas
- Próxima vez usa velocidad **"Safe"** (más lenta)
- No ejecutes múltiples instancias del script a la vez

### "El archivo HTML no se encuentra"
- Asegúrate de que se llama exactamente: `pending_follow_requests.html`
- Verifica que está en la misma carpeta que `auto_unfollower.py`
- Comprueba que descargaste correctamente desde Instagram

### "Necesito limpiar todo y empezar de nuevo"
```bash
# En PowerShell o CMD, en la carpeta del proyecto:
rmdir /s user_data          # Elimina sesión
del unfollower.log          # Elimina logs
del whitelist.txt           # Elimina whitelist (se regenera)
```

---

## ⚙️ Configuración Avanzada

### Modificar velocidades (usuarios avanzados)

Abre `auto_unfollower.py` con un editor de texto y localiza:

```python
self.speed_config = {
    "fast": {"click": 0.8, "scroll": 0.3, "page": 2, "action": 1.5},
    "balanced": {"click": 1.2, "scroll": 0.5, "page": 3, "action": 2},
    "safe": {"click": 1.8, "scroll": 0.7, "page": 4, "action": 3}
}
```

Los números son segundos de espera. Aumenta para mayor seguridad.

---

## 📝 Registro de Actividad

Cada ejecución genera un archivo `unfollower.log` con:
- Hora exacta de cada acción
- Usuarios procesados
- Errores ocurridos
- Estadísticas finales

**Ejemplo:**
```
2024-01-15 14:23:45 - INFO - [OK] Navegador iniciado
2024-01-15 14:25:10 - INFO - [1/150] Procesando @usuario1... [OK]
2024-01-15 14:25:18 - INFO - [2/150] Procesando @usuario2... [OK]
...
```

---

## ⚡ Consejos de Seguridad

1. **Usa velocidad "Balanced" o "Safe"** para evitar bloqueos temporales
2. **Espera 24-48 horas** entre ejecuciones grandes (100+ usuarios)
3. **No ejecutes múltiples instancias** del script simultáneamente
4. **Ten whitelist actualizada** con cuentas que valoras
5. **Revisa `unfollower.log`** para detectar problemas temprano
6. **Asegúrate de estar logueado** antes de usar el bookmarklet

---

## 🤝 Soporte y Contribuciones

Si encuentras un error:
1. Revisa el archivo `unfollower.log`
2. Intenta con velocidad "Safe"
3. Limpia sesión y vuelve a intentar

---

## 📄 Licencia

Uso personal. No intentes revender ni falsificar autoría.

---

## 🎯 Próximos Pasos

1. **Descarga Python** (si aún no lo tienes)
2. **Descarga el proyecto** (Git o ZIP)
3. **Instala dependencias**: `pip install -r requirements.txt`
4. **Ejecuta**: `python auto_unfollower.py`
5. **¡Disfruta automatización responsable!**

---

**Última actualización**: Enero 2024 | v3.0
