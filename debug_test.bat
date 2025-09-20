@echo off
echo === LOGGING DEBUG TEST ===
echo Current directory: %cd%
echo Current date: %date%
echo Current time: %time%

echo.
echo Testing file write permissions...

REM Test 1: Can we write to update_history.log?
echo [%date% %time%] DEBUG TEST - Can write to update_history.log >> update_history.log
if %errorlevel% equ 0 (
    echo ✅ SUCCESS: Can write to update_history.log
) else (
    echo ❌ FAILED: Cannot write to update_history.log
)

REM Test 2: Can we write to last_update_status.txt?
echo DEBUG TEST > last_update_status.txt
echo %date% %time% >> last_update_status.txt
if %errorlevel% equ 0 (
    echo ✅ SUCCESS: Can write to last_update_status.txt
) else (
    echo ❌ FAILED: Cannot write to last_update_status.txt
)

REM Test 3: Check if Python script exists and runs
echo.
echo Testing Python script...
if exist "morning_update.py" (
    echo ✅ Python script exists
    REM Quick dry run test
    python -c "print('Python working'); exit(0)"
    set TEST_EXIT=%errorlevel%
    echo Exit code test: %TEST_EXIT%
) else (
    echo ❌ Python script NOT found
)

echo.
echo === DEBUG TEST COMPLETED ===
echo Check the log files to see if writes worked.
pause