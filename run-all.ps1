# Script tu dong khoi chay toan bo du an (FE & BE)

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
if ([string]::IsNullOrEmpty($root)) { $root = Get-Location }

function Stop-PortProcess($port) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        Write-Host "Dang dung cac tien trinh tai cong $port..." -ForegroundColor Yellow
        foreach ($conn in $connections) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "=== DANG CHUAN BI MOI TRUONG ===" -ForegroundColor Cyan

# 1. Don dep cac cong
Stop-PortProcess 5026
Stop-PortProcess 3000
Stop-PortProcess 8000

Write-Host "=== DANG KHOI CHAY CAC DICH VU ===" -ForegroundColor Green

# 1. Khoi chay Backend (.NET API)
Write-Host "Dang chay Backend (.NET API)..." -ForegroundColor Blue
Start-Process powershell -WorkingDirectory "$root\API_ChatBot" -ArgumentList '-NoExit', '-Command', 'dotnet run'

# 2. Khoi chay Python API (RAG)
Write-Host "Dang chay Python API (RAG)..." -ForegroundColor Blue
if (Test-Path "$root\chatbot_api\venv\Scripts\python.exe") {
    Start-Process powershell -WorkingDirectory "$root\chatbot_api" -ArgumentList '-NoExit', '-Command', '.\venv\Scripts\python.exe main.py'
} else {
    Start-Process powershell -WorkingDirectory "$root\chatbot_api" -ArgumentList '-NoExit', '-Command', 'python main.py'
}

# 3. Khoi chay Frontend (Next.js)
Write-Host "Dang chay Frontend (Next.js)..." -ForegroundColor Blue
Start-Process powershell -WorkingDirectory "$root\frontend" -ArgumentList '-NoExit', '-Command', 'npm run dev'

Write-Host "Tat ca cac dich vu dang duoc khoi chay." -ForegroundColor Cyan
Write-Host "Backend (.NET): http://localhost:5026" -ForegroundColor Gray
Write-Host "Python API:     http://localhost:8000" -ForegroundColor Gray
Write-Host "Frontend:       http://localhost:3000" -ForegroundColor Gray
