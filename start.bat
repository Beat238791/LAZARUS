@echo off
echo ========================================
echo   PROJECT: LAZARUS - Starting...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Check if requirements are installed
echo Checking dependencies...
pip show customtkinter >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [OK] Dependencies ready
echo.

REM Launch the application
echo Launching LAZARUS...
echo.
python lazarus_app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application crashed or exited with error
    pause
)
