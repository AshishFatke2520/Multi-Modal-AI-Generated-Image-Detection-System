@echo off
echo ==============================================
echo STARTING DEEPMEDIACHECK ENVIRONMENT
echo ==============================================

echo [1/3] Checking environment...
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found in "venv".
    echo Please create it using: python -m venv venv
    pause
    exit /b
)

echo [2/3] Starting FASTAPI Backend (Port 8000)...
start "DeepMediaCheck Backend" cmd /k "call venv\Scripts\activate.bat && uvicorn app.main:app --reload"

echo [3/3] Starting REACT Frontend (Port 5173)...
cd frontend
if not exist "node_modules\" (
    echo Installing frontend dependencies...
    npm install
)
start "DeepMediaCheck Frontend" cmd /k "npm run dev"

echo.
echo Both servers have been launched in separate windows!
echo Backend API available at: http://localhost:8000
echo Frontend UI available at: http://localhost:5173
echo.
pause
