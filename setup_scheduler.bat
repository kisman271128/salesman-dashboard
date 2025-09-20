@echo off
REM Setup Windows Task Scheduler for Daily Dashboard Update
REM Run this script as Administrator

echo ============================================================
echo         SETUP TASK SCHEDULER - SALESMAN DASHBOARD
echo ============================================================
echo.

set TASK_NAME="Daily Dashboard Update"
set SCRIPT_PATH="C:\Dashboard\morning_update_automated.bat"
set LOG_PATH="C:\Dashboard\scheduler.log"

echo Setting up automated daily task...
echo.

REM Create the scheduled task
schtasks /create /tn %TASK_NAME% /tr %SCRIPT_PATH% /sc daily /st 07:00 /f /ru SYSTEM

if %errorlevel% equ 0 (
    echo ✅ Task created successfully!
    echo.
    echo Task Details:
    echo - Name: %TASK_NAME%
    echo - Schedule: Daily at 07:00 AM
    echo - Script: %SCRIPT_PATH%
    echo - User: SYSTEM (no login required)
    echo.
    
    echo To modify the schedule:
    echo schtasks /change /tn %TASK_NAME% /st [NEW_TIME]
    echo.
    echo To disable:
    echo schtasks /change /tn %TASK_NAME% /disable
    echo.
    echo To delete:
    echo schtasks /delete /tn %TASK_NAME% /f
    echo.
    
) else (
    echo ❌ Failed to create task!
    echo Make sure you run this script as Administrator.
    echo.
)

echo View current task:
schtasks /query /tn %TASK_NAME% /fo list

echo.
echo ============================================================
echo Setup complete! The dashboard will update automatically
echo every day at 07:00 AM.
echo ============================================================

pause