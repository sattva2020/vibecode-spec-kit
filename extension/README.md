# Code Memory Bank Extension

**Structured memory system for complex projects. Automates workflows, preserves context across sessions, enhances GitHub Copilot with persistent project memory.**

## Overview

Code Memory Bank transforms how you work on complex development projects by providing structured workflows and persistent context management. Never lose track of your progress or forget important decisions again.

## Key Benefits

🧠 **Persistent Memory** - Preserves project context between sessions  
🔄 **Automated Workflows** - Guided progression: VAN→PLAN→CREATIVE→IMPLEMENT→REFLECT→ARCHIVE  
🌍 **15 Languages** - Full internationalization support with auto-detection  
🎯 **Smart Complexity** - Adapts approach based on project complexity (Level 1-4)  
⚡ **Zero Startup Impact** - Hybrid activation, loads only when needed  

## Features

### 🎯 **7 Structured Modes**
- **VAN** - Project initialization and complexity assessment
- **PLAN** - Detailed implementation roadmap creation  
- **CREATIVE** - Design exploration with option analysis
- **IMPLEMENT** - Step-by-step guided development
- **REFLECT** - Review, lessons learned, improvements
- **ARCHIVE** - Documentation finalization and storage
- **SYNC** - System health check and diagnostics

### 📋 **Intelligent Task Management**
- Single source of truth for all project tasks
- Automatic progress tracking with absolute file paths
- Cross-session context restoration
- Complexity-adaptive planning (1-4 levels)

### 🤖 **GitHub Copilot Integration** 
- Enhanced context passing to Copilot
- Mode-specific prompt optimization
- Persistent conversation history
- Smart activation triggers

## Quick Start

1. **Install Extension:** Install from VS Code Marketplace
2. **Initialize Memory Bank:** Run `Memory Bank: Setup Wizard` from Command Palette
3. **Start First Task:** Type `VAN` in Copilot Chat to create your first task

## Usage

### Command Palette Commands

- `Memory Bank: VAN Mode` - Project initialization and task assessment
- `Memory Bank: PLAN Mode` - Detailed implementation planning
- `Memory Bank: CREATIVE Mode` - Design exploration and option analysis
- `Memory Bank: IMPLEMENT Mode` - Step-by-step implementation
- `Memory Bank: REFLECT Mode` - Review and retrospective
- `Memory Bank: ARCHIVE Mode` - Documentation finalization
- `Memory Bank: SYNC Mode` - System diagnostics and health check
- `Memory Bank: Setup Wizard` - Initialize Memory Bank in workspace
- `Memory Bank: Show Status` - Display current Memory Bank status

### Copilot Chat Integration

After running a command from Command Palette, simply type the mode keyword in Copilot Chat:

```
VAN
```

Copilot will load the appropriate mode instructions and guide you through the workflow.

## Settings

- **Language:** Choose from 15 supported languages (English, Russian, German, French, Spanish, etc.)
- **Default Complexity:** Set default task complexity (Level 1-4)
- **Auto-Save:** Automatically save Memory Bank files after updates
- **Templates Path:** Custom path to Memory Bank templates (optional)

## Requirements

- VS Code 1.85.0 or higher
- Node.js 18.0.0 or higher
- GitHub Copilot extension (recommended)

## Extension Structure

```
.vscode/memory-bank/
├── tasks.md              # Task tracking
├── activeContext.md      # Current focus
├── progress.md           # Implementation log
├── projectbrief.md       # Project overview
├── .language             # Language preference
├── creative/             # Creative decisions
├── reflection/           # Retrospectives
└── archive/              # Completed task archives
```

## Version

**v0.1.0-beta** - Initial public release

## License

MIT

## More Information

- [GitHub Repository](https://github.com/your-org/code-memory-bank)
- [Documentation](https://github.com/your-org/code-memory-bank/tree/main/docs)
- [Issue Tracker](https://github.com/your-org/code-memory-bank/issues)

---

**Enjoy structured development with Code Memory Bank!** 🚀
