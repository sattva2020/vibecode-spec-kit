# Changelog

All notable changes to the VS Code Memory Bank System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-02

### Added
- Initial release of VS Code Memory Bank System
- 8 specialized chat modes (VAN, PLAN, CREATIVE, IMPLEMENT, REFLECT, ARCHIVE, QA, SYNC)
- 114 hierarchical isolation rules with 64% token optimization
- PowerShell automation scripts (memory-bank.ps1, sync.ps1)
- SYNC mode for automatic documentation synchronization
- Template system for Memory Bank initialization
- Comprehensive documentation suite

### Changed
- Adapted from cursor-memory-bank v0.7-beta for VS Code + GitHub Copilot
- Relocated files from `.cursor/` to `.vscode/` and `.github/`
- Enhanced chat modes with additional tools (list_dir, grep_search)
- Implemented 7-phase SYNC process with semver automation

### Features Highlights
- **SYNC Mode**: Automated README/CHANGELOG/ADR generation
- **Token Optimization**: 64% reduction through hierarchical rule loading
- **GitHub Copilot Integration**: Native chat modes support
- **Cross-Platform**: PowerShell Core support for Linux/macOS

## [Unreleased]

### Planned
- Visual Studio Code extension for easier installation
- Interactive setup wizard
- GitHub Actions integration for CI/CD
- Additional language support for scripts (Python, Bash)
- Performance metrics and analytics

---

**Note**: This is version 1.0.0 as it represents the first complete, production-ready release adapted for VS Code.
