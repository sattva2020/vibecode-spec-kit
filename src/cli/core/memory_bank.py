"""
Memory Bank core operations
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class MemoryBankStatus:
    """Memory Bank status information"""

    initialized: bool
    memory_bank_path: Path
    essential_files: Dict[str, bool]
    subdirectories: Dict[str, bool]
    template_files: Dict[str, bool]
    constitutional_file: bool
    issues: List[str]

    def is_healthy(self) -> bool:
        """Check if Memory Bank is in healthy state"""
        return self.initialized and len(self.issues) == 0


class MemoryBank:
    """Memory Bank operations manager"""

    def __init__(self, memory_bank_path: str = "memory-bank"):
        self.memory_bank_path = Path(memory_bank_path).resolve()
        self.essential_files = {
            "tasks.md": False,
            "activeContext.md": False,
            "progress.md": False,
        }
        self.subdirectories = {"creative": False, "reflection": False, "archive": False}
        self.template_files = {
            "spec-template.md": False,
            "plan-template.md": False,
            "tasks-template.md": False,
            "constitution.md": False,
        }

    def initialize(
        self,
        with_constitution: bool = True,
        with_templates: bool = True,
        with_ai_agents: bool = True,
    ) -> MemoryBankStatus:
        """Initialize Memory Bank structure"""
        try:
            # Create main directory
            self.memory_bank_path.mkdir(parents=True, exist_ok=True)

            # Create subdirectories
            for subdir in self.subdirectories.keys():
                subdir_path = self.memory_bank_path / subdir
                subdir_path.mkdir(exist_ok=True)
                self.subdirectories[subdir] = True

            # Create essential files if they don't exist
            self._create_essential_files()

            # Create constitutional file if requested
            if with_constitution:
                self._create_constitutional_file()

            # Create template files if requested
            if with_templates:
                self._create_template_files()

            # Create AI agent configuration if requested
            if with_ai_agents:
                self._create_ai_agent_config()

            return self.get_status()

        except Exception as e:
            return MemoryBankStatus(
                initialized=False,
                memory_bank_path=self.memory_bank_path,
                essential_files=self.essential_files,
                subdirectories=self.subdirectories,
                template_files=self.template_files,
                constitutional_file=False,
                issues=[f"Initialization failed: {str(e)}"],
            )

    def _create_essential_files(self):
        """Create essential Memory Bank files"""
        # Create tasks.md
        tasks_file = self.memory_bank_path / "tasks.md"
        if not tasks_file.exists():
            tasks_file.write_text(self._get_tasks_template())
            self.essential_files["tasks.md"] = True

        # Create activeContext.md
        context_file = self.memory_bank_path / "activeContext.md"
        if not context_file.exists():
            context_file.write_text(self._get_context_template())
            self.essential_files["activeContext.md"] = True

        # Create progress.md
        progress_file = self.memory_bank_path / "progress.md"
        if not progress_file.exists():
            progress_file.write_text(self._get_progress_template())
            self.essential_files["progress.md"] = True

    def _create_constitutional_file(self):
        """Create constitutional file"""
        constitution_file = self.memory_bank_path / "constitution.md"
        if not constitution_file.exists():
            constitution_file.write_text(self._get_constitution_template())
            self.template_files["constitution.md"] = True

    def _create_template_files(self):
        """Create Spec Kit template files"""
        # Create spec-template.md
        spec_template = self.memory_bank_path / "spec-template.md"
        if not spec_template.exists():
            spec_template.write_text(self._get_spec_template())
            self.template_files["spec-template.md"] = True

        # Create plan-template.md
        plan_template = self.memory_bank_path / "plan-template.md"
        if not plan_template.exists():
            plan_template.write_text(self._get_plan_template())
            self.template_files["plan-template.md"] = True

        # Create tasks-template.md
        tasks_template = self.memory_bank_path / "tasks-template.md"
        if not tasks_template.exists():
            tasks_template.write_text(self._get_tasks_template_content())
            self.template_files["tasks-template.md"] = True

    def _create_ai_agent_config(self):
        """Create AI agent configuration"""
        ai_config_file = self.memory_bank_path / "ai-agents.json"
        if not ai_config_file.exists():
            config = {
                "enabled_agents": ["github-copilot"],
                "agent_configs": {
                    "github-copilot": {"enabled": True, "priority": 1},
                    "claude-code": {"enabled": False, "priority": 2},
                    "gemini-cli": {"enabled": False, "priority": 3},
                    "cursor": {"enabled": False, "priority": 4},
                },
            }
            ai_config_file.write_text(json.dumps(config, indent=2))

    def get_status(self) -> MemoryBankStatus:
        """Get current Memory Bank status"""
        issues = []

        # Check if main directory exists
        if not self.memory_bank_path.exists():
            return MemoryBankStatus(
                initialized=False,
                memory_bank_path=self.memory_bank_path,
                essential_files=self.essential_files,
                subdirectories=self.subdirectories,
                template_files=self.template_files,
                constitutional_file=False,
                issues=["Memory Bank directory does not exist"],
            )

        # Check essential files
        for file_name in self.essential_files.keys():
            file_path = self.memory_bank_path / file_name
            exists = file_path.exists()
            self.essential_files[file_name] = exists
            if not exists:
                issues.append(f"Missing essential file: {file_name}")

        # Check subdirectories
        for subdir in self.subdirectories.keys():
            subdir_path = self.memory_bank_path / subdir
            exists = subdir_path.exists() and subdir_path.is_dir()
            self.subdirectories[subdir] = exists
            if not exists:
                issues.append(f"Missing subdirectory: {subdir}")

        # Check template files
        for template_name in self.template_files.keys():
            template_path = self.memory_bank_path / template_name
            exists = template_path.exists()
            self.template_files[template_name] = exists

        # Check constitutional file
        constitution_file = self.memory_bank_path / "constitution.md"
        constitutional_file_exists = constitution_file.exists()

        return MemoryBankStatus(
            initialized=len(issues) == 0,
            memory_bank_path=self.memory_bank_path,
            essential_files=self.essential_files,
            subdirectories=self.subdirectories,
            template_files=self.template_files,
            constitutional_file=constitutional_file_exists,
            issues=issues,
        )

    def _get_tasks_template(self) -> str:
        """Get tasks.md template"""
        return """# Memory Bank Tasks

