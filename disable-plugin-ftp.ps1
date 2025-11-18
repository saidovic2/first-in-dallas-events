# Emergency script to disable plugin by renaming its folder
param(
    [string]$Action = "disable"  # "disable" or "enable"
)

# Load .env file
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        Set-Item -Path "env:$name" -Value $value
    }
}

$ftpHost = $env:FTP_HOST
$ftpUser = $env:FTP_USER
$ftpPassword = $env:FTP_PASSWORD

Write-Host "`n🚨 EMERGENCY: $Action Plugin`n" -ForegroundColor Red

try {
    # Create FTP request
    $ftpUri = "ftp://$ftpHost/wp-content/plugins/events-cms-directory"
    
    if ($Action -eq "disable") {
        $newName = "events-cms-directory-DISABLED"
        Write-Host "Renaming: events-cms-directory → events-cms-directory-DISABLED" -ForegroundColor Yellow
    } else {
        $newName = "events-cms-directory"
        $ftpUri = "ftp://$ftpHost/wp-content/plugins/events-cms-directory-DISABLED"
        Write-Host "Renaming: events-cms-directory-DISABLED → events-cms-directory" -ForegroundColor Yellow
    }
    
    $request = [System.Net.FtpWebRequest]::Create($ftpUri)
    $request.Method = [System.Net.WebRequestMethods+Ftp]::Rename
    $request.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
    $request.RenameTo = $newName
    
    $response = $request.GetResponse()
    $response.Close()
    
    Write-Host "✅ Plugin $Action`d successfully!" -ForegroundColor Green
    Write-Host "`nWait 10 seconds, then check: https://firstindallas.com" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "`nManual steps:" -ForegroundColor Yellow
    Write-Host "1. Connect via FTP to: $ftpHost" -ForegroundColor White
    Write-Host "2. Navigate to: /wp-content/plugins/" -ForegroundColor White
    Write-Host "3. Rename folder: events-cms-directory → events-cms-directory-DISABLED" -ForegroundColor White
}
