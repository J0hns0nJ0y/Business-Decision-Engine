@echo off
cd /d "%~dp0"
title Business Decision Engine Launcher

echo ==========================================
echo   Business Decision Engine Starting
echo ==========================================
echo Please wait. First time setup may take a few minutes.
echo Do NOT close this window.
echo.

REM Step 1 - Check virtual environment
echo [1/6] Checking Python virtual environment...
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
) ELSE (
    echo Virtual environment already exists.
)

timeout /t 2 >nul

REM Step 2 - Activate venv
echo [2/6] Activating virtual environment...
call venv\Scripts\activate

timeout /t 2 >nul

REM Step 3 - Install requirements
echo [3/6] Installing dependencies...
pip install -r requirements.txt

timeout /t 3 >nul

REM Step 4 - Start backend
echo [4/6] Starting Backend API Server...

start "Backend Server" cmd /k "cd backend && call ..\venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 5 >nul

REM Step 5 - Open API docs
echo [5/6] Opening API documentation...
start http://127.0.0.1:8000/docs

timeout /t 3 >nul

REM Step 6 - Start frontend
echo [6/6] Starting Dashboard...

start "Frontend Dashboard" cmd /k "cd frontend && call ..\venv\Scripts\activate && streamlit run dashboard.py --server.address 0.0.0.0 --server.port 8501"

echo.
echo ==========================================
echo System started successfully.
echo Backend: http://127.0.0.1:8000/docs
echo Dashboard will open automatically.
echo ==========================================
echo.
echo To close both servers type: CLOSE
echo.

:WAIT
set /p userinput=

if /I "%userinput%"=="CLOSE" goto STOP
goto WAIT

:STOP
echo Stopping servers...

REM kill uvicorn backend
taskkill /F /IM uvicorn.exe >nul 2>&1

REM kill streamlit frontend
taskkill /F /IM streamlit.exe >nul 2>&1

REM kill python processes started by them
taskkill /F /IM python.exe >nul 2>&1

echo Servers stopped.
echo ==========================================
echo SYSTEM STOPPED SUCCESSFULLY.
echo ==========================================
timeout /t 2 >nul
exit