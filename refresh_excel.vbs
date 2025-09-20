' ============================================================
' Script VBS untuk me-refresh semua file Excel
' Deskripsi: Membuka setiap file Excel di folder tertentu,
'            melakukan RefreshAll pada pivot / koneksi,
'            lalu menyimpan dan menutupnya.
' ============================================================

Option Explicit

Dim objExcel, objWorkbook, objFSO, objFolder, objFile
Dim folderPath

' Tentukan folder tempat file Excel berada
folderPath = CreateObject("Scripting.FileSystemObject").GetAbsolutePathName(".")

Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objFolder = objFSO.GetFolder(folderPath)

' Buat objek Excel
On Error Resume Next
Set objExcel = CreateObject("Excel.Application")
If Err.Number <> 0 Then
    WScript.Echo "ERROR: Excel tidak dapat dijalankan. Pastikan Microsoft Excel sudah terinstal."
    WScript.Quit 1
End If
On Error GoTo 0

objExcel.Visible = False
objExcel.DisplayAlerts = False

WScript.Echo "Memulai proses refresh semua file Excel di folder: " & folderPath

' Loop melalui semua file di folder
For Each objFile In objFolder.Files
    If LCase(Right(objFile.Name, 5)) = ".xlsx" Or LCase(Right(objFile.Name, 5)) = ".xlsm" Or LCase(Right(objFile.Name, 5)) = ".xlsb" Then
        WScript.Echo "Membuka file: " & objFile.Name
        Set objWorkbook = objExcel.Workbooks.Open(objFile.Path)

        ' Jalankan RefreshAll
        objWorkbook.RefreshAll

        ' Tunggu refresh selesai
        WScript.Sleep 5000

        ' Simpan dan tutup file
        objWorkbook.Close True
        WScript.Echo "Berhasil diperbarui: " & objFile.Name
    End If
Next

' Tutup Excel
objExcel.Quit
Set objExcel = Nothing

WScript.Echo "Proses refresh semua file Excel selesai."
