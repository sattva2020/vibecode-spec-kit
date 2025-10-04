#!/usr/bin/env python3
"""
Memory Bank CLI - Main CLI Entry Point
Workflow-aligned CLI with constitutional validation and Spec Kit integration
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Any

from .commands import (
    init_command,
    check_command,
    status_command,
    van_command,
    plan_command,
    creative_command,
    implement_command,
    reflect_command,
    archive_command,
    sync_command,
    qa_command,
)
from .commands import (
    spec_command,
    ai_command,
    constitution_command,
    research_command,
    transition_command,
    testing_command,
    rag_command,
)
from .core.config import CLIConfig
from .utils.output import OutputFormatter


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser"""
    parser = argparse.ArgumentParser(
        description="Memory Bank CLI - VS Code Memory Bank with Spec Kit integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  memory-bank init --constitution --templates
  memory-bank van --constitutional
  memory-bank spec generate --feature-name "user-auth" --level 3
  memory-bank constitution validate --mode plan
        """,
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    parser.add_argument("--config", type=str, help="Path to configuration file")

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase verbosity (use multiple times for more detail)",
    )

    parser.add_argument(
        "--format",
        choices=["text", "json", "yaml"],
        default="text",
        help="Output format (default: text)",
    )

    # Create subcommands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    # Add command parsers
    _add_workflow_commands(subparsers)
    _add_template_commands(subparsers)
    _add_ai_commands(subparsers)
    _add_constitution_commands(subparsers)
    _add_research_commands(subparsers)
    _add_transition_commands(subparsers)
    _add_testing_commands(subparsers)
    _add_rag_commands(subparsers)

    return parser


def _add_workflow_commands(subparsers):
    """Add workflow-related commands"""

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize Memory Bank structure")
    init_parser.add_argument(
        "--constitution", action="store_true", help="Enable constitutional gates"
    )
    init_parser.add_argument(
        "--templates", action="store_true", help="Install Spec Kit templates"
    )
    init_parser.add_argument(
        "--ai-agents", action="store_true", help="Configure multi-AI agent support"
    )

    # Check command
    check_parser = subparsers.add_parser("check", help="Check Memory Bank status")
    check_parser.add_argument(
        "--constitutional", action="store_true", help="Check constitutional compliance"
    )
    check_parser.add_argument(
        "--templates", action="store_true", help="Validate templates"
    )
    check_parser.add_argument(
        "--ai-agents", action="store_true", help="Check AI agent configuration"
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Show Memory Bank status")
    status_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed status"
    )
    status_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )

    # Workflow commands
    van_parser = subparsers.add_parser("van", help="VAN mode operations")
    van_parser.add_argument(
        "--constitutional", action="store_true", help="Enable constitutional validation"
    )
    van_parser.add_argument(
        "--complexity-level",
        type=int,
        choices=[1, 2, 3, 4],
        help="Set complexity level",
    )

    plan_parser = subparsers.add_parser("plan", help="PLAN mode operations")
    plan_parser.add_argument(
        "--spec", action="store_true", help="Use Spec-Driven approach"
    )
    plan_parser.add_argument(
        "--constitutional", action="store_true", help="Enable constitutional validation"
    )
    plan_parser.add_argument(
        "--research", action="store_true", help="Enable research integration"
    )

    creative_parser = subparsers.add_parser("creative", help="CREATIVE mode operations")
    creative_parser.add_argument(
        "--research", action="store_true", help="Enable research integration"
    )
    creative_parser.add_argument(
        "--templates", action="store_true", help="Use Spec Kit templates"
    )

    implement_parser = subparsers.add_parser(
        "implement", help="IMPLEMENT mode operations"
    )
    implement_parser.add_argument(
        "--test-first", action="store_true", help="Use Test-First approach"
    )
    implement_parser.add_argument(
        "--contract-tests", action="store_true", help="Enable contract testing"
    )

    reflect_parser = subparsers.add_parser("reflect", help="REFLECT mode operations")
    reflect_parser.add_argument(
        "--learning", action="store_true", help="Capture learning insights"
    )
    reflect_parser.add_argument(
        "--documentation", action="store_true", help="Update documentation"
    )

    archive_parser = subparsers.add_parser("archive", help="ARCHIVE mode operations")
    archive_parser.add_argument(
        "--spec-docs", action="store_true", help="Archive Spec Kit documentation"
    )
    archive_parser.add_argument(
        "--constitutional", action="store_true", help="Archive constitutional decisions"
    )

    sync_parser = subparsers.add_parser("sync", help="SYNC mode operations")
    sync_parser.add_argument(
        "--multi-ai", action="store_true", help="Sync with multiple AI agents"
    )
    sync_parser.add_argument(
        "--documentation", action="store_true", help="Update documentation"
    )

    qa_parser = subparsers.add_parser("qa", help="QA mode operations")
    qa_parser.add_argument(
        "--contract-tests", action="store_true", help="Run contract tests"
    )
    qa_parser.add_argument(
        "--constitutional",
        action="store_true",
        help="Validate constitutional compliance",
    )


def _add_template_commands(subparsers):
    """Add template-related commands"""

    spec_parser = subparsers.add_parser(
        "spec", help="Specification template operations"
    )
    spec_subparsers = spec_parser.add_subparsers(dest="spec_action", required=True)

    spec_generate = spec_subparsers.add_parser(
        "generate", help="Generate specification template"
    )
    spec_generate.add_argument(
        "--feature-name", required=True, help="Name of the feature"
    )
    spec_generate.add_argument(
        "--level",
        type=int,
        choices=[1, 2, 3, 4],
        help="Complexity level (auto-detected if not provided)",
    )
    spec_generate.add_argument(
        "--description", help="Feature description for complexity detection"
    )
    spec_generate.add_argument("--requirements", help="Initial requirements")
    spec_generate.add_argument(
        "--priority", choices=["low", "medium", "high", "urgent"], help="Priority level"
    )

    spec_validate = spec_subparsers.add_parser(
        "validate", help="Validate existing specification"
    )
    spec_validate.add_argument(
        "--feature-name", required=True, help="Name of the feature to validate"
    )
    spec_validate.add_argument(
        "--level", type=int, choices=[1, 2, 3, 4], help="Complexity level"
    )

    spec_preview = spec_subparsers.add_parser(
        "preview", help="Preview specification template"
    )
    spec_preview.add_argument(
        "--level",
        type=int,
        choices=[1, 2, 3, 4],
        default=1,
        help="Complexity level to preview",
    )


def _add_ai_commands(subparsers):
    """Add AI agent commands"""

    ai_parser = subparsers.add_parser("ai", help="AI agent operations")
    ai_subparsers = ai_parser.add_subparsers(dest="ai_action", required=True)

    ai_list = ai_subparsers.add_parser("list", help="List available AI agents")
    ai_config = ai_subparsers.add_parser("config", help="Configure AI agents")
    ai_config.add_argument("agent_name", help="Name of the AI agent")
    ai_config.add_argument("--enable", action="store_true", help="Enable the agent")
    ai_config.add_argument("--disable", action="store_true", help="Disable the agent")

    ai_test = ai_subparsers.add_parser("test", help="Test AI agent integration")
    ai_test.add_argument("agent_name", help="Name of the AI agent to test")


def _add_constitution_commands(subparsers):
    """Add constitutional commands"""

    constitution_parser = subparsers.add_parser(
        "constitution", help="Constitutional operations"
    )
    constitution_subparsers = constitution_parser.add_subparsers(
        dest="constitution_action", required=True
    )

    constitution_validate = constitution_subparsers.add_parser(
        "validate", help="Validate constitutional compliance"
    )
    constitution_validate.add_argument("--mode", help="Specific mode to validate")
    constitution_validate.add_argument(
        "--strict", action="store_true", help="Use strict validation"
    )

    constitution_status = constitution_subparsers.add_parser(
        "status", help="Show constitutional status"
    )
    constitution_update = constitution_subparsers.add_parser(
        "update", help="Update constitutional principles"
    )
    constitution_update.add_argument("--article", help="Specific article to update")


def _add_research_commands(subparsers):
    """Add research commands"""

    research_parser = subparsers.add_parser(
        "research", help="Research integration operations"
    )
    research_subparsers = research_parser.add_subparsers(
        dest="research_action", required=True
    )

    research_generate = research_subparsers.add_parser(
        "generate", help="Generate research template"
    )
    research_generate.add_argument(
        "--type",
        choices=["tech", "methodology", "competitive"],
        default="tech",
        help="Research type",
    )
    research_generate.add_argument("--topic", required=True, help="Research topic")
    research_generate.add_argument(
        "--depth",
        choices=["shallow", "medium", "deep"],
        default="medium",
        help="Research depth",
    )

    research_execute = research_subparsers.add_parser(
        "execute", help="Execute research pipeline"
    )
    research_execute.add_argument("--topic", required=True, help="Research topic")
    research_execute.add_argument(
        "--type",
        choices=["tech", "methodology", "competitive"],
        default="tech",
        help="Research type",
    )
    research_execute.add_argument(
        "--cache", action="store_true", help="Use cached results if available"
    )

    research_validate = research_subparsers.add_parser(
        "validate", help="Validate research results"
    )
    research_validate.add_argument(
        "--topic", required=True, help="Research topic to validate"
    )
    research_validate.add_argument(
        "--strict", action="store_true", help="Use strict validation"
    )

    research_cache = research_subparsers.add_parser(
        "cache", help="Cache management operations"
    )
    research_cache_subparsers = research_cache.add_subparsers(
        dest="cache_action", required=True
    )

    research_cache_list = research_cache_subparsers.add_parser(
        "list", help="List cached research"
    )
    research_cache_clear = research_cache_subparsers.add_parser(
        "clear", help="Clear research cache"
    )
    research_cache_clear.add_argument("--topic", help="Clear specific topic cache")


def _add_transition_commands(subparsers):
    """Add transition management commands"""

    transition_parser = subparsers.add_parser(
        "transition", help="Mode transition management"
    )
    transition_subparsers = transition_parser.add_subparsers(
        dest="transition_action", required=True
    )

    transition_check = transition_subparsers.add_parser(
        "check", help="Check if transition is possible"
    )
    transition_check.add_argument(
        "--from", dest="from_mode", required=True, help="Source mode"
    )
    transition_check.add_argument(
        "--to", dest="to_mode", required=True, help="Target mode"
    )

    transition_requirements = transition_subparsers.add_parser(
        "requirements", help="Show transition requirements"
    )
    transition_requirements.add_argument(
        "--from", dest="from_mode", required=True, help="Source mode"
    )
    transition_requirements.add_argument(
        "--to", dest="to_mode", required=True, help="Target mode"
    )

    transition_execute = transition_subparsers.add_parser(
        "execute", help="Execute mode transition"
    )
    transition_execute.add_argument(
        "--from", dest="from_mode", required=True, help="Source mode"
    )
    transition_execute.add_argument(
        "--to", dest="to_mode", required=True, help="Target mode"
    )

    transition_list = transition_subparsers.add_parser(
        "list", help="List available transitions"
    )


def _add_testing_commands(subparsers):
    """Add testing commands"""

    testing_parser = subparsers.add_parser("testing", help="Testing and QA operations")
    testing_subparsers = testing_parser.add_subparsers(
        dest="testing_action", required=True
    )

    # Test execution
    testing_run = testing_subparsers.add_parser("run", help="Run test suite")
    testing_run.add_argument(
        "--report", action="store_true", help="Generate test report"
    )

    # TDD commands
    testing_tdd = testing_subparsers.add_parser("tdd", help="TDD cycle management")
    tdd_subparsers = testing_tdd.add_subparsers(dest="tdd_action", required=True)

    tdd_start = tdd_subparsers.add_parser("start", help="Start new TDD cycle")
    tdd_start.add_argument("--feature-name", help="Feature name for TDD cycle")
    tdd_start.add_argument("--spec-file", help="Specification file path")

    tdd_red = tdd_subparsers.add_parser("red", help="Run RED phase")
    tdd_green = tdd_subparsers.add_parser("green", help="Run GREEN phase")
    tdd_refactor = tdd_subparsers.add_parser("refactor", help="Run REFACTOR phase")

    tdd_complete = tdd_subparsers.add_parser("complete", help="Complete TDD cycle")
    tdd_complete.add_argument("--feature-name", help="Feature name to complete")
    tdd_complete.add_argument(
        "--report", action="store_true", help="Generate TDD report"
    )

    # Contract testing
    testing_contract = testing_subparsers.add_parser(
        "contract", help="Contract testing"
    )
    contract_subparsers = testing_contract.add_subparsers(
        dest="contract_action", required=True
    )

    contract_load = contract_subparsers.add_parser(
        "load", help="Load contract from file"
    )
    contract_load.add_argument("contract_file", help="Contract file path")

    contract_test = contract_subparsers.add_parser(
        "test", help="Test specific contract"
    )
    contract_test_all = contract_subparsers.add_parser(
        "test-all", help="Test all contracts"
    )

    # QA assessment
    testing_qa = testing_subparsers.add_parser(
        "qa", help="Quality assurance assessment"
    )
    testing_qa.add_argument(
        "--quality-level",
        choices=["basic", "standard", "high", "enterprise"],
        default="standard",
        help="Quality level for assessment",
    )
    testing_qa.add_argument("--report", action="store_true", help="Generate QA report")

    # Test generation
    testing_generate = testing_subparsers.add_parser(
        "generate", help="Generate tests from specification"
    )
    testing_generate.add_argument("spec_file", help="Specification file path")
    testing_generate.add_argument(
        "--feature-name", help="Feature name for generated tests"
    )
    testing_generate.add_argument(
        "--test-type",
        choices=["unit", "integration", "contract", "api"],
        default="unit",
        help="Type of tests to generate",
    )


def _add_rag_commands(subparsers):
    """Add RAG-related commands"""

    # RAG command
    rag_parser = subparsers.add_parser("rag", help="RAG system operations")
    rag_subparsers = rag_parser.add_subparsers(
        dest="rag_action", help="RAG actions", required=True
    )

    # RAG status
    rag_status = rag_subparsers.add_parser("status", help="Show RAG system status")

    # RAG suggest
    rag_suggest = rag_subparsers.add_parser("suggest", help="Get AI code suggestions")
    rag_suggest.add_argument("--file-path", default="unknown", help="File path")
    rag_suggest.add_argument("--code", default="", help="Code to analyze")
    rag_suggest.add_argument("--language", default="text", help="Programming language")

    # RAG learn
    rag_learn = rag_subparsers.add_parser("learn", help="Learn from code")
    rag_learn.add_argument("--file-path", default="unknown", help="File path")
    rag_learn.add_argument("--code", default="", help="Code to learn from")
    rag_learn.add_argument("--language", default="text", help="Programming language")
    rag_learn.add_argument("--spec-type", default="general", help="Spec Kit type")

    # RAG search
    rag_search = rag_subparsers.add_parser("search", help="Search code context")
    rag_search.add_argument("query", help="Search query")

    # RAG integrate
    rag_integrate = rag_subparsers.add_parser(
        "integrate", help="Integrate with Spec Kit"
    )
    rag_integrate.add_argument("--spec-type", default="general", help="Spec Kit type")
    rag_integrate.add_argument("--code", default="", help="Code to integrate")

    # RAG health
    rag_health = rag_subparsers.add_parser("health", help="Comprehensive health check")

    # RAG setup workflows
    rag_setup_workflows = rag_subparsers.add_parser(
        "setup-workflows", help="Setup n8n workflows for RAG"
    )
    rag_setup_workflows.add_argument(
        "--project-path", default=".", help="Project path for workflow setup"
    )

    # RAG list workflows
    rag_list_workflows = rag_subparsers.add_parser(
        "list-workflows", help="List existing n8n workflows"
    )


def load_config(config_path: str = None) -> CLIConfig:
    """Load CLI configuration"""
    if config_path and Path(config_path).exists():
        return CLIConfig.from_file(config_path)
    else:
        return CLIConfig.default()


def execute_command(args: argparse.Namespace, config: CLIConfig) -> int:
    """Execute the specified command"""
    formatter = OutputFormatter(args.format, args.verbose)

    try:
        if args.command == "init":
            return init_command.execute(args, config, formatter)
        elif args.command == "check":
            return check_command.execute(args, config, formatter)
        elif args.command == "status":
            return status_command.execute(args, config, formatter)
        elif args.command == "van":
            return van_command.execute(args, config, formatter)
        elif args.command == "plan":
            return plan_command.execute(args, config, formatter)
        elif args.command == "creative":
            return creative_command.execute(args, config, formatter)
        elif args.command == "implement":
            return implement_command.execute(args, config, formatter)
        elif args.command == "reflect":
            return reflect_command.execute(args, config, formatter)
        elif args.command == "archive":
            return archive_command.execute(args, config, formatter)
        elif args.command == "sync":
            return sync_command.execute(args, config, formatter)
        elif args.command == "qa":
            return qa_command.execute(args, config, formatter)
        elif args.command == "spec":
            return spec_command.execute(args, config, formatter)
        elif args.command == "ai":
            return ai_command.execute(args, config, formatter)
        elif args.command == "constitution":
            return constitution_command.execute(args, config, formatter)
        elif args.command == "research":
            return research_command.execute(args, config, formatter)
        elif args.command == "transition":
            return transition_command.execute(args, config, formatter)
        elif args.command == "testing":
            return testing_command.execute(args, config, formatter)
        elif args.command == "rag":
            import asyncio

            return asyncio.run(rag_command.execute(args))
        else:
            formatter.error(f"Unknown command: {args.command}")
            return 1

    except Exception as e:
        formatter.error(f"Command failed: {str(e)}")
        if args.verbose > 0:
            formatter.debug(f"Exception details: {e}", exc_info=True)
        return 1


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Execute command
    exit_code = execute_command(args, config)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
