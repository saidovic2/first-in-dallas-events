#!/usr/bin/env pwsh
# WordPress Integration Setup Helper

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   Events CMS → WordPress Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if WordPress plugin folder exists
if (-not (Test-Path ".\wordpress-plugin\events-cms-directory")) {
    Write-Host "❌ Plugin folder not found!" -ForegroundColor Red
    Write-Host "Expected: .\wordpress-plugin\events-cms-directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Plugin files found" -ForegroundColor Green
Write-Host ""

# Ask for WordPress path
Write-Host "Where is your WordPress installed?" -ForegroundColor Yellow
Write-Host ""
Write-Host "Common paths:" -ForegroundColor Gray
Write-Host "  1. Local by Flywheel: C:\Users\$env:USERNAME\Local Sites\SITENAME\app\public" -ForegroundColor Gray
Write-Host "  2. XAMPP: C:\xampp\htdocs\wordpress" -ForegroundColor Gray
Write-Host "  3. WAMP: C:\wamp64\www\wordpress" -ForegroundColor Gray
Write-Host ""

$wpPath = Read-Host "Enter WordPress installation path"

# Validate path
if (-not (Test-Path $wpPath)) {
    Write-Host "❌ WordPress path not found: $wpPath" -ForegroundColor Red
    exit 1
}

# Check if wp-content/plugins exists
$pluginsPath = Join-Path $wpPath "wp-content\plugins"
if (-not (Test-Path $pluginsPath)) {
    Write-Host "❌ Plugins folder not found: $pluginsPath" -ForegroundColor Red
    Write-Host "   Make sure WordPress is properly installed" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ WordPress installation found" -ForegroundColor Green
Write-Host ""

# Copy plugin
$destinationPath = Join-Path $pluginsPath "events-cms-directory"

Write-Host "📂 Copying plugin files..." -ForegroundColor Yellow

try {
    if (Test-Path $destinationPath) {
        Write-Host "⚠️  Plugin already exists. Updating..." -ForegroundColor Yellow
        Remove-Item -Path $destinationPath -Recurse -Force
    }
    
    Copy-Item -Path ".\wordpress-plugin\events-cms-directory" -Destination $destinationPath -Recurse
    
    Write-Host "✅ Plugin copied successfully!" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "❌ Error copying plugin: $_" -ForegroundColor Red
    exit 1
}

# Display next steps
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   🎉 Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""

Write-Host "1. Login to WordPress Admin" -ForegroundColor White
Write-Host "   URL: http://localhost/wp-admin (or your WordPress URL)" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Activate the Plugin" -ForegroundColor White
Write-Host "   - Go to: Plugins → Installed Plugins" -ForegroundColor Gray
Write-Host "   - Find: 'Events CMS Directory'" -ForegroundColor Gray
Write-Host "   - Click: Activate" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Configure the Plugin" -ForegroundColor White
Write-Host "   - Go to: Settings → Events CMS" -ForegroundColor Gray
Write-Host "   - Set API URL: http://localhost:8001/api" -ForegroundColor Gray
Write-Host "   - Click: Save Changes" -ForegroundColor Gray
Write-Host ""

Write-Host "4. Create Events Page" -ForegroundColor White
Write-Host "   - Go to: Pages → Add New" -ForegroundColor Gray
Write-Host "   - Title: Events" -ForegroundColor Gray
Write-Host "   - Content: [events_directory]" -ForegroundColor Cyan
Write-Host "   - Click: Publish" -ForegroundColor Gray
Write-Host ""

Write-Host "5. View Your Events!" -ForegroundColor White
Write-Host "   Visit your new Events page" -ForegroundColor Gray
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "📖 Full guide: WORDPRESS_INTEGRATION_GUIDE.md" -ForegroundColor Gray
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to open the guide
$openGuide = Read-Host "Open the full integration guide? (Y/n)"
if ($openGuide -ne "n" -and $openGuide -ne "N") {
    Start-Process "WORDPRESS_INTEGRATION_GUIDE.md"
}
