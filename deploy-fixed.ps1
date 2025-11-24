# Fixed WordPress Plugin FTP Deployment Script

Write-Host "" -ForegroundColor Cyan
Write-Host "WordPress Plugin FTP Deployment" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan

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

Write-Host "FTP Server: $ftpHost" -ForegroundColor Gray
Write-Host "Remote Path: $ftpRemotePath/events-cms-directory" -ForegroundColor Gray
Write-Host ""

# Files to upload
$filesToUpload = @(
    @{Local="wordpress-plugin\events-cms-directory\events-cms-directory.php"; Remote="events-cms-directory.php"},
    @{Local="wordpress-plugin\events-cms-directory\css\style.css"; Remote="css/style.css"},
    @{Local="wordpress-plugin\events-cms-directory\js\events.js"; Remote="js/events.js"},
    @{Local="wordpress-plugin\events-cms-directory\README.txt"; Remote="README.txt"}
)

$successCount = 0
$failCount = 0

foreach ($file in $filesToUpload) {
    $localPath = $file.Local
    $remotePath = "$ftpRemotePath/events-cms-directory/$($file.Remote)"
    $ftpUrl = "ftp://${ftpHost}:${ftpPort}${remotePath}"
    
    if (-not (Test-Path $localPath)) {
        Write-Host "  File not found: $localPath" -ForegroundColor Yellow
        $failCount++
        continue
    }
    
    Write-Host "Uploading: $($file.Remote)..." -ForegroundColor Gray
    
    try {
        $fileContent = [System.IO.File]::ReadAllBytes($localPath)
        $request = [System.Net.FtpWebRequest]::Create($ftpUrl)
        $request.Method = [System.Net.WebRequestMethods+Ftp]::UploadFile
        $request.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
        $request.UseBinary = $true
        $request.KeepAlive = $false
        $requestStream = $request.GetRequestStream()
        $requestStream.Write($fileContent, 0, $fileContent.Length)
        $requestStream.Close()
        $response = $request.GetResponse()
        $response.Close()
        Write-Host "  SUCCESS: $($file.Remote)" -ForegroundColor Green
        $successCount++
    }
    catch {
        Write-Host "  FAILED: $($file.Remote) - $_" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "Upload Summary" -ForegroundColor Cyan
Write-Host "  Success: $successCount files" -ForegroundColor Green
Write-Host "  Failed: $failCount files" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($successCount -gt 0) {
    Write-Host "NEXT STEPS" -ForegroundColor Yellow
    Write-Host "1. Go to WordPress Admin Plugins page" -ForegroundColor White
    Write-Host "2. Deactivate Events CMS Directory" -ForegroundColor White
    Write-Host "3. Reactivate the plugin" -ForegroundColor White
    Write-Host "4. Test the date filter" -ForegroundColor White
}
