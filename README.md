# Vibecode Spec Kit

> **Modern Spec Development Kit - AI-Powered Development with Context Preservation**

A comprehensive Modern Spec Development Kit that works as both **standalone CLI tool** and **IDE integration**. Integrates GitHub Spec Kit methodologies with advanced task management, context preservation, and multi-agent AI support. Provides structured workflows, constitutional validation, and intelligent research capabilities for modern software development.

## 🎯 **Deployment Modes**

### **1. IDE Integration Mode (Recommended)**
- Integrates directly into your IDE (VS Code, Cursor, JetBrains)
- Native AI agent support through IDE extensions
- Seamless context preservation within development environment

### **2. Standalone CLI Mode**
- Independent Python CLI tool
- Full functionality without IDE dependencies
- Perfect for automation and CI/CD pipelines

### **3. Hybrid Platform Mode (Best of Both)**
- Combine IDE integration with CLI automation
- Maximum flexibility and power
- Recommended for professional development teams

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![VS Code](https://img.shields.io/badge/VS%20Code-1.85+-blue.svg)](https://code.visualstudio.com/)
[![GitHub Copilot](https://img.shields.io/badge/GitHub%20Copilot-Required-green.svg)](https://github.com/features/copilot)

## ✨ Features

- **8 Specialized Chat Modes**: VAN, PLAN, CREATIVE, IMPLEMENT, REFLECT, ARCHIVE, QA, SYNC
- **Hierarchical Rule System**: 114 isolation rules with 64% token optimization
- **Automatic Documentation Sync**: README, CHANGELOG, ADR generation
- **GitHub Copilot Integration**: Native chat modes via `.github/chatmodes/`
- **PowerShell Automation**: Scripts for Memory Bank management and synchronization
- **Complexity-Based Workflows**: Level 1-4 task classification with appropriate workflows

## ��� Quick Start

### Prerequisites

- Visual Studio Code 1.85 or later
- GitHub Copilot subscription
- PowerShell 5.1+ (Windows) or PowerShell Core 7+ (cross-platform)

### Installation

1. **Clone the repository into your project:**
   ```bash
   cd your-project
   git clone https://github.com/sattva2020/vscode-memory-bank.git .vscode-memory-bank
   ```

2. **Copy files to your project:**
   ```bash
   # Copy chatmodes
   cp -r .vscode-memory-bank/.github/chatmodes .github/
   
   # Copy VS Code configuration
   cp -r .vscode-memory-bank/.vscode/* .vscode/
   ```

3. **Initialize Memory Bank:**
   ```bash
   # Create Memory Bank structure
   mkdir -p .vscode/memory-bank/{creative,reflection,archive}
   
   # Copy templates
   cp -r .vscode/templates/memory_bank/* .vscode/memory-bank/
   ```

4. **Restart VS Code** to activate GitHub Copilot chat modes.

### First Steps

1. Open GitHub Copilot Chat in VS Code
2. Type `VAN` to start project initialization
3. Follow the workflow: `VAN → PLAN → CREATIVE → IMPLEMENT → REFLECT → ARCHIVE → SYNC`

For detailed instructions, see [docs/INSTALLATION.md](docs/INSTALLATION.md).

## ��� Documentation

- [Quick Start Guide](docs/QUICK_START.md) - Get up and running in 5 minutes
- [Chat Modes Reference](docs/CHATMODES.md) - Complete guide to all 8 modes
- [Architecture Overview](docs/ARCHITECTURE.md) - System design and components
- [SYNC Mode Explained](docs/SYNC_MODE.md) - Documentation synchronization details

## ��� Core Concepts

### Chat Modes Workflow

```
VAN → PLAN → CREATIVE → IMPLEMENT → REFLECT → ARCHIVE → SYNC
 ↓      ↓        ↓          ↓           ↓         ↓        ↓
Init  Plan  Design   Code    Review  Document  Publish
```

Each mode has specific tools and focuses:

| Mode | Purpose | Key Tools | When to Use |
|------|---------|-----------|-------------|
| **VAN** | Initialize project, assess complexity | `create_directory`, full analysis tools | Start of project or new task |
| **PLAN** | Break down tasks into components | Documentation tools | Level 2-4 tasks |
| **CREATIVE** | Design decisions and architecture | `list_dir`, `grep_search` | Level 3-4 complex features |
| **IMPLEMENT** | Code implementation | `run_in_terminal`, all dev tools | All code changes |
| **REFLECT** | Review and lessons learned | Analysis tools | After implementation |
| **ARCHIVE** | Comprehensive documentation | Documentation tools | Level 3-4 task completion |
| **QA** | Technical validation | `run_in_terminal` (no write) | Any time for validation |
| **SYNC** | Publish to README/CHANGELOG/ADR | Git + terminal tools | After ARCHIVE phase |

### Complexity Levels

- **Level 1**: Quick fixes, simple changes (→ IMPLEMENT directly)
- **Level 2**: Simple features (→ PLAN → IMPLEMENT)
- **Level 3**: Moderate complexity (→ PLAN → CREATIVE → IMPLEMENT → ARCHIVE → SYNC)
- **Level 4**: Architectural changes (Full workflow with comprehensive documentation)

## ��� Key Components

### 1. Chat Modes (`.github/chatmodes/`)

8 specialized AI modes with tool permissions and instructions:
- YAML frontmatter controls available tools
- Markdown provides AI behavioral instructions
- Auto-detected by GitHub Copilot

### 2. Isolation Rules (`.vscode/rules/isolation_rules/`)

Hierarchical rule system for context optimization:
- **Core Rules**: Always loaded (main.mdc, command-execution.mdc)
- **Level-Specific**: Loaded based on task complexity
- **Visual Maps**: Process diagrams for each mode
- **Specialized**: Loaded on-demand (e.g., CreativePhase rules)

**Token Optimization**: 64% reduction through hierarchical loading

### 3. Memory Bank (`.vscode/memory-bank/`)

Context preservation system:
- `tasks.md` - Single Source of Truth for task tracking
- `activeContext.md` - Current focus and recent decisions
- `progress.md` - Implementation status
- `creative/` - Design decision documents
- `reflection/` - Lessons learned
- `archive/` - Completed task documentation

### 4. PowerShell Scripts

**memory-bank.ps1**:
- `status` - Check Memory Bank state
- `update` - Update progress and context
- `recount` - Recalculate statistics

**sync.ps1**:
- 7-phase documentation synchronization
- README.md / CHANGELOG.md updates
- ADR generation from creative docs
- Git automation (branch, commit, PR)

## ��� SYNC Mode Highlights

SYNC mode is the "git push" for documentation - it publishes your work:

1. **Reads** latest archive document
2. **Extracts** metadata and achievements
3. **Updates** README.md with "Recent Updates" section
4. **Bumps** CHANGELOG.md version (semver)
5. **Generates** ADR documents from creative decisions
6. **Creates** git commit + branch + PR description
7. **Reports** summary of changes

**3 Creative Decisions**:
- Hybrid Version Bump (Level-based semver)
- Smart README Positioning (chronological updates)
- Template-based ADR Generation (auto-extract from creative docs)

## ��� vs Original cursor-memory-bank

| Aspect | Cursor Original | VS Code (This Repo) |
|--------|----------------|---------------------|
| **Custom Modes** | `.cursor/` directory + UI | `.github/chatmodes/*.chatmode.md` |
| **Rules Location** | `.cursor/rules/` | `.vscode/rules/` |
| **Templates** | `templates/` | `.vscode/templates/` |
| **Memory Bank** | `memory-bank/` | `.vscode/memory-bank/` |
| **Tasks** | Cursor-specific | VS Code tasks.json + PowerShell |
| **Activation** | Cursor UI | GitHub Copilot Chat commands |
| **Chat Modes** | 5 modes | 8 modes (+ QA, ARCHIVE, SYNC) |
| **Documentation Sync** | Manual | Automated (SYNC mode) |
| **Token Optimization** | Basic | Advanced (64% reduction) |

## ��� What's Included

```
vscode-memory-bank/
├── .github/chatmodes/        # 8 specialized chat modes
├── .vscode/
│   ├── rules/isolation_rules/  # 114 hierarchical rules
│   ├── templates/memory_bank/  # Initialization templates
│   └── memory-bank/scripts/    # PowerShell automation
├── docs/                     # Comprehensive documentation
│   ├── INSTALLATION.md
│   ├── QUICK_START.md
│   ├── CHATMODES.md
│   ├── ARCHITECTURE.md
│   └── SYNC_MODE.md
├── examples/                 # Usage examples
├── README.md                 # This file
├── LICENSE                   # MIT License
└── CHANGELOG.md              # Version history
```

## ��� Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ��� License

MIT License - see [LICENSE](LICENSE) file for details.

## ��� Acknowledgments

- Original [cursor-memory-bank](https://github.com/caspianmerlin/cursor-memory-bank) by caspianmerlin
- Inspired by Claude's "Think" tool methodology (Anthropic)
- GitHub Copilot team for chat modes API
- VS Code extension community

## ��� Support

- **Issues**: [GitHub Issues](https://github.com/sattva2020/vscode-memory-bank/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sattva2020/vscode-memory-bank/discussions)
- **Documentation**: [docs/](docs/)

---

**Built with ❤️ by [sattva2020](https://github.com/sattva2020)**

**Powered by GitHub Copilot ���**
# vibecode-spec-kit
