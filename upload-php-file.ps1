# Upload only the main PHP file
$ftpHost = "162.0.215.124"
$ftpUser = "windsurf@firstindallas.com"
$ftpPassword = "Windsurf2000Business"
$localFile = "wordpress-plugin\events-cms-directory\events-cms-directory.php"
$remotePath = "/wp-content/plugins/events-cms-directory/events-cms-directory.php"

Write-Host "Uploading PHP file..."
Write-Host "From: $localFile"
Write-Host "To: ftp://${ftpHost}:21${remotePath}"

try {
    $ftpUri = "ftp://${ftpHost}:21${remotePath}"
    $ftpRequest = [System.Net.FtpWebRequest]::Create($ftpUri)
    $ftpRequest.Method = [System.Net.WebRequestMethods+Ftp]::UploadFile
    $ftpRequest.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
    $ftpRequest.UseBinary = $true
    $ftpRequest.UsePassive = $true

    $fileContent = [System.IO.File]::ReadAllBytes($localFile)
    $ftpRequest.ContentLength = $fileContent.Length

    $requestStream = $ftpRequest.GetRequestStream()
    $requestStream.Write($fileContent, 0, $fileContent.Length)
    $requestStream.Close()

    $response = $ftpRequest.GetResponse()
    $response.Close()

    Write-Host "PHP file uploaded successfully!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
}
