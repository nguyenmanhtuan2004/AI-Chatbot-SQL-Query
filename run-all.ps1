# Script tự động khởi chạy toàn bộ dự án (FE & BE)

function Stop-PortProcess($port) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        Write-Host "Đang dừng các tiến trình tại cổng $port..." -ForegroundColor Yellow
        foreach ($conn in $connections) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "=== ĐANG CHUẨN BỊ MÔI TRƯỜNG ===" -ForegroundColor Cyan

# 1. Dọn dẹp Backend (Port 5026)
Stop-PortProcess 5026

# 2. Dọn dẹp Frontend (Port 3000)
Stop-PortProcess 3000

Write-Host "=== ĐANG KHỞI CHẠY CÁC DỊCH VỤ ===" -ForegroundColor Green

# Khởi chạy Backend trong cửa sổ mới
Write-Host "Đang chạy Backend (.NET API)..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd API_ChatBot; dotnet run"

# Khởi chạy Frontend trong cửa sổ mới
Write-Host "Đang chạy Frontend (Next.js)..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "Tất cả các dịch vụ đang được khởi chạy trong các cửa sổ riêng biệt." -ForegroundColor Cyan
Write-Host "Backend: http://localhost:5026" -ForegroundColor Gray
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Gray
