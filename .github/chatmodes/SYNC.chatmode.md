---
description: 'SYNC Mode - Automated documentation synchronization after ARCHIVE phase completion'
tools: [read_file, create_file, replace_string_in_file, list_dir, run_in_terminal]
---

# 🔄 SYNC MODE - Documentation Synchronization

> **Memory Bank System for VS Code** | Synchronization Phase

Автоматическая синхронизация документации после завершения ARCHIVE фазы: обновление README.md, CHANGELOG.md, генерация ADR документов.

## Когда пользователь пишет "SYNC"

1. **Immediate Response**: Ответь `OK SYNC`

2. **Memory Bank Check**:
   - Проверь наличие `.vscode/memory-bank/archive/` с документами
   - Найди последний `archive-[task_id].md`
   - Прочитай `README.md` и `CHANGELOG.md` в корне проекта
   - Проверь `.vscode/memory-bank/creative/*.md` на наличие ADR маркеров

3. **Verification**:
   ```
   ЕСЛИ нет архивных документов:
     ОШИБКА: "SYNC требует завершенного ARCHIVE документа. Запусти 'ARCHIVE' сначала."
     СТОП
   ```

## 📋 SYNC Process (7 фаз)

### Phase 1: Find Latest Archive 🔍
```
1. Список всех архивов: list_dir .vscode/memory-bank/archive/
2. Сортировка по дате создания (последний = актуальный)
3. Прочитать выбранный archive-[task_id].md
```

### Phase 2: Extract Metadata 📊
```
Извлечь из архива:
- Task ID (например: TASK_002)
- Task Name (например: "SYNC Mode Implementation")
- Complexity Level (1-4)
- Implementation Summary (краткое описание)
- Key Achievements (список достижений)
- Creative Decisions (если Level 3-4)
- Date Completed
```

### Phase 3: Update README.md 📝
```
Стратегия: Smart Positioning (Creative Decision 2)

1. Проверить наличие "## Recent Updates" секции
2. ЕСЛИ отсутствует - создать ПОСЛЕ основного описания
3. Добавить запись В НАЧАЛО списка:
   
   ### [YYYY-MM-DD] [Task Name]
   - **Task**: [TASK_XXX] - [Brief description]
   - **Level**: [1-4]
   - **Highlights**: 
     - Achievement 1
     - Achievement 2
   
4. Сохранить изменения с пустой строкой после записи
```

### Phase 4: Update CHANGELOG.md 📚
```
Стратегия: Hybrid Version Bump (Creative Decision 1)

1. Определить текущую версию (из заголовка последнего релиза)
2. Проанализировать тип изменений:
   - Level 1-2: PATCH bump (0.0.1 → 0.0.2)
   - Level 3: MINOR bump (0.1.0 → 0.2.0)
   - Level 4 + breaking keywords: MAJOR/MINOR bump (1.0.0 → 2.0.0)
     Breaking keywords: "breaking change", "removed", "incompatible"

3. Создать новую секцию:
   
   ## [NEW_VERSION] - YYYY-MM-DD
   ### Added (для Level 2-4)
   - [TASK_XXX] Task Name - brief description
   
   ### Changed (для Level 3-4)
   - Design Decision 1
   - Design Decision 2
   
   ### Fixed (для Level 1-2)
   - Bug fix / minor improvement

4. Добавить в "Unreleased" если не готов релиз
```

### Phase 5: Generate ADR Documents 📄
```
Стратегия: Template-based with Markers (Creative Decision 3)

1. Сканировать все .vscode/memory-bank/creative/*.md
2. Искать маркеры:
   <!-- ADR_CANDIDATE: architectural -->
   <!-- ADR_CANDIDATE: algorithm -->
   <!-- ADR_CANDIDATE: integration -->

3. Для каждого найденного маркера:
   a) Извлечь контекст (3-5 параграфов вокруг маркера)
   b) Определить тип ADR по маркеру
   c) Сгенерировать файл docs/adr/NNNN-title.md по MADR шаблону:
   
   # NNNN. [Title from Creative Doc]
   
   Date: YYYY-MM-DD
   
   ## Status
   Accepted
   
   ## Context
   [Extracted context from creative doc]
   
   ## Decision
   [Decision description]
   
   ## Consequences
   [Positive and negative outcomes]

4. Обновить docs/adr/README.md с индексом новых ADR
```

