# Upload cache clearing script to WordPress root

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

# Upload to WordPress root (one level up from plugins)
$localFile = "clear-wordpress-cache.php"
$remoteFile = "ftp://${ftpHost}:${ftpPort}/clear-wordpress-cache.php"

Write-Host "Uploading cache clearer to WordPress root..." -ForegroundColor Cyan
Write-Host "From: $localFile" -ForegroundColor Gray
Write-Host "To: $remoteFile" -ForegroundColor Gray

try {
    $webclient = New-Object System.Net.WebClient
    $webclient.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
    $webclient.UploadFile($remoteFile, $localFile)
    Write-Host "Cache clearer uploaded successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Visit: https://firstindallas.com/clear-wordpress-cache.php" -ForegroundColor White
    Write-Host "2. Follow the instructions on that page" -ForegroundColor White
    Write-Host "3. DELETE the file after using it (important!)" -ForegroundColor Red
} catch {
    Write-Host "Upload failed: $_" -ForegroundColor Red
}
