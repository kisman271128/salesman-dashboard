@echo off
chcp 65001 > nul 2>&1
color 0A
title Morning Batch Update - Salesman Dashboard - WITH EXCEL REFRESH

echo.
echo ============================================================
echo           MORNING BATCH UPDATE - SALESMAN DASHBOARD
echo                    Depo Tanjung - Region Kalimantan
echo                   WITH EXCEL REFRESH INTEGRATION
echo ============================================================
echo.

REM Change to YOUR repository directory
cd /d "C:\Dashboard"

echo [%time%] Starting comprehensive morning update...
echo.

REM ============================================================
REM                    PRE-FLIGHT CHECKS
REM ============================================================
echo === PRE-FLIGHT CHECKS ===

REM Check if Python is available
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Auto-installing...
    echo CRITICAL: Cannot proceed without Python. Exiting...
    exit /b 1
)
echo OK: Python found

REM Check if PowerShell is available
echo Checking PowerShell...
powershell -Command "Get-Host" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PowerShell not available!
    exit /b 1
)
echo OK: PowerShell found

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

REM Check if PowerShell refresh script exists
if not exist "excel_refresh_selective.ps1" (
    echo ERROR: PowerShell refresh script 'excel_refresh_selective.ps1' not found!
    exit /b 1
)
echo OK: Excel refresh script found

REM Check if Python script exists
if not exist "morning_update.py" (
    echo ERROR: Python script 'morning_update.py' not found!
    exit /b 1
)
echo OK: Python script found

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
echo ============================================================
echo                    STEP 1: EXCEL REFRESH
echo ============================================================

REM Clear any previous refresh logs
if exist "excel_refresh.log" (
    del "excel_refresh.log" >nul 2>&1
)

REM Clear previous status markers
if exist "excel_refresh_success.txt" (
    del "excel_refresh_success.txt" >nul 2>&1
)
if exist "excel_refresh_failure.txt" (
    del "excel_refresh_failure.txt" >nul 2>&1
)

REM Run Excel refresh script
echo [%time%] Starting Excel data refresh...
echo Target file: %EXCEL_FILE%
echo Method: Selective file handling (PowerShell)
echo --------------------------------------------------------

REM Execute PowerShell script with parameters
powershell -ExecutionPolicy Bypass -File "excel_refresh_selective.ps1" -ExcelFile "%cd%\%EXCEL_FILE%" -RefreshWaitSeconds 30 -MaxRetries 3

set EXCEL_REFRESH_RESULT=%errorlevel%

echo --------------------------------------------------------
echo [%time%] Excel refresh completed with exit code: %EXCEL_REFRESH_RESULT%

REM Check refresh results
if %EXCEL_REFRESH_RESULT% equ 0 (
    echo ============================================================
    echo                   EXCEL REFRESH: SUCCESS
    echo ============================================================
    echo.
    if exist "excel_refresh_success.txt" (
        echo Refresh details:
        echo ----------------------------------------
        type "excel_refresh_success.txt"
        echo ----------------------------------------
    )
    echo.
    echo Status: Excel data refreshed successfully
    echo File: %EXCEL_FILE% ready for processing
    echo.
    
    REM Log Excel refresh success
    echo [%date% %time%] Excel refresh completed successfully >> update_history.log
    
) else (
    echo ============================================================
    echo                   EXCEL REFRESH: FAILED
    echo ============================================================
    echo.
    echo Exit code: %EXCEL_REFRESH_RESULT%
    echo.
    
    REM Show failure details if available
    if exist "excel_refresh_failure.txt" (
        echo Failure details:
        echo ----------------------------------------
        type "excel_refresh_failure.txt"
        echo ----------------------------------------
    )
    
    REM Show last few log lines for diagnosis
    if exist "excel_refresh.log" (
        echo Last refresh log entries:
        echo ----------------------------------------
        powershell "Get-Content excel_refresh.log | Select-Object -Last 10" 2>nul
        echo ----------------------------------------
    )
    
    echo.
    echo DECISION: Continuing with existing Excel file data
    echo WARNING: Dashboard may not have the latest data
    echo.
    
    REM Log Excel refresh failure but continue
    echo [%date% %time%] Excel refresh FAILED with exit code %EXCEL_REFRESH_RESULT% - continuing with existing data >> update_history.log
)

echo.
echo ============================================================
echo                 STEP 2: DASHBOARD PROCESSING
echo ============================================================

REM Clear any previous Python log
if exist "morning_update.log" (
    del "morning_update.log" >nul 2>&1
)

