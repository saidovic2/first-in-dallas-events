# Create WordPress Plugin ZIP with correct structure
# WordPress requires: plugin-name.zip/plugin-name/plugin-name.php

$pluginName = "events-cms-directory"
$sourceDir = "wordpress-plugin\$pluginName"
$zipFile = "$pluginName.zip"
$tempDir = "temp-zip-build"

Write-Host ""
Write-Host "Creating WordPress Plugin ZIP..." -ForegroundColor Cyan
Write-Host ""

# Clean up
if (Test-Path $zipFile) {
    Remove-Item $zipFile -Force
    Write-Host "Removed old ZIP file" -ForegroundColor Yellow
}

if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}

# Create temp directory structure
Write-Host "Setting up directory structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "$tempDir\$pluginName" -Force | Out-Null

# Copy plugin files (exclude .git folder)
Write-Host "Copying plugin files..." -ForegroundColor Yellow
Get-ChildItem -Path $sourceDir -Exclude ".git" | Copy-Item -Destination "$tempDir\$pluginName\" -Recurse -Force

# Verify main plugin file exists
$mainFile = "$tempDir\$pluginName\$pluginName.php"
if (-not (Test-Path $mainFile)) {
    Write-Host "ERROR: Main plugin file not found!" -ForegroundColor Red
    Write-Host "Looking for: $mainFile" -ForegroundColor Red
    Remove-Item $tempDir -Recurse -Force
    exit 1
}

Write-Host "Main plugin file found: $pluginName.php" -ForegroundColor Green

# Create ZIP
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
Add-Type -AssemblyName System.IO.Compression.FileSystem
$source = (Resolve-Path $tempDir).Path
$destination = Join-Path (Get-Location) $zipFile
[System.IO.Compression.ZipFile]::CreateFromDirectory($source, $destination)

# Clean up temp
Remove-Item $tempDir -Recurse -Force

Write-Host ""
Write-Host "SUCCESS!" -ForegroundColor Green
Write-Host ""
Write-Host "ZIP File: $zipFile" -ForegroundColor White
Write-Host "Location: $(Get-Location)\$zipFile" -ForegroundColor Cyan
Write-Host ""

# Show ZIP contents
Write-Host "ZIP Contents:" -ForegroundColor Yellow
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($destination)
$zip.Entries | Select-Object -First 10 FullName | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
if ($zip.Entries.Count -gt 10) {
    Write-Host "  ... and $($zip.Entries.Count - 10) more files" -ForegroundColor Gray
}
$zip.Dispose()

Write-Host ""
Write-Host "Ready to upload to WordPress!" -ForegroundColor Green
Write-Host ""
