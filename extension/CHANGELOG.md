# Change Log

All notable changes to the "Code Memory Bank" extension will be documented in this file.

## [0.1.0] - 2025-10-02

### 🎉 **Initial Beta Release - "Code Memory Bank"**

#### **Core Features**
- **Structured Workflows:** 7 guided modes (VAN→PLAN→CREATIVE→IMPLEMENT→REFLECT→ARCHIVE→SYNC)
- **Setup Wizard:** One-click Memory Bank initialization in any workspace
- **Smart Activation:** Hybrid strategy (onStartupFinished + onCommand) - zero startup impact
- **Multi-language:** 15 languages with automatic system detection
- **Status Integration:** Status bar showing Memory Bank state (🗄️ active / ⚠️ not detected)

#### **Command Palette Integration**
- 9 dedicated commands with "Code Memory Bank" category
- Phase 1 MVP: Commands open Copilot Chat + show notification with keyword
- Memory Bank detection guards (prevents execution without initialized structure)

#### **Configuration Options**
- **Language Selection:** 15 supported languages (en, ru, uk, de, fr, es, pt, it, ja, zh, ko, ar, hi, pl, tr)
- **Complexity Levels:** 4 adaptive levels (Level 1-4) with time estimates
- **Auto-Save:** Automatic Memory Bank file updates
- **Templates Path:** Custom template directory support

#### **Technical Foundation**
- TypeScript 5.2.2 with strict mode
- VS Code Extension API 1.85.0+ compatibility  
- Webpack 5 bundling with source maps
- ESLint 8.52.0 configuration
- Node.js 18+ runtime requirement

#### **Memory Bank Structure**
```
.vscode/memory-bank/
├── tasks.md              # Single source of truth for task tracking
├── activeContext.md      # Current focus and state
├── progress.md           # Implementation history with absolute paths
├── projectbrief.md       # Project foundation
├── .language             # Auto-detected language preference
├── creative/             # Creative phase documentation
├── reflection/           # Retrospective archives
└── archive/              # Completed task storage
```

### 📋 **Product Positioning**
- **Official Name:** "Code Memory Bank" (rebranded from "VS Code Memory Bank")
- **Market Category:** Productivity tools for complex development projects
- **Target Audience:** Developers using VS Code + GitHub Copilot on multi-session projects
- **Unique Value:** Persistent project memory + structured workflow automation

---

**Note:** This is a preview release (v0.1.0-beta). Advanced features (UI integration, file watchers, automated testing) planned for v0.2.0+.
