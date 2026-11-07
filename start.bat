@echo off
REM Starts CareerPath on this computer. Close the two new windows to stop it.
cd /d "%~dp0backend"
venv\Scripts\python -m scripts.dev_db start
venv\Scripts\python -m alembic upgrade head
start "CareerPath API" cmd /k venv\Scripts\python -m uvicorn app.main:app --port 8001
cd /d "%~dp0frontend"
start "CareerPath website" cmd /k npm run dev
timeout /t 5 >nul
start http://localhost:5173
