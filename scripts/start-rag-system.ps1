# ===========================================
# RAG System Startup Script for Windows
# ===========================================

param(
  [switch]$SkipPrerequisites,
  [switch]$Force,
  [switch]$Verbose
)

# Set error handling
$ErrorActionPreference = "Stop"

# Colors for output
$Colors = @{
  Success = "Green"
  Warning = "Yellow"
  Error   = "Red"
  Info    = "Cyan"
  Header  = "Magenta"
}

function Write-ColorOutput {
  param(
    [string]$Message,
    [string]$Color = "White"
  )
  Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Test-Prerequisites {
  Write-ColorOutput "🔍 Checking prerequisites..." "Header"
    
  # Check Docker Desktop
  try {
    $dockerVersion = docker --version
    Write-ColorOutput "✅ Docker: $dockerVersion" "Success"
  }
  catch {
    Write-ColorOutput "❌ Docker Desktop not found. Please install Docker Desktop." "Error"
    return $false
  }
    
  # Check Docker Compose
  try {
    $composeVersion = docker compose version
    Write-ColorOutput "✅ Docker Compose: $composeVersion" "Success"
  }
  catch {
    Write-ColorOutput "❌ Docker Compose not found. Please update Docker Desktop." "Error"
    return $false
  }
    
  # Check if Docker is running
  try {
    docker ps | Out-Null
    Write-ColorOutput "✅ Docker is running" "Success"
  }
  catch {
    Write-ColorOutput "❌ Docker is not running. Please start Docker Desktop." "Error"
    return $false
  }
    
  # Check PowerShell version
  $psVersion = $PSVersionTable.PSVersion.Major
  if ($psVersion -ge 7) {
    Write-ColorOutput "✅ PowerShell $psVersion" "Success"
  }
  else {
    Write-ColorOutput "⚠️  PowerShell $psVersion detected. PowerShell 7+ recommended." "Warning"
  }
    
  # Check available memory
  $memory = Get-WmiObject -Class Win32_ComputerSystem | Select-Object -ExpandProperty TotalPhysicalMemory
  $memoryGB = [math]::Round($memory / 1GB, 2)
  if ($memoryGB -ge 8) {
    Write-ColorOutput "✅ Available memory: ${memoryGB}GB" "Success"
  }
  else {
    Write-ColorOutput "⚠️  Low memory: ${memoryGB}GB. 8GB+ recommended." "Warning"
  }
    
  return $true
}

function Initialize-Environment {
  Write-ColorOutput "🔧 Initializing environment..." "Header"
    
  # Create .env file if it doesn't exist
  if (-not (Test-Path ".env")) {
    Write-ColorOutput "📝 Creating .env file from template..." "Info"
    Copy-Item "env.rag-system.example" ".env"
    Write-ColorOutput "⚠️  Please edit .env file with your configuration!" "Warning"
        
    if (-not $Force) {
      $response = Read-Host "Continue with default settings? (y/N)"
      if ($response -ne "y" -and $response -ne "Y") {
        Write-ColorOutput "❌ Setup cancelled. Please configure .env file and try again." "Error"
        exit 1
      }
    }
  }
    
  # Create necessary directories
  $directories = @(
    "logs",
    "data",
    "monitoring/grafana/provisioning",
    "monitoring/grafana/dashboards",
    "supabase",
    "lightrag",
    "rag-proxy"
  )
    
  foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
      New-Item -ItemType Directory -Path $dir -Force | Out-Null
      Write-ColorOutput "📁 Created directory: $dir" "Info"
    }
  }
}

function Start-Services {
  Write-ColorOutput "🚀 Starting RAG system services..." "Header"
    
  # Pull latest images
  Write-ColorOutput "📥 Pulling latest Docker images..." "Info"
  docker compose -f docker-compose-rag-system.yml pull
    
  # Start services
  Write-ColorOutput "🔄 Starting services..." "Info"
  docker compose -f docker-compose-rag-system.yml up -d
    
  # Wait for services to be ready
  Write-ColorOutput "⏳ Waiting for services to be ready..." "Info"
  Start-Sleep -Seconds 10
    
  # Check service health
  Test-ServiceHealth
}

