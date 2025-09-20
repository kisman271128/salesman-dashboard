@echo off
chcp 65001 > nul 2>&1
color 0A
title Morning Batch Update - Salesman Dashboard - AUTOMATED

echo.
echo ============================================================
echo           MORNING BATCH UPDATE - SALESMAN DASHBOARD
echo                    Depo Tanjung - Region Kalimantan
echo                         AUTOMATED MODE
echo ============================================================
echo.

REM Change to YOUR repository directory
cd /d "C:\Dashboard"

echo [%time%] Starting automated morning update...
echo.

REM Pre-flight checks (no user interaction)
echo === PRE-FLIGHT CHECKS ===

REM Check if Python is available
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Auto-installing...
    REM You could add auto-install logic here if needed
    echo CRITICAL: Cannot proceed without Python. Exiting...
    exit /b 1
)
echo OK: Python found

REM Check if we're in the right directory
if not exist ".git" (
    echo ERROR: Not in repository directory!
    echo Current directory: %cd%
    echo Expected: C:\Dashboard
    exit /b 1
)
echo OK: Git repository found

REM Check if Excel file exists
if not exist "DbaseSalesmanWebApp.xlsm" (
    if not exist "DbaseSalesmanWebApp.xlsx" (
        echo ERROR: Excel file not found in %cd%
        exit /b 1
    ) else (
        echo OK: Excel file found (.xlsx)
        set EXCEL_FILE=DbaseSalesmanWebApp.xlsx
    )
) else (
    echo OK: Excel file found (.xlsm)
    set EXCEL_FILE=DbaseSalesmanWebApp.xlsm
)

REM Check if Python script exists
if not exist "morning_update.py" (
    echo ERROR: Python script 'morning_update.py' not found!
    exit /b 1
)
echo OK: Python script found

REM Auto-close Excel if running (for automation)
echo Checking Excel processes...
tasklist | findstr /i excel >nul 2>&1
if %errorlevel% equ 0 (
    echo WARNING: Excel is running. Auto-closing for automation...
    taskkill /F /IM EXCEL.EXE >nul 2>&1
    timeout /t 3 /nobreak >nul
    echo OK: Excel processes terminated
) else (
    echo OK: No Excel processes running
)

echo.
echo === DEPENDENCY CHECKS ===

REM Auto-install missing Python packages
echo Checking Python dependencies...
python -c "import pandas, json, subprocess, logging" >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Missing Python packages. Auto-installing...
    pip install pandas openpyxl xlrd gitpython requests >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Failed to auto-install Python packages!
        exit /b 1
    )
    echo OK: Python packages installed
) else (
    echo OK: Python packages ready
)

echo.
echo === RUNNING UPDATE ===

REM Clear any previous log
if exist "morning_update.log" (
    del "morning_update.log" >nul 2>&1
)

REM Run the Python script with explicit error handling
echo [%time%] Executing Python script...
echo --------------------------------------------------------

REM CRITICAL FIX: Proper exit code capture
python morning_update.py
set SCRIPT_RESULT=%errorlevel%

REM DEBUG: Show captured exit code immediately
echo [DEBUG] Python script exit code captured: %SCRIPT_RESULT%

echo --------------------------------------------------------
echo [%time%] Python script completed with exit code: %SCRIPT_RESULT%

REM CRITICAL FIX: Force logging regardless of exit code evaluation issues
echo.
echo === FORCED LOGGING TEST ===
echo [%date% %time%] BATCH DEBUG - About to check script result: %SCRIPT_RESULT% >> update_history.log
echo %SCRIPT_RESULT% > last_update_status.txt
echo %date% %time% >> last_update_status.txt
echo [DEBUG] Forced logging completed

echo.
echo === RESULTS ===

REM IMPROVED: More robust exit code checking
if "%SCRIPT_RESULT%"=="0" (
    echo ============================================================
    echo                     SUCCESS: UPDATE COMPLETED
    echo ============================================================
    echo.
    echo Dashboard URL: https://kisman271128.github.io/salesman-dashboard
    echo Update time: %date% %time%
    echo Status: Ready for team access
    echo Next update: Tomorrow at 07:00
    echo.
    
    REM Log success to system log
    echo [%date% %time%] Morning update completed successfully >> update_history.log
    
    echo ============================================================
    
) else (
    echo ============================================================
    echo                     FAILED: UPDATE ERROR
    echo ============================================================
    echo.
    echo Exit code: %SCRIPT_RESULT%
    echo Update time: %date% %time%
    echo.
    
    REM Show last few log lines for diagnosis
    if exist "morning_update.log" (
        echo Last log entries:
        echo ----------------------------------------
        powershell "Get-Content morning_update.log | Select-Object -Last 5" 2>nul
        echo ----------------------------------------
    )
    
    REM Log failure to system log
    echo [%date% %time%] Morning update FAILED with exit code %SCRIPT_RESULT% >> update_history.log
    
    REM Quick diagnostics
    echo.
    echo Diagnostics:
    echo - Excel file: %EXCEL_FILE%
    echo - Directory: %cd%
    echo - Git status: 
    git status --porcelain 2>nul
    
    echo ============================================================
)

echo.
echo === AUTOMATION SUMMARY ===
echo Start time: %time%
echo Date: %date%
echo Mode: Fully Automated
echo Excel file: %EXCEL_FILE%
echo Working directory: %cd%
echo.

REM CRITICAL FIX: Always update status files at the end
echo.
echo === FINAL STATUS UPDATE ===
echo Updating final status files...

REM Overwrite status file with current info
echo %SCRIPT_RESULT% > last_update_status.txt
echo %date% %time% >> last_update_status.txt

REM Final log entry with timestamp
echo [%date% %time%] Batch script completed - Exit code: %SCRIPT_RESULT% >> update_history.log

echo Status files updated with current timestamp: %date% %time%

REM Exit with the same code as Python script
exit /b %SCRIPT_RESULT%