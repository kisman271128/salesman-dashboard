@echo off
chcp 65001 > nul 2>&1
color 0B
title AUTO SETUP - Task Scheduler 04:30 AM - Dashboard Update

echo.
echo ============================================================
echo              AUTO SETUP TASK SCHEDULER - 04:30 AM
echo           Morning Dashboard Update - Depo Tanjung
echo                      FULLY AUTOMATED
echo ============================================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Script harus dijalankan sebagai Administrator!
    echo.
    echo SOLUSI CEPAT:
    echo 1. Klik kanan file ini
    echo 2. Pilih "Run as administrator"
    echo 3. Script akan langsung setup otomatis
    echo.
    pause
    exit /b 1
)

echo [%time%] Starting automated setup for 04:30 AM schedule...

REM Get current directory (dashboard folder)
set DASHBOARD_DIR=%cd%
set BAT_FILE=%DASHBOARD_DIR%\morning_update_automated.bat

echo Dashboard Directory: %DASHBOARD_DIR%
echo Target Batch File: %BAT_FILE%

REM Check if batch file exists
if not exist "%BAT_FILE%" (
    echo ERROR: File morning_update_automated.bat tidak ditemukan!
    echo Expected location: %BAT_FILE%
    echo.
    echo SOLUSI:
    echo 1. Pastikan file morning_update_automated.bat ada di folder ini
    echo 2. Jalankan script ini dari folder dashboard yang benar
    echo.
    pause
    exit /b 1
)

echo OK: Batch file found
echo.

REM FIXED CONFIGURATION - Removed problematic /sd parameter
set TASK_NAME=Dashboard430
set TASK_DESCRIPTION=Auto update dashboard salesman setiap hari jam 04:30 AM
set START_TIME=04:30
set USER_ACCOUNT=%USERNAME%

echo ============================================================
echo                    AUTO CONFIGURATION
echo ============================================================
echo Task Name        : %TASK_NAME%
echo Description      : %TASK_DESCRIPTION%
echo Schedule         : DAILY at %START_TIME% (04:30 AM)
echo User Account     : %USER_ACCOUNT%
echo Batch File       : %BAT_FILE%
echo Working Directory: %DASHBOARD_DIR%
echo ============================================================
echo.
echo [%time%] Proceeding with automatic setup...
echo.

REM Delete existing task if exists
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorlevel% equ 0 (
    echo INFO: Task "%TASK_NAME%" sudah ada. Menghapus task lama...
    schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1
    if %errorlevel% equ 0 (
        echo OK: Task lama berhasil dihapus
    ) else (
        echo WARNING: Gagal menghapus task lama, melanjutkan...
    )
)

REM Create new scheduled task - FIXED: Removed /sd parameter that caused date format error
echo [%time%] Creating scheduled task for 04:30 AM...

schtasks /create ^
    /tn "%TASK_NAME%" ^
    /tr "\"%BAT_FILE%\"" ^
    /sc daily ^
    /st %START_TIME% ^
    /ru "%USER_ACCOUNT%" ^
    /rl highest ^
    /f

set TASK_RESULT=%errorlevel%

if %TASK_RESULT% equ 0 (
    echo.
    echo ============================================================
    echo            🌅 SETUP BERHASIL - 04:30 AM! 🌅
    echo ============================================================
    echo.
    echo ✅ Task "%TASK_NAME%" berhasil dibuat
    echo ✅ Jadwal: SETIAP HARI JAM 04:30 AM (PAGI BUTA!)
    echo ✅ User: %USER_ACCOUNT%
    echo ✅ File: %BAT_FILE%
    echo ✅ Privilege: Highest (Administrator)
    echo.
    echo 🎯 INFORMASI PENTING:
    echo • Dashboard akan update otomatis setiap jam 04:30 AM
    echo • Computer HARUS NYALA saat jam 04:30 AM
    echo • Excel akan di-refresh + Dashboard di-update
    echo • Hasil akan di-push ke GitHub otomatis
    echo • Log tersimpan di folder dashboard
    echo.
    echo 🔧 MANAJEMEN TASK:
    echo • Lihat task: Win + R → taskschd.msc
    echo • Cari: %TASK_NAME%
    echo • Test manual: Klik kanan → Run
    echo.
    
    REM Show task details untuk konfirmasi
    echo 📋 DETAIL TASK YANG TELAH DIBUAT:
    echo ----------------------------------------
    schtasks /query /tn "%TASK_NAME%" /fo LIST 2>nul | findstr /i "TaskName Schedule Next"
    echo ----------------------------------------
    
    echo.
    echo 🎉 DASHBOARD SIAP UPDATE OTOMATIS JAM 04:30 AM! 🎉
    
) else (
    echo.
    echo ============================================================
    echo                ❌ SETUP GAGAL! ❌
    echo ============================================================
    echo.
    echo Error Code: %TASK_RESULT%
    echo.
    echo 🔍 DIAGNOSIS OTOMATIS:
    echo • Script status: Berjalan sebagai Administrator ✅
    echo • Batch file: %BAT_FILE%
    
    if exist "%BAT_FILE%" (
        echo • File exists: ✅
    ) else (
        echo • File exists: ❌
    )
    
    echo • Working directory: %DASHBOARD_DIR%
    echo.
    echo 💡 KEMUNGKINAN PENYEBAB:
    echo • User account permission issue
    echo • Windows Task Scheduler service tidak aktif
    echo • Antivirus blocking task creation
    echo.
    echo 🛠️ SOLUSI ALTERNATIF:
    echo 1. Restart computer sebagai Administrator
    echo 2. Disable antivirus sementara
    echo 3. Manual setup via Task Scheduler GUI
    echo 4. Coba jalankan: services.msc → cek Task Scheduler service
    echo.
)

echo.
echo ============================================================
echo                   QUICK REFERENCE
echo ============================================================
echo.
echo 📱 PERINTAH BERGUNA:
echo.
echo LIHAT STATUS TASK:
echo   schtasks /query /tn "%TASK_NAME%"
echo.
echo JALANKAN SEKARANG (TEST):
echo   schtasks /run /tn "%TASK_NAME%"
echo.
echo HAPUS TASK:
echo   schtasks /delete /tn "%TASK_NAME%" /f
echo.
echo BUKA TASK SCHEDULER GUI:
echo   taskschd.msc
echo.
echo 🌐 DASHBOARD URL:
echo   https://kisman271128.github.io/salesman-dashboard
echo.
echo ⏰ JADWAL BERIKUTNYA: Besok jam 04:30 AM
echo.

REM Create quick info file
echo TASK_NAME=%TASK_NAME% > task_scheduler_info.txt
echo SCHEDULE_TIME=04:30 AM >> task_scheduler_info.txt
echo SETUP_DATE=%date% %time% >> task_scheduler_info.txt
echo SETUP_STATUS=%TASK_RESULT% >> task_scheduler_info.txt

echo 📁 Info tersimpan di: task_scheduler_info.txt
echo.
echo ============================================================

if %TASK_RESULT% equ 0 (
    echo 🎯 SETUP SUKSES! Dashboard akan update otomatis jam 04:30 AM
    echo.
    echo Script akan tertutup otomatis dalam 10 detik...
    timeout /t 10 >nul
) else (
    echo ⚠️ Setup gagal, coba lagi atau setup manual
    echo.
    pause
)

exit /b %TASK_RESULT%