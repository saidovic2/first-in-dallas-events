# Quick CSS Upload Script
# Load environment variables
$envFile = ".env"
$envVars = @{}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$key] = $value
    }
}

$ftpHost = $envVars['FTP_HOST']
$ftpPort = if ([string]::IsNullOrWhiteSpace($envVars['FTP_PORT'])) { "21" } else { $envVars['FTP_PORT'] }
$ftpUser = $envVars['FTP_USER']
$ftpPassword = $envVars['FTP_PASSWORD']
$ftpRemotePath = $envVars['FTP_REMOTE_PATH']

# Upload CSS file
$localCss = "wordpress-plugin\events-cms-directory\css\style.css"
$ftpUri = "ftp://${ftpHost}:${ftpPort}${ftpRemotePath}/events-cms-directory/css/style.css"

Write-Host "Uploading CSS file..." -ForegroundColor Yellow
Write-Host "From: $localCss" -ForegroundColor Gray
Write-Host "To: $ftpUri" -ForegroundColor Gray

try {
    $webclient = New-Object System.Net.WebClient
    $webclient.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
    $webclient.UploadFile($ftpUri, $localCss)
    Write-Host "CSS file uploaded successfully!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Manually upload the file:" -ForegroundColor Yellow
    Write-Host "Local file: $localCss" -ForegroundColor Cyan
    Write-Host "Server path: $ftpRemotePath/events-cms-directory/css/style.css" -ForegroundColor Cyan
}
