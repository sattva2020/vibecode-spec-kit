# 🔧 Configure Cursor IDE MCP Auto-Approval
# 
# Этот скрипт настраивает Cursor IDE для автоматического 
# одобрения MCP инструментов без подтверждения пользователя

param(
  [switch]$Force = $false
)

Write-Host "🔧 Настройка Cursor IDE для автоматического одобрения MCP инструментов..." -ForegroundColor Blue

# Пути к конфигурационным файлам Cursor
$cursorConfigDir = "$env:APPDATA\Cursor\User"
$workspaceConfigDir = ".vscode"
$cursorMCPConfigDir = ".cursor"

# Создаем директории если не существуют
if (!(Test-Path $cursorConfigDir)) {
  New-Item -ItemType Directory -Path $cursorConfigDir -Force | Out-Null
}

if (!(Test-Path $workspaceConfigDir)) {
  New-Item -ItemType Directory -Path $workspaceConfigDir -Force | Out-Null
}

if (!(Test-Path $cursorMCPConfigDir)) {
  New-Item -ItemType Directory -Path $cursorMCPConfigDir -Force | Out-Null
}

# 1. Настройка глобальных настроек Cursor
Write-Host "📝 Создание глобальных настроек Cursor..." -ForegroundColor Yellow

$globalSettings = @{
  "cursor.mcp.autoApprove"        = $true
  "cursor.mcp.allowlist"          = @(
    "sequential-thinking:sequentialthinking",
    "memory:*",
    "github:*",
    "filesystem:*",
    "supabase:*",
    "playwright:*"
  )
  "cursor.mcp.trustedTools"       = @(
    "sequential-thinking",
    "memory", 
    "github",
    "filesystem",
    "supabase",
    "playwright"
  )
  "cursor.general.enableMCP"      = $true
  "cursor.general.autoApproveMCP" = $true
  "cursor.mcp.autoApproveReason"  = "Trusted development tools for RAG-Powered Code Assistant project"
} | ConvertTo-Json -Depth 3

$globalSettingsPath = Join-Path $cursorConfigDir "settings.json"

# Объединяем с существующими настройками
if (Test-Path $globalSettingsPath) {
  $existingSettings = Get-Content $globalSettingsPath -Raw | ConvertFrom-Json
  $existingSettings | Add-Member -NotePropertyName "cursor.mcp.autoApprove" -NotePropertyValue $true -Force
  $existingSettings | Add-Member -NotePropertyName "cursor.mcp.allowlist" -NotePropertyValue $globalSettings.allowlist -Force
  $globalSettings = $existingSettings | ConvertTo-Json -Depth 3
}

$globalSettings | Out-File -FilePath $globalSettingsPath -Encoding UTF8
Write-Host "✅ Глобальные настройки Cursor обновлены" -ForegroundColor Green

# 2. Настройка workspace настроек
Write-Host "📝 Обновление workspace настроек..." -ForegroundColor Yellow

$workspaceSettings = @{
  "cursor.mcp.autoApprove"        = $true
  "cursor.mcp.allowlist"          = @(
    "sequential-thinking:sequentialthinking",
    "memory:*",
    "github:*",
    "filesystem:*",
    "supabase:*",
    "playwright:*"
  )
  "cursor.mcp.trustedTools"       = @(
    "sequential-thinking",
    "memory",
    "github", 
    "filesystem",
    "supabase",
    "playwright",
    "context7"
  )
  "cursor.general.enableMCP"      = $true
  "cursor.general.autoApproveMCP" = $true
  "cursor.mcp.autoApproveReason"  = "Trusted development tools for RAG-Powered Code Assistant project"
} | ConvertTo-Json -Depth 3

$workspaceSettingsPath = Join-Path $workspaceConfigDir "settings.json"
$workspaceSettings | Out-File -FilePath $workspaceSettingsPath -Encoding UTF8
Write-Host "✅ Workspace настройки обновлены" -ForegroundColor Green

# 3. Создание MCP конфигурации
Write-Host "📝 Создание MCP конфигурации..." -ForegroundColor Yellow

$mcpConfig = @{
  "mcpTools"        = @{
    "allowlist"      = @(
      "sequential-thinking:sequentialthinking",
      "memory:*",
      "github:*",
      "filesystem:*",
      "supabase:*",
      "playwright:*",
      "context7:*"
    )
    "autoApprove"    = $true
    "trustedDomains" = @(
      "localhost",
      "127.0.0.1"
    )
  }
  "toolPermissions" = @{
    "sequential-thinking" = @{
      "sequentialthinking" = @{
        "autoApprove" = $true
        "reason"      = "Required for VAN mode analysis and complex problem solving"
      }
    }
    "memory"              = @{
      "*" = @{
        "autoApprove" = $true
        "reason"      = "Memory bank operations for project context"
      }
    }
    "github"              = @{
      "*" = @{
        "autoApprove" = $true
        "reason"      = "GitHub integration for repository management"
      }
    }
    "context7"            = @{
      "*" = @{
        "autoApprove" = $true
        "reason"      = "Context7 for modern technology documentation and API context"
      }
    }
  }
} | ConvertTo-Json -Depth 4

$mcpConfigPath = Join-Path $cursorMCPConfigDir "mcp-allowlist.json"
$mcpConfig | Out-File -FilePath $mcpConfigPath -Encoding UTF8
Write-Host "✅ MCP конфигурация создана" -ForegroundColor Green

# 4. Создание batch файла для быстрой настройки
Write-Host "📝 Создание batch файла для быстрой настройки..." -ForegroundColor Yellow

$batchContent = @"
@echo off
echo 🔧 Настройка Cursor IDE для автоматического одобрения MCP инструментов...
echo.

REM Копируем настройки в папку Cursor
copy ".vscode\settings.json" "%APPDATA%\Cursor\User\settings.json" /Y
echo ✅ Настройки скопированы

REM Перезапускаем Cursor IDE
taskkill /f /im "Cursor.exe" 2>nul
echo ⏳ Перезапуск Cursor IDE...
start "" "C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe"

echo.
echo 🎉 Настройка завершена! MCP инструменты теперь будут одобряться автоматически.
pause
"@

$batchContent | Out-File -FilePath "scripts\setup-cursor-auto-approval.bat" -Encoding ASCII
Write-Host "✅ Batch файл создан: scripts\setup-cursor-auto-approval.bat" -ForegroundColor Green

# 5. Инструкции по применению
Write-Host "`n📋 Инструкции по применению настроек:" -ForegroundColor Cyan
Write-Host "1. Закройте Cursor IDE" -ForegroundColor White
Write-Host "2. Запустите: scripts\setup-cursor-auto-approval.bat" -ForegroundColor White
Write-Host "3. Или вручную скопируйте .vscode\settings.json в %APPDATA%\Cursor\User\" -ForegroundColor White
Write-Host "4. Перезапустите Cursor IDE" -ForegroundColor White
Write-Host "`n🎯 Альтернативно:" -ForegroundColor Cyan
Write-Host "- Откройте Cursor IDE" -ForegroundColor White
Write-Host "- Нажмите Ctrl+Shift+P" -ForegroundColor White
Write-Host "- Найдите 'Preferences: Open Settings (JSON)'" -ForegroundColor White
Write-Host "- Добавьте настройки из .vscode\settings.json" -ForegroundColor White

Write-Host "`n✅ Настройка MCP автоодобрения завершена!" -ForegroundColor Green