**Status**: ACTIVE  
**Last Updated**: [DATE]  
**Current Phase**: [PHASE]

## Current Task
- **Task**: [Task Description]
- **Complexity Level**: [1/2/3/4]
- **Status**: [Status]

## Task Queue
- [ ] [Task 1]
- [ ] [Task 2]

## Notes
- [Note 1]
- [Note 2]
"""

    def _get_context_template(self) -> str:
        """Get activeContext.md template"""
        return """# Active Context

**Session**: [Session Name]  
**Date**: [DATE]  
**Current Focus**: [Focus Area]

## Current Context
- **Mode**: [Current Mode]
- **Platform**: [Platform]
- **Location**: [Location]
- **Status**: [Status]

## Recent Decisions
- [Decision 1]
- [Decision 2]

## Next Steps
- [Step 1]
- [Step 2]
"""

    def _get_progress_template(self) -> str:
        """Get progress.md template"""
        return """# Progress Tracking

**Project**: [Project Name]  
**Start Date**: [DATE]  
**Current Phase**: [Current Phase]

## Phase Status
- [ ] [Phase 1]
- [ ] [Phase 2]

## Completed Tasks
1. **[Task 1]**: [Description]
2. **[Task 2]**: [Description]

## Current Task
- **Task**: [Current Task]
- **Status**: [Status]
- **Next**: [Next Step]

## Metrics
- **Files Created**: [Count]
- **Directories Created**: [Count]
- **Time Elapsed**: [Duration]
"""

    def _get_constitution_template(self) -> str:
        """Get constitution.md template"""
        return """# Memory Bank Constitution

**Project**: [Project Name]  
**Version**: 1.0  
**Last Updated**: [DATE]

## Nine Articles of Development

### Article I: Memory-First Principle
[Constitutional principle description]

### Article II: Spec-Driven Development
[Constitutional principle description]

### Article III: Test-First Imperative
[Constitutional principle description]

[Additional articles...]

## Constitutional Validation Process
[Validation process description]
"""

    def _get_spec_template(self) -> str:
        """Get spec-template.md template"""
        return """# Feature Specification Template

**Feature ID**: [FEATURE-XXX]  
**Created**: [DATE]  
**Status**: Draft/Review/Approved  
**Complexity Level**: [1/2/3/4]

## User Story
**As a** [user type]  
**I want** [functionality]  
**So that** [benefit/value]

## Acceptance Criteria
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]

## Requirements
[Requirements section]

## Constitutional Review
[Constitutional compliance check]
"""

    def _get_plan_template(self) -> str:
        """Get plan-template.md template"""
        return """# Implementation Plan Template

**Plan ID**: [PLAN-XXX]  
**Feature**: [FEATURE-XXX]  
**Created**: [DATE]  
**Status**: Draft/Review/Approved  
**Complexity Level**: [1/2/3/4]

## Technical Context
[Technical context section]

## Constitutional Compliance Check
[Constitutional compliance section]

## Implementation Phases
[Implementation phases section]

