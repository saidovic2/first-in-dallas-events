#!/usr/bin/env pwsh
# Test Railway API and fix configuration

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Testing Railway API                  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test common Railway domains
$domains = @(
    "first-in-dallas-events-production.up.railway.app",
    "wonderful-vibrancy-production.up.railway.app",
    "astonishing-warmth-production.up.railway.app"
)

$workingDomain = $null

Write-Host "🔍 Testing Railway domains..." -ForegroundColor Yellow
Write-Host ""

foreach ($domain in $domains) {
    $url = "https://$domain"
    Write-Host "Testing: $url" -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri "$url/health" -Method Get -TimeoutSec 5 -ErrorAction Stop
        $result = $response.Content | ConvertFrom-Json
        
        if ($result.status -eq "healthy") {
            Write-Host "✅ FOUND WORKING API: $url" -ForegroundColor Green
            $workingDomain = $url
            break
        }
    } catch {
        Write-Host "   Not responding" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($workingDomain) {
    Write-Host "✅ API IS WORKING!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your Railway API URL: $workingDomain" -ForegroundColor White
    Write-Host ""
    
    # Test events endpoint
    Write-Host "Testing events endpoint..." -ForegroundColor Cyan
    try {
        $eventsResponse = Invoke-WebRequest -Uri "$workingDomain/api/events?limit=5" -Method Get -ErrorAction Stop
        $events = $eventsResponse.Content | ConvertFrom-Json
        
        Write-Host "✅ Events endpoint working!" -ForegroundColor Green
        Write-Host "   Found $($events.Count) events" -ForegroundColor White
        
        if ($events.Count -eq 0) {
            Write-Host ""
            Write-Host "⚠️  No events in database!" -ForegroundColor Yellow
            Write-Host "   This is why your CMS directory is empty." -ForegroundColor White
            Write-Host ""
            Write-Host "Possible causes:" -ForegroundColor Yellow
            Write-Host "   1. Events are DRAFT status (need to be PUBLISHED)" -ForegroundColor White
            Write-Host "   2. No events have been synced yet" -ForegroundColor White
            Write-Host "   3. Database is empty" -ForegroundColor White
        } else {
            Write-Host ""
            Write-Host "Sample events:" -ForegroundColor Cyan
            $events | Select-Object -First 3 | ForEach-Object {
                Write-Host "   • $($_.title) - Status: $($_.status)" -ForegroundColor White
            }
        }
    } catch {
        Write-Host "❌ Events endpoint error: $_" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   NEXT STEPS                          " -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "1️⃣  Update WordPress:" -ForegroundColor Yellow
    Write-Host "   WordPress Admin → Settings → Events CMS" -ForegroundColor White
    Write-Host "   Set API URL to: $workingDomain/api" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "2️⃣  Fix Database (if no events found):" -ForegroundColor Yellow
    Write-Host "   Go to Railway → PostgreSQL → Query tab" -ForegroundColor White
    Write-Host "   Run this SQL:" -ForegroundColor White
    Write-Host ""
    Write-Host "   UPDATE events SET status = 'PUBLISHED' WHERE status = 'DRAFT';" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "3️⃣  Test Sync:" -ForegroundColor Yellow
    Write-Host "   After WordPress is configured, try syncing from Eventbrite" -ForegroundColor White
    Write-Host ""
    
    # Save URL to file
    "$workingDomain/api" | Out-File -FilePath "WORKING_API_URL.txt" -Encoding UTF8
    Write-Host "✅ API URL saved to WORKING_API_URL.txt" -ForegroundColor Green
    
} else {
    Write-Host "❌ NO WORKING API FOUND" -ForegroundColor Red
    Write-Host ""
    Write-Host "This means Railway services are deployed but not accessible." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Common causes:" -ForegroundColor Yellow
    Write-Host "   1. Services don't have public domains generated" -ForegroundColor White
    Write-Host "   2. Environment variables missing (DATABASE_URL, REDIS_URL)" -ForegroundColor White
    Write-Host "   3. Services crashed after deployment" -ForegroundColor White
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "   FIX STEPS                           " -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    
    Write-Host "1️⃣  Generate Domain in Railway:" -ForegroundColor Yellow
    Write-Host "   Railway → first-in-dallas-events service" -ForegroundColor White
    Write-Host "   Settings → Networking → 'Generate Domain'" -ForegroundColor White
    Write-Host ""
    
    Write-Host "2️⃣  Check Environment Variables:" -ForegroundColor Yellow
    Write-Host "   Railway → first-in-dallas-events → Variables tab" -ForegroundColor White
    Write-Host "   Must have:" -ForegroundColor White
    Write-Host "   • DATABASE_URL" -ForegroundColor Cyan
    Write-Host "   • REDIS_URL" -ForegroundColor Cyan
    Write-Host "   • JWT_SECRET" -ForegroundColor Cyan
    Write-Host "   • EVENTBRITE_API_TOKEN=MOZFNTBR4O22QQV33X2C" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "3️⃣  Check Deployment Logs:" -ForegroundColor Yellow
    Write-Host "   Railway → first-in-dallas-events → Deployments" -ForegroundColor White
    Write-Host "   Click latest deployment → View logs" -ForegroundColor White
    Write-Host ""
    
    Write-Host "4️⃣  After fixing, run this script again:" -ForegroundColor Yellow
    Write-Host "   .\TEST_API.ps1" -ForegroundColor White
}

Write-Host ""
