# Installation Guide

Полное руководство по установке VS Code Memory Bank System.

## 1. Требования

### Обязательные
- Visual Studio Code 1.85+
- GitHub Copilot с поддержкой Chat
- PowerShell 7+ (на Windows установите PowerShell Core)

### Рекомендуемые
- Git для контроля версий
- Python 3.9+ (для python-установщика)
- Node.js 18+ (если планируете использовать автоматизацию документации)

## 2. Быстрая автоматическая установка

### Вариант A — PowerShell
```powershell
pwsh scripts/install.ps1 -TargetPath C:\Projects\my-app
```
Опции:
- `-Force` — перезаписывать существующие файлы
- `-SkipInit` — пропустить инициализацию Memory Bank
- `-DryRun` — показать шаги без записи на диск

### Вариант B — Python
```bash
python scripts/install.py --target /path/to/project
```
Опции:
- `--force` — перезаписывать существующие файлы
- `--skip-init` — пропустить инициализацию Memory Bank
- `--dry-run` — показать шаги без записи на диск

Оба скрипта:
1. Копируют `.github/chatmodes`, `.vscode/rules`, `.vscode/templates`, `.vscode/memory-bank/scripts`
2. Создают директории Memory Bank (`creative`, `plan`, `reflection`, и т.д.)
3. Разворачивают шаблоны `activeContext.md`, `progress.md`, `projectbrief.md`, `tasks.md`

## 3. Ручная установка (если автоматизация недоступна)

### Шаг 1. Клонируйте репозиторий
```bash
git clone https://github.com/sattva2020/vscode-memory-bank.git
cd vscode-memory-bank
```

### Шаг 2. Скопируйте компоненты в ваш проект
```bash
# Chat modes
cp -r .github/chatmodes /path/to/project/.github/

# Isolation rules и шаблоны
cp -r .vscode/rules /path/to/project/.vscode/
cp -r .vscode/templates /path/to/project/.vscode/

# Скрипты автоматизации
mkdir -p /path/to/project/.vscode/memory-bank
cp -r .vscode/memory-bank/scripts /path/to/project/.vscode/memory-bank/
```

### Шаг 3. Инициализируйте Memory Bank
```powershell
cd /path/to/project
pwsh .vscode/memory-bank/scripts/memory-bank.ps1 init
```

### Шаг 4. Перезапустите VS Code
`Ctrl+Shift+P → Developer: Reload Window`

## 4. Проверка установки

### Chat Modes
1. Откройте GitHub Copilot Chat
2. Введите `VAN`
3. Убедитесь, что отображается приветствие режима и оценка сложности

### Isolation Rules
```bash
ls .vscode/rules/isolation_rules | wc -l
# Ожидается: 114
```

### PowerShell-скрипты
```powershell
pwsh .vscode/memory-bank/scripts/memory-bank.ps1 status
```
Вы должны увидеть сводку по файлам и директориям Memory Bank.

## 5. Обновление до новой версии
```bash
cd /path/to/vscode-memory-bank
git pull origin main

# При необходимости повторите установку
pwsh scripts/install.ps1 -TargetPath /path/to/project -Force
```
Перед обновлением сделайте резервную копию пользовательских данных:
```bash
cp -r /path/to/project/.vscode/memory-bank /path/to/project/.vscode/memory-bank.backup
```
После обновления восстановите файлы `*.md` и каталоги `creative/`, `reflection/`, `archive/` из резервной копии.

## 6. Устранение неполадок

| Проблема | Решение |
|----------|---------|
| Chat modes не отображаются | Проверьте расположение файлов `.chatmode.md`, перезапустите VS Code |
| `pwsh` не найден | Установите PowerShell 7+ и добавьте в PATH |
| Скрипт не перезаписывает файлы | Используйте `-Force` / `--force` |
| Ошибка доступа при копировании | Запустите терминал от имени администратора или убедитесь в правах на запись |
| Документация не обновляется после SYNC | Убедитесь, что `progress.md` и `creative/` содержат актуальные данные |

## 7. Следующие шаги
- Заполните `.vscode/memory-bank/projectbrief.md`
- Создайте первую задачу в `.vscode/memory-bank/tasks.md`
- Запустите режим `VAN` и следуйте рекомендованному потоку
- Изучите [Quick Start Guide](QUICK_START.md) и [Chat Modes Reference](CHATMODES.md)

## 8. Поддержка
- Issues: <https://github.com/sattva2020/vscode-memory-bank/issues>
- Discussions: <https://github.com/sattva2020/vscode-memory-bank/discussions>
- Документация: директория `docs/`
