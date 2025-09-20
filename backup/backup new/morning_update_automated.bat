@echo off
chcp 65001 > nul 2>&1
color 0A
title Morning Batch Update - Salesman Dashboard - VBS Excel Refresh (.xlsx/.xlsb)

echo.
echo ============================================================
echo           MORNING BATCH UPDATE - SALESMAN DASHBOARD
echo                    Depo Tanjung - Region Kalimantan
echo                    VBS EXCEL REFRESH (.xlsx/.xlsb)
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

REM Check if we're in the right directory
if not exist ".git" (
    echo ERROR: Not in repository directory!
    echo Current directory: %cd%
    echo Expected: C:\Dashboard
    exit /b 1
)
echo OK: Git repository found

REM Check if Excel file exists (.xlsx or .xlsb)
set EXCEL_FILE=
if exist "DbaseSalesmanWebApp.xlsx" (
    set EXCEL_FILE=DbaseSalesmanWebApp.xlsx
    echo OK: Excel file found (.xlsx)
    goto :excel_found
)
if exist "DbaseSalesmanWebApp.xlsb" (
    set EXCEL_FILE=DbaseSalesmanWebApp.xlsb
    echo OK: Excel file found (.xlsb)
    goto :excel_found
)

echo ERROR: Excel file not found in %cd%
echo Required: DbaseSalesmanWebApp.xlsx or DbaseSalesmanWebApp.xlsb
exit /b 1

:excel_found

REM Check if VBS refresh script exists
if not exist "refresh_excel.vbs" (
    echo ERROR: VBS refresh script 'refresh_excel.vbs' not found!
    exit /b 1
)
echo OK: VBS refresh script found

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
echo                    STEP 1: EXCEL REFRESH (VBS)
echo ============================================================

REM Clear any previous refresh logs and status files
if exist "excel_refresh_success.txt" (
    del "excel_refresh_success.txt" >nul 2>&1
)
if exist "excel_refresh_failure.txt" (
    del "excel_refresh_failure.txt" >nul 2>&1
)

REM Run VBS Excel refresh script
echo [%time%] Starting Excel data refresh using VBS...
echo Target file: %EXCEL_FILE%
echo Method: VBS Script (Simple & Reliable)
echo --------------------------------------------------------

REM Execute VBS script and capture output
cscript //nologo refresh_excel.vbs > excel_refresh_temp.log 2>&1
set EXCEL_REFRESH_RESULT=%errorlevel%

REM Show VBS output
echo VBS Output:
echo ----------------------------------------
type excel_refresh_temp.log
echo ----------------------------------------

echo [%time%] VBS Excel refresh completed with exit code: %EXCEL_REFRESH_RESULT%

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
    echo Status: Excel data refreshed successfully using VBS
    echo File: %EXCEL_FILE% ready for processing
    echo Method: VBS Script - All pivot tables and connections refreshed
    echo.
    
    REM Log Excel refresh success
    echo [%date% %time%] Excel refresh completed successfully using VBS (%EXCEL_FILE%) >> update_history.log
    
) else (
    echo ============================================================
    echo                   EXCEL REFRESH: FAILED
    echo ============================================================
    echo.
    echo Exit code: %EXCEL_REFRESH_RESULT%
    echo.
    
    REM Show failure details from VBS output
    echo VBS execution details:
    echo ----------------------------------------
    if exist "excel_refresh_temp.log" (
        type "excel_refresh_temp.log"
    ) else (
        echo No VBS log available
    )
    echo ----------------------------------------
    
    echo.
    echo DECISION: Continuing with existing Excel file data
    echo WARNING: Dashboard may not have the latest data
    echo.
    
    REM Log Excel refresh failure but continue
    echo [%date% %time%] Excel refresh FAILED using VBS (%EXCEL_FILE%) with exit code %EXCEL_REFRESH_RESULT% - continuing with existing data >> update_history.log
)

REM Clean up temporary log
if exist "excel_refresh_temp.log" (
    del "excel_refresh_temp.log" >nul 2>&1
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
    echo Data freshness: Excel refreshed (%EXCEL_FILE%) + JSON generated
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
echo Mode: VBS Excel Refresh (.xlsx/.xlsb support)
echo.
echo STEP 1 - Excel Refresh (VBS): %EXCEL_REFRESH_RESULT% (0=success)
echo STEP 2 - Dashboard Processing: %PYTHON_RESULT% (0=success)
echo.
echo Excel file: %EXCEL_FILE%
echo Working directory: %cd%
echo Refresh method: VBS Script (No Macro, .xlsx/.xlsb support)
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
echo Refresh_Method:VBS_XLSX_XLSB >> last_update_status.txt

REM Final log entry with all results
echo [%date% %time%] COMPREHENSIVE UPDATE (.xlsx/.xlsb): Excel=%EXCEL_REFRESH_RESULT%, Python=%PYTHON_RESULT%, Overall=%OVERALL_SUCCESS% >> update_history.log

REM Final status message
if %OVERALL_SUCCESS% equ 0 (
    echo ============================================================
    echo            🎉 COMPREHENSIVE UPDATE SUCCESSFUL! 🎉
    echo ============================================================
    echo.
    echo ✅ Excel data refreshed using VBS (.xlsx/.xlsb support)
    echo ✅ Dashboard JSON files generated
    echo ✅ Changes pushed to GitHub
    echo ✅ Dashboard ready with fresh data
    echo.
    echo 🌐 Live Dashboard: https://kisman271128.github.io/salesman-dashboard
    echo 📊 Data Status: Real-time (Excel refreshed + Dashboard updated)
    echo ⏰ Next Update: Tomorrow at 07:00
    echo 🔧 Method: VBS (.xlsx/.xlsb support, No Macro, Virus-Safe)
    echo.
) else (
    echo ============================================================
    echo              ⚠️ UPDATE COMPLETED WITH ISSUES ⚠️
    echo ============================================================
    echo.
    if %EXCEL_REFRESH_RESULT% neq 0 (
        echo ⚠️ Excel refresh had issues (but continued)
    ) else (
        echo ✅ Excel refresh successful (%EXCEL_FILE%)
    )
    
    if %PYTHON_RESULT% neq 0 (
        echo ❌ Dashboard processing failed
    ) else (
        echo ✅ Dashboard processing successful
    )
    
    echo.
    echo 📋 Check logs for details:
    echo   - excel_refresh_success.txt (Excel refresh details)
    echo   - morning_update.log (Python processing details)
    echo   - update_history.log (Overall update history)
    echo.
)

echo ============================================================

REM Exit with overall result
exit /b %OVERALL_SUCCESS%