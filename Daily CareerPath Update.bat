@echo off
rem Runs once a day from Windows Task Scheduler. It checks official pages and collects career news.
rem It never changes rules or roadmaps by itself: changes wait for review on the Admin page.
set "ROOT=C:\Projects\CareerPath"
set "LOG=%ROOT%\backend\daily-update.log"
echo. >> "%LOG%"
echo ===== %date% %time% ===== >> "%LOG%"

netstat -ano | findstr "127.0.0.1:5433" | findstr "LISTENING" >nul
if errorlevel 1 (
  echo Starting the database >> "%LOG%"
  start "CareerPath database - keep this window open" /min /d "%ROOT%\backend" cmd /k venv\Lib\site-packages\pgserver\pginstall\bin\postgres.exe -D .devdb -p 5433 -h 127.0.0.1
  timeout /t 10 /nobreak >nul
)

cd /d "%ROOT%\backend"
venv\Scripts\python -m scripts.watch_sources >> "%LOG%" 2>&1
venv\Scripts\python -m scripts.fetch_updates >> "%LOG%" 2>&1
venv\Scripts\python -m scripts.sync_official >> "%LOG%" 2>&1
rem Backups: the database and the code history go to OneDrive, so nothing is lost if this laptop breaks.
venv\Scripts\python -m scripts.backup_db >> "%LOG%" 2>&1
cd /d "%ROOT%"
git add -A >> "%LOG%" 2>&1
git commit -q -m "Daily snapshot %date%" >> "%LOG%" 2>&1
git bundle create "%OneDrive%\CareerPath-backups\careerpath-code.bundle" --all >> "%LOG%" 2>&1
echo Finished >> "%LOG%"
