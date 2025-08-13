@echo off
echo 🚀 Starting Financial Statement Analysis API...
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo ✅ Virtual environment found, activating...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment not found
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo 🚀 Starting API server...
echo 📚 API Documentation will be available at: http://localhost:8000/docs
echo 🔍 Alternative docs at: http://localhost:8000/redoc
echo.
echo Press Ctrl+C to stop the server
echo.

python api.py

pause
