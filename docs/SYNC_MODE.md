# SYNC Mode Deep Dive

SYNC transforms internal Memory Bank knowledge into polished public documentation.

## Why SYNC Matters
- Acts as a "git push" for human-readable artefacts
- Ensures README, CHANGELOG, docs/ stay aligned with actual work
- Converts ADR candidates and progress logs into sharable narratives

## Seven-Phase Pipeline

1. **Context Load**
   - Reads `tasks.md`, `progress.md`, `creative/`, `archive/`
   - Detects completed tasks since last sync
2. **Changelog Draft**
   - Generates semantic version bump (major/minor/patch)
   - Drafts entries grouped by feature/fix/chore
3. **Documentation Assembly**
   - Updates README sections (features, metrics, roadmap)
   - Creates/refreshes docs in `docs/`
4. **ADR Extraction**
   - Scans for `ADR_CANDIDATE` markers
   - Converts into formal ADR files under `docs/adr/`
5. **Quality Gate**
   - Validates Markdown structure
   - Ensures links resolve and TODOs resolved
6. **Git Integration** (optional)
   - Suggests meaningful commit message
   - Lists files impacted for review
7. **Publishing**
   - Writes final artefacts to disk
   - Logs summary to console and `progress.md`

## Running SYNC

### Via Chat Mode
```
SYNC
```
- Best for interactive runs
- Accepts inline instructions (e.g., "skip changelog")

### Via PowerShell
```powershell
pwsh .vscode/memory-bank/scripts/sync.ps1
```

Flags:
- `-DryRun` – preview changes without writing
- `-SkipChangelog` – keep existing changelog intact
- `-Verbose` – detailed logging for debugging

## Inputs & Outputs

| Input | Source |
|-------|--------|
| Completed tasks | `.vscode/memory-bank/tasks.md` |
| Progress timeline | `.vscode/memory-bank/progress.md` |
| Design notes | `.vscode/memory-bank/creative/*.md` |
| Reflections | `.vscode/memory-bank/reflection/*.md` |

| Output | Destination |
|--------|-------------|
| Project overview | `README.md` |
| Release notes | `CHANGELOG.md` |
| Documentation bundle | `docs/` |
| ADRs | `docs/adr/` |

## Best Practices
- Run SYNC after QA passes and before pushing to remote
- Ensure Memory Bank files are up to date (plan/creative/progress)
- Use `-DryRun` on CI to validate documentation drift
- Pair SYNC with manual review for critical releases

## Example Workflow
```text
IMPLEMENT ✅
QA ✅
SYNC (Dry Run) → Review diff
SYNC (Write) → Commit → Push
```

## Troubleshooting
| Symptom | Fix |
|---------|-----|
| Missing changelog entry | Confirm task marked as completed in `tasks.md` |
| Docs not updating | Check write permissions, ensure SYNC not run with `-DryRun` |
| ADR not generated | Ensure note contains `ADR_CANDIDATE` marker |
| Markdown validation failed | Inspect console output for line numbers |

## Roadmap Ideas
- GitHub Actions workflow for automated SYNC on main branch merges
- Template-driven release notes with visuals
- Integration with project management tools (Linear, Jira) for cross-linking
