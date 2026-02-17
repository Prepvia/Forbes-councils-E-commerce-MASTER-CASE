@echo off
title Master Case Optimizer v2.0

cd /d "%~dp0"

echo ============================================================
echo   MASTER CASE OPTIMIZER v2.0
echo ============================================================
echo.
echo   Checking for existing processes on port 8002...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002 ^| findstr LISTENING 2^>nul') do (
    echo   Killing PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo   Starting server...
echo   Browser will open automatically
echo.
echo   Press Ctrl+C to stop
echo ============================================================
echo.

python -u optimizer_engine.py

pause
