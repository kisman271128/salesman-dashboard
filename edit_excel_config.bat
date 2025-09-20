@echo off
chcp 65001 > nul 2>&1
color 0E
title QUICK CONFIG EDITOR - Excel Automation

echo.
echo ============================================================
echo              QUICK CONFIG EDITOR - EXCEL AUTOMATION
echo                    Update Excel Path/Filename
echo ============================================================
echo.

cd /d "C:\Dashboard"

REM Check if config file exists
if not exist "excel_config.txt" (
    echo Config file tidak ditemukan. Membuat file baru...
    goto :create_new
)

echo Current configuration:
echo ============================================================
type excel_config.txt | findstr /v "^#" | findstr /v "^$"
echo ============================================================
echo.

echo Pilihan:
echo 1. Edit folder Excel
echo 2. Edit nama file Excel  
echo 3. Edit pengaturan lainnya
echo 4. Lihat config lengkap
echo 5. Create new config
echo 6. Exit
echo.
set /p CHOICE=Pilih opsi (1-6): 

if "%CHOICE%"=="1" goto :edit_folder
if "%CHOICE%"=="2" goto :edit_filename
if "%CHOICE%"=="3" goto :edit_settings
if "%CHOICE%"=="4" goto :view_config
if "%CHOICE%"=="5" goto :create_new
if "%CHOICE%"=="6" goto :end
goto :main

:edit_folder
echo.
echo === EDIT FOLDER EXCEL ===
echo.
echo Current folder:
for /f "usebackq tokens=2 delims==" %%a in (`findstr "EXCEL_FOLDER" excel_config.txt`) do echo %%a
echo.
echo Contoh path:
echo C:\Dashboard\Reports
echo D:\Data\Excel\Monthly
echo C:\Users\%USERNAME%\Documents\Dashboard
echo.
set /p NEW_FOLDER=Masukkan folder baru: 

if "%NEW_FOLDER%"=="" (
    echo Folder tidak boleh kosong!
    goto :edit_folder
)

REM Update config file
powershell -Command "(Get-Content excel_config.txt) -replace 'EXCEL_FOLDER=.*', 'EXCEL_FOLDER=%NEW_FOLDER%' | Set-Content excel_config.txt"

echo.
echo ✅ Folder berhasil diupdate: %NEW_FOLDER%
goto :success

:edit_filename
echo.
echo === EDIT NAMA FILE EXCEL ===
echo.
echo Current filename:
for /f "usebackq tokens=2 delims==" %%a in (`findstr "EXCEL_FILENAME" excel_config.txt`) do echo %%a
echo.
echo Contoh nama file:
echo DashBoard Aug 25 KaliBer - Depo Tanjung.xlsm
echo DashBoard Sep 25 KaliBer - Depo Tanjung.xlsm
echo Report_Oktober_2025.xlsm
echo.
set /p NEW_FILENAME=Masukkan nama file baru (dengan .xlsm): 

if "%NEW_FILENAME%"=="" (
    echo Nama file tidak boleh kosong!
    goto :edit_filename
)

REM Check if filename has .xlsm extension
echo %NEW_FILENAME% | findstr /i "\.xlsm$" >nul
if %errorlevel% neq 0 (
    echo WARNING: File harus berekstensi .xlsm
    echo Menambahkan ekstensi otomatis...
    set NEW_FILENAME=%NEW_FILENAME%.xlsm
)

REM Update config file
powershell -Command "(Get-Content excel_config.txt) -replace 'EXCEL_FILENAME=.*', 'EXCEL_FILENAME=%NEW_FILENAME%' | Set-Content excel_config.txt"

echo.
echo ✅ Nama file berhasil diupdate: %NEW_FILENAME%
goto :success

:edit_settings
echo.
echo === EDIT PENGATURAN LAINNYA ===
echo.
echo 1. Refresh wait time (detik)
echo 2. Enable/disable backup
echo 3. Log level (detail/simple)
echo.
set /p SETTING_CHOICE=Pilih setting (1-3): 

if "%SETTING_CHOICE%"=="1" goto :edit_refresh_time
if "%SETTING_CHOICE%"=="2" goto :edit_backup
if "%SETTING_CHOICE%"=="3" goto :edit_log_level
goto :edit_settings

:edit_refresh_time
echo.
for /f "usebackq tokens=2 delims==" %%a in (`findstr "REFRESH_WAIT_TIME" excel_config.txt`) do echo Current refresh time: %%a seconds
echo.
echo Recommended:
echo - Simple data: 15-30 seconds
echo - Complex data: 60-120 seconds
echo - Very complex: 180+ seconds
echo.
set /p NEW_TIME=Masukkan waktu refresh (detik): 

if "%NEW_TIME%"=="" goto :edit_refresh_time

