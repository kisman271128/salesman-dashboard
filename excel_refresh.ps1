# Excel Auto-Refresh Script - Robust Version
# File: C:\Dashboard\excel_refresh_robust.ps1
# Purpose: Handle RPC errors and Excel hanging issues

param(
    [string]$ExcelFile = "C:\Dashboard\DbaseSalesmanWebApp.xlsm",
    [int]$RefreshWaitSeconds = 30,
    [int]$MaxRetries = 3
)

# Setup logging
$LogFile = "C:\Dashboard\excel_refresh.log"
$TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Log {
    param([string]$Message)
    $LogEntry = "$TimeStamp - $Message"
    Write-Host $LogEntry -ForegroundColor Green
    Add-Content -Path $LogFile -Value $LogEntry
}

function Write-ErrorLog {
    param([string]$Message)
    $LogEntry = "$TimeStamp - ERROR: $Message"
    Write-Host $LogEntry -ForegroundColor Red
    Add-Content -Path $LogFile -Value $LogEntry
}

function Kill-ExcelProcesses {
    Write-Log "Killing all Excel processes..."
    try {
        Get-Process -Name "EXCEL" -ErrorAction SilentlyContinue | Stop-Process -Force
        Start-Sleep -Seconds 3
        Write-Log "Excel processes terminated"
    } catch {
        Write-Log "No Excel processes to kill"
    }
}

function Test-ExcelFileAccess {
    param([string]$FilePath)
    
    try {
        # Test if file can be opened for read/write
        $FileStream = [System.IO.File]::Open($FilePath, 'Open', 'ReadWrite', 'None')
        $FileStream.Close()
        return $true
    } catch {
        Write-ErrorLog "File access test failed: $($_.Exception.Message)"
        return $false
    }
}

