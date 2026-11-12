@echo off
title Starting PathMithra
set "ROOT=C:\Projects\CareerPath"
echo Starting PathMithra. Please wait...
echo.

netstat -ano | findstr "127.0.0.1:5433" | findstr "LISTENING" >nul
if errorlevel 1 (
  echo Starting the database...
  start "PathMithra database - keep this window open" /min /d "%ROOT%\backend" cmd /k venv\Lib\site-packages\pgserver\pginstall\bin\postgres.exe -D .devdb -p 5433 -h 127.0.0.1
  timeout /t 8 /nobreak >nul
) else (
  echo The database is already running.
)

rem Free AI on this computer. If Ollama is missing, the assistant still answers without it.
netstat -ano | findstr "127.0.0.1:11434" | findstr "LISTENING" >nul
if errorlevel 1 (
  if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    echo Starting the free AI...
    start "PathMithra AI - keep this window open" /min "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
  )
)

netstat -ano | findstr ":8001" | findstr "LISTENING" >nul
if errorlevel 1 (
  echo Starting the server...
  start "PathMithra server - keep this window open" /min /d "%ROOT%\backend" cmd /k venv\Scripts\python -m uvicorn app.main:app --port 8001
) else (
  echo The server is already running.
)

netstat -ano | findstr ":5173" | findstr "LISTENING" >nul
if errorlevel 1 (
  echo Starting the website...
  start "PathMithra website - keep this window open" /min /d "%ROOT%\frontend" cmd /k npm run dev
) else (
  echo The website is already running.
)

echo Checking official pages for changes...
start "PathMithra page check" /min /d "%ROOT%\backend" cmd /c "venv\Scripts\python -m scripts.watch_sources & venv\Scripts\python -m scripts.fetch_updates"

echo.
echo Opening PathMithra in your browser...
timeout /t 8 /nobreak >nul
start "" "http://localhost:5173/admin"