REM Run the Python script
echo [%time%] Executing Python dashboard processing...
echo Source: %EXCEL_FILE%
echo Output: JSON files for dashboard
echo --------------------------------------------------------

python morning_update.py
set PYTHON_RESULT=%errorlevel%

REM DEBUG: Show captured exit code immediately
echo [DEBUG] Python script exit code captured: %PYTHON_RESULT%

echo --------------------------------------------------------
echo [%time%] Python processing completed with exit code: %PYTHON_RESULT%

echo.
echo === PROCESSING RESULTS ===

REM Check Python results
if "%PYTHON_RESULT%"=="0" (
    echo ============================================================
    echo                DASHBOARD PROCESSING: SUCCESS
    echo ============================================================
    echo.
    echo Dashboard URL: https://kisman271128.github.io/salesman-dashboard
    echo Update time: %date% %time%
    echo Status: Dashboard updated with refreshed data
    echo Data freshness: Excel refreshed + JSON generated
    echo Next update: Tomorrow at 07:00
    echo.
    
    REM Log Python success to system log
    echo [%date% %time%] Dashboard processing completed successfully >> update_history.log
    
    echo ============================================================
    
) else (
    echo ============================================================
    echo                DASHBOARD PROCESSING: FAILED
    echo ============================================================
    echo.
    echo Exit code: %PYTHON_RESULT%
    echo Update time: %date% %time%
    echo.
    
    REM Show last few log lines for diagnosis
    if exist "morning_update.log" (
        echo Last processing log entries:
        echo ----------------------------------------
        powershell "Get-Content morning_update.log | Select-Object -Last 10" 2>nul
        echo ----------------------------------------
    )
    
    REM Log Python failure to system log
    echo [%date% %time%] Dashboard processing FAILED with exit code %PYTHON_RESULT% >> update_history.log
    
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
echo ============================================================
echo                    COMPREHENSIVE SUMMARY
echo ============================================================
echo Start time: %time%
echo Date: %date%
echo Mode: Fully Automated with Excel Refresh
echo.
echo STEP 1 - Excel Refresh: %EXCEL_REFRESH_RESULT% (0=success)
echo STEP 2 - Dashboard Processing: %PYTHON_RESULT% (0=success)
echo.
echo Excel file: %EXCEL_FILE%
echo Working directory: %cd%
echo.

REM Determine overall success
set OVERALL_SUCCESS=0
if %PYTHON_RESULT% neq 0 (
    set OVERALL_SUCCESS=1
)

REM Create comprehensive status file
echo %OVERALL_SUCCESS% > last_update_status.txt
echo %date% %time% >> last_update_status.txt
echo Excel_Refresh_Code:%EXCEL_REFRESH_RESULT% >> last_update_status.txt
echo Python_Processing_Code:%PYTHON_RESULT% >> last_update_status.txt

REM Final log entry with all results
echo [%date% %time%] COMPREHENSIVE UPDATE: Excel=%EXCEL_REFRESH_RESULT%, Python=%PYTHON_RESULT%, Overall=%OVERALL_SUCCESS% >> update_history.log

REM Final status message
if %OVERALL_SUCCESS% equ 0 (
    echo ============================================================
    echo            🎉 COMPREHENSIVE UPDATE SUCCESSFUL! 🎉
    echo ============================================================
    echo.
    echo ✅ Excel data refreshed from sources
    echo ✅ Dashboard JSON files generated
    echo ✅ Changes pushed to GitHub
    echo ✅ Dashboard ready with fresh data
    echo.
    echo 🌐 Live Dashboard: https://kisman271128.github.io/salesman-dashboard
    echo 📊 Data Status: Real-time (Excel refreshed + Dashboard updated)
    echo ⏰ Next Update: Tomorrow at 07:00
    echo.
) else (
    echo ============================================================
    echo              ⚠️ UPDATE COMPLETED WITH ISSUES ⚠️
    echo ============================================================
    echo.
    if %EXCEL_REFRESH_RESULT% neq 0 (
        echo ⚠️ Excel refresh had issues (but continued)
    ) else (
        echo ✅ Excel refresh successful
    )
    
    if %PYTHON_RESULT% neq 0 (
        echo ❌ Dashboard processing failed
    ) else (
        echo ✅ Dashboard processing successful
    )
    
    echo.
    echo 📋 Check logs for details:
    echo   - excel_refresh.log (Excel refresh details)
    echo   - morning_update.log (Python processing details)
    echo   - update_history.log (Overall update history)
    echo.
)

echo ============================================================

REM Exit with overall result
exit /b %OVERALL_SUCCESS%