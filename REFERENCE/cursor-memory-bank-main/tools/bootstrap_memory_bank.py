#!/usr/bin/env python3
"""Bootstrap Memory Bank working files from templates."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "memory_bank"
TEMPLATE_FILES = [
    "tasks.md",
    "progress.md",
    "activeContext.md",
    "projectbrief.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy Memory Bank templates into a project directory."
    )
    parser.add_argument(
        "--dest",
        required=True,
        help="Destination directory where Memory Bank files should be created.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files if they are already present.",
    )
    return parser.parse_args()


def ensure_template_dir_exists() -> None:
    if not TEMPLATE_DIR.exists():
        sys.stderr.write(
            f"Template directory not found at {TEMPLATE_DIR}. Did you move the project files?\n"
        )
        raise SystemExit(1)


def copy_templates(destination: Path, force: bool) -> None:
    created = []
    skipped = []
    overwritten = []

    for filename in TEMPLATE_FILES:
        source = TEMPLATE_DIR / filename
        if not source.exists():
            sys.stderr.write(f"Missing template: {source}\n")
            raise SystemExit(1)

        target = destination / filename
        existed_before_copy = target.exists()

        if existed_before_copy and not force:
            skipped.append(target)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if existed_before_copy:
            overwritten.append(target)
        else:
            created.append(target)

    for path in created:
        print(f"Created {path}")
    for path in overwritten:
        print(f"Overwrote {path}")
    for path in skipped:
        print(f"Skipped {path} (already exists)")

    summary_parts = []
    if created:
        summary_parts.append(f"created {len(created)}")
    if overwritten:
        summary_parts.append(f"overwrote {len(overwritten)}")
    if skipped:
        summary_parts.append(f"skipped {len(skipped)} existing")

    if summary_parts:
        print("Summary: " + ", ".join(summary_parts))
    else:
        print("No files processed.")


def main() -> None:
    args = parse_args()
    ensure_template_dir_exists()

    destination = Path(args.dest).expanduser()
    if destination.exists() and not destination.is_dir():
        sys.stderr.write(
            f"Destination '{destination}' exists and is not a directory. Aborting.\n"
        )
        raise SystemExit(1)

    destination.mkdir(parents=True, exist_ok=True)
    copy_templates(destination, force=args.force)


if __name__ == "__main__":
    main()
