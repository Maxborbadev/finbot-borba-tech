Clear-Host

# -------------------------------------------------
# AMBIENTE
# -------------------------------------------------
$env:ENV="development"
Write-Host "Ambiente: $env:ENV"
Write-Host ""

Write-Host "======================================"
Write-Host "        INICIANDO FINBOT"
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
$botPath     = Join-Path $base "whatsapp_bot"

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

 #=================================================
 # 1️⃣ WHATSAPP BOT (NODE)
 #=================================================
Write-Host "[1/4] Iniciando WhatsApp Bot (Node)..."
Start-Process "cmd.exe" `
    -ArgumentList "/c npm start" `
    -WorkingDirectory $botPath `
    -NoNewWindow

Start-Sleep -Seconds 6

# =================================================
# 2️⃣ BOT PYTHON PRINCIPAL
# =================================================
Write-Host "[2/4] Iniciando Bot Python..."
Start-Process $python `
    -ArgumentList "app.py" `
    -WorkingDirectory $backendPath `
    -NoNewWindow

Start-Sleep -Seconds 4

# =================================================
# 3️⃣ PAINEL ADMIN (MÓDULO PYTHON)
# =================================================
Write-Host "[3/4] Iniciando Painel Administrativo..."
Start-Process $python `
    -ArgumentList "-m admin_painel.app" `
    -WorkingDirectory $backendPath `
    -NoNewWindow

Start-Sleep -Seconds 4

# =================================================
# 4️⃣ SCHEDULER
# =================================================
Write-Host "[4/4] Iniciando Scheduler..."
Start-Process $python `
    -ArgumentList "scheduler.py" `
    -WorkingDirectory $backendPath `
    -NoNewWindow

Write-Host ""
Write-Host "======================================"
Write-Host "   FINBOT INICIADO COM SUCESSO"
Write-Host "======================================"
Write-Host ""
Write-Host "Painel Admin: http://127.0.0.1:5001"
Write-Host ""
Write-Host "Para encerrar tudo, pressione CTRL + C"
Write-Host ""

while ($true) {
    Start-Sleep -Seconds 5
}
