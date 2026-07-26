#!/usr/bin/env python3
"""Create a safe, self-contained Quaestio Socratica course workspace."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path


TEXT_SUFFIXES = {".md", ".csv", ".mdc"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize a portable Quaestio Socratica course folder."
    )
    parser.add_argument("destination", type=Path)
    parser.add_argument(
        "--mode",
        choices=("teacher", "self", "undecided"),
        default="undecided",
        help="Optional. Leave undecided to confirm the mode in the first dialogue.",
    )
    parser.add_argument("--title", required=True)
    return parser.parse_args()


def ensure_safe_destination(destination: Path) -> None:
    if destination.is_symlink():
        raise ValueError(f"Refusing symlink destination: {destination}")
    if destination.exists() and not destination.is_dir():
        raise ValueError(f"Destination is not a directory: {destination}")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(
            f"Destination is not empty; no files were changed: {destination}"
        )


def substitute_tokens(root: Path, *, title: str, mode: str) -> None:
    replacements = {
        "{{COURSE_TITLE}}": title,
        "{{INITIALIZATION_MODE}}": mode,
        "{{CREATED_ON}}": date.today().isoformat(),
    }
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for token, value in replacements.items():
            text = text.replace(token, value)
        path.write_text(text, encoding="utf-8")


def embed_runtime_skill(skill_dir: Path, workspace: Path) -> None:
    target = workspace / ".agents" / "skills" / "quaestio-socratica"
    (target / "agents").mkdir(parents=True)
    (target / "references").mkdir()
    (target / "scripts").mkdir()

    shutil.copy2(skill_dir / "SKILL.md", target / "SKILL.md")
    shutil.copy2(
        skill_dir / "agents" / "openai.yaml", target / "agents" / "openai.yaml"
    )
    for reference in sorted((skill_dir / "references").glob("*.md")):
        shutil.copy2(reference, target / "references" / reference.name)
    for script_name in ("build_mindmap.py", "validate_course.py"):
        shutil.copy2(
            skill_dir / "scripts" / script_name, target / "scripts" / script_name
        )


def initialize(destination: Path, *, mode: str, title: str) -> Path:
    title = title.strip()
    if not title:
        raise ValueError("Course title cannot be blank")

    destination = destination.expanduser().resolve()
    ensure_safe_destination(destination)

    skill_dir = Path(__file__).resolve().parents[1]
    template = skill_dir / "assets" / "course-template"
    if not template.is_dir():
        raise RuntimeError(f"Bundled course template is missing: {template}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    staging_parent = Path(
        tempfile.mkdtemp(prefix=".quaestio-init-", dir=destination.parent)
    )
    staging = staging_parent / destination.name
    try:
        shutil.copytree(template, staging)
        substitute_tokens(staging, title=title, mode=mode)
        embed_runtime_skill(skill_dir, staging)

        if destination.exists():
            destination.rmdir()  # Proven empty by ensure_safe_destination.
        staging.replace(destination)
    finally:
        shutil.rmtree(staging_parent, ignore_errors=True)

    return destination


def main() -> int:
    args = parse_args()
    try:
        destination = initialize(
            args.destination, mode=args.mode, title=args.title
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Created {args.mode} course workspace: {destination}")
    print("Next: open START-HERE.md and compile the course for explicit approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
