# Simple WordPress Plugin FTP Deployment
# This version uploads files one by one with clear error handling

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Simple Plugin FTP Upload" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# FTP Configuration
$ftpHost = "162.0.215.124"
$ftpUser = "windsurf@firstindallas.com"
$ftpPassword = "Windsurf2000Business"
$remotePath = "/wp-content/plugins/events-cms-directory"

# Local plugin path
$pluginDir = "wordpress-plugin\events-cms-directory"

Write-Host "Uploading plugin files..." -ForegroundColor Yellow
Write-Host ""

# Get all files
$files = @(
    "events-cms-directory.php",
    "README.txt",
    "README.md",
    "css\style.css",
    "js\events.js"
)

$uploadedCount = 0
$failedCount = 0

foreach ($file in $files) {
    $localFile = Join-Path $pluginDir $file
    $remoteFile = $remotePath + "/" + ($file.Replace('\', '/'))
    
    if (Test-Path $localFile) {
        try {
            $ftpUri = "ftp://${ftpHost}${remoteFile}"
            Write-Host "Uploading: $file" -ForegroundColor Gray
            
            $webclient = New-Object System.Net.WebClient
            $webclient.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
            $webclient.UploadFile($ftpUri, $localFile) | Out-Null
            
            Write-Host "  ✓ Success" -ForegroundColor Green
            $uploadedCount++
        } catch {
            Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
            $failedCount++
        }
    } else {
        Write-Host "  ⚠ File not found: $localFile" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Results:" -ForegroundColor Cyan
Write-Host "  Uploaded: $uploadedCount files" -ForegroundColor Green
Write-Host "  Failed: $failedCount files" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT: Deactivate and reactivate the plugin in WordPress admin" -ForegroundColor Yellow
