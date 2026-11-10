@echo off
rem Runs every 10 minutes from Windows Task Scheduler. If the database, server or website has stopped,
rem it starts that part again. Parts that are already running are left alone.
set "ROOT=C:\Projects\CareerPath"
set "LOG=%ROOT%\backend\keep-running.log"

netstat -ano | findstr "127.0.0.1:5433" | findstr "LISTENING" >nul
if errorlevel 1 (
  echo %date% %time% database was stopped, starting it >> "%LOG%"
  start "CareerPath database - keep this window open" /min /d "%ROOT%\backend" cmd /k venv\Lib\site-packages\pgserver\pginstall\bin\postgres.exe -D .devdb -p 5433 -h 127.0.0.1
  ping -n 11 127.0.0.1 >nul
)

netstat -ano | findstr ":8001" | findstr "LISTENING" >nul
if errorlevel 1 (
  echo %date% %time% server was stopped, starting it >> "%LOG%"
  rem A server window left stuck (for example after Windows blocked a file) is closed first
  taskkill /F /T /FI "WINDOWTITLE eq CareerPath server - keep this window open*" >nul 2>&1
  start "CareerPath server - keep this window open" /min /d "%ROOT%\backend" cmd /k venv\Scripts\python -m uvicorn app.main:app --port 8001
)

netstat -ano | findstr ":5173" | findstr "LISTENING" >nul
if errorlevel 1 (
  echo %date% %time% website was stopped, starting it >> "%LOG%"
  taskkill /F /T /FI "WINDOWTITLE eq CareerPath website - keep this window open*" >nul 2>&1
  start "CareerPath website - keep this window open" /min /d "%ROOT%\frontend" cmd /k npm run dev
)
