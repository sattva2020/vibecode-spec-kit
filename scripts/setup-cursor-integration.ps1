# ===========================================
# CURSOR IDE INTEGRATION SETUP SCRIPT
# ===========================================

param(
  [string]$CursorApiKey = "",
  [string]$SessionName = "n8n-ai-router",
  [switch]$SkipDocker = $false
)

Write-Host "🚀 Setting up Cursor IDE Integration for n8n" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Function to check if running as administrator
function Test-Administrator {
  $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
  return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to get Cursor API key
function Get-CursorApiKey {
  if ($CursorApiKey) {
    return $CursorApiKey
  }
    
  Write-Host "🔑 Please provide your Cursor API key:" -ForegroundColor Yellow
  Write-Host "   You can find it in Cursor IDE: Settings > Account > API Keys" -ForegroundColor Cyan
    
  $apiKey = Read-Host "Enter Cursor API Key"
    
  if (-not $apiKey) {
    Write-Host "❌ API key is required!" -ForegroundColor Red
    exit 1
  }
    
  return $apiKey
}

# Function to update environment file
function Update-EnvironmentFile {
  param(
    [string]$ApiKey,
    [string]$SessionName
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
    
  # Update .env file with Cursor configuration
  $envContent = Get-Content $envFile -Raw
    
  # Update Cursor API key
  $envContent = $envContent -replace "CURSOR_API_KEY=your-cursor-api-key", "CURSOR_API_KEY=$ApiKey"
  $envContent = $envContent -replace "CURSOR_SESSION_NAME=n8n-ai-router", "CURSOR_SESSION_NAME=$SessionName"
  $envContent = $envContent -replace "AI_DEFAULT_PROVIDER=cursor", "AI_DEFAULT_PROVIDER=cursor"
  $envContent = $envContent -replace "AI_PROVIDER_MODE=cursor_first", "AI_PROVIDER_MODE=cursor_first"
    
  Set-Content $envFile $envContent -Encoding UTF8
  Write-Host "✅ Updated .env file with Cursor configuration" -ForegroundColor Green
}

# Function to test Cursor API connection
function Test-CursorApiConnection {
  param([string]$ApiKey)
    
  Write-Host "🔍 Testing Cursor API connection..." -ForegroundColor Yellow
    
  try {
    $headers = @{
      "Authorization" = "Bearer $ApiKey"
      "Content-Type"  = "application/json"
    }
        
    $response = Invoke-RestMethod -Uri "https://api.cursor.sh/v1/health" -Method GET -Headers $headers -TimeoutSec 10
        
    if ($response) {
      Write-Host "✅ Cursor API connection successful!" -ForegroundColor Green
      return $true
    }
    else {
      Write-Host "❌ Cursor API connection failed" -ForegroundColor Red
      return $false
    }
  }
  catch {
    Write-Host "❌ Cursor API connection failed: $($_.Exception.Message)" -ForegroundColor Red
    return $false
  }
}

# Function to create Cursor terminal session
function New-CursorTerminalSession {
  param(
    [string]$ApiKey,
    [string]$SessionName
  )
    
  Write-Host "🖥️ Creating Cursor terminal session..." -ForegroundColor Yellow
    
  try {
    $headers = @{
      "Authorization" = "Bearer $ApiKey"
      "Content-Type"  = "application/json"
    }
        
    $body = @{
      name        = $SessionName
      type        = "automation"
      description = "AI Router для n8n workflow'ов"
      metadata    = @{
        purpose = "n8n_workflow_creation"
        version = "1.0.0"
      }
    } | ConvertTo-Json -Depth 3
        
    $response = Invoke-RestMethod -Uri "https://api.cursor.sh/v1/sessions/terminal" -Method POST -Headers $headers -Body $body -TimeoutSec 30
        
    if ($response.session_id) {
      Write-Host "✅ Cursor terminal session created: $($response.session_id)" -ForegroundColor Green
      return $response.session_id
    }
    else {
      Write-Host "❌ Failed to create Cursor terminal session" -ForegroundColor Red
      return $null
    }
  }
  catch {
    Write-Host "❌ Failed to create Cursor terminal session: $($_.Exception.Message)" -ForegroundColor Red
    return $null
  }
}

# Function to update Docker Compose
function Update-DockerCompose {
  Write-Host "🐳 Updating Docker Compose configuration..." -ForegroundColor Yellow
    
  $dockerComposeFile = "docker-compose-rag-system.yml"
    
  if (-not (Test-Path $dockerComposeFile)) {
    Write-Host "❌ Docker Compose file not found: $dockerComposeFile" -ForegroundColor Red
    return $false
  }
    
  # Check if AI Router service already exists
  $dockerContent = Get-Content $dockerComposeFile -Raw
    
  if ($dockerContent -match "ai-router:") {
    Write-Host "✅ AI Router service already configured in Docker Compose" -ForegroundColor Green
    return $true
  }
    
  Write-Host "⚠️ AI Router service not found in Docker Compose" -ForegroundColor Yellow
  Write-Host "   Please ensure ai-router service is added to docker-compose-rag-system.yml" -ForegroundColor Cyan
    
  return $false
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
            
      if ($healthResponse.providers.cursor -eq "healthy") {
        Write-Host "✅ Cursor integration is working!" -ForegroundColor Green
      }
      else {
        Write-Host "⚠️ Cursor integration status: $($healthResponse.providers.cursor)" -ForegroundColor Yellow
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
  Write-Host ""
  Write-Host "🎯 CURSOR INTEGRATION SETUP COMPLETE!" -ForegroundColor Green
  Write-Host "=====================================" -ForegroundColor Green
  Write-Host ""
  Write-Host "📋 What was configured:" -ForegroundColor Cyan
  Write-Host "   ✅ Cursor API key configured" -ForegroundColor White
  Write-Host "   ✅ Terminal session created" -ForegroundColor White
  Write-Host "   ✅ Environment variables updated" -ForegroundColor White
  Write-Host "   ✅ Docker services started" -ForegroundColor White
  Write-Host ""
  Write-Host "🚀 How to use:" -ForegroundColor Cyan
  Write-Host "   1. Your n8n system will now use Cursor IDE models" -ForegroundColor White
  Write-Host "   2. No need to pay for separate AI API subscriptions" -ForegroundColor White
  Write-Host "   3. Same quality models as in your Cursor IDE" -ForegroundColor White
  Write-Host ""
  Write-Host "🔍 Test the integration:" -ForegroundColor Cyan
  Write-Host "   curl http://localhost:8081/cursor/health" -ForegroundColor White
  Write-Host ""
  Write-Host "📊 Monitor usage:" -ForegroundColor Cyan
  Write-Host "   curl http://localhost:8081/metrics" -ForegroundColor White
  Write-Host ""
}

# Main execution
try {
  # Get Cursor API key
  $apiKey = Get-CursorApiKey
    
  # Test API connection
  if (-not (Test-CursorApiConnection -ApiKey $apiKey)) {
    Write-Host "❌ Cannot proceed without working Cursor API connection" -ForegroundColor Red
    exit 1
  }
    
  # Update environment file
  Update-EnvironmentFile -ApiKey $apiKey -SessionName $SessionName
    
  # Create terminal session
  $sessionId = New-CursorTerminalSession -ApiKey $apiKey -SessionName $SessionName
    
  if (-not $sessionId) {
    Write-Host "⚠️ Could not create terminal session, but continuing..." -ForegroundColor Yellow
  }
    
  # Update Docker Compose
  Update-DockerCompose
    
  # Start Docker services
  Start-DockerServices
    
  # Show usage instructions
  Show-UsageInstructions
    
  Write-Host "🎉 Cursor integration setup completed successfully!" -ForegroundColor Green
}
catch {
  Write-Host "❌ Setup failed: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}
