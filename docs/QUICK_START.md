# Quick Start Guide

Launch your first Memory Bank workflow in minutes.

## 1. Install
```bash
git clone https://github.com/sattva2020/vscode-memory-bank.git
cd vscode-memory-bank
cp -r .github /path/to/project/
cp -r .vscode /path/to/project/
cd /path/to/project
pwsh .vscode/memory-bank/scripts/memory-bank.ps1 init
```
Restart VS Code (`Ctrl+Shift+P → Developer: Reload Window`).

## 2. Understand the Flow
```
VAN → PLAN → CREATIVE → IMPLEMENT → QA → REFLECT → ARCHIVE → SYNC
```
Each mode represents a phase in your feature development lifecycle.

## 3. Your First Task
Edit `.vscode/memory-bank/tasks.md`:
```markdown
## TASK_001: Add user login
**Complexity**: Level 2 (Medium)
**Status**: Not Started (red)
**Assigned Mode**: PLAN

### Description
Implement email/password login using existing API.

### Requirements
- [ ] Login form
- [ ] API endpoint
- [ ] Session handling
- [ ] Tests
```

## 4. Run Through the Modes

1. **VAN** – Analyze task
   ```
   VAN
   ```
   - Confirms complexity level
   - Suggests next mode

2. **PLAN** – Break down work
   ```
   PLAN
   ```
   - Generates sub-tasks
   - Creates plan doc under `.vscode/memory-bank/plan/`

3. **IMPLEMENT** – Write code
   ```
   IMPLEMENT
   ```
   - Guides coding sequence
   - Encourages tests and commits

4. **QA** – Validate
   ```
   QA
   ```
   - Runs through readiness checklist

5. **SYNC** – Publish documentation
   ```
   SYNC
   ```
   - Updates README, CHANGELOG, docs/

## 5. PowerShell Shortcuts
```powershell
# View status
pwsh .vscode/memory-bank/scripts/memory-bank.ps1 status

# Update progress
pwsh .vscode/memory-bank/scripts/memory-bank.ps1 update

# Run SYNC with preview
pwsh .vscode/memory-bank/scripts/sync.ps1 -DryRun
```

## 6. Complexity Cheat Sheet
| Level | Typical Work | Recommended Modes |
|-------|---------------|-------------------|
| 1     | Bugfix / copy tweak | VAN → IMPLEMENT → QA → SYNC |
| 2     | Feature addition | VAN → PLAN → IMPLEMENT → QA → SYNC |
| 3     | Architecture change | VAN → PLAN → CREATIVE → IMPLEMENT → QA → REFLECT → SYNC |
| 4     | System redesign | Full workflow with ARCHIVE snapshot |

## 7. Tips
- Add current context when invoking modes:
  ```
  PLAN

  Context:
  - Backend already exposes /api/login
  - Need to support remember-me checkbox
  ```
- After each mode, glance at `.vscode/memory-bank/progress.md`
- Use ARCHIVE only when finalizing major milestones

## 8. Explore Further
- [Chat Modes Reference](CHATMODES.md)
- [Architecture Overview](ARCHITECTURE.md)
- [SYNC Mode Deep Dive](SYNC_MODE.md)

Ready to ship your first feature!
