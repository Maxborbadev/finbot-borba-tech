Clear-Host

# -------------------------------------------------
# AMBIENTE
# -------------------------------------------------
$env:ENV="development"

Write-Host "Ambiente: $env:ENV"
Write-Host ""

Write-Host "======================================"
Write-Host "   BACKEND (SEM WHATSAPP)"
Write-Host "======================================"
Write-Host ""

# -------------------------------------------------
# BASE DO PROJETO
# -------------------------------------------------
$base = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "$base\venv\Scripts\python.exe"

if (!(Test-Path $python)) {
    Write-Host "ERRO: Python do venv nao encontrado:" -ForegroundColor Red
    Write-Host $python -ForegroundColor Yellow
    Pause
    exit
}

Write-Host "Python encontrado em:"
Write-Host $python
Write-Host ""

# -------------------------------------------------
# CAMINHOS
# -------------------------------------------------
$backendPath = Join-Path $base "backend"
$adminPath   = Join-Path $backendPath "admin_painel"

if (!(Test-Path $backendPath)) {
    Write-Host "ERRO: pasta backend nao encontrada" -ForegroundColor Red
    Pause
    exit
}

if (!(Test-Path $adminPath)) {
    Write-Host "ERRO: pasta admin_painel nao encontrada" -ForegroundColor Red
    Pause
    exit
}

# =================================================
# 1️⃣ BACKEND (COM DEBUG/RELOAD)
# =================================================
Write-Host "[1/3] Iniciando Backend..."

Start-Process $python `
    -ArgumentList "app.py" `
    -WorkingDirectory $backendPath `
    -NoNewWindow

Start-Sleep -Seconds 3

# =================================================
# 2️⃣ PAINEL ADMIN
# =================================================
Write-Host "[2/3] Iniciando Painel Administrativo..."

Start-Process $python `
    -ArgumentList "-m admin_painel.app" `
    -WorkingDirectory $backendPath `
    -NoNewWindow

Start-Sleep -Seconds 3

# =================================================
# 3️⃣ SCHEDULER
# =================================================
Write-Host "[3/3] Iniciando Scheduler..."

Start-Process $python `
    -ArgumentList "scheduler.py" `
    -WorkingDirectory $backendPath `
    -NoNewWindow

Write-Host ""
Write-Host "======================================"
Write-Host "   BACKEND RODANDO"
Write-Host "======================================"
Write-Host ""
Write-Host "API:           http://127.0.0.1:5000"
Write-Host "Painel Admin:  http://127.0.0.1:5001"
Write-Host ""
Write-Host "WhatsApp: OFF"
Write-Host ""

Write-Host "Dica:"
Write-Host "- Backend já reinicia sozinho (debug=True)"
Write-Host "- Painel precisa restart manual se alterar"
Write-Host ""

Write-Host "CTRL + C para encerrar"
Write-Host ""

while ($true) {
    Start-Sleep -Seconds 5
}