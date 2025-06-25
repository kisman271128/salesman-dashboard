@echo off
chcp 65001 > nul 2>&1
color 0A
title Morning Batch Update - Salesman Dashboard

echo.
echo ============================================================
echo           MORNING BATCH UPDATE - SALESMAN DASHBOARD
echo                    Depo Tanjung - Region Kalimantan
echo ============================================================
echo.

REM Change to YOUR repository directory
cd /d "C:\Dashboard"

echo [%time%] Starting morning update...
echo.

REM Pre-flight checks
echo === PRE-FLIGHT CHECKS ===

REM Check if Python is available
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found! Please install Python first.
    echo Download from: https://python.org/downloads
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
echo ✓ Python found

REM Check if we're in the right directory
if not exist ".git" (
    echo ❌ ERROR: Not in repository directory!
    echo Please make sure you're in C:\Dashboard
    echo Current directory: %cd%
    pause
    exit /b 1
)
echo ✓ Git repository found

REM Check if Excel file exists
if not exist "DbaseSalesmanWebApp.xlsm" (
    if not exist "DbaseSalesmanWebApp.xlsx" (
        echo ❌ ERROR: Excel file not found!
        echo.
        echo Please copy your Excel file to this directory:
        echo %cd%\DbaseSalesmanWebApp.xlsm
        echo or %cd%\DbaseSalesmanWebApp.xlsx
        echo.
        pause
        exit /b 1
    ) else (
        echo ✓ Excel file found (.xlsx)
        set EXCEL_FILE=DbaseSalesmanWebApp.xlsx
    )
) else (
    echo ✓ Excel file found (.xlsm)
    set EXCEL_FILE=DbaseSalesmanWebApp.xlsm
)

REM Check if Python script exists
if not exist "morning_update.py" (
    echo ❌ ERROR: Python script 'morning_update.py' not found!
    echo Please copy the Python script to this directory.
    pause
    exit /b 1
)
echo ✓ Python script found

REM Check if Excel is currently open
echo Checking if Excel is running...
tasklist | findstr /i excel >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  WARNING: Excel is currently running!
    echo Please close Excel completely before continuing.
    echo.
    echo Press any key to continue anyway, or Ctrl+C to cancel...
    pause >nul
    echo.
)

echo.
echo === DEPENDENCY CHECKS ===

REM Check if required Python packages are installed
echo Checking Python dependencies...
python -c "import pandas, json, subprocess, logging" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  WARNING: Missing Python packages. Installing...
    pip install pandas openpyxl xlrd gitpython requests
    if %errorlevel% neq 0 (
        echo ❌ ERROR: Failed to install Python packages!
        echo Please run manually: pip install pandas openpyxl xlrd gitpython requests
        pause
        exit /b 1
    )
)
echo ✓ Python packages ready

echo.
echo === RUNNING UPDATE ===

REM Clear any previous log
if exist "morning_update.log" (
    echo Clearing previous log...
    del "morning_update.log" >nul 2>&1
)

REM Run the Python script with detailed error capture
echo [%time%] Running Python script...
echo --------------------------------------------------------
python morning_update.py
set SCRIPT_RESULT=%errorlevel%
echo --------------------------------------------------------
echo [%time%] Python script completed with exit code: %SCRIPT_RESULT%

REM Check if script was successful
if %SCRIPT_RESULT% equ 0 (
    echo.
    echo ============================================================
    echo                     ✅ UPDATE SUCCESSFUL!
    echo ============================================================
    echo.
    echo 📱 Dashboard URL: 
    echo    https://kisman271128.github.io/salesman-dashboard
    echo.
    echo 📊 Data updated successfully!
    echo 🔔 Team can now see latest numbers.
    echo ⏰ Next update: Tomorrow morning at 07:00
    echo.
    echo 💡 TIP: Bookmark this batch file for daily updates!
    echo    Right-click → Send to → Desktop (create shortcut)
    echo.
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo                      ❌ UPDATE FAILED!
    echo ============================================================
    echo.
    echo Exit code: %SCRIPT_RESULT%
    echo.
    
    REM Show recent log entries
    if exist "morning_update.log" (
        echo 📋 Recent log entries:
        echo ----------------------------------------
        powershell "Get-Content morning_update.log | Select-Object -Last 10"
        echo ----------------------------------------
        echo.
    )
    
    echo 🔍 Common Solutions:
    echo 1. Make sure Excel file is saved and closed completely
    echo 2. Check internet connection for GitHub push
    echo 3. Verify Excel sheets: d.dashboard, d.performance, etc.
    echo 4. Run: git status (to check repository state)
    echo 5. Check the log file: morning_update.log
    echo.
    
    REM Additional diagnostics
    echo 🔧 Quick Diagnostics:
    echo ----------------------------------------
    
    echo Git status:
    git status --porcelain
    
    echo.
    echo Data directory contents:
    if exist "data" (
        dir "data" /b
    ) else (
        echo (data directory not found)
    )
    
    echo.
    echo Excel file info:
    if exist "%EXCEL_FILE%" (
        dir "%EXCEL_FILE%" | findstr /v "Directory"
    ) else (
        echo (Excel file not found)
    )
    
    echo ----------------------------------------
    echo.
    echo 📞 Contact IT support if problem persists.
    echo.
)

echo.
echo ⏰ Started at: %time%
echo 📅 Date: %date%
echo 📂 Directory: %cd%
echo 📄 Excel file: %EXCEL_FILE%
echo.

REM Option to view full log
if exist "morning_update.log" (
    echo Would you like to view the full log file? (Y/N)
    set /p viewlog=Enter choice: 
    if /i "%viewlog%"=="Y" (
        echo.
        echo === FULL LOG ===
        type "morning_update.log"
        echo === END LOG ===
        echo.
    )
)

echo Press any key to close...
pause >nul