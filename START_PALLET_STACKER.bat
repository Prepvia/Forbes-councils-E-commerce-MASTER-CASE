@echo off
title 3D Pallet Stacker Server
color 0A
echo ========================================
echo   3D PALLET STACKER - START SERVER
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found!
echo.

echo [2/3] Checking if pallet_calculator.py exists...
if not exist "pallet_calculator.py" (
    echo [ERROR] pallet_calculator.py not found!
    echo.
    echo Make sure you're running this from the correct directory.
    echo.
    pause
    exit /b 1
)
echo [OK] pallet_calculator.py found!
echo.

echo [3/3] Starting server on port 8000...
echo.
echo ========================================
echo   SERVER STARTING...
echo ========================================
echo.
echo IMPORTANT:
echo - Keep this window open while using the app
echo - Browser will open automatically
echo - If browser doesn't open, go to: http://localhost:8000/pallet_3d.html
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python pallet_calculator.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo   ERROR: Server failed to start!
    echo ========================================
    echo.
    echo Possible causes:
    echo 1. Port 8000 is already in use
    echo    - Close other programs using port 8000
    echo    - Or close any other Python servers
    echo.
    echo 2. Missing Python dependencies
    echo    - Python should work with standard library only
    echo.
    echo 3. File pallet_calculator.py has errors
    echo    - Check the error message above
    echo.
    echo ========================================
    pause
    exit /b 1
)

pause

