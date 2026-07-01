#!/bin/bash

# ============================================================
# AI YouTube Analytics - Backend Startup Script
# ============================================================

echo ""
echo "======================================================"
echo "AI YouTube Analytics - Backend Startup"
echo "======================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo "[OK] Python found"
python3 --version

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "[OK] Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "[*] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi
echo "[OK] Virtual environment activated"

# Install requirements
echo ""
echo "[*] Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi
echo "[OK] Dependencies installed"

# Check if model files exist
if [ ! -f "backend/models/model.pkl" ]; then
    echo ""
    echo "WARNING: Model file not found at backend/models/model.pkl"
    echo "Please run train_model.py first:"
    echo "  python backend/train_model.py"
fi

if [ ! -f "backend/models/features.pkl" ]; then
    echo ""
    echo "WARNING: Features file not found at backend/models/features.pkl"
    echo "Please run train_model.py first:"
    echo "  python backend/train_model.py"
fi

# Start backend in background so it survives terminal shutdown
echo ""
echo "======================================================"
echo "[*] Starting Backend Server..."
echo "======================================================"
echo ""
echo "Backend URL: http://localhost:8000"
echo "Health Check: http://localhost:8000/health"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Starting backend as a detached background process..."
echo ""

nohup python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

for i in {1..5}; do
  sleep 1
  curl -s http://127.0.0.1:8000/health >/dev/null 2>&1 && echo "[OK] Backend is responding on port 8000" && exit 0
done

echo "[WARN] Backend may still be starting. Check backend.log for details."
