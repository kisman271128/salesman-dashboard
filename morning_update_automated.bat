@echo off
title MORNING UPDATE - DASHBOARD SALESMAN
echo.
echo ============================================================
echo          MORNING UPDATE OTOMATIS - DASHBOARD SALESMAN
echo                   Depo Tanjung - Region Kalimantan
echo                   VBS EXCEL REFRESH (.xlsx/.xlsb)
echo ============================================================
echo.

echo [ %time% ] Memulai proses menyeluruh...
echo.

:: === Cek Pemeriksaan Awal ===
echo Memeriksa Python...
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan. Pastikan Python sudah terinstal dan ada di PATH.
    pause
    exit /b
) else (
    echo OK: Python ditemukan
)

echo Memeriksa repository Git...
if exist .git (
    echo OK: Repository Git ditemukan
) else (
    echo PERINGATAN: Repository Git tidak ditemukan
)

echo Memeriksa script VBS refresh...
if exist excel_refresh_all.vbs (
    echo OK: Script VBS ditemukan
) else (
    echo ERROR: Script VBS excel_refresh_all.vbs tidak ada
    pause
    exit /b
)

echo.
echo === MEMULAI PROSES ===

:: Jalankan script VBS untuk refresh Excel
echo [ %time% ] Menjalankan refresh semua file Excel...
cscript //nologo excel_refresh_all.vbs
if errorlevel 1 (
    echo ERROR: Terjadi masalah saat menjalankan script VBS
    pause
    exit /b
)

echo [ %time% ] Semua file Excel berhasil diperbarui.

:: Jalankan Python untuk update database
echo [ %time% ] Menjalankan update database dengan Python...
python update_database.py
if errorlevel 1 (
    echo ERROR: Update database gagal
    pause
    exit /b
)

echo [ %time% ] Update database selesai.

:: Commit dan push ke Git
echo [ %time% ] Menyimpan perubahan ke repository Git...
git add .
git commit -m "Update morning %date% %time%"
git push
if errorlevel 1 (
    echo PERINGATAN: Git push gagal (mungkin tidak ada perubahan)
) else (
    echo OK: Perubahan berhasil dikirim ke Git
)

echo.
echo ============================================================
echo [ %time% ] PROSES Update PAGI SELESAI
echo ============================================================
echo.
pause
