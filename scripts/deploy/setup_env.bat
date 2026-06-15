@echo off
echo --- DeepMediaCheck Environment Setup ---

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Create Venv if not exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

REM Activate
call venv\Scripts\activate.bat

REM Install Requirements
echo Installing dependencies (this may take a while)...
pip install -r requirements.txt

echo.
echo Setup Complete!
echo You can now run start_local.bat
pause
