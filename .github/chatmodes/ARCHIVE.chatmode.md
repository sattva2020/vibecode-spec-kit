---
description: 'ARCHIVE Mode - Comprehensive documentation and project archival (Level 3-4 recommended)'
tools: [read_file, create_file, replace_string_in_file, list_dir, grep_search, semantic_search]
---

# 📚 ARCHIVE MODE - Final Documentation

> **Memory Bank System for VS Code** | Archival Phase

Создание comprehensive documentation и архивирование проекта (рекомендовано для Level 3-4).

## Когда пользователь пишет "ARCHIVE"

1. **Immediate Response**: Ответь `OK ARCHIVE`

2. **Memory Bank Check**:
   - Прочитай `.vscode/memory-bank/tasks.md`
   - Прочитай `.vscode/memory-bank/progress.md`
   - Прочитай все `.vscode/memory-bank/creative/*.md`
   - Прочитай `.vscode/memory-bank/reflection/reflect-[task_id].md`

3. **Rule Loading**:
   - Загрузи `.vscode/rules/isolation_rules/visual-maps/archive-mode-map.mdc`
   - Загрузи level-specific archive:
     - Level 2: `.vscode/rules/isolation_rules/Level2/archive-basic.mdc`
     - Level 3: `.vscode/rules/isolation_rules/Level3/archive-intermediate.mdc`
     - Level 4: `.vscode/rules/isolation_rules/Level4/archive-comprehensive.mdc`

4. **Archiving Process**:

   **Phase 1: Consolidate Documentation**
   - Соберите все документы feature/task:
     - Plan section from tasks.md
     - All creative-*.md files
     - reflect-*.md file
     - Relevant summaries from progress.md

   **Phase 2: Create Archive Summary**
   - Создай dedicated archive summary:
     ```
     .vscode/memory-bank/archive/feature-[feature_id]_YYYYMMDD.md
     ```

   **Phase 3: Link Documents**
   - Link to detailed docs within archive summary

   **Phase 4: Final Updates**
   - Update tasks.md (mark COMPLETED & ARCHIVED)
   - Clear activeContext.md (prepare for next task)

5. **Archive Summary Format**:
   ```markdown
   # Archive: [Feature/Task Title]
   **Task ID**: [TASK_ID]
   **Archive Date**: YYYY-MM-DD
   **Complexity**: Level X
   **Status**: COMPLETED & ARCHIVED

   ## Overview
   Brief description of the feature/task and its purpose.

   ## Key Documents

   ### Planning
   - [Plan Details](../tasks.md#task_id) - Original plan from tasks.md

   ### Design Decisions
   - [Architecture Design](../creative/creative-architecture.md)
   - [UI/UX Design](../creative/creative-uiux.md)
   - [Algorithm Selection](../creative/creative-algorithm.md)

   ### Implementation
   - [Implementation Progress](../progress.md#task_id)
   - Key files modified: [list]
   - Tests added: [list]

   ### Review
   - [Reflection Document](../reflection/reflect-task_id.md)

   ## Summary

   ### What Was Built
   - Feature X with capabilities Y and Z
   - Integration with subsystems A, B
   - 95% test coverage

   ### Key Decisions
   - **Architecture**: Chose microservices pattern for scalability
   - **UI/UX**: Implemented Material Design components
   - **Algorithm**: Selected binary search tree for O(log n) lookup

   ### Outcomes
   - Performance: 40% faster than previous implementation
   - User feedback: Positive (8.5/10 rating)
   - Technical debt: Minimal

   ### Lessons Learned
   - See [reflection document](../reflection/reflect-task_id.md) for details
   - Key insight: [brief summary]

   ## Related Tasks/Features
   - Depends on: [TASK_001], [TASK_002]
   - Enables: [TASK_005], [TASK_006]

   ## Future Considerations
   - Potential enhancements: [list]
   - Technical debt to address: [list]
   - Monitoring: [metrics to watch]

   ## Archive Checklist
   - [x] All documentation consolidated
   - [x] Archive summary created
   - [x] Links to detailed docs verified
   - [x] tasks.md marked COMPLETED & ARCHIVED
   - [x] activeContext.md cleared
   ```

6. **Update tasks.md**:
   ```markdown
   ## [TASK_ID] Task Title
   **Status**: COMPLETED & ARCHIVED
   **Archive**: [feature-id_YYYYMMDD.md](.vscode/memory-bank/archive/feature-id_YYYYMMDD.md)
   **Completion Date**: YYYY-MM-DD
   ```

7. **Clear activeContext.md**:
   ```markdown
   # Active Context
   **Status**: Ready for new task
   **Last Archived**: [TASK_ID] Task Title ([archive link])
   ```

8. **Mode Transition**:
   - Task fully completed → `Suggest VAN Mode for next task`
   - Project complete → Comprehensive documentation ready

## Archive Levels

**Level 2 (Basic Archive)**:
- Summary document
- Links to plan and implementation
- Brief outcomes

**Level 3 (Intermediate Archive)**:
- Summary with key decisions
- Links to all documents
- Outcomes and lessons

**Level 4 (Comprehensive Archive)**:
- Full documentation consolidation
- Architectural diagrams
- Performance metrics
- Related tasks mapping
- Future considerations

## Verification Checklist

```
✓ ARCHIVE CHECKPOINT
- Feature archive summary created? [YES/NO]
- Archive summary links to all relevant docs? [YES/NO]
- tasks.md shows COMPLETED and ARCHIVED with link? [YES/NO]
- activeContext.md cleared and ready for new task? [YES/NO]

→ If all YES: Task Fully Completed. Suggest VAN for next task
→ If any NO: Complete archiving steps
```

## Memory Bank Final State

После ARCHIVE mode:
- **tasks.md**: Task marked COMPLETED & ARCHIVED
- **archive/feature-[id].md**: Archive summary document
- **activeContext.md**: Cleared, ready for next task
- **All docs preserved**: plan, creative, progress, reflection

---

**Adapted from**: cursor-memory-bank v0.7-beta  
**VS Code**: Uses `.vscode/` instead of `.cursor/`  
**GitHub Copilot**: Activated via chat command "ARCHIVE"
