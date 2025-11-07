# Test FTP Connection Script

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
$ftpPort = $envVars['FTP_PORT']
$ftpUser = $envVars['FTP_USER']
$ftpPassword = $envVars['FTP_PASSWORD']
$ftpRemotePath = $envVars['FTP_REMOTE_PATH']

Write-Host "Testing FTP Connection..." -ForegroundColor Cyan
Write-Host "Host: $ftpHost" -ForegroundColor White
Write-Host "Port: $ftpPort" -ForegroundColor White
Write-Host "User: $ftpUser" -ForegroundColor White
Write-Host "Path: $ftpRemotePath" -ForegroundColor White
Write-Host ""

try {
    $ftpUri = "ftp://${ftpHost}:${ftpPort}${ftpRemotePath}"
    Write-Host "Testing connection to: $ftpUri" -ForegroundColor Yellow
    
    $request = [System.Net.FtpWebRequest]::Create($ftpUri)
    $request.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
    $request.Method = [System.Net.WebRequestMethods+Ftp]::ListDirectory
    
    $response = $request.GetResponse()
    $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
    $listing = $reader.ReadToEnd()
    $reader.Close()
    $response.Close()
    
    Write-Host "✓ Connection successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Directory listing:" -ForegroundColor Green
    Write-Host $listing
    
} catch {
    Write-Host "✗ Connection failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. Path does not exist on server" -ForegroundColor White
    Write-Host "2. FTP credentials are incorrect" -ForegroundColor White
    Write-Host "3. FTP server is blocking connections" -ForegroundColor White
    Write-Host "4. Path might need adjustment" -ForegroundColor White
}
