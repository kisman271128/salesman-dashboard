# Excel Auto-Refresh Script - Selective File Handling
# File: C:\Dashboard\excel_refresh_selective.ps1
# Purpose: Check and close only specific file if in use, not all Excel processes

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

function Test-FileInUse {
    param([string]$FilePath)
    
    try {
        # Try to open file with exclusive access
        $FileStream = [System.IO.File]::Open($FilePath, 'Open', 'ReadWrite', 'None')
        $FileStream.Close()
        Write-Log "File is not in use: $FilePath"
        return $false
    } catch [System.IO.IOException] {
        if ($_.Exception.Message -match "used by another process") {
            Write-Log "File is currently in use: $FilePath"
            return $true
        } else {
            Write-ErrorLog "File access error: $($_.Exception.Message)"
            throw
        }
    } catch {
        Write-ErrorLog "Unexpected error checking file: $($_.Exception.Message)"
        throw
    }
}

function Get-ExcelInstances {
    Write-Log "Checking for existing Excel instances..."
    $ExcelInstances = @()
    
    try {
        # Try to get existing Excel application instances
        $ExcelApp = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Excel.Application")
        if ($ExcelApp) {
            $ExcelInstances += $ExcelApp
            Write-Log "Found active Excel instance"
        }
    } catch {
        Write-Log "No active Excel instances found via COM"
    }
    
    # Alternative method: Check running processes
    $ExcelProcesses = Get-Process -Name "EXCEL" -ErrorAction SilentlyContinue
    if ($ExcelProcesses) {
        Write-Log "Found $($ExcelProcesses.Count) Excel process(es) running"
    } else {
        Write-Log "No Excel processes found"
    }
    
    return $ExcelInstances
}

function Close-SpecificWorkbook {
    param([string]$FilePath)
    
    Write-Log "Attempting to close specific workbook: $([System.IO.Path]::GetFileName($FilePath))"
    $Closed = $false
    
    try {
        # Get all Excel instances
        $ExcelInstances = Get-ExcelInstances
        
        if ($ExcelInstances.Count -eq 0) {
            # Try alternative method to connect to Excel
            try {
                $Excel = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Excel.Application")
                $ExcelInstances = @($Excel)
            } catch {
                Write-Log "No Excel instances available to check"
                return $false
            }
        }
        
        foreach ($Excel in $ExcelInstances) {
            try {
                Write-Log "Checking Excel instance with $($Excel.Workbooks.Count) workbook(s)"
                
                # Check each workbook in this Excel instance
                for ($i = 1; $i -le $Excel.Workbooks.Count; $i++) {
                    try {
                        $Workbook = $Excel.Workbooks.Item($i)
                        $WorkbookPath = $Workbook.FullName
                        
                        Write-Log "Checking workbook: $([System.IO.Path]::GetFileName($WorkbookPath))"
                        
                        # Compare file paths (resolve to absolute paths)
                        $TargetPath = [System.IO.Path]::GetFullPath($FilePath)
                        $CurrentPath = [System.IO.Path]::GetFullPath($WorkbookPath)
                        
                        if ($TargetPath -eq $CurrentPath) {
                            Write-Log "Found target workbook open in Excel"
                            
                            # Check if workbook has unsaved changes
                            if ($Workbook.Saved -eq $false) {
                                Write-Log "Workbook has unsaved changes, saving before close..."
                                $Workbook.Save()
                            }
                            
                            # Close the specific workbook
                            $Workbook.Close($false)  # False = don't save again
                            Write-Log "Successfully closed target workbook"
                            $Closed = $true
                            break
                        }
                    } catch {
                        Write-Log "Error checking workbook $i : $($_.Exception.Message)"
                        continue
                    }
                }
                
                if ($Closed) {
                    break
                }
                
            } catch {
                Write-Log "Error accessing Excel instance: $($_.Exception.Message)"
                continue
            }
        }
        
        if ($Closed) {
            Write-Log "Target workbook closed successfully"
            # Wait a moment for Excel to release the file
            Start-Sleep -Seconds 2
        } else {
            Write-Log "Target workbook was not found in any Excel instance"
        }
        
        return $Closed
        
    } catch {
        Write-ErrorLog "Error in Close-SpecificWorkbook: $($_.Exception.Message)"
        return $false
    }
}

function Remove-LockFiles {
    param([string]$TargetFile)
    
    Write-Log "Removing lock files for target file..."
    $FileName = [System.IO.Path]::GetFileNameWithoutExtension($TargetFile)
    $Directory = [System.IO.Path]::GetDirectoryName($TargetFile)
    
    # Look for lock files specific to our target file
    $LockPatterns = @(
        "$Directory\~`$$FileName*.xlsx",
        "$Directory\~`$$FileName*.tmp",
        "$Directory\$FileName*.tmp"
    )
    
    $removed = 0
    
    foreach ($pattern in $LockPatterns) {
        $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            try {
                Remove-Item $file.FullName -Force
                Write-Log "Removed lock file: $($file.Name)"
                $removed++
            } catch {
                Write-Log "Could not remove lock file: $($file.Name) - $($_.Exception.Message)"
            }
        }
    }
    
    if ($removed -eq 0) {
        Write-Log "No lock files found for target file"
    } else {
        Write-Log "Removed $removed lock file(s)"
    }
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
        
        # Test if file is in use
        if (Test-FileInUse $FilePath) {
            Write-Log "File is currently locked by another process"
            return $false
        }
        
        Write-Log "File access test: PASSED"
        return $true
        
    } catch {
        Write-ErrorLog "File access test failed: $($_.Exception.Message)"
        return $false
    }
}

