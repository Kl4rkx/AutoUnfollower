# Script para iniciar Auto-Unfollower en PowerShell

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     ENHANCED INSTAGRAM AUTO-UNFOLLOWER v2.0" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si playwright está instalado
try {
    python -c "import playwright" 2>&1 | Out-Null
} catch {
    Write-Host "[!] Instalando dependencias..." -ForegroundColor Yellow
    pip install -r requirements.txt
    playwright install chromium
    Write-Host "[OK] Dependencias instaladas" -ForegroundColor Green
    Write-Host ""
}

# Iniciar el script
Write-Host "[+] Iniciando script..." -ForegroundColor Green
Write-Host ""
python auto_unfollower.py

Read-Host "Presiona Enter para salir"
