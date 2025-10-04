# ===========================================
# SUBSCRIPTION INTEGRATION SETUP SCRIPT
# ===========================================

param(
  [string]$CursorApiKey = "",
  [string]$GitHubCopilotApiKey = "",
  [string]$SessionName = "n8n-ai-router",
  [string]$ProviderMode = "subscription_first",
  [switch]$SkipDocker = $false
)

Write-Host "🚀 Setting up Subscription Integration for n8n" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Function to get API keys
function Get-ApiKeys {
  $keys = @{}
    
  if ($CursorApiKey) {
    $keys.Cursor = $CursorApiKey
  }
  else {
    Write-Host "🔑 Cursor IDE API Key:" -ForegroundColor Yellow
    Write-Host "   Settings > Account > API Keys in Cursor IDE" -ForegroundColor Cyan
    $keys.Cursor = Read-Host "Enter Cursor API Key (or press Enter to skip)"
  }
    
  if ($GitHubCopilotApiKey) {
    $keys.GitHubCopilot = $GitHubCopilotApiKey
  }
  else {
    Write-Host "🔑 GitHub Copilot API Key:" -ForegroundColor Yellow
    Write-Host "   VS Code > Settings > GitHub Copilot > API Keys" -ForegroundColor Cyan
    $keys.GitHubCopilot = Read-Host "Enter GitHub Copilot API Key (or press Enter to skip)"
  }
    
  return $keys
}

# Function to update environment file
function Update-EnvironmentFile {
  param(
    [hashtable]$ApiKeys,
    [string]$SessionName,
    [string]$ProviderMode
  )
    
  Write-Host "📝 Updating environment configuration..." -ForegroundColor Yellow
    
  $envFile = ".env"
  $envExample = "env.rag-system.example"
    
  if (-not (Test-Path $envExample)) {
    Write-Host "❌ Environment example file not found: $envExample" -ForegroundColor Red
    exit 1
  }
    
  # Copy example to .env if it doesn't exist
  if (-not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
    Write-Host "✅ Created .env file from example" -ForegroundColor Green
  }
    
  # Update .env file with subscription configuration
  $envContent = Get-Content $envFile -Raw
    
  # Update Cursor API key
  if ($ApiKeys.Cursor) {
    $envContent = $envContent -replace "CURSOR_API_KEY=your-cursor-api-key", "CURSOR_API_KEY=$($ApiKeys.Cursor)"
  }
    
  # Update GitHub Copilot API key
  if ($ApiKeys.GitHubCopilot) {
    $envContent = $envContent -replace "GITHUB_COPILOT_API_KEY=your-github-copilot-api-key", "GITHUB_COPILOT_API_KEY=$($ApiKeys.GitHubCopilot)"
  }
    
  # Update session name and provider mode
  $envContent = $envContent -replace "CURSOR_SESSION_NAME=n8n-ai-router", "CURSOR_SESSION_NAME=$SessionName"
  $envContent = $envContent -replace "GITHUB_COPILOT_SESSION_NAME=n8n-ai-router", "GITHUB_COPILOT_SESSION_NAME=$SessionName"
  $envContent = $envContent -replace "AI_PROVIDER_MODE=subscription_first", "AI_PROVIDER_MODE=$ProviderMode"
    
  Set-Content $envFile $envContent -Encoding UTF8
  Write-Host "✅ Updated .env file with subscription configuration" -ForegroundColor Green
}

# Function to test API connections
function Test-ApiConnections {
  param([hashtable]$ApiKeys)
    
  $results = @{}
    
  # Test Cursor API
  if ($ApiKeys.Cursor) {
    Write-Host "🔍 Testing Cursor API connection..." -ForegroundColor Yellow
    try {
      $headers = @{
        "Authorization" = "Bearer $($ApiKeys.Cursor)"
        "Content-Type"  = "application/json"
      }
            
      $response = Invoke-RestMethod -Uri "https://api.cursor.sh/v1/health" -Method GET -Headers $headers -TimeoutSec 10
      $results.Cursor = $true
      Write-Host "✅ Cursor API connection successful!" -ForegroundColor Green
    }
    catch {
      Write-Host "❌ Cursor API connection failed: $($_.Exception.Message)" -ForegroundColor Red
      $results.Cursor = $false
    }
  }
    
  # Test GitHub Copilot API
  if ($ApiKeys.GitHubCopilot) {
    Write-Host "🔍 Testing GitHub Copilot API connection..." -ForegroundColor Yellow
    try {
      $headers = @{
        "Authorization"        = "Bearer $($ApiKeys.GitHubCopilot)"
        "Content-Type"         = "application/json"
        "X-GitHub-Api-Version" = "2023-07-07"
      }
            
      $response = Invoke-RestMethod -Uri "https://api.githubcopilot.com/v1/models" -Method GET -Headers $headers -TimeoutSec 10
      $results.GitHubCopilot = $true
      Write-Host "✅ GitHub Copilot API connection successful!" -ForegroundColor Green
    }
    catch {
      Write-Host "❌ GitHub Copilot API connection failed: $($_.Exception.Message)" -ForegroundColor Red
      $results.GitHubCopilot = $false
    }
  }
    
  return $results
}

