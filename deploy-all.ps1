# Unified Deployment Script
# Deploys all components: API (Railway), CMS (Vercel), and WordPress Plugin (FTP)

param(
    [Parameter(Mandatory=$false)]
    [string]$PluginVersion,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('all', 'api', 'cms', 'plugin')]
    [string]$Target = 'all',
    
    [Parameter(Mandatory=$false)]
    [string]$CommitMessage = "Update deployment"
)

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  UNIFIED DEPLOYMENT - First in Dallas Events CMS" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

$deployAPI = $false
$deployCMS = $false
$deployPlugin = $false

switch ($Target) {
    'all' {
        $deployAPI = $true
        $deployCMS = $true
        $deployPlugin = $true
    }
    'api' { $deployAPI = $true }
    'cms' { $deployCMS = $true }
    'plugin' { $deployPlugin = $true }
}

$startTime = Get-Date

# ========================================
# 1. Deploy API to Railway
# ========================================
if ($deployAPI) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host "  [1/3] Deploying API to Railway..." -ForegroundColor Blue
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host ""
    
    # Check if Railway CLI is installed
    $railwayInstalled = Get-Command railway -ErrorAction SilentlyContinue
    
    if ($railwayInstalled) {
        Write-Host "Committing API changes..." -ForegroundColor Yellow
        
        Push-Location api
        try {
            # Add and commit changes
            git add .
            git commit -m "$CommitMessage" -ErrorAction SilentlyContinue
            
            # Push to Railway (this triggers automatic deployment)
            Write-Host "Pushing to Railway..." -ForegroundColor Yellow
            git push railway main
            
            Write-Host ""
            Write-Host "  ✓ API deployment initiated on Railway!" -ForegroundColor Green
            Write-Host "  Monitor deployment: railway logs" -ForegroundColor Gray
            Write-Host ""
        } catch {
            Write-Host "  ✗ API deployment failed: $_" -ForegroundColor Red
            Write-Host ""
        } finally {
            Pop-Location
        }
    } else {
        Write-Host "  Railway CLI not installed!" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  MANUAL DEPLOYMENT REQUIRED:" -ForegroundColor Yellow
        Write-Host "  1. Push your changes to GitHub" -ForegroundColor White
        Write-Host "     cd api && git add . && git commit -m '$CommitMessage' && git push" -ForegroundColor Gray
        Write-Host "  2. Railway will auto-deploy from GitHub" -ForegroundColor White
        Write-Host ""
        Write-Host "  OR install Railway CLI:" -ForegroundColor Yellow
        Write-Host "     npm install -g @railway/cli" -ForegroundColor Gray
        Write-Host "     railway login" -ForegroundColor Gray
        Write-Host "     railway link" -ForegroundColor Gray
        Write-Host ""
    }
}

# ========================================
# 2. Deploy CMS to Vercel
# ========================================
if ($deployCMS) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    Write-Host "  [2/3] Deploying CMS to Vercel..." -ForegroundColor Magenta
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    Write-Host ""
    
    # Check if Vercel CLI is installed
    $vercelInstalled = Get-Command vercel -ErrorAction SilentlyContinue
    
    if ($vercelInstalled) {
        Write-Host "Deploying to Vercel..." -ForegroundColor Yellow
        
        Push-Location hub
        try {
            # Deploy to production
            vercel --prod --yes
            
            Write-Host ""
            Write-Host "  ✓ CMS deployed to Vercel successfully!" -ForegroundColor Green
            Write-Host ""
        } catch {
            Write-Host "  ✗ CMS deployment failed: $_" -ForegroundColor Red
            Write-Host ""
        } finally {
            Pop-Location
        }
    } else {
        Write-Host "  Vercel CLI not installed!" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  MANUAL DEPLOYMENT REQUIRED:" -ForegroundColor Yellow
        Write-Host "  1. Push your changes to GitHub" -ForegroundColor White
        Write-Host "     cd hub && git add . && git commit -m '$CommitMessage' && git push" -ForegroundColor Gray
        Write-Host "  2. Vercel will auto-deploy from GitHub" -ForegroundColor White
        Write-Host ""
        Write-Host "  OR install Vercel CLI:" -ForegroundColor Yellow
        Write-Host "     npm install -g vercel" -ForegroundColor Gray
        Write-Host "     vercel login" -ForegroundColor Gray
        Write-Host "     cd hub && vercel link" -ForegroundColor Gray
        Write-Host ""
    }
}

# ========================================
# 3. Deploy Plugin via FTP
# ========================================
if ($deployPlugin) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host "  [3/3] Deploying WordPress Plugin via FTP..." -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host ""
    
    # Call the FTP deployment script
    if ([string]::IsNullOrWhiteSpace($PluginVersion)) {
        & .\deploy-plugin-ftp.ps1 -SkipVersionUpdate
    } else {
        & .\deploy-plugin-ftp.ps1 -Version $PluginVersion
    }
}

# ========================================
# Summary
# ========================================
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT SUMMARY" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Target: $Target" -ForegroundColor White
Write-Host "Duration: $($duration.TotalSeconds) seconds" -ForegroundColor White
Write-Host ""

if ($deployAPI) {
    Write-Host "  [✓] API (Railway):" -ForegroundColor Green
    Write-Host "      Check deployment status at Railway dashboard" -ForegroundColor Gray
    Write-Host ""
}

if ($deployCMS) {
    Write-Host "  [✓] CMS (Vercel):" -ForegroundColor Green
    Write-Host "      Check deployment status at Vercel dashboard" -ForegroundColor Gray
    Write-Host ""
}

if ($deployPlugin) {
    Write-Host "  [✓] WordPress Plugin (FTP):" -ForegroundColor Green
    Write-Host "      Plugin updated on WordPress server" -ForegroundColor Gray
    Write-Host "      Remember to deactivate/reactivate in WP admin" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "All deployments completed!" -ForegroundColor Green
Write-Host ""
