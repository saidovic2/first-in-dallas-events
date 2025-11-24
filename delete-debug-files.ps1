# Delete debug files from WordPress server via FTP

# Load environment variables
$envFile = ".env"
$envVars = @{}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*)$') {
        $envVars[$matches[1].Trim()] = $matches[2].Trim()
    }
}

$ftpHost = $envVars['FTP_HOST']
$ftpPort = if ([string]::IsNullOrWhiteSpace($envVars['FTP_PORT'])) { "21" } else { $envVars['FTP_PORT'] }
$ftpUser = $envVars['FTP_USER']
$ftpPassword = $envVars['FTP_PASSWORD']

# Files to delete
$filesToDelete = @(
    "wp-debug-events.php",
    "clear-wordpress-cache.php"
)

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Deleting Debug Files from WordPress" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

foreach ($file in $filesToDelete) {
    $ftpUri = "ftp://${ftpHost}:${ftpPort}/${file}"
    
    Write-Host "Deleting: $file ..." -ForegroundColor Yellow
    
    try {
        $ftpRequest = [System.Net.FtpWebRequest]::Create($ftpUri)
        $ftpRequest.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
        $ftpRequest.Method = [System.Net.WebRequestMethods+Ftp]::DeleteFile
        
        $response = $ftpRequest.GetResponse()
        Write-Host "  Deleted successfully!" -ForegroundColor Green
        $response.Close()
    } catch {
        if ($_.Exception.Message -like "*550*") {
            Write-Host "  File not found (already deleted or never existed)" -ForegroundColor Gray
        } else {
            Write-Host "  Error: $_" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Cleanup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