function Prepare-FileForRefresh {
    param([string]$FilePath)
    
    Write-Log "=== Preparing file for refresh ==="
    
    # Step 1: Check if file is in use
    if (Test-FileInUse $FilePath) {
        Write-Log "File is in use, attempting to close specific workbook..."
        
        # Try to close only the specific workbook
        $Closed = Close-SpecificWorkbook $FilePath
        
        if ($Closed) {
            Write-Log "Successfully closed specific workbook"
            Start-Sleep -Seconds 2
            
            # Verify file is no longer in use
            if (-not (Test-FileInUse $FilePath)) {
                Write-Log "File is now available for refresh"
            } else {
                Write-Log "File is still in use after closing workbook"
                return $false
            }
        } else {
            Write-Log "Could not close specific workbook, file may be locked by another process"
            return $false
        }
    } else {
        Write-Log "File is not in use, ready for refresh"
    }
    
    # Step 2: Remove any lock files for this specific file
    Remove-LockFiles $FilePath
    
    # Step 3: Final access test
    return Test-FileAccess $FilePath
}

function Kill-ExcelProcesses {
    Write-Log "FALLBACK: Terminating all Excel processes..."
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

function Refresh-Excel-Selective {
    param([int]$AttemptNumber)
    
    Write-Log "=== Selective Refresh Attempt #$AttemptNumber ==="
    
    $Excel = $null
    $Workbook = $null
    
    try {
        # Step 1: Prepare file (selective close if needed)
        if (-not (Prepare-FileForRefresh $ExcelFile)) {
            Write-Log "File preparation failed, trying fallback method..."
            
            # Fallback: Kill all Excel processes if selective close failed
            Kill-ExcelProcesses | Out-Null
            Remove-LockFiles $ExcelFile
            
            if (-not (Test-FileAccess $ExcelFile)) {
                throw "File access failed even after fallback cleanup"
            }
        }
        
        # Step 2: Start fresh Excel instance
        Write-Log "Starting Excel application..."
        $Excel = New-Object -ComObject Excel.Application
        
        # Wait for Excel to fully initialize
        Start-Sleep -Seconds 2
        
        # Set basic properties
        $Excel.Visible = $false
        $Excel.DisplayAlerts = $false
        $Excel.AskToUpdateLinks = $false
        
        Write-Log "Excel application ready"
        
        # Step 3: Open workbook
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
        
        # Step 4: Refresh all data
        Write-Log "Starting data refresh..."
        $RefreshStartTime = Get-Date
        
        try {
            $Workbook.RefreshAll()
            Write-Log "RefreshAll command executed"
        } catch {
            Write-Log "RefreshAll warning: $($_.Exception.Message)"
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
        
        # Step 5: Save workbook
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
        
        # Step 6: Close Excel cleanly
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
        
        # Step 7: Verify success
        $FinalFileInfo = Get-Item $ExcelFile
        $RecentTime = (Get-Date).AddMinutes(-5)
        
        if ($FinalFileInfo.LastWriteTime -gt $RecentTime) {
            Write-Log "SUCCESS: Excel refresh completed successfully!"
            Write-Log "Final timestamp: $($FinalFileInfo.LastWriteTime)"
            
            # Create success marker
            $SuccessMarker = "C:\Dashboard\excel_refresh_success.txt"
            $SuccessMessage = @"
Excel Refresh Successful - Selective Method
==========================================
Time: $(Get-Date)
Attempt: #$AttemptNumber
File: $ExcelFile
Size: $([math]::Round($FinalFileInfo.Length / 1MB, 2)) MB
Last Modified: $($FinalFileInfo.LastWriteTime)
Connections: $ConnectionCount
Method: Selective file handling (only target file closed)
Status: Ready for dashboard update
"@
            Set-Content -Path $SuccessMarker -Value $SuccessMessage
            
            return $true
        } else {
            throw "File timestamp verification failed"
        }
        
    } catch {
        Write-ErrorLog "Selective refresh attempt #$AttemptNumber failed: $($_.Exception.Message)"
        
        # Emergency cleanup
        try {
            if ($Workbook) { $Workbook.Close($false) }
            if ($Excel) { $Excel.Quit() }
        } catch {
            # Silent cleanup
        }
        
        return $false
    }
}

# Main execution
Write-Log "================================================"
Write-Log "Excel Auto-Refresh Script - Selective File Handling"
Write-Log "Target file: $ExcelFile"
Write-Log "Refresh wait time: $RefreshWaitSeconds seconds"
Write-Log "Max retries: $MaxRetries"
Write-Log "Method: Selective (only close target file if in use)"

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
    
    $Success = Refresh-Excel-Selective -AttemptNumber $Attempt
    
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
Excel Refresh Failed - Selective Method
======================================
Time: $(Get-Date)
File: $ExcelFile
Attempts: $MaxRetries
Duration: $([math]::Round($TotalTime, 1)) seconds
Error: Could not access or refresh target file

Troubleshooting:
1. Check if file is open in Excel manually
2. Verify file permissions
3. Check data connections manually
4. Try running script as administrator
5. Contact IT support if issue persists

Log File: $LogFile
"@
    Set-Content -Path $FailureMarker -Value $FailureMessage
    
    exit 1
}

Write-Log "================================================"