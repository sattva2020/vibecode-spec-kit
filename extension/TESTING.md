# Phase 1 Testing Instructions

## Prerequisites
- VS Code 1.85.0+
- Extension compiled (`npm run compile` completed successfully)
- `dist/extension.js` exists (8.78 KiB)

## Test Environment Setup

### 1. Open Extension Workspace in VS Code
```bash
code e:\My\vscode-memory-bank\extension
```

### 2. Launch Extension Development Host
- Press **F5** (or Run → Start Debugging)
- New VS Code window opens with extension loaded
- Look for "Extension Development Host" in title bar

## Test Suite

### Test 1: Extension Activation
**Expected:** Extension activates on startup (onStartupFinished)

**Steps:**
1. Open Extension Development Host
2. Check Debug Console for log messages
3. Look for: "Memory Bank extension activating..."

**✅ Pass Criteria:**
- Extension activates without errors
- Console shows activation message
- Status bar shows Memory Bank icon (warning if not detected, database icon if detected)

---

### Test 2: Memory Bank Detection (Not Initialized)
**Expected:** Extension detects absence of Memory Bank

**Steps:**
1. Open a folder WITHOUT `.vscode/memory-bank/` (or use empty folder)
2. Check status bar

**✅ Pass Criteria:**
- Status bar shows "⚠️ Memory Bank" (warning icon)
- Tooltip: "Memory Bank Not Detected - Click to setup"
- Click opens Setup Wizard

---

### Test 3: Setup Wizard
**Expected:** Creates Memory Bank structure

**Steps:**
1. Command Palette (Ctrl+Shift+P)
2. Type "Memory Bank: Setup Wizard"
3. Run command

**✅ Pass Criteria:**
- Progress notification appears ("Setting up Memory Bank...")
- Directory created: `.vscode/memory-bank/`
- Subdirectories: `creative/`, `reflection/`, `archive/`
- Files created: `tasks.md`, `activeContext.md`, `progress.md`, `projectbrief.md`, `.language`
- Success notification: "✅ Memory Bank initialized successfully!"
- Button: "Open Chat"

**Validation:**
```bash
# Check directory structure
ls .vscode/memory-bank/
# Expected: tasks.md, activeContext.md, progress.md, projectbrief.md, .language, creative/, reflection/, archive/
```

---

### Test 4: Memory Bank Detection (Initialized)
**Expected:** Extension detects presence of Memory Bank

**Steps:**
1. After running Setup Wizard
2. Reload VS Code window (Ctrl+R or F5 again)
3. Check status bar

**✅ Pass Criteria:**
- Status bar shows "$(database) Memory Bank" (database icon)
- Tooltip: "Memory Bank Active - Click for status"
- Console log: "Memory Bank detected at: [path]"

---

### Test 5: Show Status Command
**Expected:** Displays Memory Bank status in Output Channel

**Steps:**
1. Command Palette → "Memory Bank: Show Status"
2. Or click status bar icon

**✅ Pass Criteria:**
- Output Channel opens: "Memory Bank Status"
- Shows:
  - ✅ Memory Bank: ACTIVE
  - 📁 Location: [path]
  - Configuration (language, complexity, autoSave, templatesPath)
  - Available Modes (VAN, PLAN, CREATIVE, etc.)

---

### Test 6: Settings UI
**Expected:** 4 Memory Bank settings visible

**Steps:**
1. File → Preferences → Settings (Ctrl+,)
2. Search "Memory Bank"

**✅ Pass Criteria:**
- **Language** dropdown: 15 options (en, ru, uk, de, fr, es, pt, it, ja, zh, ko, ar, hi, pl, tr) with native names
- **Default Complexity** dropdown: 4 options (Level 1-4) with descriptions
- **Auto Save** checkbox: enabled by default
- **Templates Path** text field: empty by default

**Test changes:**
- Change language to "ru" (Русский) → Save → Check `.vscode/memory-bank/.language` file (should contain "ru")

---

### Test 7: VAN Mode Command
**Expected:** Opens Copilot Chat with notification

**Steps:**
1. Command Palette → "Memory Bank: VAN Mode"
2. (Ensure Memory Bank initialized)

**✅ Pass Criteria:**
- Copilot Chat panel opens
- Information notification: "💡 Memory Bank: Type "VAN" in Copilot Chat to activate VAN mode"
- Button: "Got it"

