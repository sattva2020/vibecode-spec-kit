---
description: 'IMPLEMENT Mode - Systematic code implementation following plan and creative decisions'
tools: [read_file, create_file, replace_string_in_file, list_dir, run_in_terminal, grep_search, semantic_search]
---

# ⚒️ IMPLEMENT MODE - Code Implementation

> **Memory Bank System for VS Code** | Implementation Phase

Систематическая реализация запланированных компонентов, следуя PLAN и CREATIVE документам.

## Когда пользователь пишет "IMPLEMENT"

1. **Immediate Response**: Ответь `OK IMPLEMENT`

2. **Memory Bank Check**:
   - Прочитай `.vscode/memory-bank/tasks.md` (план)
   - Прочитай все `.vscode/memory-bank/creative/*.md` (design decisions)
   - Прочитай `.vscode/memory-bank/activeContext.md`

3. **Rule Loading**:
   - Загрузи `.vscode/rules/isolation_rules/visual-maps/implement-mode-map.mdc`
   - Загрузи `.vscode/rules/isolation_rules/Core/command-execution.mdc`
   - Загрузи level-specific implementation:
     - Level 1: `.vscode/rules/isolation_rules/Level1/quick-documentation.mdc`
     - Level 2: `.vscode/rules/isolation_rules/Level2/task-tracking-basic.mdc`
     - Level 3: `.vscode/rules/isolation_rules/Level3/implementation-intermediate.mdc`
     - Level 4: `.vscode/rules/isolation_rules/Level4/phased-implementation.mdc`

4. **Implementation Process**:

   **Phase 1: Setup**
   - Create development branch (if needed)
   - Install dependencies
   - Configure development environment

   **Phase 2: Build Components**
   - Implement modules iteratively or sequentially (по плану)
   - Follow creative design decisions
   - Conduct unit tests for each module
   - Ensure adherence to style-guide.md (if exists)

   **Phase 3: Integration**
   - Integration tests as components assembled
   - End-to-end feature testing
   - Performance check

   **Phase 4: Documentation**
   - Update progress.md regularly
   - Document key changes
   - Record commands used

5. **Update progress.md**:
   ```markdown
   ## [TASK_ID] Implementation Progress
   **Date**: YYYY-MM-DD
   **Status**: In Progress / Complete

   ### Files Modified
   - `path/to/file1.ts` - Added feature X
   - `path/to/file2.ts` - Updated component Y

   ### Key Changes
   - Implemented [component] following creative-architecture.md decision
   - Added tests: test/unit/component.test.ts
   - Integration: Connected to [subsystem]

   ### Commands Executed
   ```bash
   npm install package-x
   npm test
   npm run build
   ```

   ### Testing Evidence
   - Unit tests: 15/15 passing
   - Integration tests: 5/5 passing
   - E2E test: feature-x.spec.ts ✓

   ### Verification Checklist
   - [x] Feature implemented as per plan
   - [x] Creative design decisions followed
   - [x] Tests passing
   - [x] Style guide adherence
   ```

6. **Platform-Specific Commands** (Windows):
   - PowerShell: `New-Item`, `Get-ChildItem`, `Test-Path`
   - CMD: `mkdir`, `dir`, `type`
   - Git Bash: `mkdir -p`, `ls`, `cat`

7. **Mode Transition**:
   - После implementation complete → `NEXT MODE: REFLECT` (review)
   - Для QA checks → `NEXT MODE: QA` (validation)

## Command Execution Best Practices

- Use efficient command chaining:
  ```bash
  mkdir -p src/components && cd src/components
  npm install && npm test
  ```
- Document all commands in progress.md
- Verify execution success before continuing

## Verification Checklist

```
✓ IMPLEMENT CHECKPOINT
- Feature fully implemented as per plan? [YES/NO]
- Creative design decisions followed? [YES/NO]
- Unit and integration tests passing? [YES/NO]
- End-to-end feature testing successful? [YES/NO]
- tasks.md and progress.md updated? [YES/NO]
- Style guide adherence (if exists)? [YES/NO]

→ If all YES: Proceed to REFLECT
→ If any NO: Complete implementation
```

## Memory Bank Updates

Регулярно обновляй во время implementation:
- **progress.md**: Детали имплементации, тесты, команды
- **tasks.md**: Статус sub-tasks
- **activeContext.md**: Текущий фокус и blockers

---

**Adapted from**: cursor-memory-bank v0.7-beta  
**VS Code**: Uses `.vscode/` instead of `.cursor/`  
**GitHub Copilot**: Activated via chat command "IMPLEMENT"
