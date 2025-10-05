@echo off
echo ?? Настройка Cursor IDE для автоматического одобрения MCP инструментов...
echo.

REM Проверяем наличие Cursor IDE
if not exist "%APPDATA%\Cursor" (
    echo ? Cursor IDE не найден в %APPDATA%\Cursor
    echo    Убедитесь, что Cursor IDE установлен
    pause
    exit /b 1
)

REM Создаем папку настроек если не существует
if not exist "%APPDATA%\Cursor\User" (
    mkdir "%APPDATA%\Cursor\User"
    echo ? Создана папка настроек Cursor IDE
)

REM Копируем настройки workspace в глобальные настройки
if exist ".vscode\settings.json" (
    copy ".vscode\settings.json" "%APPDATA%\Cursor\User\settings.json" /Y
    echo ? Workspace настройки скопированы в глобальные настройки
) else (
    echo ? Файл .vscode\settings.json не найден
    echo    Убедитесь, что вы находитесь в корне проекта
    pause
    exit /b 1
)

REM Копируем MCP конфигурацию
if exist ".cursor\mcp-allowlist.json" (
    if not exist "%APPDATA%\Cursor\User\.cursor" (
        mkdir "%APPDATA%\Cursor\User\.cursor"
    )
    copy ".cursor\mcp-allowlist.json" "%APPDATA%\Cursor\User\.cursor\mcp-allowlist.json" /Y
    echo ? MCP конфигурация скопирована
)

echo.
echo ?? Перезапуск Cursor IDE для применения настроек...

REM Закрываем Cursor IDE если запущен
taskkill /f /im "Cursor.exe" 2>nul
timeout /t 2 /nobreak >nul

REM Запускаем Cursor IDE
echo ? Запуск Cursor IDE...
start "" "C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe" "%CD%"

echo.
echo ?? Настройка завершена!
echo.
echo ?? Что было настроено:
echo    ? Автоматическое одобрение sequential-thinking:sequentialthinking
echo    ? Автоматическое одобрение memory:* инструментов
echo    ? Автоматическое одобрение github:* инструментов
echo    ? Автоматическое одобрение filesystem:* инструментов
echo    ? Автоматическое одобрение supabase:* инструментов
echo    ? Автоматическое одобрение playwright:* инструментов
echo    ? Автоматическое одобрение context7:* инструментов
echo.
echo ?? Теперь MCP инструменты будут выполняться автоматически без подтверждения!
echo.
pause