function Refresh-ExcelWithRetry {
    param([int]$AttemptNumber)
    
    Write-Log "Refresh attempt #$AttemptNumber of $MaxRetries"
    
    $Excel = $null
    $Workbook = $null
    
    try {
        # Clean start
        Kill-ExcelProcesses
        
        # Test file access first
        if (-not (Test-ExcelFileAccess $ExcelFile)) {
            throw "Cannot access Excel file for read/write operations"
        }
        
        Write-Log "Starting Excel application (attempt #$AttemptNumber)..."
        $Excel = New-Object -ComObject Excel.Application
        $Excel.Visible = $false
        $Excel.DisplayAlerts = $false
        $Excel.AskToUpdateLinks = $false
        $Excel.EnableEvents = $false
        $Excel.ScreenUpdating = $false
        
        Write-Log "Opening workbook..."
        $Workbook = $Excel.Workbooks.Open($ExcelFile, 0, $false)
        
        # Get connection count before refresh
        $ConnectionCount = 0
        try {
            $ConnectionCount = $Workbook.Connections.Count
            Write-Log "Found $ConnectionCount data connection(s)"
        } catch {
            Write-Log "Could not get connection count (this may be normal)"
        }
        
        # Refresh all data connections
        Write-Log "Starting refresh of all data connections..."
        $Workbook.RefreshAll()
        
        # Progressive wait with shorter intervals
        Write-Log "Waiting for refresh to complete ($RefreshWaitSeconds seconds)..."
        for ($i = 1; $i -le $RefreshWaitSeconds; $i++) {
            Start-Sleep -Seconds 1
            
            # Check if Excel is still responsive every 10 seconds
            if ($i % 10 -eq 0) {
                try {
                    $AppName = $Excel.Name
                    Write-Log "Excel still responsive at $i seconds - App: $AppName"
                } catch {
                    Write-Log "Excel may have become unresponsive at $i seconds"
                    break
                }
            }
        }
        
        # Additional wait for complex refreshes
        Write-Log "Additional 5-second wait for complex data sources..."
        Start-Sleep -Seconds 5
        
        # Try to save with multiple methods
        Write-Log "Attempting to save workbook..."
        
        # Method 1: Standard Save
        try {
            $Workbook.Save()
            Write-Log "Workbook saved successfully (Method 1: Standard Save)"
        } catch {
            Write-Log "Method 1 failed: $($_.Exception.Message)"
            
            # Method 2: SaveAs to same location
            try {
                $Workbook.SaveAs($ExcelFile)
                Write-Log "Workbook saved successfully (Method 2: SaveAs)"
            } catch {
                Write-Log "Method 2 failed: $($_.Exception.Message)"
                
                # Method 3: Force save with DoNotPrompt
                try {
                    $Excel.DisplayAlerts = $false
                    $Workbook.Save()
                    Write-Log "Workbook saved successfully (Method 3: Force Save)"
                } catch {
                    throw "All save methods failed: $($_.Exception.Message)"
                }
            }
        }
        
        # Get file info after save
        $FileInfo = Get-Item $ExcelFile
        Write-Log "File timestamp after save: $($FileInfo.LastWriteTime)"
        Write-Log "File size: $([math]::Round($FileInfo.Length / 1MB, 2)) MB"
        
        # Close workbook first
        Write-Log "Closing workbook..."
        try {
            $Workbook.Close($false)
            Write-Log "Workbook closed successfully"
        } catch {
            Write-Log "Workbook close warning: $($_.Exception.Message)"
        }
        
        # Quit Excel
        Write-Log "Quitting Excel application..."
        try {
            $Excel.Quit()
            Write-Log "Excel quit successfully"
        } catch {
            Write-Log "Excel quit warning: $($_.Exception.Message)"
        }
        
        # COM cleanup with error handling
        Write-Log "Cleaning up COM objects..."
        try {
            if ($Workbook) {
                [System.Runtime.Interopservices.Marshal]::ReleaseComObject($Workbook) | Out-Null
            }
            if ($Excel) {
                [System.Runtime.Interopservices.Marshal]::ReleaseComObject($Excel) | Out-Null
            }
            [System.GC]::Collect()
            [System.GC]::WaitForPendingFinalizers()
            Write-Log "COM cleanup completed"
        } catch {
            Write-Log "COM cleanup warning: $($_.Exception.Message)"
        }
        
        # Final verification
        $FinalFileInfo = Get-Item $ExcelFile
        $RecentTime = (Get-Date).AddMinutes(-5)
        
        if ($FinalFileInfo.LastWriteTime -gt $RecentTime) {
            Write-Log "SUCCESS: Excel refresh completed successfully!"
            Write-Log "Final file timestamp: $($FinalFileInfo.LastWriteTime)"
            
            # Create success marker
            $SuccessMarker = "C:\Dashboard\excel_refresh_success.txt"
            Set-Content -Path $SuccessMarker -Value "Excel refreshed successfully at $(Get-Date) on attempt #$AttemptNumber"
            
            return $true
        } else {
            throw "File timestamp verification failed - refresh may not have completed"
        }
        
    } catch {
        Write-ErrorLog "Attempt #$AttemptNumber failed: $($_.Exception.Message)"
        
        # Emergency cleanup
        try {
            if ($Workbook) { $Workbook.Close($false) }
            if ($Excel) { $Excel.Quit() }
        } catch {
            Write-Log "Emergency cleanup performed"
        }
        
        # Force kill Excel processes
        Kill-ExcelProcesses
        
        return $false
    }
}

# Main execution
Write-Log "=========================================="
Write-Log "Starting Excel auto-refresh process (Robust Version)"
Write-Log "Target file: $ExcelFile"
Write-Log "Refresh wait time: $RefreshWaitSeconds seconds"
Write-Log "Max retries: $MaxRetries"

# Check if Excel file exists
if (-not (Test-Path $ExcelFile)) {
    Write-ErrorLog "Excel file not found: $ExcelFile"
    exit 1
}

Write-Log "Excel file found and accessible"

# Try refresh with retries
$Success = $false
for ($Attempt = 1; $Attempt -le $MaxRetries; $Attempt++) {
    $Success = Refresh-ExcelWithRetry -AttemptNumber $Attempt
    
    if ($Success) {
        Write-Log "Excel refresh succeeded on attempt #$Attempt"
        break
    } else {
        if ($Attempt -lt $MaxRetries) {
            Write-Log "Attempt #$Attempt failed, waiting 10 seconds before retry..."
            Start-Sleep -Seconds 10
        }
    }
}

if ($Success) {
    Write-Log "FINAL RESULT: Excel refresh completed successfully!"
    Write-Log "Ready for morning dashboard update at 07:00"
    exit 0
} else {
    Write-ErrorLog "FINAL RESULT: Excel refresh failed after $MaxRetries attempts"
    
    # Create failure marker
    $FailureMarker = "C:\Dashboard\excel_refresh_failure.txt"
    Set-Content -Path $FailureMarker -Value "Excel refresh failed after $MaxRetries attempts at $(Get-Date)"
    
    exit 1
}

Write-Log "=========================================="