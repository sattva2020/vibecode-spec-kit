---
description: 'CREATIVE Mode - Design decisions, architecture, UI/UX, algorithm exploration (Level 3-4)'
tools: [read_file, create_file, replace_string_in_file, list_dir, grep_search, semantic_search]
---

# 🎨 CREATIVE MODE - Design Decisions

> **Memory Bank System for VS Code** | Creative Phase based on Claude "Think" Tool methodology

Исследование вариантов дизайна и принятие архитектурных решений для компонентов, отмеченных в PLAN режиме.

## Когда пользователь пишет "CREATIVE"

1. **Immediate Response**: Ответь `OK CREATIVE`

2. **Memory Bank Check**:
   - Прочитай `.vscode/memory-bank/tasks.md`
   - Найди "Creative Phase Components" из PLAN phase
   - Проверь complexity (должен быть Level 3-4)

3. **Rule Loading**:
   - Загрузи `.vscode/rules/isolation_rules/visual-maps/creative-mode-map.mdc`
   - Загрузи `.vscode/rules/isolation_rules/Core/creative-phase-enforcement.mdc`
   - **Lazy-load specialized rules** (по требованию):
     - Architecture: `.vscode/rules/isolation_rules/Phases/CreativePhase/creative-phase-architecture.mdc`
     - UI/UX: `.vscode/rules/isolation_rules/Phases/CreativePhase/creative-phase-uiux.mdc`
     - Algorithm: `.vscode/rules/isolation_rules/Phases/CreativePhase/creative-phase-algorithm.mdc`

4. **Creative Process** (для каждого flagged aspect):

   **Step 1: Problem Definition**
   - Опиши проектную задачу
   - Определи constraints и требования

   **Step 2: Options Exploration**
   - Исследуй 2-4 возможных подхода
   - Для каждого опишите:
     - Преимущества
     - Недостатки
     - Сложность реализации

   **Step 3: Analysis Table**
   | Option | Pros | Cons | Complexity | Score |
   |--------|------|------|------------|-------|
   | Option A | ... | ... | Low/Med/High | X/10 |
   | Option B | ... | ... | Low/Med/High | Y/10 |

   **Step 4: Decision**
   - Выбери лучший вариант
   - Обоснуй выбор

   **Step 5: Implementation Notes**
   - Опиши ключевые моменты реализации
   - Укажи риски и их митигацию

5. **Create Design Document**:
   ```
   .vscode/memory-bank/creative/creative-[aspect_name].md
   ```

   Формат:
   ```markdown
   # Creative Design: [Aspect Name]
   **Task**: [TASK_ID]
   **Date**: YYYY-MM-DD
   **Complexity**: Level X

   ## Problem
   ...

   ## Options Explored
   ### Option A: ...
   - **Pros**: ...
   - **Cons**: ...
   - **Complexity**: ...

   ### Option B: ...
   ...

   ## Analysis Table
   | Option | Pros | Cons | Complexity | Score |
   |--------|------|------|------------|-------|
   ...

   ## Decision
   **Selected**: Option X
   **Rationale**: ...

   ## Implementation Notes
   - Key points: ...
   - Risks: ...
   - Mitigation: ...

   ## Verification
   - [ ] Decision documented with rationale
   - [ ] Implementation notes complete
   - [ ] Linked in tasks.md
   ```

6. **Update tasks.md**:
   - Отметь Creative Phase Component как complete
   - Добавь ссылку на creative document:
     ```markdown
     - [x] Architecture decisions → [creative-architecture.md](.vscode/memory-bank/creative/creative-architecture.md)
     ```

7. **Mode Transition**:
   - Если есть еще Creative Phase Components → continue CREATIVE
   - Если все complete → `NEXT MODE: IMPLEMENT`

## Token Optimization (Claude "Think" Tool)

- **Progressive Documentation**: Короткие шаблоны, расширяемые по сложности
- **Detail-on-demand**: Детали только когда нужны
- **Tabular Options**: Компактное сравнение опций
- **Structured Templates**: Масштабируемые с complexity

## Specialized Rules (Lazy-loaded)

Загружай только при работе с конкретным aspect:
- **Architecture**: Микросервисы, patterns, слои
- **UI/UX**: Компоненты, layouts, accessibility
- **Algorithm**: Оптимизация, структуры данных, performance

## Verification Checklist

```
✓ CREATIVE CHECKPOINT
- All flagged aspects addressed? [YES/NO]
- Design decisions documented in creative-*.md? [YES/NO]
- Rationale clearly stated? [YES/NO]
- tasks.md updated with links to decision docs? [YES/NO]

→ If all YES: Proceed to IMPLEMENT
→ If any NO: Complete creative phase work
```

---

**Adapted from**: cursor-memory-bank v0.7-beta + Claude "Think" Tool  
**VS Code**: Uses `.vscode/` instead of `.cursor/`  
**GitHub Copilot**: Activated via chat command "CREATIVE"
