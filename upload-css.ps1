# Load environment variables from .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#].+?)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}

$FTP_HOST = $env:FTP_HOST
$FTP_PORT = $env:FTP_PORT
$FTP_USER = $env:FTP_USER
$FTP_PASSWORD = $env:FTP_PASSWORD
$FTP_REMOTE_PATH = $env:FTP_REMOTE_PATH

Write-Host "Uploading CSS file..." -ForegroundColor Cyan

$localFile = "wordpress-plugin\events-cms-directory\css\style.css"
$remotePath = "$FTP_REMOTE_PATH/events-cms-directory/css/style.css"

try {
    $ftpUri = "ftp://${FTP_HOST}:${FTP_PORT}${remotePath}"
    
    $ftpRequest = [System.Net.FtpWebRequest]::Create($ftpUri)
    $ftpRequest.Method = [System.Net.WebRequestMethods+Ftp]::UploadFile
    $ftpRequest.Credentials = New-Object System.Net.NetworkCredential($FTP_USER, $FTP_PASSWORD)
    $ftpRequest.UseBinary = $true
    
    $fileContent = [System.IO.File]::ReadAllBytes($localFile)
    $ftpRequest.ContentLength = $fileContent.Length
    
    $requestStream = $ftpRequest.GetRequestStream()
    $requestStream.Write($fileContent, 0, $fileContent.Length)
    $requestStream.Close()
    
    $response = $ftpRequest.GetResponse()
    $response.Close()
    
    Write-Host "From: $localFile" -ForegroundColor Gray
    Write-Host "To: $ftpUri" -ForegroundColor Gray
    Write-Host ""
    Write-Host "CSS file uploaded successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "ERROR: Failed to upload CSS file" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
