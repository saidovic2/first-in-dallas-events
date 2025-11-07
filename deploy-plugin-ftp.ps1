# WordPress Plugin FTP Deployment Script
# Deploys the plugin to WordPress server via FTP

param(
    [Parameter(Mandatory=$false)]
    [string]$Version,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipVersionUpdate
)

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  WordPress Plugin FTP Deployment" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Load environment variables
$envFile = ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and fill in your FTP credentials." -ForegroundColor Yellow
    exit 1
}

# Parse .env file
$envVars = @{}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$key] = $value
    }
}

# Get FTP credentials
$ftpHost = $envVars['FTP_HOST']
$ftpPort = $envVars['FTP_PORT']
$ftpUser = $envVars['FTP_USER']
$ftpPassword = $envVars['FTP_PASSWORD']
$ftpRemotePath = $envVars['FTP_REMOTE_PATH']

# Validate FTP credentials
if ([string]::IsNullOrWhiteSpace($ftpHost) -or [string]::IsNullOrWhiteSpace($ftpUser) -or [string]::IsNullOrWhiteSpace($ftpPassword)) {
    Write-Host "ERROR: FTP credentials not configured!" -ForegroundColor Red
    Write-Host "Please update your .env file with FTP credentials:" -ForegroundColor Yellow
    Write-Host "  - FTP_HOST" -ForegroundColor Yellow
    Write-Host "  - FTP_USER" -ForegroundColor Yellow
    Write-Host "  - FTP_PASSWORD" -ForegroundColor Yellow
    Write-Host "  - FTP_REMOTE_PATH" -ForegroundColor Yellow
    exit 1
}

# Set default port if not specified
if ([string]::IsNullOrWhiteSpace($ftpPort)) {
    $ftpPort = "21"
}

$pluginPath = "wordpress-plugin\events-cms-directory"

# Step 1: Update version if specified
if (-not $SkipVersionUpdate -and -not [string]::IsNullOrWhiteSpace($Version)) {
    Write-Host "Step 1: Updating plugin version to $Version..." -ForegroundColor Yellow
    $phpFile = "$pluginPath\events-cms-directory.php"
    $content = Get-Content $phpFile -Raw
    $content = $content -replace "(\* Version:\s+)[\d\.]+", "`$1$Version"
    Set-Content $phpFile $content -NoNewline
    Write-Host "  Version updated to $Version!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Skipping version update..." -ForegroundColor Gray
    Write-Host ""
}

# Step 2: Check if WinSCP is available (more reliable for FTP)
$useWinSCP = $false
$winscpPath = "C:\Program Files (x86)\WinSCP\WinSCP.com"
if (Test-Path $winscpPath) {
    $useWinSCP = $true
    Write-Host "Found WinSCP - using for FTP transfer (recommended)" -ForegroundColor Green
} else {
    Write-Host "WinSCP not found - using PowerShell FTP (basic)" -ForegroundColor Yellow
    Write-Host "For better reliability, install WinSCP from: https://winscp.net/eng/download.php" -ForegroundColor Gray
}
Write-Host ""

# Step 3: Upload files via FTP
Write-Host "Step 2: Uploading plugin files to WordPress server..." -ForegroundColor Yellow

if ($useWinSCP) {
    # Use WinSCP for reliable FTP transfer
    $winscpScript = @"
open ftp://${ftpUser}:${ftpPassword}@${ftpHost}:${ftpPort}
option batch abort
option confirm off
synchronize remote "$pluginPath" "$ftpRemotePath" -delete -mirror
close
exit
"@
    
    $scriptPath = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $scriptPath -Value $winscpScript
    
    try {
        & $winscpPath /script=$scriptPath
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Plugin files uploaded successfully!" -ForegroundColor Green
        } else {
            Write-Host "  ERROR: WinSCP upload failed with exit code $LASTEXITCODE" -ForegroundColor Red
            exit 1
        }
    } finally {
        Remove-Item $scriptPath -ErrorAction SilentlyContinue
    }
} else {
    # Fallback to PowerShell FTP (basic, less reliable)
    Write-Host "  Using PowerShell FTP (may be slower)..." -ForegroundColor Gray
    
    # Create WebClient for FTP
    $ftpBase = "ftp://${ftpHost}:${ftpPort}${ftpRemotePath}"
    
    # Get all files to upload
    $files = Get-ChildItem -Path $pluginPath -Recurse -File | Where-Object { 
        $_.FullName -notmatch '\\\.git\\' 
    }
    
    $totalFiles = $files.Count
    $uploadedFiles = 0
    
    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($pluginPath.Length + 1).Replace('\', '/')
        $ftpUri = "$ftpBase/$relativePath"
        
        # Create directory structure
        $dirPath = Split-Path $ftpUri -Parent
        try {
            $request = [System.Net.FtpWebRequest]::Create($dirPath)
            $request.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
            $request.Method = [System.Net.WebRequestMethods+Ftp]::MakeDirectory
            $request.GetResponse() | Out-Null
        } catch {
            # Directory might already exist, ignore error
        }
        
        # Upload file
        try {
            $webclient = New-Object System.Net.WebClient
            $webclient.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
            $webclient.UploadFile($ftpUri, $file.FullName) | Out-Null
            $uploadedFiles++
            Write-Host "    [$uploadedFiles/$totalFiles] Uploaded: $relativePath" -ForegroundColor Gray
        } catch {
            Write-Host "    ERROR uploading $relativePath : $_" -ForegroundColor Red
        }
    }
    
    Write-Host "  Uploaded $uploadedFiles/$totalFiles files!" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Plugin deployed to: $ftpHost" -ForegroundColor Cyan
Write-Host "Remote path: $ftpRemotePath" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Go to your WordPress admin panel" -ForegroundColor White
Write-Host "2. Navigate to Plugins page" -ForegroundColor White
Write-Host "3. Deactivate and reactivate the plugin to load changes" -ForegroundColor White
Write-Host "4. Or use the following PHP to clear plugin cache:" -ForegroundColor White
Write-Host "   wp plugin deactivate events-cms-directory && wp plugin activate events-cms-directory" -ForegroundColor Gray
Write-Host ""
