# Script tự động dừng tiến trình cũ và chạy API
$processName = "API_ChatBot"
$port = 5026

Write-Host "--- Dang kiem tra va don dep he thong ---" -ForegroundColor Cyan

# 1. Tat tien trinh theo ten
$proc = Get-Process | Where-Object { $_.ProcessName -eq $processName }
if ($proc) {
    Write-Host "Dang dung tien trinh $processName..." -ForegroundColor Yellow
    Stop-Process -Name $processName -Force -ErrorAction SilentlyContinue
}

# 2. Giai phong cong 5026 (neu co)
$portProcess = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($portProcess) {
    Write-Host "Dang giai phong cong $port..." -ForegroundColor Yellow
    foreach ($p in $portProcess) {
        Stop-Process -Id $p.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "--- Bat dau chay dotnet run ---" -ForegroundColor Green
dotnet run
