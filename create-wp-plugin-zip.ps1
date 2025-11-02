# Create WordPress-compatible plugin ZIP
# This ensures the correct folder structure for WordPress

Add-Type -AssemblyName System.IO.Compression.FileSystem

$sourceFolder = "wordpress-plugin\events-cms-directory"
$destination = "events-cms-directory.zip"

Write-Host ""
Write-Host "Creating WordPress-compatible plugin ZIP..." -ForegroundColor Cyan
Write-Host ""

# Clean up old zip
if (Test-Path $destination) {
    Remove-Item $destination -Force
    Write-Host "Removed old ZIP" -ForegroundColor Yellow
}

# Verify source exists
if (-not (Test-Path $sourceFolder)) {
    Write-Host "ERROR: Source folder not found!" -ForegroundColor Red
    exit 1
}

# Get full paths
$sourcePath = (Resolve-Path $sourceFolder).Path
$destPath = Join-Path (Get-Location) $destination

Write-Host "Creating ZIP archive..." -ForegroundColor Yellow

# Create ZIP - includeBaseDirectory = $true ensures the folder is named correctly
[System.IO.Compression.ZipFile]::CreateFromDirectory($sourcePath, $destPath, [System.IO.Compression.CompressionLevel]::Optimal, $true)

Write-Host ""
Write-Host "SUCCESS!" -ForegroundColor Green
Write-Host ""
Write-Host "File: $destination" -ForegroundColor White
Write-Host "Location: $(Get-Location)\$destination" -ForegroundColor Cyan
Write-Host ""
Write-Host "This ZIP is ready for WordPress upload!" -ForegroundColor Yellow
Write-Host ""
