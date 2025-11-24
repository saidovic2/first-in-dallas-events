# Upload debug script to WordPress root

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

# Upload to WordPress root
$localFile = "wp-debug-events.php"
$remoteFile = "ftp://${ftpHost}:${ftpPort}/wp-debug-events.php"

Write-Host "Uploading debug script to WordPress..." -ForegroundColor Cyan
Write-Host "From: $localFile" -ForegroundColor Gray
Write-Host "To: $remoteFile" -ForegroundColor Gray

try {
    $webclient = New-Object System.Net.WebClient
    $webclient.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
    $webclient.UploadFile($remoteFile, $localFile)
    Write-Host "Debug script uploaded!" -ForegroundColor Green
    Write-Host ""
    Write-Host "NEXT STEP:" -ForegroundColor Yellow
    Write-Host "Visit: https://firstindallas.com/wp-debug-events.php" -ForegroundColor White
    Write-Host ""
    Write-Host "This will show:" -ForegroundColor Gray
    Write-Host "  - What API URL WordPress is using" -ForegroundColor Gray
    Write-Host "  - What events the API is returning" -ForegroundColor Gray
    Write-Host "  - Whether date filtering is working" -ForegroundColor Gray
    Write-Host "  - Plugin version info" -ForegroundColor Gray
    Write-Host ""
    Write-Host "IMPORTANT: Delete the file after viewing!" -ForegroundColor Red
} catch {
    Write-Host "Upload failed: $_" -ForegroundColor Red
}
