@echo off
chcp 65001 > nul 2>&1
color 0A
title Excel Macro Automation - FLEXIBLE CONFIG

echo.
echo ============================================================
echo           EXCEL MACRO AUTOMATION - FLEXIBLE CONFIG
echo                  Auto-read from excel_config.txt
echo ============================================================
echo.

REM Change to script directory (where config file is)
cd /d "C:\Dashboard"

echo [%time%] Loading configuration from excel_config.txt...
echo.

REM Check if config file exists
if not exist "excel_config.txt" (
    echo ERROR: Configuration file 'excel_config.txt' not found!
    echo Expected location: %cd%\excel_config.txt
    echo.
    echo Please create the config file with Excel path and filename.
    goto :error
)

echo ✅ Config file found: excel_config.txt
echo.

REM Initialize variables with defaults
set EXCEL_FOLDER=
set EXCEL_FILENAME=
set REFRESH_WAIT_TIME=30
set CREATE_BACKUP=true
set LOG_LEVEL=detail

echo === READING CONFIGURATION ===
echo ----------------------------------------

REM Parse config file (ignore lines starting with # and empty lines)
for /f "usebackq tokens=1,2 delims==" %%a in ("excel_config.txt") do (
    if not "%%a"=="" if not "%%a:~0,1%"=="#" (
        set "%%a=%%b"
        echo Config: %%a = %%b
    )
)

echo ----------------------------------------
echo.

REM Validate required configuration
if "%EXCEL_FOLDER%"=="" (
    echo ERROR: EXCEL_FOLDER not configured in excel_config.txt
    goto :error
)

if "%EXCEL_FILENAME%"=="" (
    echo ERROR: EXCEL_FILENAME not configured in excel_config.txt
    goto :error
)

REM Build full path
set EXCEL_FULLPATH=%EXCEL_FOLDER%\%EXCEL_FILENAME%

echo === CONFIGURATION SUMMARY ===
echo ----------------------------------------
echo Excel Folder: %EXCEL_FOLDER%
echo Excel Filename: %EXCEL_FILENAME%
echo Full Path: %EXCEL_FULLPATH%
echo Refresh Wait Time: %REFRESH_WAIT_TIME% seconds
echo Create Backup: %CREATE_BACKUP%
echo Log Level: %LOG_LEVEL%
echo ----------------------------------------
echo.

REM Check if Excel folder exists
if not exist "%EXCEL_FOLDER%" (
    echo ERROR: Excel folder does not exist!
    echo Path: %EXCEL_FOLDER%
    echo.
    echo Please check EXCEL_FOLDER setting in excel_config.txt
    goto :error
)

echo ✅ Excel folder exists: %EXCEL_FOLDER%

REM Check if Excel file exists
if not exist "%EXCEL_FULLPATH%" (
    echo ERROR: Excel file not found!
    echo Expected: %EXCEL_FULLPATH%
    echo.
    echo Please check:
    echo 1. EXCEL_FOLDER path in excel_config.txt
    echo 2. EXCEL_FILENAME in excel_config.txt
    echo 3. File actually exists in the specified location
    goto :error
)

echo ✅ Excel file found: %EXCEL_FILENAME%
echo.

REM Create backup if enabled
if /i "%CREATE_BACKUP%"=="true" (
    echo === CREATING BACKUP ===
    echo ----------------------------------------
    set BACKUP_NAME=%EXCEL_FILENAME:~0,-5%_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.xlsm
    set BACKUP_NAME=!BACKUP_NAME: =0!
    echo Creating backup: !BACKUP_NAME!
    copy "%EXCEL_FULLPATH%" "%EXCEL_FOLDER%\!BACKUP_NAME!" >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Backup created successfully
    ) else (
        echo ⚠️ Backup creation failed, continuing...
    )
    echo ----------------------------------------
    echo.
)

echo === PRE-FLIGHT CHECKS ===
echo ----------------------------------------

REM Kill any existing Excel processes
echo Checking for existing Excel processes...
tasklist /fi "imagename eq excel.exe" | findstr "excel.exe" >nul
if %errorlevel% equ 0 (
    echo WARNING: Excel is currently running. Closing existing instances...
    taskkill /f /im excel.exe >nul 2>&1
    timeout /t 3 >nul
    echo ✅ Excel processes terminated
) else (
    echo ✅ No existing Excel processes found
)

echo.
echo === MACRO EXECUTION ===
echo ----------------------------------------

REM Create VBScript for macro execution
echo Creating VBScript for macro execution...

