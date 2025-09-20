Option Explicit

Dim objExcel, objWorkbook, objFSO, strFilePath, objWMI, colProcesses, objProcess
Dim startTime, endTime

' Path file Excel (auto-detect .xlsx atau .xlsb)
Dim baseFilePath
baseFilePath = "C:\Dashboard\DbaseSalesmanWebApp"

Set objFSO = CreateObject("Scripting.FileSystemObject")

' Cek file .xlsx dulu, kalau tidak ada cek .xlsb
If objFSO.FileExists(baseFilePath & ".xlsx") Then
    strFilePath = baseFilePath & ".xlsx"
    WScript.Echo "File ditemukan: " & strFilePath & " (format .xlsx)"
ElseIf objFSO.FileExists(baseFilePath & ".xlsb") Then
    strFilePath = baseFilePath & ".xlsb"
    WScript.Echo "File ditemukan: " & strFilePath & " (format .xlsb)"
Else
    WScript.Echo "ERROR: File tidak ditemukan!"
    WScript.Quit 1
End If

' Tutup semua instance Excel yang sedang berjalan
Set objWMI = GetObject("winmgmts:\\.\root\cimv2")
Set colProcesses = objWMI.ExecQuery("Select * from Win32_Process Where Name = 'EXCEL.EXE'")
For Each objProcess in colProcesses
    objProcess.Terminate()
Next

WScript.Echo "Memulai Excel (invisible mode)..."
Set objExcel = CreateObject("Excel.Application")
objExcel.Visible = False
objExcel.DisplayAlerts = False
objExcel.EnableEvents = False
objExcel.ScreenUpdating = False

' Buka workbook
WScript.Echo "Membuka workbook..."
On Error Resume Next
Set objWorkbook = objExcel.Workbooks.Open(strFilePath, 0, False)
If Err.Number <> 0 Then
    WScript.Echo "ERROR: Tidak dapat membuka file - " & Err.Description
    objExcel.Quit
    WScript.Quit 1
End If
On Error GoTo 0

' Refresh semua data
WScript.Echo "Melakukan refresh semua data..."
objWorkbook.RefreshAll

' Tunggu semua refresh selesai
Do
    Dim bRefreshing, conn
    bRefreshing = False
    For Each conn In objWorkbook.Connections
        On Error Resume Next
        If conn.OLEDBConnection.Refreshing Then
            bRefreshing = True
        End If
        On Error GoTo 0
    Next
    WScript.Sleep 1000
Loop While bRefreshing

WScript.Echo "Simpan workbook..."
objWorkbook.Save

objWorkbook.Close False
objExcel.Quit

WScript.Echo "Proses selesai."
