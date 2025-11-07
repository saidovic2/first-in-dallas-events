# Simple FTP Connection Test

$ftpHost = "162.0.215.124"
$ftpUser = "windsurf@firstindallas.com"
$ftpPassword = "Windsurf2000Business"
$ftpPath = "/wp-content/plugins/events-cms-directory"

Write-Host "Testing FTP Connection..." -ForegroundColor Cyan
Write-Host "Host: $ftpHost"
Write-Host "User: $ftpUser"
Write-Host "Path: $ftpPath"
Write-Host ""

try {
    $ftpUri = "ftp://${ftpHost}${ftpPath}"
    $request = [System.Net.FtpWebRequest]::Create($ftpUri)
    $request.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
    $request.Method = [System.Net.WebRequestMethods+Ftp]::ListDirectory
    
    $response = $request.GetResponse()
    $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
    $listing = $reader.ReadToEnd()
    $reader.Close()
    $response.Close()
    
    Write-Host "SUCCESS! Connection works!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Files in plugin directory:" -ForegroundColor Green
    Write-Host $listing
    
} catch {
    Write-Host "FAILED! Connection error!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
