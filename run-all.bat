@echo off
TITLE SQL AI Insight Runner
echo =================================================================
echo    DANG KHOI CHAY SQL AI INSIGHT (FE ^& BE)
echo =================================================================
echo.

:: Chạy script PowerShell với quyền thực thi được bỏ qua (Bypass)
powershell -ExecutionPolicy Bypass -File "%~dp0run-all.ps1"

echo.
echo =================================================================
echo    Script da hoan tat. Vui long kiem tra cac cua so Terminal moi.
echo =================================================================
pause
