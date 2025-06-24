# Excel Auto-Refresh Script - Simplified & Fixed
# File: C:\Dashboard\excel_refresh_simplified.ps1
# Purpose: Fixed HRESULT 0x800A03EC calculation error

param(
    [string]$ExcelFile = "C:\Dashboard\DbaseSalesmanWebApp.xlsx",
    [int]$RefreshWaitSeconds = 30,
    [int]$MaxRetries = 3
)

# Setup logging
$LogFile = "C:\Dashboard\excel_refresh.log"

function Write-Log {
    param([string]$Message)
    $TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "$TimeStamp - $Message"
    Write-Host $LogEntry -ForegroundColor Green
    Add-Content -Path $LogFile -Value $LogEntry
}

function Write-ErrorLog {
    param([string]$Message)
    $TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "$TimeStamp - ERROR: $Message"
    Write-Host $LogEntry -ForegroundColor Red
    Add-Content -Path $LogFile -Value $LogEntry
}

function Kill-ExcelProcesses {
    Write-Log "Terminating Excel processes..."
    try {
        $result = Start-Process -FilePath "taskkill" -ArgumentList "/F", "/IM", "EXCEL.EXE" -Wait -PassThru -NoNewWindow -ErrorAction SilentlyContinue
        Write-Log "Taskkill exit code: $($result.ExitCode)"
    } catch {
        Write-Log "Taskkill info: $($_.Exception.Message)"
    }
    
    Start-Sleep -Seconds 3
    
    $remainingProcesses = Get-Process -Name "EXCEL" -ErrorAction SilentlyContinue
    if ($remainingProcesses) {
        Write-Log "Warning: $($remainingProcesses.Count) Excel processes still running"
        return $false
    } else {
        Write-Log "All Excel processes terminated"
        return $true
    }
}

function Remove-LockFiles {
    Write-Log "Removing lock files..."
    $patterns = @("C:\Dashboard\~`$*.xlsx", "C:\Dashboard\*.tmp")
    $removed = 0
    
    foreach ($pattern in $patterns) {
        $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            try {
                Remove-Item $file.FullName -Force
                $removed++
            } catch {
                Write-Log "Could not remove: $($file.Name)"
            }
        }
    }
    Write-Log "Removed $removed lock files"
}

function Test-FileAccess {
    param([string]$FilePath)
    
    try {
        if (-not (Test-Path $FilePath)) {
            throw "File not found: $FilePath"
        }
        
        $fileInfo = Get-Item $FilePath
        Write-Log "File size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB"
        Write-Log "Last modified: $($fileInfo.LastWriteTime)"
        
        # Test exclusive access
        $stream = [System.IO.File]::Open($FilePath, 'Open', 'ReadWrite', 'None')
        $stream.Close()
        Write-Log "File access test: PASSED"
        
        return $true
    } catch {
        Write-ErrorLog "File access test failed: $($_.Exception.Message)"
        return $false
    }
}

