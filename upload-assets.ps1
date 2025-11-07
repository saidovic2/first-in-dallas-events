# Upload Plugin CSS and JS Files

$ftpHost = "162.0.215.124"
$ftpUser = "windsurf@firstindallas.com"
$ftpPassword = "Windsurf2000Business"

$files = @{
    "wordpress-plugin\events-cms-directory\css\style.css" = "/wp-content/plugins/events-cms-directory/css/style.css"
    "wordpress-plugin\events-cms-directory\js\events.js" = "/wp-content/plugins/events-cms-directory/js/events.js"
}

foreach ($localPath in $files.Keys) {
    $remotePath = $files[$localPath]
    Write-Host "Uploading: $remotePath"
    
    try {
        $ftpUri = "ftp://${ftpHost}${remotePath}"
        $webclient = New-Object System.Net.WebClient
        $webclient.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
        $webclient.UploadFile($ftpUri, $localPath) | Out-Null
        Write-Host "  SUCCESS!" -ForegroundColor Green
    } catch {
        Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Done! Plugin updated on server." -ForegroundColor Cyan
