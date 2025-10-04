# Chat Modes Reference

Eight specialized modes orchestrate the development lifecycle. Trigger each mode by typing its name into GitHub Copilot Chat.

## VAN — Vanishing Analysis Navigator
- **Purpose**: Establish context, classify task complexity, outline next steps
- **Best for**: Kick-off of any work item, unfamiliar repositories, exploratory analysis
- **Tools Enabled**: `list_dir`, `read_file`, `grep_search`, `semantic_search`, `run_in_terminal`
- **Outputs**:
  - Complexity level (1—4)
  - Suggested mode sequence
  - Initial notes appended to `progress.md`
- **Tips**:
  - Provide task brief as plain text under the command
  - Ask for risk assessment or tech debt highlights when needed

## PLAN — Programmatic Layout Architect for Navigation
- **Purpose**: Break down tasks into actionable subcomponents with estimates
- **Tools Enabled**: `read_file`, `list_dir`, `run_in_terminal`, `insert_edit_into_file`
- **Outputs**:
  - Structured plan in `.vscode/memory-bank/plan/TASK_xxx_plan.md`
  - Updated checklist in `tasks.md`
- **Tips**:
  - Provide deadline or iteration length to get better scheduling
  - Ask for acceptance criteria refinements

## CREATIVE — Conceptual Research & Experimentation Venue
- **Purpose**: Explore alternative designs, produce architectural decisions, generate prototypes
- **Tools Enabled**: `read_file`, `semantic_search`, `run_in_terminal`
- **Outputs**:
  - ADR candidates (`ADR_CANDIDATE` markers in `creative/*.md`)
  - Design proposals with pros/cons
- **Tips**:
  - Use for Level 3+ tasks or whenever decisions need documentation
  - Request comparison tables or architecture diagrams

## IMPLEMENT — Iterative Module Production Engine
- **Purpose**: Execute the plan with guarded edits and inline verification
- **Tools Enabled**: `insert_edit_into_file`, `apply_patch`, `run_in_terminal`, `get_errors`, `runTests`
- **Outputs**:
  - Code changes applied to repository
  - Updates to `progress.md` (time-stamped notes)
- **Tips**:
  - Provide file list or function names to accelerate targeting
  - Ask for test scaffolds before implementation for TDD

## QA — Quality Assurance Sentinel
- **Purpose**: Validate implementation across dependencies, configuration, and automated checks
- **Tools Enabled**: `run_in_terminal`, `get_errors`, `runTests`, `list_dir`
- **Outputs**:
  - Validation report appended to `progress.md`
  - Suggested remediations for failed checks
- **Checklist**:
  - Dependencies resolved?
  - Environment variables configured?
  - Lint/build/tests passing?
  - Rollback plan identified?

## REFLECT — Retrospective Evaluation Facilitator
- **Purpose**: Capture lessons learned, blockers, and improvements after implementation
- **Tools Enabled**: `read_file`, `insert_edit_into_file`, `run_in_terminal`
- **Outputs**:
  - Reflection entry in `reflection/`
  - Updated `progress.md` timeline
- **Prompts**:
  - What worked well?
  - What slowed us down?
  - Which decisions should be revisited?

## ARCHIVE — Automated Repository Chronicle Hub
- **Purpose**: Consolidate final deliverables, store ADRs, snapshot context for future onboarding
- **Tools Enabled**: `read_file`, `list_dir`, `run_in_terminal`
- **Outputs**:
  - Archived packets in `archive/`
  - Summary links into Memory Bank index
- **Usage**:
  - End of sprint/milestone
  - Major release cut

## SYNC — Synchronization & Narrative Compiler
- **Purpose**: Publish project knowledge base, update public documentation and changelog
- **Tools Enabled**: `read_file`, `run_in_terminal`, `insert_edit_into_file`
- **Outputs**:
  - README.md sections refreshed
  - `CHANGELOG.md` entry for latest release
  - Docs generated from `creative/` + `progress.md`
- **Triggers**:
  - After QA passes
  - Before pushing to remote repository

## Choosing the Right Mode
| Scenario | Recommended Mode |
|----------|------------------|
| New feature, unknown domain | VAN → PLAN → CREATIVE |
| Bug fix with clear repro | VAN → IMPLEMENT |
| Refactor legacy module | VAN → PLAN → IMPLEMENT → QA → REFLECT |
| Release preparation | QA → SYNC → ARCHIVE |

## Mode Interactions
- Modes append to shared artefacts (`progress.md`, `tasks.md`) automatically
- Modes can be re-run; they detect previous sections and append rather than overwrite
- Complexity escalations (e.g., VAN detects Level 3) prompt additional modes (CREATIVE, REFLECT)

## Customization
- Adjust isolation rules in `.vscode/rules/isolation_rules/`
- Extend modes by editing corresponding `.chatmode.md` files
- Add company-specific governance inside templates under `.vscode/templates/memory_bank/`