function Refresh-Excel-Simple {
    param([int]$AttemptNumber)
    
    Write-Log "=== Simple Refresh Attempt #$AttemptNumber ==="
    
    $Excel = $null
    $Workbook = $null
    
    try {
        # Clean start
        Kill-ExcelProcesses | Out-Null
        Remove-LockFiles
        
        if (-not (Test-FileAccess $ExcelFile)) {
            throw "File access failed"
        }
        
        # Start Excel with minimal settings (avoid problematic properties)
        Write-Log "Starting Excel application..."
        $Excel = New-Object -ComObject Excel.Application
        
        # Wait for Excel to fully initialize
        Start-Sleep -Seconds 2
        
        # Set basic properties only (avoid Calculation property)
        $Excel.Visible = $false
        $Excel.DisplayAlerts = $false
        $Excel.AskToUpdateLinks = $false
        
        Write-Log "Excel application ready"
        
        # Open workbook
        Write-Log "Opening workbook..."
        $Workbook = $Excel.Workbooks.Open($ExcelFile)
        
        Write-Log "Workbook opened: $($Workbook.Name)"
        
        # Check for data connections
        $ConnectionCount = 0
        try {
            if ($Workbook.Connections) {
                $ConnectionCount = $Workbook.Connections.Count
                Write-Log "Found $ConnectionCount data connection(s)"
            } else {
                Write-Log "No data connections found"
            }
        } catch {
            Write-Log "Could not check connections (may be normal)"
        }
        
        # Refresh all data
        Write-Log "Starting data refresh..."
        $RefreshStartTime = Get-Date
        
        try {
            $Workbook.RefreshAll()
            Write-Log "RefreshAll command executed"
        } catch {
            Write-Log "RefreshAll warning: $($_.Exception.Message)"
            # Continue anyway, some refreshes may still work
        }
        
        # Wait for refresh with progress
        Write-Log "Waiting $RefreshWaitSeconds seconds for refresh to complete..."
        for ($i = 1; $i -le $RefreshWaitSeconds; $i++) {
            Start-Sleep -Seconds 1
            
            if ($i % 10 -eq 0) {
                Write-Log "Still waiting... ($i/$RefreshWaitSeconds seconds)"
            }
        }
        
        $RefreshDuration = ((Get-Date) - $RefreshStartTime).TotalSeconds
        Write-Log "Refresh phase completed in $([math]::Round($RefreshDuration, 1)) seconds"
        
        # Save workbook
        Write-Log "Saving workbook..."
        try {
            $Workbook.Save()
            Write-Log "Workbook saved successfully"
        } catch {
            Write-ErrorLog "Save failed: $($_.Exception.Message)"
            
            # Try alternative save method
            try {
                $Workbook.SaveAs($ExcelFile)
                Write-Log "Workbook saved using SaveAs method"
            } catch {
                throw "All save methods failed: $($_.Exception.Message)"
            }
        }
        
        # Get updated file info
        $UpdatedFileInfo = Get-Item $ExcelFile
        Write-Log "File timestamp after save: $($UpdatedFileInfo.LastWriteTime)"
        Write-Log "File size after save: $([math]::Round($UpdatedFileInfo.Length / 1MB, 2)) MB"
        
        # Close Excel
        Write-Log "Closing workbook and Excel..."
        try {
            $Workbook.Close($false)
            Write-Log "Workbook closed"
        } catch {
            Write-Log "Workbook close info: $($_.Exception.Message)"
        }
        
        try {
            $Excel.Quit()
            Write-Log "Excel quit"
        } catch {
            Write-Log "Excel quit info: $($_.Exception.Message)"
        }
        
        # COM cleanup
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
            Write-Log "COM cleanup info: $($_.Exception.Message)"
        }
        
        # Verify success by checking file timestamp
        $FinalFileInfo = Get-Item $ExcelFile
        $RecentTime = (Get-Date).AddMinutes(-5)
        
        if ($FinalFileInfo.LastWriteTime -gt $RecentTime) {
            Write-Log "SUCCESS: Excel refresh completed successfully!"
            Write-Log "Final timestamp: $($FinalFileInfo.LastWriteTime)"
            
            # Create success marker
            $SuccessMarker = "C:\Dashboard\excel_refresh_success.txt"
            $SuccessMessage = @"
Excel Refresh Successful - Simplified Method
==========================================
Time: $(Get-Date)
Attempt: #$AttemptNumber
File: $ExcelFile
Size: $([math]::Round($FinalFileInfo.Length / 1MB, 2)) MB
Last Modified: $($FinalFileInfo.LastWriteTime)
Connections: $ConnectionCount
Status: Ready for dashboard update
"@
            Set-Content -Path $SuccessMarker -Value $SuccessMessage
            
            return $true
        } else {
            throw "File timestamp verification failed"
        }
        
    } catch {
        Write-ErrorLog "Simple refresh attempt #$AttemptNumber failed: $($_.Exception.Message)"
        
        # Emergency cleanup
        try {
            if ($Workbook) { $Workbook.Close($false) }
            if ($Excel) { $Excel.Quit() }
        } catch {
            # Silent cleanup
        }
        
        Kill-ExcelProcesses | Out-Null
        return $false
    }
}

# Main execution
Write-Log "================================================"
Write-Log "Excel Auto-Refresh Script - Simplified Version"
Write-Log "Target file: $ExcelFile"
Write-Log "Refresh wait time: $RefreshWaitSeconds seconds"
Write-Log "Max retries: $MaxRetries"
Write-Log "Method: Simplified (avoid problematic COM properties)"

# Check file exists
if (-not (Test-Path $ExcelFile)) {
    Write-ErrorLog "Excel file not found: $ExcelFile"
    exit 1
}

Write-Log "Excel file confirmed: $ExcelFile"

# Execute with retries
$Success = $false
$StartTime = Get-Date

for ($Attempt = 1; $Attempt -le $MaxRetries; $Attempt++) {
    Write-Log "Starting attempt $Attempt of $MaxRetries"
    
    $Success = Refresh-Excel-Simple -AttemptNumber $Attempt
    
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

$TotalTime = ((Get-Date) - $StartTime).TotalSeconds

# Final results
if ($Success) {
    Write-Log "FINAL RESULT: Excel refresh completed successfully!"
    Write-Log "Total execution time: $([math]::Round($TotalTime, 1)) seconds"
    Write-Log "System ready for dashboard update at 07:00"
    exit 0
} else {
    Write-ErrorLog "FINAL RESULT: Excel refresh failed after $MaxRetries attempts"
    Write-ErrorLog "Total execution time: $([math]::Round($TotalTime, 1)) seconds"
    
    # Create failure marker
    $FailureMarker = "C:\Dashboard\excel_refresh_failure.txt"
    $FailureMessage = @"
Excel Refresh Failed - Simplified Method
=======================================
Time: $(Get-Date)
File: $ExcelFile
Attempts: $MaxRetries
Duration: $([math]::Round($TotalTime, 1)) seconds
Error: Calculation property or COM initialization issue

Next Steps:
1. Try manual refresh in Excel
2. Check data connections manually
3. Verify Excel version compatibility
4. Contact IT support if issue persists

Log File: $LogFile
"@
    Set-Content -Path $FailureMarker -Value $FailureMessage
    
    exit 1
}

Write-Log "================================================"