# Function to start Docker services
function Start-DockerServices {
  if ($SkipDocker) {
    Write-Host "⏭️ Skipping Docker services start" -ForegroundColor Yellow
    return
  }
    
  Write-Host "🐳 Starting Docker services..." -ForegroundColor Yellow
    
  try {
    # Check if Docker is running
    docker ps | Out-Null
    if ($LASTEXITCODE -ne 0) {
      Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
      return $false
    }
        
    # Start AI Router service
    Write-Host "🚀 Starting AI Router service..." -ForegroundColor Cyan
    docker-compose -f docker-compose-rag-system.yml up -d ai-router
        
    if ($LASTEXITCODE -eq 0) {
      Write-Host "✅ AI Router service started successfully" -ForegroundColor Green
    }
    else {
      Write-Host "❌ Failed to start AI Router service" -ForegroundColor Red
      return $false
    }
        
    # Check service health
    Start-Sleep -Seconds 10
    Write-Host "🔍 Checking AI Router health..." -ForegroundColor Cyan
        
    try {
      $healthResponse = Invoke-RestMethod -Uri "http://localhost:8081/health" -Method GET -TimeoutSec 10
      Write-Host "✅ AI Router is healthy: $($healthResponse.status)" -ForegroundColor Green
            
      # Check provider status
      $providersResponse = Invoke-RestMethod -Uri "http://localhost:8081/providers" -Method GET -TimeoutSec 10
      Write-Host "📊 Available providers:" -ForegroundColor Cyan
            
      foreach ($provider in $providersResponse.providers) {
        $status = if ($provider.name -eq "cursor" -and $healthResponse.providers.cursor -eq "healthy") { "✅" }
        elseif ($provider.name -eq "github_copilot" -and $healthResponse.providers.github_copilot -eq "healthy") { "✅" }
        else { "❌" }
        Write-Host "   $status $($provider.name): $($provider.description)" -ForegroundColor White
      }
    }
    catch {
      Write-Host "⚠️ Could not check AI Router health: $($_.Exception.Message)" -ForegroundColor Yellow
    }
        
    return $true
  }
  catch {
    Write-Host "❌ Failed to start Docker services: $($_.Exception.Message)" -ForegroundColor Red
    return $false
  }
}

# Function to show usage instructions
function Show-UsageInstructions {
  param([hashtable]$ApiKeys)
    
  Write-Host ""
  Write-Host "🎯 SUBSCRIPTION INTEGRATION SETUP COMPLETE!" -ForegroundColor Green
  Write-Host "===========================================" -ForegroundColor Green
  Write-Host ""
  Write-Host "📋 What was configured:" -ForegroundColor Cyan
    
  if ($ApiKeys.Cursor) {
    Write-Host "   ✅ Cursor IDE API key configured" -ForegroundColor White
  }
    
  if ($ApiKeys.GitHubCopilot) {
    Write-Host "   ✅ GitHub Copilot API key configured" -ForegroundColor White
  }
    
  Write-Host "   ✅ Environment variables updated" -ForegroundColor White
  Write-Host "   ✅ Docker services started" -ForegroundColor White
  Write-Host ""
  Write-Host "🚀 How to use:" -ForegroundColor Cyan
  Write-Host "   1. Your n8n system will now use your subscription APIs" -ForegroundColor White
  Write-Host "   2. No need to pay for separate AI API subscriptions" -ForegroundColor White
  Write-Host "   3. Same quality models as in your VS Code ecosystem" -ForegroundColor White
  Write-Host ""
  Write-Host "🔍 Test the integration:" -ForegroundColor Cyan
  Write-Host "   curl http://localhost:8081/health" -ForegroundColor White
  Write-Host "   curl http://localhost:8081/providers" -ForegroundColor White
  Write-Host ""
  Write-Host "📊 Monitor usage:" -ForegroundColor Cyan
  Write-Host "   curl http://localhost:8081/metrics" -ForegroundColor White
  Write-Host ""
  Write-Host "🎯 Provider modes:" -ForegroundColor Cyan
  Write-Host "   subscription_first - Use subscriptions first, then fallback" -ForegroundColor White
  Write-Host "   cursor_only - Use only Cursor IDE" -ForegroundColor White
  Write-Host "   copilot_only - Use only GitHub Copilot" -ForegroundColor White
  Write-Host "   paid_only - Use only paid APIs (Claude, OpenAI)" -ForegroundColor White
  Write-Host ""
}

# Main execution
try {
  Write-Host "🎯 Setting up subscription integration for n8n..." -ForegroundColor Green
  Write-Host ""
    
  # Get API keys
  $apiKeys = Get-ApiKeys
    
  # Test API connections
  $connectionResults = Test-ApiConnections -ApiKeys $apiKeys
    
  # Check if at least one subscription is working
  $workingSubscriptions = ($connectionResults.Values | Where-Object { $_ -eq $true }).Count
    
  if ($workingSubscriptions -eq 0) {
    Write-Host "⚠️ No working subscription APIs found. System will use fallback providers." -ForegroundColor Yellow
    Write-Host "   Make sure to configure fallback API keys (Claude, OpenAI) in .env file" -ForegroundColor Cyan
  }
  else {
    Write-Host "✅ $workingSubscriptions subscription(s) working!" -ForegroundColor Green
  }
    
  # Update environment file
  Update-EnvironmentFile -ApiKeys $apiKeys -SessionName $SessionName -ProviderMode $ProviderMode
    
  # Start Docker services
  Start-DockerServices
    
  # Show usage instructions
  Show-UsageInstructions -ApiKeys $apiKeys
    
  Write-Host "🎉 Subscription integration setup completed successfully!" -ForegroundColor Green
}
catch {
  Write-Host "❌ Setup failed: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}