---

### Test 8: All 9 Commands
**Expected:** All commands open Chat + show notification

**Test each command:**
1. Memory Bank: VAN Mode
2. Memory Bank: PLAN Mode
3. Memory Bank: CREATIVE Mode
4. Memory Bank: IMPLEMENT Mode
5. Memory Bank: REFLECT Mode
6. Memory Bank: ARCHIVE Mode
7. Memory Bank: SYNC Mode
8. Memory Bank: Setup Wizard (tested in Test 3)
9. Memory Bank: Show Status (tested in Test 5)

**✅ Pass Criteria (for modes 1-7):**
- Copilot Chat opens
- Notification shows correct keyword ("Type [KEYWORD] in Copilot Chat...")
- No errors in Debug Console

---

### Test 9: Guard - Memory Bank Not Detected
**Expected:** Warning message when Memory Bank absent

**Steps:**
1. Delete `.vscode/memory-bank/` directory
2. Reload Extension Development Host (F5)
3. Command Palette → "Memory Bank: VAN Mode"

**✅ Pass Criteria:**
- Warning notification: "Memory Bank not detected. [reason]. Run "Memory Bank: Setup Wizard" to initialize."
- Button: "Setup Wizard"
- Chat does NOT open

---

### Test 10: Language Detection
**Expected:** System language detected during setup

**Steps:**
1. Delete `.vscode/memory-bank/` if exists
2. Run Setup Wizard
3. Check `.vscode/memory-bank/.language` file

**✅ Pass Criteria:**
- `.language` file contains system language code (e.g., "en", "ru")
- Code matches `vscode.env.language` (first part before hyphen)
- Example: `ru-RU` → `ru`, `en-US` → `en`

---

## Test Summary Template

```markdown
## Phase 1 Testing Results

**Date:** 2025-10-02  
**Tester:** [Name]  
**Environment:** VS Code [version], Windows/Mac/Linux

| Test | Status | Notes |
|------|--------|-------|
| 1. Extension Activation | ✅ PASS | [Notes] |
| 2. Memory Bank Detection (Not Init) | ✅ PASS | [Notes] |
| 3. Setup Wizard | ✅ PASS | [Notes] |
| 4. Memory Bank Detection (Init) | ✅ PASS | [Notes] |
| 5. Show Status Command | ✅ PASS | [Notes] |
| 6. Settings UI | ✅ PASS | [Notes] |
| 7. VAN Mode Command | ✅ PASS | [Notes] |
| 8. All 9 Commands | ✅ PASS | [Notes] |
| 9. Guard (Not Detected) | ✅ PASS | [Notes] |
| 10. Language Detection | ✅ PASS | [Notes] |

**Overall Result:** ✅ PASS / ❌ FAIL

**Issues Found:**
- [List any bugs or unexpected behavior]

**Performance Notes:**
- Extension activation time: [ms]
- Setup Wizard completion time: [seconds]
- Memory Bank detection time: [ms]
```

---

## Known Issues (Expected)

1. **Webpack Mode Warning:** "mode option not set" - Non-critical, defaults to production
2. **onCommand Activation Events:** VS Code shows warning about redundant events - Safe to ignore
3. **Copilot Chat API:** Phase 1 MVP uses command to open Chat, not direct API integration (Phase 3 feature)

## Debugging Tips

**Debug Console:** View → Debug Console (shows extension logs)

**Check logs:**
```javascript
// src/extension.ts logs:
console.log('Memory Bank extension activating...');
console.log(`Memory Bank detected at: ${detection.path}`);
console.log(`Memory Bank not detected: ${detection.reason}`);
console.log('Memory Bank extension activated successfully');
```

**Common issues:**
- Extension not loading → Check `dist/extension.js` exists
- Commands not appearing → Reload Extension Development Host (Ctrl+R)
- Status bar not showing → Check Memory Bank detection in Debug Console

---

## Next Steps After Testing

1. Document results in `progress.md`
2. Take screenshots (optional):
   - Command Palette with Memory Bank commands
   - Settings UI with 4 settings
   - Status Output Channel
   - Extension in action (Chat opened)
3. Fix any critical bugs found
4. Update `tasks.md` with Phase 1 completion status
5. Consider Phase 2 or REFLECT mode
