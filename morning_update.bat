@echo off
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

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found! Please install Python first.
    echo Download from: https://python.org/downloads
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist ".git" (
    echo ❌ ERROR: Not in repository directory!
    echo Please make sure you're in C:\salesman-dashboard
    echo Run: cd /d "C:\salesman-dashboard"
    pause
    exit /b 1
)

REM Check if Excel file exists
if not exist "DbaseSalesmanWebApp.xlsm" (
    echo ❌ ERROR: Excel file 'DbaseSalesmanWebApp.xlsm' not found!
    echo.
    echo Please copy your Excel file to this directory:
    echo C:\salesman-dashboard\DbaseSalesmanWebApp.xlsm
    echo.
    pause
    exit /b 1
)

REM Check if Python script exists
if not exist "morning_update.py" (
    echo ❌ ERROR: Python script 'morning_update.py' not found!
    echo Please copy the Python script to this directory.
    pause
    exit /b 1
)

echo 📊 Excel file found ✓
echo 🐍 Python ready ✓
echo 📁 Repository ready ✓
echo.

REM Check if required Python packages are installed
echo [%time%] Checking Python dependencies...
python -c "import pandas, json, subprocess" >nul 2>&1
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

echo 📦 Python packages ready ✓
echo.

REM Run the Python script
echo [%time%] Running Python script...
echo --------------------------------------------------------
python morning_update.py
set SCRIPT_RESULT=%errorlevel%
echo --------------------------------------------------------

REM Check if script was successful
if %SCRIPT_RESULT% equ 0 (
    echo.
    echo ============================================================
    echo                     ✅ UPDATE SUCCESSFUL!
    echo ============================================================
    echo.
    echo 📱 Dashboard URL: 
    echo    https://[USERNAME].github.io/salesman-dashboard
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
    echo 🔍 Common Solutions:
    echo 1. Make sure Excel file is saved and closed
    echo 2. Check internet connection for GitHub push
    echo 3. Verify Excel sheets: d.dashboard, d.performance, etc.
    echo 4. Run: git status (to check repository state)
    echo.
    echo 📞 Contact IT support if problem persists.
    echo.
)

echo.
echo ⏰ Started at: %time%
echo 📅 Date: %date%
echo.
echo Press any key to close...
pause >nul