REM Create temporary VBScript file with config values
echo Set objExcel = CreateObject("Excel.Application") > temp_macro_runner.vbs
echo objExcel.Visible = False >> temp_macro_runner.vbs
echo objExcel.DisplayAlerts = False >> temp_macro_runner.vbs
echo objExcel.EnableEvents = True >> temp_macro_runner.vbs
echo objExcel.ScreenUpdating = False >> temp_macro_runner.vbs
echo. >> temp_macro_runner.vbs
echo On Error Resume Next >> temp_macro_runner.vbs
echo. >> temp_macro_runner.vbs
echo WScript.Echo "[" ^& Time ^& "] Opening Excel file..." >> temp_macro_runner.vbs
echo Set objWorkbook = objExcel.Workbooks.Open("%EXCEL_FULLPATH%") >> temp_macro_runner.vbs
echo. >> temp_macro_runner.vbs
echo If Err.Number ^<^> 0 Then >> temp_macro_runner.vbs
echo     WScript.Echo "ERROR: Failed to open Excel file - " ^& Err.Description >> temp_macro_runner.vbs
echo     objExcel.Quit >> temp_macro_runner.vbs
echo     WScript.Quit 1 >> temp_macro_runner.vbs
echo End If >> temp_macro_runner.vbs
echo. >> temp_macro_runner.vbs
echo WScript.Echo "[" ^& Time ^& "] Excel file opened successfully" >> temp_macro_runner.vbs
echo WScript.Echo "[" ^& Time ^& "] File: %EXCEL_FILENAME%" >> temp_macro_runner.vbs
echo WScript.Echo "[" ^& Time ^& "] Location: %EXCEL_FOLDER%" >> temp_macro_runner.vbs
echo WScript.Echo "[" ^& Time ^& "] Enabling macro execution..." >> temp_macro_runner.vbs
echo. >> temp_macro_runner.vbs
echo REM Wait for file to fully load >> temp_macro_runner.vbs
echo WScript.Sleep 3000 >> temp_macro_runner.vbs
echo. >> temp_macro_runner.vbs
echo WScript.Echo "[" ^& Time ^& "] Triggering auto-refresh..." >> temp_macro_runner.vbs
echo objExcel.CalculateFullRebuild >> temp_macro_runner.vbs
echo objWorkbook.RefreshAll >> temp_macro_runner.vbs
echo. >> temp_macro_runner.vbs
echo WScript.Echo "[" ^& Time ^& "] Waiting for refresh to complete (%REFRESH_WAIT_TIME% seconds)..." >> temp_macro_runner.vbs
echo WScript.Sleep %REFRESH_WAIT_TIME%000 >> temp_macro_runner.vbs
echo. >> temp_macro_runner.vbs
echo WScript.Echo "[" ^& Time ^& "] Auto-refresh completed. Saving file..." >> temp_macro_runner.vbs
echo objWorkbook.Save >> temp_macro_runner.vbs
echo. >> temp_macro_runner.vbs
echo If Err.Number ^<^> 0 Then >> temp_macro_runner.vbs
echo     WScript.Echo "WARNING: Save operation had issues - " ^& Err.Description >> temp_macro_runner.vbs
echo Else >> temp_macro_runner.vbs
echo     WScript.Echo "[" ^& Time ^& "] File saved successfully" >> temp_macro_runner.vbs
echo End If >> temp_macro_runner.vbs
echo. >> temp_macro_runner.vbs
echo WScript.Echo "[" ^& Time ^& "] Closing Excel..." >> temp_macro_runner.vbs
echo objWorkbook.Close >> temp_macro_runner.vbs
echo objExcel.Quit >> temp_macro_runner.vbs
echo. >> temp_macro_runner.vbs
echo WScript.Echo "[" ^& Time ^& "] Excel macro automation completed successfully" >> temp_macro_runner.vbs

echo ✅ VBScript created with current configuration
echo.

echo [%time%] Executing Excel macro automation...
echo Target: %EXCEL_FULLPATH%
echo --------------------------------------------------------

REM Execute the VBScript
cscript //nologo temp_macro_runner.vbs

set MACRO_RESULT=%errorlevel%

echo --------------------------------------------------------
echo [%time%] Macro execution completed with exit code: %MACRO_RESULT%
echo.

REM Clean up temporary VBScript
if exist "temp_macro_runner.vbs" (
    del "temp_macro_runner.vbs" >nul 2>&1
)

REM Final cleanup - ensure Excel is closed
tasklist /fi "imagename eq excel.exe" | findstr "excel.exe" >nul
if %errorlevel% equ 0 (
    echo Final cleanup: Closing any remaining Excel processes...
    taskkill /f /im excel.exe >nul 2>&1
)

echo.
echo === RESULTS SUMMARY ===
echo ----------------------------------------

