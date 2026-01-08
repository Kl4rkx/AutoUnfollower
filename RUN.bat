@echo off
REM Script para iniciar Auto-Unfollower en Windows

echo.
echo ============================================================
echo     ENHANCED INSTAGRAM AUTO-UNFOLLOWER v2.0
echo ============================================================
echo.

REM Verificar si playwright está instalado
python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo [!] Instalando dependencias...
    pip install -r requirements.txt
    playwright install chromium
    echo [OK] Dependencias instaladas
    echo.
)

REM Iniciar el script
echo [+] Iniciando script...
echo.
python auto_unfollower.py

pause
