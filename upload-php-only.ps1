# Upload only the main PHP file to WordPress via FTP

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
$ftpRemotePath = $envVars['FTP_REMOTE_PATH']

# Upload PHP file
$localPhp = "wordpress-plugin\events-cms-directory\events-cms-directory.php"
$remotePhp = "ftp://${ftpHost}:${ftpPort}${ftpRemotePath}/events-cms-directory/events-cms-directory.php"

Write-Host "Uploading PHP file..." -ForegroundColor Cyan
Write-Host "From: $localPhp" -ForegroundColor Gray
Write-Host "To: $remotePhp" -ForegroundColor Gray

try {
    $webclient = New-Object System.Net.WebClient
    $webclient.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
    $webclient.UploadFile($remotePhp, $localPhp)
    Write-Host "PHP file uploaded successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Go to WordPress Admin - Plugins" -ForegroundColor White
    Write-Host "2. Deactivate and reactivate the Events CMS Directory plugin" -ForegroundColor White
    Write-Host "3. Test the date filter on your calendar page" -ForegroundColor White
} catch {
    Write-Host "✗ Upload failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "MANUAL FIX:" -ForegroundColor Yellow
    Write-Host "Copy the file manually using FTP client:" -ForegroundColor White
    Write-Host "  Local: $localPhp" -ForegroundColor Gray
    Write-Host "  Remote: ${ftpRemotePath}/events-cms-directory/events-cms-directory.php" -ForegroundColor Gray
}