## Testing Strategy
[Testing strategy section]
"""

    def get_context(self) -> Dict[str, Any]:
        """Get current Memory Bank context"""
        try:
            context_file = self.memory_bank_path / "activeContext.md"
            if context_file.exists():
                # Parse activeContext.md for current context
                with open(context_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract mode information (simple parsing)
                context = {"current_mode": "unknown"}

                if "**Mode**:" in content:
                    lines = content.split("\n")
                    for line in lines:
                        if "**Mode**:" in line:
                            mode_part = line.split("**Mode**:")[1].strip()
                            context["current_mode"] = mode_part.split()[0].lower()
                            break

                return context
            else:
                return {"current_mode": "unknown"}
        except Exception:
            return {"current_mode": "unknown"}

    def update_context(self, context_data: Dict[str, Any]) -> None:
        """Update Memory Bank context"""
        try:
            context_file = self.memory_bank_path / "activeContext.md"

            # Read existing context
            existing_content = ""
            if context_file.exists():
                with open(context_file, "r", encoding="utf-8") as f:
                    existing_content = f.read()

            # Update context information
            updated_content = existing_content

            # Simple context update (could be enhanced)
            if "current_mode" in context_data:
                mode = context_data["current_mode"]
                if "**Mode**:" in updated_content:
                    import re

                    updated_content = re.sub(
                        r"\*\*Mode\*\*:.*", f"**Mode**: {mode.upper()}", updated_content
                    )
                else:
                    updated_content += f"\n**Mode**: {mode.upper()}"

            # Write updated content
            with open(context_file, "w", encoding="utf-8") as f:
                f.write(updated_content)

        except Exception as e:
            print(f"Warning: Failed to update context: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Health check for RAG integration"""
        try:
            status = self.get_status()
            return {
                "status": "healthy" if status.is_healthy() else "unhealthy",
                "memory_bank": status.is_healthy(),
                "issues": status.issues,
                "rag_enabled": True,
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "rag_enabled": False}

    async def integrate_rag_context(self, spec_type: str, code: str) -> str:
        """Integrate RAG context with Spec Kit methodologies"""
        try:
            # Get current context
            context = self.get_context()

            # Create RAG context based on Spec Kit methodology
            rag_context = f"""
Vibecode Spec Kit Context:
- Current Mode: {context.get("current_mode", "unknown")}
- Spec Type: {spec_type}
- Memory Bank Status: {self.get_status().is_healthy()}

Code Context:
{code}

Integration Points:
- Spec-driven development methodology
- Memory-first principle
- Constitutional AI approach
"""

            # Store in memory bank for future reference
            rag_file = self.memory_bank_path / "rag_context.md"
            with open(rag_file, "w", encoding="utf-8") as f:
                f.write(f"# RAG Integration Context\n\n{rag_context}")

            return "Memory Bank integrated with RAG context"

        except Exception as e:
            raise Exception(f"Failed to integrate RAG context: {str(e)}")

    def get_rag_context(self, query: str) -> Optional[str]:
        """Get RAG context for a specific query"""
        try:
            # Read RAG context file
            rag_file = self.memory_bank_path / "rag_context.md"
            if rag_file.exists():
                with open(rag_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Simple query matching (could be enhanced with semantic search)
                if query.lower() in content.lower():
                    return content

            # Fallback to activeContext.md
            context_file = self.memory_bank_path / "activeContext.md"
            if context_file.exists():
                with open(context_file, "r", encoding="utf-8") as f:
                    return f.read()

            return None

        except Exception:
            return None

    def _get_tasks_template_content(self) -> str:
        """Get tasks-template.md template"""
        return """# Task Breakdown Template

**Task ID**: [TASK-XXX]  
**Plan**: [PLAN-XXX]  
**Feature**: [FEATURE-XXX]  
**Created**: [DATE]  
**Status**: Draft/Review/Approved

## Task Overview
**Objective**: [Clear, specific objective]  
**Estimated Effort**: [X hours/days]  
**Priority**: [High/Medium/Low]  
**Complexity**: [Level 1/2/3/4]

## Implementation Steps
[Implementation steps section]

## Definition of Done
[Definition of done section]

## Testing Strategy
[Testing strategy section]
"""

    def get_context(self) -> Dict[str, Any]:
        """Get current Memory Bank context"""
        try:
            context_file = self.memory_bank_path / "activeContext.md"
            if context_file.exists():
                # Parse activeContext.md for current context
                with open(context_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract mode information (simple parsing)
                context = {"current_mode": "unknown"}

                if "**Mode**:" in content:
                    lines = content.split("\n")
                    for line in lines:
                        if "**Mode**:" in line:
                            mode_part = line.split("**Mode**:")[1].strip()
                            context["current_mode"] = mode_part.split()[0].lower()
                            break

                return context
            else:
                return {"current_mode": "unknown"}
        except Exception:
            return {"current_mode": "unknown"}

    def update_context(self, context_data: Dict[str, Any]) -> None:
        """Update Memory Bank context"""
        try:
            context_file = self.memory_bank_path / "activeContext.md"

            # Read existing context
            existing_content = ""
            if context_file.exists():
                with open(context_file, "r", encoding="utf-8") as f:
                    existing_content = f.read()

            # Update context information
            updated_content = existing_content

            # Simple context update (could be enhanced)
            if "current_mode" in context_data:
                mode = context_data["current_mode"]
                if "**Mode**:" in updated_content:
                    import re

                    updated_content = re.sub(
                        r"\*\*Mode\*\*:.*", f"**Mode**: {mode.upper()}", updated_content
                    )
                else:
                    updated_content += f"\n**Mode**: {mode.upper()}"

            # Write updated content
            with open(context_file, "w", encoding="utf-8") as f:
                f.write(updated_content)

        except Exception as e:
            print(f"Warning: Failed to update context: {e}")
