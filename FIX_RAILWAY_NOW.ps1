#!/usr/bin/env pwsh
# Railway Services Troubleshooting & Fix Script

Write-Host "========================================" -ForegroundColor Red
Write-Host "   🚨 RAILWAY SERVICES TROUBLESHOOT    " -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

Write-Host "❌ PROBLEM: Railway API services returning 404" -ForegroundColor Red
Write-Host ""
Write-Host "This means either:" -ForegroundColor Yellow
Write-Host "  1. Services are still deploying (wait 2-3 minutes)" -ForegroundColor White
Write-Host "  2. Railway domains have changed" -ForegroundColor White
Write-Host "  3. Services crashed during deployment" -ForegroundColor White
Write-Host "  4. Environment variables missing" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   STEP 1: CHECK RAILWAY DASHBOARD      " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1️⃣  Open Railway Dashboard:" -ForegroundColor Yellow
Write-Host "   https://railway.app/dashboard" -ForegroundColor White
Write-Host ""

Write-Host "2️⃣  Check your project and services status:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   For EACH service (API, Worker), check:" -ForegroundColor White
Write-Host "   ✅ Status is 'Active' (green dot)" -ForegroundColor Green
Write-Host "   ❌ If 'Building' - wait 2-3 more minutes" -ForegroundColor Yellow
Write-Host "   ❌ If 'Crashed' - click to see error logs" -ForegroundColor Red
Write-Host ""

Write-Host "3️⃣  Get the correct Railway domain:" -ForegroundColor Yellow
Write-Host "   • Click on API service" -ForegroundColor White
Write-Host "   • Go to 'Settings' tab" -ForegroundColor White
Write-Host "   • Click 'Networking' section" -ForegroundColor White
Write-Host "   • If no domain exists, click 'Generate Domain'" -ForegroundColor White
Write-Host "   • Copy the full domain URL" -ForegroundColor White
Write-Host ""

$apiDomain = Read-Host "Paste your Railway API domain here (e.g., https://something.up.railway.app)"

if ([string]::IsNullOrWhiteSpace($apiDomain)) {
    Write-Host ""
    Write-Host "⚠️  No domain provided. Please go to Railway and get the domain first." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Instructions:" -ForegroundColor Cyan
    Write-Host "1. Go to https://railway.app/dashboard" -ForegroundColor White
    Write-Host "2. Click your project" -ForegroundColor White
    Write-Host "3. Click API service" -ForegroundColor White
    Write-Host "4. Settings → Networking → Generate/Copy Domain" -ForegroundColor White
    Write-Host "5. Run this script again with the domain" -ForegroundColor White
    Write-Host ""
    exit 0
}

