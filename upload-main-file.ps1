# Upload Main Plugin File

$ftpHost = "162.0.215.124"
$ftpUser = "windsurf@firstindallas.com"
$ftpPassword = "Windsurf2000Business"
$remotePath = "/wp-content/plugins/events-cms-directory"

$localFile = "wordpress-plugin\events-cms-directory\events-cms-directory.php"
$remoteFile = $remotePath + "/events-cms-directory.php"

Write-Host "Uploading main plugin file..."

try {
    $ftpUri = "ftp://${ftpHost}${remoteFile}"
    $webclient = New-Object System.Net.WebClient
    $webclient.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
    $webclient.UploadFile($ftpUri, $localFile) | Out-Null
    Write-Host "SUCCESS! Main plugin file uploaded" -ForegroundColor Green
} catch {
    Write-Host "FAILED! Error: $($_.Exception.Message)" -ForegroundColor Red
}
