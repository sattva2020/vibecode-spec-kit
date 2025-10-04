#!/usr/bin/env python3
"""Install VS Code Memory Bank assets into a target project."""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COPY_MAP = [
    ("Chat modes", Path(".github/chatmodes"), Path(".github/chatmodes")),
    ("Isolation rules", Path(".vscode/rules"), Path(".vscode/rules")),
    ("Templates", Path(".vscode/templates"), Path(".vscode/templates")),
    ("Automation scripts", Path(".vscode/memory-bank/scripts"), Path(".vscode/memory-bank/scripts")),
]
WORKING_DIRS = [
    Path(".vscode/memory-bank"),
    Path(".vscode/memory-bank/archive"),
    Path(".vscode/memory-bank/auto"),
    Path(".vscode/memory-bank/creative"),
    Path(".vscode/memory-bank/plan"),
    Path(".vscode/memory-bank/reflection"),
    Path(".vscode/memory-bank/tests"),
    Path(".vscode/memory-bank/van"),
]
TEMPLATES = ["activeContext.md", "progress.md", "projectbrief.md", "tasks.md"]


def log(prefix: str, message: str) -> None:
    print(f"[{prefix}] {message}")


def ensure_target(target: Path, dry_run: bool) -> Path:
    if target.exists():
        return target.resolve()
    if dry_run:
        log("EXEC", f"Would create target directory {target}")
        return target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    return target.resolve()


def copy_tree(name: str, source_rel: Path, dest_rel: Path, *, target: Path, dry_run: bool, force: bool) -> None:
    source = REPO_ROOT / source_rel
    dest = target / dest_rel
    if not source.exists():
        raise FileNotFoundError(f"Source path not found: {source}")

    if dry_run:
        log("EXEC", f"Would copy {source_rel} -> {dest_rel}")
        return

    if dest.exists():
        if force:
            shutil.rmtree(dest)
        else:
            log("SKIP", f"{dest_rel} already exists (use --force to overwrite)")
            return

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest, dirs_exist_ok=True)
    log("EXEC", f"Copied {name}: {source_rel} -> {dest_rel}")


def ensure_dirs(target: Path, dry_run: bool) -> None:
    for rel in WORKING_DIRS:
        path = target / rel
        if dry_run:
            log("EXEC", f"Would create directory {rel}")
            continue
        path.mkdir(parents=True, exist_ok=True)
        log("EXEC", f"Ensured directory {rel}")


def seed_templates(target: Path, dry_run: bool, force: bool) -> None:
    for name in TEMPLATES:
        source = REPO_ROOT / ".vscode/templates/memory_bank" / name
        dest = target / ".vscode/memory-bank" / name
        if not source.exists():
            raise FileNotFoundError(f"Template not found: {source}")

        if dry_run:
            log("EXEC", f"Would seed {name}")
            continue

        if dest.exists() and not force:
            log("SKIP", f"{name} already exists (use --force to overwrite)")
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        log("EXEC", f"Seeded {name}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=os.getcwd(), help="Destination project directory")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without modifying the file system")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    target = ensure_target(Path(args.target), dry_run=args.dry_run)

    log("INFO", f"Repository root: {REPO_ROOT}")
    log("INFO", f"Target project:  {target}")
    if args.dry_run:
        log("INFO", "Dry-run mode enabled")
    if args.force:
        log("INFO", "Force overwrite enabled")

    for name, source_rel, dest_rel in COPY_MAP:
        copy_tree(name, source_rel, dest_rel, target=target, dry_run=args.dry_run, force=args.force)

    ensure_dirs(target, dry_run=args.dry_run)
    seed_templates(target, dry_run=args.dry_run, force=args.force)

    if not args.dry_run:
        log("INFO", "Memory Bank assets installed successfully.")
        log("INFO", "Next steps: restart VS Code and trigger VAN mode.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