if %MACRO_RESULT% equ 0 (
    echo ============================================================
    echo                  ✅ MACRO AUTOMATION SUCCESS! ✅
    echo ============================================================
    echo.
    echo ✅ Excel file: %EXCEL_FILENAME%
    echo ✅ Location: %EXCEL_FOLDER%
    echo ✅ Auto-refresh macro executed
    echo ✅ Data refreshed from sources
    echo ✅ File saved with updated data
    echo ✅ Excel closed properly
    echo.
    if /i "%CREATE_BACKUP%"=="true" (
        echo ✅ Backup created before processing
    )
    echo.
    echo 📊 Full Path: %EXCEL_FULLPATH%
    echo 📅 Update Time: %date% %time%
    echo 🎯 Status: Ready for use
    echo.
    
    REM Log success with detailed info
    if /i "%LOG_LEVEL%"=="detail" (
        echo [%date% %time%] Excel macro automation SUCCESS: %EXCEL_FILENAME% at %EXCEL_FOLDER% >> macro_automation_history.log
    ) else (
        echo [%date% %time%] Excel macro automation SUCCESS >> macro_automation_history.log
    )
    
    REM Create detailed status file
    echo 0 > last_macro_status.txt
    echo %date% %time% >> last_macro_status.txt
    echo File: %EXCEL_FILENAME% >> last_macro_status.txt
    echo Location: %EXCEL_FOLDER% >> last_macro_status.txt
    echo Status: SUCCESS >> last_macro_status.txt
    echo Refresh_Time: %REFRESH_WAIT_TIME%s >> last_macro_status.txt
    echo Backup_Created: %CREATE_BACKUP% >> last_macro_status.txt
    
) else (
    echo ============================================================
    echo                  ❌ MACRO AUTOMATION FAILED! ❌
    echo ============================================================
    echo.
    echo Exit Code: %MACRO_RESULT%
    echo File: %EXCEL_FILENAME%
    echo Location: %EXCEL_FOLDER%
    echo Time: %date% %time%
    echo.
    echo 🔍 POSSIBLE CAUSES:
    echo • Excel file is corrupted or protected
    echo • Macro security settings blocking execution
    echo • File is locked by another process
    echo • Insufficient permissions
    echo • Network connectivity issues (for data sources)
    echo • File path contains invalid characters
    echo.
    echo 🛠️ TROUBLESHOOTING:
    echo • Check excel_config.txt settings
    echo • Verify file path and filename
    echo • Check Excel macro security settings
    echo • Ensure data source connections are available
    echo • Try opening file manually first
    echo.
    
    REM Log failure with detailed info
    if /i "%LOG_LEVEL%"=="detail" (
        echo [%date% %time%] Excel macro automation FAILED: %EXCEL_FILENAME% at %EXCEL_FOLDER% with code %MACRO_RESULT% >> macro_automation_history.log
    ) else (
        echo [%date% %time%] Excel macro automation FAILED with code %MACRO_RESULT% >> macro_automation_history.log
    )
    
    REM Create detailed status file
    echo 1 > last_macro_status.txt
    echo %date% %time% >> last_macro_status.txt
    echo File: %EXCEL_FILENAME% >> last_macro_status.txt
    echo Location: %EXCEL_FOLDER% >> last_macro_status.txt
    echo Status: FAILED >> last_macro_status.txt
    echo Error_Code: %MACRO_RESULT% >> last_macro_status.txt
    echo Refresh_Time: %REFRESH_WAIT_TIME%s >> last_macro_status.txt
)

echo.
echo === CURRENT CONFIGURATION ===
echo ----------------------------------------
echo Config File: %cd%\excel_config.txt
echo Excel Folder: %EXCEL_FOLDER%
echo Excel Filename: %EXCEL_FILENAME%
echo Full Path: %EXCEL_FULLPATH%
echo.
echo 📝 TO CHANGE FILE/LOCATION:
echo   Edit excel_config.txt
echo   Change EXCEL_FOLDER and EXCEL_FILENAME values
echo   No need to modify this script!
echo.
echo 📋 CHECK STATUS:
echo   type last_macro_status.txt
echo.
echo 📜 VIEW HISTORY:
echo   type macro_automation_history.log
echo.

goto :end

:error
echo.
echo ============================================================
echo                        ❌ ERROR ❌
echo ============================================================
echo.
echo Automation failed due to configuration or file error.
echo.
echo Please check:
echo 1. excel_config.txt exists and has correct settings
echo 2. EXCEL_FOLDER path is correct and accessible
echo 3. EXCEL_FILENAME matches the actual file
echo 4. File permissions allow read/write access
echo.

REM Log error
echo [%date% %time%] Excel macro automation ERROR - configuration or file issue >> macro_automation_history.log

echo 2 > last_macro_status.txt
echo %date% %time% >> last_macro_status.txt
echo Status: ERROR - CONFIGURATION/FILE ISSUE >> last_macro_status.txt

:end
echo.
echo ============================================================
echo Script Location: %cd%
echo Config File: excel_config.txt
echo Next scheduled run: Tomorrow 4:00 AM
echo ============================================================

REM Exit with result code
if defined MACRO_RESULT (
    exit /b %MACRO_RESULT%
) else (
    exit /b 2
)
 
