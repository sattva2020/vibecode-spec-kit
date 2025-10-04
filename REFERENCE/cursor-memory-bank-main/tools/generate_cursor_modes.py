#!/usr/bin/env python3
"""Generate Cursor custom modes configuration.

Reads Markdown instruction files from ``custom_modes/`` and produces a
JSON (or zipped JSON) bundle that Cursor can import through its
"Import custom modes" UI.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import zipfile
from datetime import datetime, timezone

# Cursor's built-in tool identifiers. These strings match the internal
# identifiers that Cursor uses when exporting custom modes. They are the
# camelCase version of the tool labels that appear in the UI.
CURSOR_TOOL_IDS = {
    "codebase_search": "codebaseSearch",
    "read_file": "readFile",
    "list_directory": "listDirectory",
    "terminal": "terminal",
    "edit_file": "editFile",
    "fetch_rules": "fetchRules",
}

# Static metadata for each Memory Bank mode.
MODE_SPECS = [
    {
        "slug": "van",
        "name": "🔍 VAN",
        "description": "Initialization",
        "tools": [
            CURSOR_TOOL_IDS["codebase_search"],
            CURSOR_TOOL_IDS["read_file"],
            CURSOR_TOOL_IDS["terminal"],
            CURSOR_TOOL_IDS["list_directory"],
            CURSOR_TOOL_IDS["fetch_rules"],
        ],
        "icon": "Sparkle",
    },
    {
        "slug": "plan",
        "name": "📋 PLAN",
        "description": "Task Planning",
        "tools": [
            CURSOR_TOOL_IDS["codebase_search"],
            CURSOR_TOOL_IDS["read_file"],
            CURSOR_TOOL_IDS["terminal"],
            CURSOR_TOOL_IDS["list_directory"],
        ],
        "icon": "ClipboardDocumentCheck",
    },
    {
        "slug": "creative",
        "name": "🎨 CREATIVE",
        "description": "Design Decisions",
        "tools": [
            CURSOR_TOOL_IDS["codebase_search"],
            CURSOR_TOOL_IDS["read_file"],
            CURSOR_TOOL_IDS["terminal"],
            CURSOR_TOOL_IDS["list_directory"],
            CURSOR_TOOL_IDS["edit_file"],
            CURSOR_TOOL_IDS["fetch_rules"],
        ],
        "icon": "Sparkle",
    },
    {
        "slug": "implement",
        "name": "⚒️ IMPLEMENT",
        "description": "Implementation",
        "tools": list(CURSOR_TOOL_IDS.values()),
        "icon": "Cog6Tooth",
    },
    {
        "slug": "reflect_archive",
        "name": "🔍 REFLECT / ARCHIVE",
        "description": "Review & Archival",
        "tools": [
            CURSOR_TOOL_IDS["codebase_search"],
            CURSOR_TOOL_IDS["read_file"],
            CURSOR_TOOL_IDS["terminal"],
            CURSOR_TOOL_IDS["list_directory"],
        ],
        "icon": "Sparkle",
    },
]

DEFAULT_EXPORT_FILENAME = "cursor_modes.json"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the JSON or ZIP file that should be written.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Write indented JSON (useful for version control).",
    )
    return parser.parse_args(argv)


def load_mode_content(root: Path) -> dict:
    modes = []
    for spec in MODE_SPECS:
        md_path = root / "custom_modes" / f"{spec['slug']}_instructions.md"
        if not md_path.exists():
            raise FileNotFoundError(f"Missing instructions file: {md_path}")
        content = md_path.read_text(encoding="utf-8")
        modes.append(
            {
                "name": spec["name"],
                "description": spec["description"],
                "icon": spec["icon"],
                "tools": spec["tools"],
                "instructions": content,
                "sourcePath": str(md_path.relative_to(root)),
            }
        )
    return {
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "modes": modes,
    }


def write_output(data: dict, output_path: Path, pretty: bool = False) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    json_bytes = json.dumps(
        data,
        ensure_ascii=False,
        indent=2 if pretty else None,
    ).encode("utf-8")

    if output_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(DEFAULT_EXPORT_FILENAME, json_bytes)
    else:
        output_path.write_bytes(json_bytes)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    try:
        data = load_mode_content(root)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    output_path = Path(args.output)
    write_output(data, output_path, pretty=args.pretty)
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
