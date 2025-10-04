# ===========================================
# KNOWLEDGE BASE INITIALIZATION SCRIPT
# ===========================================

Write-Host "🧠 Initializing Knowledge Base for n8n System" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Функция для вывода цветного текста
function Write-ColorOutput {
  param (
    [string]$Message,
    [string]$Type = "Info" # Can be "Info", "Success", "Warning", "Error", "Header"
  )
  switch ($Type) {
    "Info" { Write-Host -ForegroundColor Cyan $Message }
    "Success" { Write-Host -ForegroundColor Green $Message }
    "Warning" { Write-Host -ForegroundColor Yellow $Message }
    "Error" { Write-Host -ForegroundColor Red $Message }
    "Header" { Write-Host -ForegroundColor Magenta "`n--- $Message ---`n" }
    default { Write-Host $Message }
  }
}

Write-ColorOutput "Step 1: Checking Python Environment" "Info"
try {
  $pythonVersion = python --version 2>&1
  Write-ColorOutput "✅ Python found: $pythonVersion" "Success"
}
catch {
  Write-ColorOutput "❌ Python not found. Please install Python 3.8+" "Error"
  exit 1
}

Write-ColorOutput "Step 2: Installing Dependencies" "Info"
try {
  Set-Location "intelligent-n8n-system"
  pip install -r requirements.txt
  Write-ColorOutput "✅ Dependencies installed successfully" "Success"
}
catch {
  Write-ColorOutput "❌ Failed to install dependencies" "Error"
  exit 1
}

Write-ColorOutput "Step 3: Initializing Knowledge Base" "Info"
try {
  python scripts/manage_knowledge.py init
  Write-ColorOutput "✅ Knowledge base initialized successfully" "Success"
}
catch {
  Write-ColorOutput "❌ Failed to initialize knowledge base" "Error"
  exit 1
}

Write-ColorOutput "Step 4: Testing Knowledge Base" "Info"
try {
  # Тест поиска
  Write-ColorOutput "Testing technology search..." "Info"
  python scripts/manage_knowledge.py search "Python FastAPI" --limit 5
    
  # Тест рекомендаций
  Write-ColorOutput "Testing technology recommendations..." "Info"
  python scripts/manage_knowledge.py recommend --technologies "Python" "PostgreSQL" --architecture "microservices"
    
  # Тест workflow предложений
  Write-ColorOutput "Testing workflow suggestions..." "Info"
  python scripts/manage_knowledge.py workflows "Python" "FastAPI" "PostgreSQL"
    
  Write-ColorOutput "✅ Knowledge base tests completed successfully" "Success"
}
catch {
  Write-ColorOutput "❌ Knowledge base tests failed" "Error"
  exit 1
}

Write-ColorOutput "Step 5: Syncing with Context7" "Info"
try {
  Write-ColorOutput "Syncing with Context7 for latest technology data..." "Info"
  python scripts/manage_knowledge.py sync-context7
  
  Write-ColorOutput "✅ Context7 sync completed successfully" "Success"
}
catch {
  Write-ColorOutput "❌ Context7 sync failed" "Error"
  # Не прерываем выполнение, так как это дополнительная функция
}

Write-ColorOutput "Step 6: Exporting Knowledge Base" "Info"
try {
  python scripts/manage_knowledge.py export "knowledge_base_export.json"
  Write-ColorOutput "✅ Knowledge base exported to knowledge_base_export.json" "Success"
}
catch {
  Write-ColorOutput "❌ Failed to export knowledge base" "Error"
  exit 1
}

Write-ColorOutput "Step 7: Showing Statistics" "Info"
try {
  python scripts/manage_knowledge.py stats
  Write-ColorOutput "✅ Knowledge base statistics displayed" "Success"
}
catch {
  Write-ColorOutput "❌ Failed to show statistics" "Error"
  exit 1
}

Set-Location ".."

Write-ColorOutput "🎉 Knowledge Base Initialization Complete!" "Success"
Write-ColorOutput "=============================================" "Success"
Write-Host ""
Write-ColorOutput "📊 What was created:" "Info"
Write-ColorOutput "   ✅ Technology entities (languages, frameworks, tools)" "Success"
Write-ColorOutput "   ✅ Technology relationships and connections" "Success"
Write-ColorOutput "   ✅ N8N integration mappings" "Success"
Write-ColorOutput "   ✅ Use case categorizations" "Success"
Write-ColorOutput "   ✅ Complexity assessments" "Success"
Write-Host ""
Write-ColorOutput "🚀 How to use:" "Info"
Write-ColorOutput "   • Search technologies: python scripts/manage_knowledge.py search 'query'" "Success"
Write-ColorOutput "   • Get recommendations: python scripts/manage_knowledge.py recommend --technologies 'Python'" "Success"
Write-ColorOutput "   • Get workflows: python scripts/manage_knowledge.py workflows 'Python' 'FastAPI'" "Success"
Write-ColorOutput "   • Update popularity: python scripts/manage_knowledge.py update" "Success"
Write-ColorOutput "   • Show stats: python scripts/manage_knowledge.py stats" "Success"
Write-Host ""
Write-ColorOutput "🎯 Integration with AI Router:" "Info"
Write-ColorOutput "   The knowledge base is now integrated with AI Router for intelligent" "Success"
Write-ColorOutput "   technology recommendations and n8n workflow suggestions!" "Success"