REM Validate numeric input
echo %NEW_TIME%| findstr /r "^[0-9][0-9]*$" >nul
if %errorlevel% neq 0 (
    echo Input harus berupa angka!
    goto :edit_refresh_time
)

powershell -Command "(Get-Content excel_config.txt) -replace 'REFRESH_WAIT_TIME=.*', 'REFRESH_WAIT_TIME=%NEW_TIME%' | Set-Content excel_config.txt"
echo ✅ Refresh time diupdate: %NEW_TIME% seconds
goto :success

:edit_backup
echo.
for /f "usebackq tokens=2 delims==" %%a in (`findstr "CREATE_BACKUP" excel_config.txt`) do echo Current backup setting: %%a
echo.
echo 1. Enable backup (true)
echo 2. Disable backup (false)
echo.
set /p BACKUP_CHOICE=Pilih (1-2): 

if "%BACKUP_CHOICE%"=="1" (
    powershell -Command "(Get-Content excel_config.txt) -replace 'CREATE_BACKUP=.*', 'CREATE_BACKUP=true' | Set-Content excel_config.txt"
    echo ✅ Backup enabled
) else if "%BACKUP_CHOICE%"=="2" (
    powershell -Command "(Get-Content excel_config.txt) -replace 'CREATE_BACKUP=.*', 'CREATE_BACKUP=false' | Set-Content excel_config.txt"
    echo ✅ Backup disabled
) else (
    goto :edit_backup
)
goto :success

:edit_log_level
echo.
for /f "usebackq tokens=2 delims==" %%a in (`findstr "LOG_LEVEL" excel_config.txt`) do echo Current log level: %%a
echo.
echo 1. Detail logging (detail)
echo 2. Simple logging (simple)
echo.
set /p LOG_CHOICE=Pilih (1-2): 

if "%LOG_CHOICE%"=="1" (
    powershell -Command "(Get-Content excel_config.txt) -replace 'LOG_LEVEL=.*', 'LOG_LEVEL=detail' | Set-Content excel_config.txt"
    echo ✅ Log level: detail
) else if "%LOG_CHOICE%"=="2" (
    powershell -Command "(Get-Content excel_config.txt) -replace 'LOG_LEVEL=.*', 'LOG_LEVEL=simple' | Set-Content excel_config.txt"
    echo ✅ Log level: simple
) else (
    goto :edit_log_level
)
goto :success

:view_config
echo.
echo === CURRENT FULL CONFIGURATION ===
echo ============================================================
type excel_config.txt
echo ============================================================
echo.
pause
goto :main

:create_new
echo.
echo === CREATE NEW CONFIG ===
echo.
set /p FOLDER=Masukkan folder Excel (contoh: C:\Dashboard\Reports): 
set /p FILENAME=Masukkan nama file Excel (contoh: Dashboard Aug 25.xlsm): 

if "%FOLDER%"=="" goto :create_new
if "%FILENAME%"=="" goto :create_new

REM Create new config file
echo # ============================================================ > excel_config.txt
echo # KONFIGURASI EXCEL MACRO AUTOMATION >> excel_config.txt
echo # Edit file ini saat nama/lokasi Excel berubah >> excel_config.txt
echo # ============================================================ >> excel_config.txt
echo. >> excel_config.txt
echo # LOKASI FOLDER EXCEL (gunakan full path) >> excel_config.txt
echo EXCEL_FOLDER=%FOLDER% >> excel_config.txt
echo. >> excel_config.txt
echo # NAMA FILE EXCEL (dengan ekstensi) >> excel_config.txt
echo EXCEL_FILENAME=%FILENAME% >> excel_config.txt
echo. >> excel_config.txt
echo # WAKTU REFRESH (dalam detik) >> excel_config.txt
echo REFRESH_WAIT_TIME=30 >> excel_config.txt
echo. >> excel_config.txt
echo # BACKUP ENABLED (true/false) >> excel_config.txt
echo CREATE_BACKUP=true >> excel_config.txt
echo. >> excel_config.txt
echo # LOG LEVEL (detail/simple) >> excel_config.txt
echo LOG_LEVEL=detail >> excel_config.txt

echo ✅ Config file baru berhasil dibuat!
goto :success

:success
echo.
echo === UPDATED CONFIGURATION ===
echo ============================================================
for /f "usebackq tokens=1,2 delims==" %%a in ("excel_config.txt") do (
    if not "%%a"=="" if not "%%a:~0,1%"=="#" (
        echo %%a = %%b
    )
)
echo ============================================================
echo.
echo ✅ Konfigurasi berhasil diupdate!
echo.
echo NEXT STEPS:
echo 1. Test manual: schtasks /run /tn "ExcelMacro400"
echo 2. Check status: type last_macro_status.txt
echo 3. Automation akan menggunakan config baru besok jam 4:00 AM
echo.
pause
goto :end

:main
cls
goto :start

:end
echo.
echo Terima kasih! Config editor selesai.
echo.
pause