# Clean up the domain
$apiDomain = $apiDomain.Trim()
if (-not $apiDomain.StartsWith("http")) {
    $apiDomain = "https://$apiDomain"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   STEP 2: TEST RAILWAY API              " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Testing: $apiDomain/health" -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "$apiDomain/health" -Method Get -ErrorAction Stop
    $result = $response.Content | ConvertFrom-Json
    
    if ($result.status -eq "healthy") {
        Write-Host "✅ API is HEALTHY!" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "Testing events endpoint..." -ForegroundColor Cyan
        $eventsResponse = Invoke-WebRequest -Uri "$apiDomain/api/events?limit=5" -Method Get
        $events = $eventsResponse.Content | ConvertFrom-Json
        
        Write-Host "✅ Found $($events.Count) events" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "   ✅ API IS WORKING!                   " -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "Next Step: Update WordPress" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Go to WordPress Admin → Settings → Events CMS" -ForegroundColor White
        Write-Host "2. Set API URL to: $apiDomain/api" -ForegroundColor Cyan
        Write-Host "3. Save Changes" -ForegroundColor White
        Write-Host ""
        
        # Save to file for reference
        "$apiDomain/api" | Out-File -FilePath "RAILWAY_API_URL.txt" -Encoding UTF8
        Write-Host "✅ API URL saved to RAILWAY_API_URL.txt" -ForegroundColor Green
        
    } else {
        Write-Host "⚠️  API responded but status is: $($result.status)" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ API is NOT responding" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "   TROUBLESHOOTING STEPS                " -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    
    Write-Host "1️⃣  CHECK RAILWAY DEPLOYMENT LOGS:" -ForegroundColor Yellow
    Write-Host "   • Railway Dashboard → API Service → 'Deployments' tab" -ForegroundColor White
    Write-Host "   • Click latest deployment" -ForegroundColor White
    Write-Host "   • Look for error messages" -ForegroundColor White
    Write-Host ""
    
    Write-Host "2️⃣  CHECK ENVIRONMENT VARIABLES:" -ForegroundColor Yellow
    Write-Host "   Railway → API Service → 'Variables' tab" -ForegroundColor White
    Write-Host ""
    Write-Host "   Required variables:" -ForegroundColor White
    Write-Host "   • DATABASE_URL (from Railway PostgreSQL)" -ForegroundColor Cyan
    Write-Host "   • REDIS_URL (from Railway Redis)" -ForegroundColor Cyan
    Write-Host "   • JWT_SECRET (any random string)" -ForegroundColor Cyan
    Write-Host "   • EVENTBRITE_API_TOKEN=MOZFNTBR4O22QQV33X2C" -ForegroundColor Cyan
    Write-Host "   • TICKETMASTER_API_KEY=Tx3dcKearAsHFOrhBsO6JVK2HbT0AEoK" -ForegroundColor Cyan
    Write-Host "   • TICKETMASTER_AFFILIATE_ID=6497023" -ForegroundColor Cyan
    Write-Host "   • SUPABASE_URL=https://jwlvikkbcjrnzsvhyfgy.supabase.co" -ForegroundColor Cyan
    Write-Host "   • SUPABASE_SERVICE_ROLE_KEY=<your-key>" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "3️⃣  COMMON ERRORS & SOLUTIONS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Error: 'DATABASE_URL not set'" -ForegroundColor Red
    Write-Host "   Fix: Add DATABASE_URL from PostgreSQL service" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Error: 'Port already in use'" -ForegroundColor Red
    Write-Host "   Fix: Dockerfile uses $PORT variable (already fixed)" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Error: 'ModuleNotFoundError'" -ForegroundColor Red
    Write-Host "   Fix: Check requirements.txt exists in /api folder" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "4️⃣  REDEPLOY IF NEEDED:" -ForegroundColor Yellow
    Write-Host "   Railway → API Service → 'Deployments' tab → 'Redeploy'" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ADDITIONAL CHECKS                     " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 Database Status:" -ForegroundColor Yellow
Write-Host "   Check if events exist with PUBLISHED status" -ForegroundColor White
Write-Host ""
Write-Host "   Run this in Railway → PostgreSQL → Query:" -ForegroundColor Cyan
Write-Host ""
Write-Host @"
   SELECT 
       status, 
       COUNT(*) as count,
       MIN(start_at) as earliest,
       MAX(start_at) as latest
   FROM events
   GROUP BY status;
"@ -ForegroundColor White
Write-Host ""

Write-Host "   If all events are 'DRAFT', run this:" -ForegroundColor Yellow
Write-Host ""
Write-Host @"
   UPDATE events 
   SET status = 'PUBLISHED'
   WHERE status = 'DRAFT';
"@ -ForegroundColor White
Write-Host ""

Write-Host "🔄 Worker Status:" -ForegroundColor Yellow
Write-Host "   Check if Worker service is also Active in Railway" -ForegroundColor White
Write-Host "   Worker needs same environment variables as API" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "   NEXT STEPS                            " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "1. Fix any issues found above" -ForegroundColor White
Write-Host "2. Wait for Railway services to be 'Active'" -ForegroundColor White
Write-Host "3. Run this script again to test" -ForegroundColor White
Write-Host "4. Update WordPress with correct API URL" -ForegroundColor White
Write-Host "5. Update database events to PUBLISHED status" -ForegroundColor White
Write-Host ""

Write-Host "📖 For detailed help, see: URGENT_FIX_NOW.md" -ForegroundColor Cyan
Write-Host ""
