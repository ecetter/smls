@echo off
REM Social Media Login Service (SMLS) Launch Script for Windows

echo 🚀 Social Media Login Service (SMLS) - Launching...
echo ================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo    Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "smls_env" (
    echo ❌ SMLS virtual environment not found!
    echo    Please run the setup script first:
    echo    python scripts/setup.py
    pause
    exit /b 1
)

REM Activate virtual environment and run the app
echo 🌐 Starting SMLS...
echo 📱 Open your browser and go to the URL shown below
echo ⏹️  Press Ctrl+C to stop the server
echo ================================
echo.

call smls_env\Scripts\activate
python src/app.py
pause
