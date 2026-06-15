@echo off
echo --- Starting DeepMediaCheck API Server ---

if not exist "venv" (
    echo Error: venv not found. Please run setup_env.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Server starting at http://127.0.0.1:8000
echo Documentation available at http://127.0.0.1:8000/docs
echo Press Ctrl+C to stop.
echo.

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
