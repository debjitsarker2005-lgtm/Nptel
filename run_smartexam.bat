@echo off
title SmartExam AI - NPTEL 2026 Platform
color 0B
echo =========================================================================
echo               🎓 Starting SmartExam AI (NPTEL 2026)
echo =========================================================================
echo.

cd /d "%~dp0"
set PATH=C:\Users\debji\AppData\Local\Programs\Python\Python312;C:\Users\debji\AppData\Local\Programs\Python\Python312\Scripts;%PATH%

echo [1/3] Checking Python runtime...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in path. Please check Python installation.
    pause
    exit /b 1
)

echo [2/3] Initializing SmartExam Database...
python -m backend.app.init_db

echo [3/3] Launching FastAPI backend server at http://127.0.0.1:8000/ ...
start "SmartExam Backend" /b python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

timeout /t 2 >nul
echo Opening SmartExam in default browser...
start http://127.0.0.1:8000/

echo.
echo =========================================================================
echo   SmartExam AI is RUNNING!
echo   Access at: http://127.0.0.1:8000/
echo   API Docs:  http://127.0.0.1:8000/docs
echo   (Keep this window open while practicing)
echo =========================================================================
echo.
pause
