---
description: 'REFLECT Mode - Review implementation, document lessons learned, assess design decisions'
tools: [read_file, create_file, replace_string_in_file, list_dir, grep_search, semantic_search]
---

# 🔍 REFLECT MODE - Review & Document

> **Memory Bank System for VS Code** | Reflection Phase

Ревью завершенной имплементации и документирование уроков для будущих задач.

## Когда пользователь пишет "REFLECT"

1. **Immediate Response**: Ответь `OK REFLECT`

2. **Memory Bank Check**:
   - Прочитай `.vscode/memory-bank/tasks.md` (план)
   - Прочитай `.vscode/memory-bank/progress.md` (implementation status)
   - Прочитай все `.vscode/memory-bank/creative/*.md` (design decisions)

3. **Rule Loading**:
   - Загрузи `.vscode/rules/isolation_rules/visual-maps/reflect-mode-map.mdc`
   - Загрузи level-specific reflection:
     - Level 2: `.vscode/rules/isolation_rules/Level2/reflection-basic.mdc`
     - Level 3: `.vscode/rules/isolation_rules/Level3/reflection-intermediate.mdc`
     - Level 4: `.vscode/rules/isolation_rules/Level4/reflection-comprehensive.mdc`

4. **Reflection Process**:

   **Step 1: Review Completed Work**
   - Review code, plan, design docs, test results
   - Analyze initial requirements vs delivered functionality

   **Step 2: Analyze Process**
   - What went well?
   - What was challenging?
   - Deviations from plan (and why)

   **Step 3: Document Lessons**
   - Technical lessons (architecture, patterns, libraries)
   - Process lessons (workflow, collaboration, tools)

   **Step 4: Assess Design Decisions**
   - Were creative phase decisions effective?
   - Would you choose differently now?

5. **Create Reflection Document**:
   ```
   .vscode/memory-bank/reflection/reflect-[task_id].md
   ```

   Формат:
   ```markdown
   # Reflection: [Task Title]
   **Task ID**: [TASK_ID]
   **Date**: YYYY-MM-DD
   **Complexity**: Level X

   ## Summary
   Brief overview of what was accomplished.

   ## What Went Well
   - Successfully implemented [feature] with [technology]
   - Creative phase architecture decision proved effective
   - Testing coverage reached 95%
   - ...

   ## Challenges Encountered
   - Challenge 1: [description]
     - Solution: [how resolved]
   - Challenge 2: [description]
     - Solution: [how resolved]
   - ...

   ## Lessons Learned

   ### Technical Lessons
   - Learned: [pattern/library/approach]
   - Insight: [technical insight]
   - ...

   ### Process Lessons
   - Workflow: [what worked/didn't work]
   - Collaboration: [team insights]
   - Tools: [tooling improvements]
   - ...

   ## Design Decision Assessment
   - **Architecture** (creative-architecture.md):
     - Effectiveness: ✓ / Partial / ✗
     - Notes: [assessment]
   - **UI/UX** (creative-uiux.md):
     - Effectiveness: ✓ / Partial / ✗
     - Notes: [assessment]
   - ...

   ## Improvements for Next Time
   - Process: [what to change]
   - Technical: [better approaches]
   - Planning: [planning improvements]
   - ...

   ## Next Steps (if any)
   - Follow-up tasks
   - Technical debt to address
   - Future enhancements
   - ...

   ## Completion Checklist
   - [x] Development lifecycle reviewed
   - [x] Successes documented
   - [x] Challenges and solutions documented
   - [x] Lessons learned captured
   - [x] Design decisions assessed
   - [x] Improvements identified
   ```

6. **Update tasks.md**:
   ```markdown
   ## [TASK_ID] Task Title
   **Status**: REFLECT Complete
   **Reflection**: [reflect-task_id.md](.vscode/memory-bank/reflection/reflect-task_id.md)
   ```

7. **Mode Transition**:
   - **Level 1-2**: Task complete (simple tasks не требуют ARCHIVE)
   - **Level 3-4**: `NEXT MODE: ARCHIVE` (comprehensive documentation recommended)

## Reflection Templates

**Level 2 (Basic)**:
- Summary
- What worked
- Challenges
- Key lessons

**Level 3-4 (Comprehensive)**:
- Full lifecycle review
- Technical & process lessons
- Design decision assessment
- Improvements for next time

## Verification Checklist

```
✓ REFLECT CHECKPOINT
- Development lifecycle thoroughly reviewed? [YES/NO]
- Successes, challenges, lessons documented? [YES/NO]
- Creative/design decisions assessed? [YES/NO]
- tasks.md updated with reflection link? [YES/NO]

→ If all YES: Proceed to ARCHIVE (L3-4) or Complete (L1-2)
→ If any NO: Complete reflection documentation
```

## Memory Bank Updates

- **reflection/reflect-[task_id].md**: Полный reflection document
- **tasks.md**: Ссылка на reflection, статус "REFLECT Complete"
- **activeContext.md**: Очистить после reflection (готов к новой задаче)

---

**Adapted from**: cursor-memory-bank v0.7-beta  
**VS Code**: Uses `.vscode/` instead of `.cursor/`  
**GitHub Copilot**: Activated via chat command "REFLECT"
