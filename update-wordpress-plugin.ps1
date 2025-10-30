# Update WordPress Plugin Script
Write-Host "Updating Events CMS Directory Plugin..." -ForegroundColor Cyan

$sourcePath = ".\wordpress-plugin\events-cms-directory"
$destPath = "C:\Users\HP\Local Sites\first-in-dallas\app\public\wp-content\plugins\events-cms-directory"

# Check if source exists
if (-not (Test-Path $sourcePath)) {
    Write-Host "ERROR: Source plugin folder not found!" -ForegroundColor Red
    exit 1
}

# Check if destination exists
if (-not (Test-Path $destPath)) {
    Write-Host "ERROR: WordPress plugin folder not found!" -ForegroundColor Red
    Write-Host "Make sure the plugin is installed at: $destPath" -ForegroundColor Yellow
    exit 1
}

# Copy files
Write-Host "Copying updated files..." -ForegroundColor Yellow
try {
    Copy-Item -Path "$sourcePath\*" -Destination $destPath -Recurse -Force
    Write-Host ""
    Write-Host "Plugin updated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Changes applied:" -ForegroundColor Cyan
    Write-Host "  - Removed Category filter" -ForegroundColor White
    Write-Host "  - Added Date Picker filter" -ForegroundColor White
    Write-Host "  - Added 20-per-page pagination" -ForegroundColor White
    Write-Host "  - Added URL query sync" -ForegroundColor White
    Write-Host "  - Updated empty state messages" -ForegroundColor White
    Write-Host "  - Added Upcoming Events sidebar widget" -ForegroundColor White
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Go to your WordPress page with [events_directory]" -ForegroundColor White
    Write-Host "  2. Refresh the page (Ctrl + F5)" -ForegroundColor White
    Write-Host "  3. Go to Appearance -> Widgets to add the 'Upcoming Events' widget" -ForegroundColor White
    Write-Host "  4. Drag the widget to your sidebar or any widget area" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "ERROR: Failed to copy files" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