function Test-ServiceHealth {
  Write-ColorOutput "🏥 Checking service health..." "Header"
    
  $services = @(
    @{ Name = "Supabase DB"; Url = "http://localhost:5432"; Port = 5432 },
    @{ Name = "Supabase Kong"; Url = "http://localhost:8000"; Port = 8000 },
    @{ Name = "Supabase Realtime"; Url = "http://localhost:4000"; Port = 4000 },
    @{ Name = "Ollama"; Url = "http://localhost:11434"; Port = 11434 },
    @{ Name = "LightRAG"; Url = "http://localhost:8001"; Port = 8001 },
    @{ Name = "n8n"; Url = "http://localhost:5678"; Port = 5678 },
    @{ Name = "Intelligent N8N API"; Url = "http://localhost:8002"; Port = 8002 },
    @{ Name = "RAG Proxy"; Url = "http://localhost:8080"; Port = 8080 },
    @{ Name = "Prometheus"; Url = "http://localhost:9090"; Port = 9090 },
    @{ Name = "Grafana"; Url = "http://localhost:3000"; Port = 3000 }
  )
    
  $healthyServices = 0
  $totalServices = $services.Count
    
  foreach ($service in $services) {
    try {
      $response = Invoke-WebRequest -Uri $service.Url -TimeoutSec 5 -UseBasicParsing
      if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 401) {
        Write-ColorOutput "✅ $($service.Name) is healthy" "Success"
        $healthyServices++
      }
      else {
        Write-ColorOutput "⚠️  $($service.Name) responded with status $($response.StatusCode)" "Warning"
      }
    }
    catch {
      Write-ColorOutput "❌ $($service.Name) is not responding" "Error"
    }
  }
    
  Write-ColorOutput "📊 Health check summary: $healthyServices/$totalServices services healthy" "Info"
    
  if ($healthyServices -eq $totalServices) {
    Write-ColorOutput "🎉 All services are running successfully!" "Success"
    Show-ServiceUrls
  }
  else {
    Write-ColorOutput "⚠️  Some services are not healthy. Check logs with: docker compose -f docker-compose-rag-system.yml logs" "Warning"
  }
}

function Show-ServiceUrls {
  Write-ColorOutput "🌐 Service URLs:" "Header"
  Write-ColorOutput "  📊 Grafana Dashboard: http://localhost:3000 (admin/admin)" "Info"
  Write-ColorOutput "  📈 Prometheus: http://localhost:9090" "Info"
  Write-ColorOutput "  🔄 n8n Workflows: http://localhost:5678 (admin/password)" "Info"
  Write-ColorOutput "  🤖 Ollama: http://localhost:11434" "Info"
  Write-ColorOutput "  🧠 LightRAG: http://localhost:8001" "Info"
  Write-ColorOutput "  🔗 Intelligent N8N API: http://localhost:8002" "Info"
  Write-ColorOutput "  ⚡ RAG Proxy: http://localhost:8080" "Info"
  Write-ColorOutput "  🗄️  Supabase: http://localhost:8000" "Info"
}

function Install-OllamaModels {
  Write-ColorOutput "🤖 Installing Ollama models..." "Header"
    
  $models = @(
    "qwen2.5-coder:1.5b",
    "qwen2.5-coder:7b",
    "nomic-embed-text"
  )
    
  foreach ($model in $models) {
    Write-ColorOutput "📥 Installing model: $model" "Info"
    docker exec rag-ollama ollama pull $model
  }
    
  Write-ColorOutput "✅ Ollama models installed successfully" "Success"
}

function Show-Logs {
  Write-ColorOutput "📋 Recent logs:" "Header"
  docker compose -f docker-compose-rag-system.yml logs --tail=10
}

function Show-Status {
  Write-ColorOutput "📊 Service status:" "Header"
  docker compose -f docker-compose-rag-system.yml ps
}

# Main execution
try {
  Write-ColorOutput "🚀 RAG System Startup Script" "Header"
  Write-ColorOutput "================================" "Header"
    
  if (-not $SkipPrerequisites) {
    if (-not (Test-Prerequisites)) {
      Write-ColorOutput "❌ Prerequisites check failed. Use -SkipPrerequisites to bypass." "Error"
      exit 1
    }
  }
    
  Initialize-Environment
  Start-Services
    
  # Ask if user wants to install Ollama models
  $installModels = Read-Host "Install Ollama models? (y/N)"
  if ($installModels -eq "y" -or $installModels -eq "Y") {
    Install-OllamaModels
  }
    
  Show-Status
  Show-ServiceUrls
    
  Write-ColorOutput "🎉 RAG system started successfully!" "Success"
  Write-ColorOutput "💡 Use 'docker compose -f docker-compose-rag-system.yml logs -f' to follow logs" "Info"
    
}
catch {
  Write-ColorOutput "❌ Error: $($_.Exception.Message)" "Error"
  Write-ColorOutput "📋 Check logs with: docker compose -f docker-compose-rag-system.yml logs" "Info"
  exit 1
}