### Phase 6: Git Operations ⚙️
```
ЕСЛИ пользователь НЕ указал -DryRun:
  1. Создать feature branch: git checkout -b sync/[task_id]-update
  2. Stage changes: git add README.md CHANGELOG.md docs/adr/
  3. Commit: git commit -m "docs: sync [TASK_XXX] documentation"
  4. ЕСЛИ НЕ -SkipPR:
     - Вывести PR description шаблон:
       
       ## Documentation Sync: [TASK_XXX]
       
       Automated documentation synchronization after ARCHIVE phase.
       
       **Changes**:
       - Updated README.md with recent achievements
       - Bumped CHANGELOG.md to v[NEW_VERSION]
       - Generated [N] ADR documents from creative decisions
       
       **Related Archive**: `.vscode/memory-bank/archive/archive-[task_id].md`
```

### Phase 7: Summary Report 📊
```
Вывести итоговый отчет:

=== SYNC COMPLETE ===

📦 Task: [TASK_XXX] - [Name]
📅 Date: [YYYY-MM-DD]
🎯 Level: [1-4]

📝 Updates:
  ✅ README.md - Added recent update entry
  ✅ CHANGELOG.md - Bumped to v[NEW_VERSION] ([TYPE] bump)
  ✅ Generated [N] ADR documents in docs/adr/
  
⚙️  Git:
  ✅ Branch: sync/[task_id]-update
  ✅ Commit: [commit_hash]
  
🚀 Next Steps:
  1. Review changes: git diff main
  2. Push branch: git push origin sync/[task_id]-update
  3. Create Pull Request with provided description
  4. После merge: удалить архив (опционально)

===========================
```

## 🔧 PowerShell Integration

SYNC режим может использовать PowerShell скрипт `.vscode/memory-bank/scripts/sync.ps1`:

```powershell
# Запуск SYNC с PowerShell
.vscode/memory-bank/scripts/sync.ps1

# Dry run (без git operations)
.vscode/memory-bank/scripts/sync.ps1 -DryRun

# Без создания PR description
.vscode/memory-bank/scripts/sync.ps1 -SkipPR

# Verbose режим
.vscode/memory-bank/scripts/sync.ps1 -Verbose
```

**Когда использовать PowerShell скрипт**:
- Пользователь явно просит "запусти sync.ps1"
- Нужна автоматизация без ручного контроля
- Batch обработка нескольких архивов

**Когда использовать SYNC chatmode**:
- Пользователь пишет "SYNC" в чате
- Нужен интерактивный режим с обратной связью
- Требуется кастомизация процесса

## 🎨 Creative Decisions Reference

Этот режим реализует 3 creative решения из TASK_002:

### Decision 1: Hybrid Version Bump
- **Problem**: Как определить MAJOR vs MINOR для Level 4?
- **Solution**: Level 4 + breaking keywords → MAJOR, иначе MINOR
- **Implementation**: String scan для "breaking", "removed", "incompatible"

### Decision 2: Smart README Positioning
- **Problem**: Где добавлять новые записи в README?
- **Solution**: Секция "Recent Updates" в начале + пустая строка separator
- **Implementation**: Regex поиск секции, создание если отсутствует

### Decision 3: Template-based ADR
- **Problem**: Как автоматизировать ADR из творческих документов?
- **Solution**: Маркеры `<!-- ADR_CANDIDATE: type -->` + MADR шаблон
- **Implementation**: Grep search → extract context → generate MADR

## 📊 Example Usage

```
User: SYNC