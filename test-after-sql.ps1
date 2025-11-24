# Test script - Run this AFTER executing the SQL in Railway

Write-Host "`n🧪 Testing Featured Events System...`n" -ForegroundColor Cyan

# Test 1: Events API
Write-Host "1️⃣ Testing Events API..." -ForegroundColor Yellow
try {
    $events = Invoke-WebRequest -Uri "https://wonderful-vibrancy-production.up.railway.app/api/events?status=PUBLISHED&limit=2" -ErrorAction Stop
    Write-Host "   ✅ Events API: Working ($($events.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Events API: Failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Featured Pricing API
Write-Host "`n2️⃣ Testing Featured Pricing API..." -ForegroundColor Yellow
try {
    $pricing = Invoke-WebRequest -Uri "https://wonderful-vibrancy-production.up.railway.app/api/featured/pricing" -ErrorAction Stop
    $tiers = ($pricing.Content | ConvertFrom-Json)
    if ($tiers.Count -gt 0) {
        Write-Host "   ✅ Featured Pricing: $($tiers.Count) tiers found" -ForegroundColor Green
        $tiers | Select-Object tier, slot_position, base_price_weekly | Format-Table -AutoSize
    } else {
        Write-Host "   ⚠️ Featured Pricing: No tiers found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Featured Pricing: Failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Featured Active Events
Write-Host "3️⃣ Testing Featured Active Events API..." -ForegroundColor Yellow
try {
    $featured = Invoke-WebRequest -Uri "https://wonderful-vibrancy-production.up.railway.app/api/featured/active" -ErrorAction Stop
    Write-Host "   ✅ Featured Active: Working (currently empty - no slots booked yet)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Featured Active: Failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: WordPress
Write-Host "`n4️⃣ Testing WordPress Site..." -ForegroundColor Yellow
try {
    $wp = Invoke-WebRequest -Uri "https://firstindallas.com/events-calendar/" -ErrorAction Stop
    Write-Host "   ✅ WordPress: Site loading ($($wp.StatusCode))" -ForegroundColor Green
    if ($wp.Content -like "*event-card*") {
        Write-Host "   ✅ WordPress: Events displaying" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ WordPress: Failed - $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n✨ Testing Complete!`n" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Go to WordPress Admin → Plugins" -ForegroundColor White
Write-Host "2. Deactivate + Reactivate 'Events CMS Directory'" -ForegroundColor White
Write-Host "3. Clear browser cache (Ctrl+Shift+Delete)" -ForegroundColor White
Write-Host "4. Visit your events page" -ForegroundColor White
