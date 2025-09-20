@echo off
chcp 65001 > nul 2>&1
color 0B
title Dashboard Update Monitor

echo ============================================================
echo             DASHBOARD UPDATE MONITOR
echo ============================================================
echo.

cd /d "C:\Dashboard"

echo === CURRENT STATUS ===
echo.

REM Check last update status
if exist "last_update_status.txt" (
    echo Last Update Status:
    echo ----------------------------------------
    set /p EXIT_CODE=<last_update_status.txt
    if "%EXIT_CODE%"=="0" (
        echo ✅ SUCCESS - Last update completed successfully
    ) else (
        echo ❌ FAILED - Last update failed with code: %EXIT_CODE%
    )
    
    echo.
    echo Status file content:
    type "last_update_status.txt"
    echo ----------------------------------------
    echo.
) else (
    echo ⚠️  No status file found (no updates run yet)
    echo.
)

REM Check update history
echo === UPDATE HISTORY ===
if exist "update_history.log" (
    echo Last 10 updates:
    echo ----------------------------------------
    powershell "Get-Content update_history.log | Select-Object -Last 10"
    echo ----------------------------------------
) else (
    echo No update history found
)
echo.

REM Check current data files
echo === DATA FILES STATUS ===
echo.
if exist "data" (
    echo Data directory contents:
    dir "data" /b
    echo.
    
    REM Check last modified times
    echo File timestamps:
    echo ----------------------------------------
    dir "data\*.json" /tw | findstr /v "Directory"
    echo ----------------------------------------
) else (
    echo ❌ Data directory not found
)
echo.

REM Check scheduled task
echo === SCHEDULER STATUS ===
echo.
schtasks /query /tn "Daily Dashboard Update" /fo list 2>nul
if %errorlevel% neq 0 (
    echo ❌ Scheduled task not found
    echo Run setup_scheduler.bat to create it
) else (
    echo ✅ Scheduled task is configured
)
echo.

REM Check recent log
echo === RECENT LOG ENTRIES ===
if exist "morning_update.log" (
    echo Last 15 lines from morning_update.log:
    echo ----------------------------------------
    powershell "Get-Content morning_update.log | Select-Object -Last 15"
    echo ----------------------------------------
) else (
    echo No log file found
)
echo.

REM Dashboard URL status
echo === DASHBOARD ACCESS ===
echo.
echo 📱 Dashboard URL: https://kisman271128.github.io/salesman-dashboard
echo 🔍 Check if accessible from browser
echo.

REM Quick connectivity test
echo Testing GitHub connectivity...
ping github.com -n 1 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ GitHub connectivity: OK
) else (
    echo ❌ GitHub connectivity: FAILED
)
echo.

echo === MANUAL ACTIONS ===
echo.
echo 1. Run update now: morning_update_automated.bat
echo 2. View full log: type morning_update.log
echo 3. Check git status: git status
echo 4. Test Python: python --version
echo 5. Setup scheduler: setup_scheduler.bat
echo.

echo ============================================================
echo Monitor completed at: %date% %time%
echo ============================================================
echo.

echo Press any key to close or Ctrl+C to exit...
pause >nul