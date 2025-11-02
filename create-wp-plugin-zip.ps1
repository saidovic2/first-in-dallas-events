# Create WordPress-compatible plugin ZIP
# This ensures the correct folder structure for WordPress

Add-Type -AssemblyName System.IO.Compression.FileSystem

$sourceFolder = "wordpress-plugin\events-cms-directory"
$destination = "events-cms-directory-wordpress.zip"
$tempFolder = "temp-wp-plugin"

Write-Host ""
Write-Host "Creating WordPress-compatible plugin ZIP..." -ForegroundColor Cyan
Write-Host ""

# Clean up
if (Test-Path $destination) {
    Remove-Item $destination -Force
}

if (Test-Path $tempFolder) {
    Remove-Item $tempFolder -Recurse -Force
}

# Create temp structure
New-Item -ItemType Directory -Path "$tempFolder\events-cms-directory" -Force | Out-Null

# Copy all files
Write-Host "Copying plugin files..." -ForegroundColor Yellow
Copy-Item -Path "$sourceFolder\*" -Destination "$tempFolder\events-cms-directory\" -Recurse -Force

# Create ZIP
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
$sourcePath = (Resolve-Path "$tempFolder\events-cms-directory").Path
$destPath = Join-Path (Get-Location) $destination

[System.IO.Compression.ZipFile]::CreateFromDirectory($sourcePath, $destPath, [System.IO.Compression.CompressionLevel]::Optimal, $false)

# Clean up temp
Remove-Item $tempFolder -Recurse -Force

Write-Host ""
Write-Host "SUCCESS!" -ForegroundColor Green
Write-Host ""
Write-Host "WordPress plugin ZIP created: $destination" -ForegroundColor White
Write-Host "Location: $(Get-Location)\$destination" -ForegroundColor Cyan
Write-Host ""
Write-Host "Upload this file to WordPress now!" -ForegroundColor Yellow
Write-Host ""
