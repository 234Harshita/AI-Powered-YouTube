@echo off
REM ============================================================
REM AI YouTube Analytics - Backend Startup Script
REM ============================================================

echo.
echo ======================================================
echo AI YouTube Analytics - Backend Startup
echo ======================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check if virtual environment exists
if not exist "venv\" (
    echo.
    echo [*] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

REM Install requirements
echo.
echo [*] Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Check if model files exist
if not exist "backend\models\model.pkl" (
    echo.
    echo WARNING: Model file not found at backend\models\model.pkl
    echo Please run train_model.py first:
    echo   python backend\train_model.py
)

if not exist "backend\models\features.pkl" (
    echo.
    echo WARNING: Features file not found at backend\models\features.pkl
    echo Please run train_model.py first:
    echo   python backend\train_model.py
)

REM Start backend in background so it survives VS Code/terminal shutdown
echo.
echo ======================================================
echo [*] Starting Backend Server...
echo ======================================================
echo.
echo Backend URL: http://localhost:8000
echo Health Check: http://localhost:8000/health
echo API Docs: http://localhost:8000/docs
echo.
echo Starting backend as a detached background process...
echo.

start "" /B cmd /c "call venv\Scripts\activate.bat && python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 > backend.log 2>&1"

for /L %%i in (1,1,5) do (
    timeout /t 1 >nul
    curl -s http://127.0.0.1:8000/health >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Backend is responding on port 8000
        goto :done
    )
)

echo [WARN] Backend may still be starting. Check backend.log for details.

:done
echo.
echo Backend will keep running after this terminal closes.
exit /b 0
