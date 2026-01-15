# Guía de Uso

## Paso 1: Preparación

Asegúrate de tener instalado:
```bash
pip install playwright
python -m playwright install chromium
```

## Paso 2: Ejecutar el Script

```bash
python auto_unfollower.py
```

Se abrirá una ventana de Chrome automáticamente.

## Paso 3: Inicia Sesión (si es necesario)

Si no estás logeado, Instagram te pedirá:
- Email/usuario
- Contraseña
- **Si tienes 2FA**: El script pausará automáticamente y te pedirá el código

Tu sesión queda guardada en `./user_data`, por lo que en próximas ejecuciones normalmente no tendrás que volver a iniciar sesión.

## Paso 4: Ejecutar el Bookmarklet

1. En la ventana de Chrome, ve a: **Perfil → Siguiendo**
2. Ejecuta el bookmarklet **"Enhanced Instagram Unfollowers"**
   - Si no lo tienes instalado, ve a [instagram.dcastillo.dev](https://instagram.dcastillo.dev/) y sigue las instrucciones
3. Verás una lista de usuarios que no te siguen

## Paso 5: El Script Continúa Automáticamente

El script:
- ✅ Detectará que el bookmarklet se ejecutó
- ✅ Mostrará un indicador de carga (si hay muchos usuarios)
- ✅ Comenzará a dejar de seguir automáticamente
- ✅ Navegará entre páginas automáticamente

## Durante la Ejecución

Verás logs como:
```
[1/50] Procesando @usuario... [OK]
[2/50] Procesando @usuario2... [OK]
[NEXT] Siguiente pagina
[PAGE] 5/19
```

## Cuando Termina

Mostrará un resumen:
```
Paginas procesadas: 19
Total usuarios: 380
Desfollowados: 350
Fallos: 30
```

## Cancelar en Cualquier Momento

Presiona `Ctrl + C` en la terminal para detener.

## Configuración Avanzada

Ver [SETUP.md](SETUP.md) para opciones de velocidad y límites.

### Whitelist persistente

Se crea automáticamente `whitelist.txt` en la carpeta del proyecto. Escribe allí, uno por línea, los usuarios que deban ser omitidos (no se les hará unfollow).

## 2FA (Autenticación de Dos Factores)

Si tienes 2FA habilitado:

1. Cuando intra al script, te pedirá ingresar el código
2. Abre tu app de autenticación (Google Authenticator, Authy, etc.)
3. Copia el código de 6 dígitos
4. Pégalo en la terminal y presiona Enter

El script continuará automáticamente después.

## Troubleshooting

| Problema | Solución |
|----------|----------|
| No detecta usuarios | Asegúrate de ejecutar el bookmarklet en "Siguiendo" |
| Muy lento | Cambia SPEED a "fast" en auto_unfollower.py |
| Instagram me bloquea | Usa SPEED = "safe" y espera 1-2 horas antes de reintentar |
| Ventana se cierra | Es normal, significa que terminó |

## Notas Importantes

⚠️ **Instagram puede limitar temporalmente tu cuenta** si:
- Desigues muchos usuarios muy rápido
- Usas "fast" mode constantemente
- Lo repites varias veces en el mismo día

**Recomendación**: Usa "balanced" y haz descansos entre ejecuciones.
