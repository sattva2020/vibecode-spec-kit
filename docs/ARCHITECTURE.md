# Architecture Overview

The VS Code Memory Bank System adapts the original Cursor Memory Bank concept for a Copilot-first workflow inside Visual Studio Code.

## High-Level Components

```text
├── .github/chatmodes/          # Conversation blueprints for each mode
├── .vscode/rules/isolation_rules/  # Hierarchical governance rules
├── .vscode/templates/          # Markdown scaffolds for outputs
└── .vscode/memory-bank/
    ├── scripts/                # Automation (PowerShell)
    └── *.md                    # Working memory data
```

### Chat Modes
- Markdown definitions with YAML frontmatter
- Declare available tools, guard rails, and prompts
- Loaded by GitHub Copilot Chat on workspace open

### Isolation Rules
- 114 rules grouped by mode and concern
- Example directories: `0000_core`, `0200_plan`, `0700_archive`
- Each rule defines `isolationLevel`, `priority`, contextual examples
- Progressive loading ensures only relevant context is fed to Copilot → **64% token savings**

### Templates
- Reside in `.vscode/templates/memory_bank/`
- Provide consistent structure for plans, reflections, archives
- Support multi-language (EN/RU) placeholders

### Automation Scripts
- `memory-bank.ps1`: Initialize/inspect Memory Bank state
- `sync.ps1`: Run full documentation pipeline
- Implement colored logging, dry-run support, Git metadata extraction

## Data Flow

```text
User Task → VAN → PLAN → CREATIVE → IMPLEMENT → QA → REFLECT → ARCHIVE → SYNC
```

1. **VAN** reads repository structure using `list_dir`, stores initial findings in `progress.md`
2. **PLAN** expands task into sub-components using templates
3. **CREATIVE** records ADR candidates under `creative/`
4. **IMPLEMENT** modifies codebase, updates progress timeline
5. **QA** executes validation routines, attaches reports
6. **REFLECT** captures retrospective insights
7. **ARCHIVE** snapshots outcomes for knowledge retention
8. **SYNC** aggregates Memory Bank artefacts into public docs

## Token Optimization Strategy
- Base context: Core rules (`0000_core`) always loaded
- Mode-specific rules inserted on demand (e.g., PLAN adds `0200_plan`)
- Optional packs (architecture, testing) loaded lazily when referenced
- SYNC compiles final narrative → large documents generated once, not repeatedly shared with Copilot

## Extensibility
- Add new modes by creating `.chatmode.md` files
- Compose additional isolation packs for domain-specific workflows (e.g., data science, embedded systems)
- Replace PowerShell scripts with language of choice (Python prototype planned)

## Security Considerations
- Memory Bank files (*.md) stored locally; `.gitignore` excludes user data by default
- SYNC outputs sanitized documentation for public sharing
- No network calls within scripts; Git operations optional

## Release Pipeline
1. Developer runs through workflow locally
2. `sync.ps1` generates documentation bundle
3. Git commit includes README, CHANGELOG, docs/
4. Optional – GitHub Actions validate docs consistency

## Future Enhancements
- VS Code extension for UI-driven mode switching
- Telemetry (opt-in) for workflow metrics
- Script parity in Bash/Python
- Visual dashboards for progress tracking
