Option Explicit

Dim objExcel, objWorkbook, startTime, endTime, elapsed, fso, logFile, filePath

Set fso = CreateObject("Scripting.FileSystemObject")
Set logFile = fso.CreateTextFile("refresh_benchmark_log.txt", True)

' ===== List file yang mau diuji =====
Dim files(1)
files(0) = "C:\Dashboard\DbaseSalesmanWebApp.xlsx"
files(1) = "C:\Dashboard\DbaseSalesmanWebApp.xlsb"

For Each filePath In files
    If fso.FileExists(filePath) Then
        logFile.WriteLine "----------------------------------------"
        logFile.WriteLine "File: " & filePath
        logFile.WriteLine "Start: " & Now

        startTime = Timer

        ' buka Excel hidden
        Set objExcel = CreateObject("Excel.Application")
        objExcel.Visible = False
        objExcel.DisplayAlerts = False

        Set objWorkbook = objExcel.Workbooks.Open(filePath)

        ' Refresh semua (connection + pivot)
        objWorkbook.RefreshAll
        objExcel.CalculateUntilAsyncQueriesDone

        WScript.Sleep 10000 ' kasih jeda 10 detik biar semua settle

        objWorkbook.Save
        objWorkbook.Close False
        objExcel.Quit

        endTime = Timer
        elapsed = endTime - startTime

        logFile.WriteLine "End: " & Now
        logFile.WriteLine "Elapsed: " & Round(elapsed,2) & " seconds"
        logFile.WriteLine "----------------------------------------"

        Set objWorkbook = Nothing
        Set objExcel = Nothing
    Else
        logFile.WriteLine "File not found: " & filePath
    End If
Next

logFile.Close
Set fso = Nothing
