# Create plugin ZIP for upload to live site
Add-Type -AssemblyName System.IO.Compression.FileSystem

$sourceFolder = "wordpress-plugin\events-cms-directory"
$destination = "events-cms-directory.zip"

# Clean up old zip
if (Test-Path $destination) {
    Remove-Item $destination -Force
    Write-Host "Removed old ZIP file" -ForegroundColor Yellow
}

# Verify source exists
if (-not (Test-Path $sourceFolder)) {
    Write-Host "ERROR: Source folder not found: $sourceFolder" -ForegroundColor Red
    exit 1
}

# Create the ZIP file
try {
    Write-Host "Creating ZIP file..." -ForegroundColor Cyan
    
    # Get full paths
    $sourcePath = (Resolve-Path $sourceFolder).Path
    $destPath = Join-Path (Get-Location) $destination
    
    # Create ZIP with proper structure
    [System.IO.Compression.ZipFile]::CreateFromDirectory($sourcePath, $destPath, [System.IO.Compression.CompressionLevel]::Optimal, $true)
    
    Write-Host ""
    Write-Host "SUCCESS! Plugin zipped: $destination" -ForegroundColor Green
    Write-Host ""
    Write-Host "File location: $(Get-Location)\$destination" -ForegroundColor White
    Write-Host ""
    Write-Host "Upload Instructions:" -ForegroundColor Cyan
    Write-Host "1. Go to WordPress Admin -> Plugins -> Add New" -ForegroundColor White
    Write-Host "2. Click 'Upload Plugin'" -ForegroundColor White
    Write-Host "3. Choose this file: $destination" -ForegroundColor White
    Write-Host "4. Click 'Install Now' and REPLACE the existing plugin" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "ERROR creating ZIP: $_" -ForegroundColor Red
    exit 1
}
