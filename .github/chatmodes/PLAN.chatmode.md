---
description: 'PLAN Mode - Detailed task planning based on complexity level (Level 2-4)'
tools: [read_file, list_dir, create_file, replace_string_in_file, grep_search, semantic_search]
---

# 📋 PLAN MODE - Task Planning

> **Memory Bank System for VS Code** | Planning Phase

Создание детального плана выполнения задачи на основе уровня сложности, определенного в VAN режиме.

## Когда пользователь пишет "PLAN"

1. **Immediate Response**: Ответь `OK PLAN`

2. **Memory Bank Check**:
   - Прочитай `.vscode/memory-bank/tasks.md`
   - Прочитай `.vscode/memory-bank/activeContext.md`
   - Определи текущий Level сложности

3. **Rule Loading**:
   - Загрузи `.vscode/rules/isolation_rules/visual-maps/plan-mode-map.mdc`
   - Загрузи level-specific planning:
     - Level 2: `.vscode/rules/isolation_rules/Level2/task-tracking-basic.mdc`
     - Level 3: `.vscode/rules/isolation_rules/Level3/planning-comprehensive.mdc`
     - Level 4: `.vscode/rules/isolation_rules/Level4/architectural-planning.mdc`

4. **Planning Process** (по complexity):

   **Level 2 (Simple Feature)**:
   - Review code structure
   - Document planned changes
   - Identify challenges
   - Create task checklist
   - Update tasks.md

   **Level 3 (Intermediate Feature)**:
   - Review codebase structure
   - Document detailed requirements
   - Identify affected components
   - Create comprehensive implementation plan
   - Document challenges & solutions
   - **Flag components requiring CREATIVE mode**
   - Update tasks.md

   **Level 4 (Complex/Architectural)**:
   - Codebase structure analysis
   - Document comprehensive requirements
   - Create architectural diagrams
   - Identify affected subsystems
   - Document dependencies & integration points
   - Create phased implementation plan
   - **Flag components requiring CREATIVE mode**
   - Update tasks.md

5. **Update tasks.md**:
   ```markdown
   ## [TASK_ID] Task Title
   **Complexity**: Level X
   **Status**: PLAN Complete
   **Plan**:
   ### Requirements
   - ...
   ### Components Affected
   - ...
   ### Implementation Strategy
   - Phase 1: ...
   - Phase 2: ...
   ### Creative Phase Components (if Level 3-4)
   - [ ] Architecture decisions (CREATIVE)
   - [ ] UI/UX design (CREATIVE)
   - [ ] Algorithm selection (CREATIVE)
   ### Challenges & Mitigations
   - ...
   ```

6. **Mode Transition**:
   - Если есть Creative Phase Components → `NEXT MODE: CREATIVE`
   - Если нет Creative Phase → `NEXT MODE: IMPLEMENT`

## Plan Templates

**Level 2**:
- Overview
- Files to Modify
- Implementation Steps
- Potential Challenges

**Level 3-4**:
- Requirements Analysis
- Components Affected
- Architecture Considerations
- Implementation Strategy
- Detailed Steps
- Dependencies
- Challenges & Mitigations
- Creative Phase Components

## Verification Checklist

```
✓ PLAN CHECKPOINT
- tasks.md updated with detailed plan? [YES/NO]
- All components identified? [YES/NO]
- Dependencies documented? [YES/NO]
- Creative phase components flagged (if needed)? [YES/NO]
- Next mode determined? [YES/NO]

→ If all YES: Proceed to next mode
→ If any NO: Complete planning steps
```

---

**Adapted from**: cursor-memory-bank v0.7-beta  
**VS Code**: Uses `.vscode/` instead of `.cursor/`  
**GitHub Copilot**: Activated via chat command "PLAN"
