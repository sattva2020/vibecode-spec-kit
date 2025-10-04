#!/usr/bin/env python3
"""Build an importable Cursor custom modes manifest for the Memory Bank system.

This script collects the Markdown instruction files that live in ``custom_modes``
and emits a single JSON manifest that Cursor can import through *Settings → Features →
Chat → Custom modes → Import from file*.

Usage
-----
    python scripts/build_cursor_modes.py [--out custom_modes/memory_bank_modes.json]

The resulting file is encoded as UTF-8 and keeps the Markdown formatting untouched.
"""
from __future__ import annotations

import argparse
import json
import uuid
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CUSTOM_MODES_DIR = REPO_ROOT / "custom_modes"


@dataclass(frozen=True)
class ModeConfig:
    name: str
    slug: str
    description: str
    tools: list[str]
    shortcut: str | None
    instruction_file: str
    trigger_words: list[str]
    icon: str

    def build_payload(self) -> dict:
        instruction_path = CUSTOM_MODES_DIR / self.instruction_file
        if not instruction_path.exists():
            raise FileNotFoundError(f"Missing instruction file: {instruction_path}")

        instructions = instruction_path.read_text(encoding="utf-8").strip()
        mode_id = uuid.uuid5(uuid.UUID("38a3b9ec-a222-46fb-9b4b-b6872d7f084f"), self.slug)

        payload = {
            "id": str(mode_id),
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "instructions": instructions,
            "tools": self.tools,
            "triggerWords": self.trigger_words,
            "defaultModel": "claude-3.5-sonnet",
            "icon": self.icon,
        }

        if self.shortcut:
            payload["shortcut"] = self.shortcut

        return payload


MODES: list[ModeConfig] = [
    ModeConfig(
        name="🔍 VAN",
        slug="van",
        description="Initialization, repo inspection, and complexity assessment.",
        tools=["codebaseSearch", "readFile", "terminal", "listDirectory", "fetchRules"],
        shortcut="ctrl+shift+1",
        instruction_file="van_instructions.md",
        trigger_words=["VAN"],
        icon="search",
    ),
    ModeConfig(
        name="📋 PLAN",
        slug="plan",
        description="Structured implementation planning for multi-step tasks.",
        tools=["codebaseSearch", "readFile", "terminal", "listDirectory"],
        shortcut="ctrl+shift+2",
        instruction_file="plan_instructions.md",
        trigger_words=["PLAN"],
        icon="checklist",
    ),
    ModeConfig(
        name="🎨 CREATIVE",
        slug="creative",
        description="Design exploration and option analysis for complex components.",
        tools=[
            "codebaseSearch",
            "readFile",
            "terminal",
            "listDirectory",
            "editFile",
            "fetchRules",
        ],
        shortcut="ctrl+shift+3",
        instruction_file="creative_instructions.md",
        trigger_words=["CREATIVE"],
        icon="sparkle",
    ),
    ModeConfig(
        name="⚒️ IMPLEMENT",
        slug="implement",
        description="Step-by-step implementation of the approved plan.",
        tools=[
            "codebaseSearch",
            "readFile",
            "terminal",
            "listDirectory",
            "editFile",
            "fetchRules",
        ],
        shortcut="ctrl+shift+4",
        instruction_file="implement_instructions.md",
        trigger_words=["IMPLEMENT"],
        icon="hammer",
    ),
    ModeConfig(
        name="🧭 REFLECT / ARCHIVE",
        slug="reflect-archive",
        description="Retrospective review, QA validation, and documentation hand-off.",
        tools=["codebaseSearch", "readFile", "terminal", "listDirectory"],
        shortcut="ctrl+shift+5",
        instruction_file="reflect_archive_instructions.md",
        trigger_words=["REFLECT", "ARCHIVE"],
        icon="compass",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default=str(CUSTOM_MODES_DIR / "memory_bank_modes.json"),
        help="Destination path for the generated manifest (default: %(default)s)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output with indentation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = {
        "version": 1,
        "modes": [mode.build_payload() for mode in MODES],
        "metadata": {
            "generatedBy": "scripts/build_cursor_modes.py",
            "source": "memory-bank",
        },
    }

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.pretty:
        text = json.dumps(payload, ensure_ascii=False, indent=2)
    else:
        text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    output_path.write_text(text + "\n", encoding="utf-8")
    print(f"Wrote {output_path.relative_to(REPO_ROOT)} ({len(text)} bytes)")


if __name__ == "__main__":
    main()
