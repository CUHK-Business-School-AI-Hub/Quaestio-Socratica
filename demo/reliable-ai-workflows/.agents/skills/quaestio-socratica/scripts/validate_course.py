#!/usr/bin/env python3
"""Validate a Quaestio Socratica workspace by lifecycle phase."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


SOURCE_HEADER = [
    "source_id",
    "title",
    "kind",
    "location",
    "provenance",
    "authority",
    "time_sensitive",
    "retrieved_on",
    "used_for",
    "notes",
]
KNOWLEDGE_HEADER = [
    "node_id",
    "title",
    "parent_ids",
    "checkpoint_id",
    "core",
    "estimated_minutes",
    "learning_outcome",
    "evidence",
    "source_ids",
]
PROGRESS_HEADER = [
    "checkpoint_id",
    "node_id",
    "status",
    "confidence_basis",
    "started_on",
    "completed_on",
    "route_delta",
    "notes",
]
AFFINITY_HEADER = [
    "tutor_id",
    "tutor_name",
    "affinity",
    "route_stage",
    "last_checkpoint",
    "notes",
]
PROVENANCE = {"provided", "external", "ai-synthesis", "inference"}
NODE_STATUS = {
    "planned",
    "in_progress",
    "mastered",
    "self_reported",
    "forced_skip",
    "needs_review",
}
TERMINAL_STATUS = {"mastered", "self_reported", "forced_skip", "needs_review"}
COMPILED_LIFECYCLES = {"approved", "learning", "completed"}
TUTOR_STYLES = {"friendly", "strict", "humorous"}
AFFINITY_STAGES = {
    0: "acquaintance",
    1: "trust",
    2: "fondness",
    3: "route-ready",
}

# The mindmap must stay a single offline file. Flag constructs that load
# external resources, not plain URLs quoted inside learner-visible text
# (citations with links are legitimate and required for time-sensitive
# claims).
MINDMAP_NETWORK_CHECKS = [
    (
        "a script loaded from a file or URL",
        re.compile(r"<script\b[^>]*\bsrc\s*=", re.IGNORECASE),
    ),
    (
        "a stylesheet, font, icon, or other linked resource",
        re.compile(r"<link\b[^>]*\bhref\s*=\s*[\"']?\s*(?!data:)", re.IGNORECASE),
    ),
    (
        "an image, frame, or media file loaded from a file or URL",
        re.compile(
            r"<(?:img|iframe|audio|video|source|track|embed|object)\b"
            r"[^>]*\b(?:src|srcset|poster|data)\s*=\s*[\"']?\s*(?!data:)",
            re.IGNORECASE,
        ),
    ),
    (
        "a CSS url() reference to a file or URL",
        re.compile(r"\burl\(\s*[\"']?\s*(?!data:|#)", re.IGNORECASE),
    ),
    (
        "a CSS @import",
        re.compile(r"@import\b", re.IGNORECASE),
    ),
]

REQUIRED_TEMPLATE_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "START-HERE.md",
    ".agents/skills/quaestio-socratica/SKILL.md",
    "course/course-status.md",
    "course/course-brief.md",
    "course/source-register.csv",
    "course/knowledge-map.csv",
    "course/standard-route.md",
    "course/student-materials/_index.md",
    "course/tutor-materials/_index.md",
    "source-materials/INBOX.md",
    "learner/learner-profile.md",
    "learner/personalized-route.md",
    "learner/progress.csv",
    "learner/callbacks.md",
    "learner/checkpoint-notes.md",
    "learner/session-archive.md",
    "outputs/OUTPUTS.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course_root", type=Path)
    parser.add_argument(
        "--phase", choices=("template", "compiled", "final"), default="template"
    )
    return parser.parse_args()


def read_csv(path: Path, expected_header: list[str], errors: list[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != expected_header:
                errors.append(
                    f"{path}: expected CSV header {expected_header}, got {reader.fieldnames}"
                )
                return []
            return [
                {key: (value or "").strip() for key, value in row.items()}
                for row in reader
            ]
    except OSError as exc:
        errors.append(f"{path}: cannot read CSV: {exc}")
        return []


def read_status(path: Path, errors: list[str]) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: cannot read status: {exc}")
        return {}

    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^-\s+([^:]+):\s*(.*)$", line)
        if match:
            fields[match.group(1).strip()] = match.group(2).strip()

    required = {
        "Lifecycle",
        "Initialization mode",
        "Course title",
        "Course version",
        "Tutor mode",
        "First dialogue language",
        "Approved by",
        "Approved on",
    }
    missing = sorted(required - fields.keys())
    if missing:
        errors.append(f"{path}: missing status fields: {', '.join(missing)}")
    if fields.get("Initialization mode") not in {"teacher", "self", "undecided"}:
        errors.append(f"{path}: invalid Initialization mode")
    if fields.get("Tutor mode") not in {
        "unselected",
        "course-mentor",
        "immersive",
        "affinity",
    }:
        errors.append(f"{path}: invalid Tutor mode")
    return fields


def read_learner_profile(path: Path, errors: list[str]) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: cannot read learner profile: {exc}")
        return {}

    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^-\s+([^:]+):\s*(.*)$", line)
        if match:
            fields[match.group(1).strip()] = match.group(2).strip()

    # Workspaces created before questioning styles existed are friendly by
    # default. This preserves compatibility while validating any explicit
    # selection.
    tutor_style = fields.get("Fixed tutor style") or "friendly"
    fields["Fixed tutor style"] = tutor_style
    if tutor_style not in TUTOR_STYLES:
        errors.append(
            f"{path}: invalid Fixed tutor style {tutor_style!r}; "
            f"expected one of {', '.join(sorted(TUTOR_STYLES))}"
        )

    adult_opt_in = fields.get("Affinity adult opt-in") or "no"
    fields["Affinity adult opt-in"] = adult_opt_in
    if adult_opt_in not in {"yes", "no"}:
        errors.append(
            f"{path}: invalid Affinity adult opt-in {adult_opt_in!r}; "
            "expected yes or no"
        )
    return fields


def split_ids(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def validate_affinity_state(
    status: dict[str, str],
    profile: dict[str, str],
    affinity_rows: list[dict[str, str]],
    affinity_file_exists: bool,
    errors: list[str],
) -> None:
    mode = status.get("Tutor mode")
    if mode != "affinity":
        if affinity_rows:
            errors.append("learner/affinity.csv must stay empty outside affinity mode")
        return

    if profile.get("Affinity adult opt-in") != "yes":
        errors.append("affinity mode requires explicit adult opt-in yes")
    if not affinity_file_exists:
        errors.append("affinity mode requires learner/affinity.csv")
    if not 1 <= len(affinity_rows) <= 3:
        errors.append("affinity mode requires one to three tutors")

    tutor_ids: set[str] = set()
    for row_number, row in enumerate(affinity_rows, start=2):
        tutor_id = row["tutor_id"]
        if not re.fullmatch(r"T0[1-3]", tutor_id):
            errors.append(
                f"affinity.csv row {row_number}: tutor_id must be T01, T02, or T03"
            )
        elif tutor_id in tutor_ids:
            errors.append(f"affinity.csv row {row_number}: duplicate tutor_id {tutor_id}")
        tutor_ids.add(tutor_id)

        if not row["tutor_name"]:
            errors.append(f"affinity.csv row {row_number}: tutor_name is required")

        try:
            affinity = int(row["affinity"])
        except ValueError:
            errors.append(
                f"affinity.csv row {row_number}: affinity must be an integer from 0 to 3"
            )
            continue
        if affinity not in AFFINITY_STAGES:
            errors.append(
                f"affinity.csv row {row_number}: affinity must be an integer from 0 to 3"
            )
            continue

        expected_stage = AFFINITY_STAGES[affinity]
        if row["route_stage"] != expected_stage:
            errors.append(
                f"affinity.csv row {row_number}: affinity {affinity} requires "
                f"route_stage {expected_stage}"
            )

        checkpoint = row["last_checkpoint"]
        if affinity == 0 and checkpoint:
            errors.append(
                f"affinity.csv row {row_number}: zero affinity requires blank "
                "last_checkpoint"
            )
        if affinity > 0 and not re.fullmatch(r"CP\d{2,}", checkpoint):
            errors.append(
                f"affinity.csv row {row_number}: positive affinity requires a "
                "checkpoint such as CP01"
            )


def validate_template(root: Path, errors: list[str]) -> dict[str, object]:
    if not root.is_dir():
        errors.append(f"{root}: course root is not a directory")
        return {}

    for relative in REQUIRED_TEMPLATE_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    status = (
        read_status(root / "course/course-status.md", errors)
        if (root / "course/course-status.md").is_file()
        else {}
    )
    sources = (
        read_csv(root / "course/source-register.csv", SOURCE_HEADER, errors)
        if (root / "course/source-register.csv").is_file()
        else []
    )
    nodes = (
        read_csv(root / "course/knowledge-map.csv", KNOWLEDGE_HEADER, errors)
        if (root / "course/knowledge-map.csv").is_file()
        else []
    )
    progress = (
        read_csv(root / "learner/progress.csv", PROGRESS_HEADER, errors)
        if (root / "learner/progress.csv").is_file()
        else []
    )
    profile = (
        read_learner_profile(root / "learner/learner-profile.md", errors)
        if (root / "learner/learner-profile.md").is_file()
        else {}
    )
    affinity_path = root / "learner/affinity.csv"
    affinity_file_exists = affinity_path.is_file()
    affinity_rows = (
        read_csv(affinity_path, AFFINITY_HEADER, errors)
        if affinity_file_exists
        else []
    )
    validate_affinity_state(
        status,
        profile,
        affinity_rows,
        affinity_file_exists,
        errors,
    )
    return {
        "status": status,
        "sources": sources,
        "nodes": nodes,
        "progress": progress,
        "profile": profile,
        "affinity": affinity_rows,
    }


def populated_materials(directory: Path) -> list[Path]:
    return [
        path
        for path in directory.glob("*.md")
        if path.name != "_index.md"
        and len(path.read_text(encoding="utf-8").strip()) >= 80
    ]


def validate_compiled(root: Path, state: dict[str, object], errors: list[str]) -> None:
    status = state["status"]
    sources = state["sources"]
    nodes = state["nodes"]

    assert isinstance(status, dict)
    assert isinstance(sources, list)
    assert isinstance(nodes, list)

    if status.get("Lifecycle") not in COMPILED_LIFECYCLES:
        errors.append("compiled phase requires Lifecycle approved, learning, or completed")
    if status.get("Initialization mode") not in {"teacher", "self"}:
        errors.append("compiled phase requires Initialization mode teacher or self")
    if not status.get("Approved by") or not status.get("Approved on"):
        errors.append("compiled phase requires explicit Approved by and Approved on")
    if not sources:
        errors.append("compiled phase requires at least one registered source")
    if not nodes:
        errors.append("compiled phase requires at least one knowledge node")
        return

    source_ids: set[str] = set()
    for row_number, source in enumerate(sources, start=2):
        source_id = source["source_id"]
        if not source_id or source_id in source_ids:
            errors.append(f"source-register.csv row {row_number}: missing or duplicate source_id")
        source_ids.add(source_id)
        if source["provenance"] not in PROVENANCE:
            errors.append(f"source {source_id}: invalid provenance")
        if source["time_sensitive"] not in {"true", "false"}:
            errors.append(f"source {source_id}: time_sensitive must be true or false")
        if source["time_sensitive"] == "true" and not source["retrieved_on"]:
            errors.append(f"source {source_id}: time-sensitive source needs retrieved_on")

    node_ids: set[str] = set()
    checkpoints: set[str] = set()
    for row_number, node in enumerate(nodes, start=2):
        node_id = node["node_id"]
        if not node_id or node_id in node_ids:
            errors.append(f"knowledge-map.csv row {row_number}: missing or duplicate node_id")
        node_ids.add(node_id)
        if node["core"] not in {"true", "false"}:
            errors.append(f"node {node_id}: core must be true or false")
        try:
            if int(node["estimated_minutes"]) <= 0:
                raise ValueError
        except ValueError:
            errors.append(f"node {node_id}: estimated_minutes must be a positive integer")
        if not re.fullmatch(r"CP\d{2,}", node["checkpoint_id"]):
            errors.append(f"node {node_id}: invalid checkpoint_id")
        checkpoints.add(node["checkpoint_id"])
        if not node["learning_outcome"] or not node["evidence"]:
            errors.append(f"node {node_id}: learning_outcome and evidence are required")

    for node in nodes:
        for parent_id in split_ids(node["parent_ids"]):
            if parent_id not in node_ids:
                errors.append(f"node {node['node_id']}: unknown parent {parent_id}")
        for source_id in split_ids(node["source_ids"]):
            if source_id not in source_ids:
                errors.append(f"node {node['node_id']}: unknown source {source_id}")

    if not checkpoints:
        errors.append("compiled phase requires at least one checkpoint")
    standard_route = (root / "course/standard-route.md").read_text(encoding="utf-8")
    for checkpoint in sorted(checkpoints):
        if checkpoint not in standard_route:
            errors.append(f"standard-route.md does not mention {checkpoint}")

    if not populated_materials(root / "course/student-materials"):
        errors.append("compiled phase requires populated learner material")
    if not populated_materials(root / "course/tutor-materials"):
        errors.append("compiled phase requires populated tutor material")


def validate_final(root: Path, state: dict[str, object], errors: list[str]) -> None:
    status = state["status"]
    nodes = state["nodes"]
    progress = state["progress"]
    assert isinstance(status, dict)
    assert isinstance(nodes, list)
    assert isinstance(progress, list)

    if status.get("Lifecycle") != "completed":
        errors.append("final phase requires Lifecycle completed")

    progress_by_node: dict[str, dict[str, str]] = {}
    for row_number, row in enumerate(progress, start=2):
        if row["status"] not in NODE_STATUS:
            errors.append(f"progress.csv row {row_number}: invalid status {row['status']}")
        if row["node_id"] in progress_by_node:
            errors.append(f"progress.csv row {row_number}: duplicate node_id {row['node_id']}")
        progress_by_node[row["node_id"]] = row

    for node in nodes:
        row = progress_by_node.get(node["node_id"])
        if row is None:
            errors.append(f"final phase missing progress for node {node['node_id']}")
        elif row["status"] not in TERMINAL_STATUS:
            errors.append(
                f"final phase node {node['node_id']} has non-terminal status {row['status']}"
            )

    notes = root / "outputs/personalized-cornell-notes.md"
    if not notes.is_file() or len(notes.read_text(encoding="utf-8").strip()) < 200:
        errors.append("final phase requires substantive personalized Cornell notes")

    mindmap = root / "outputs/personalized-mindmap.html"
    if not mindmap.is_file():
        errors.append("final phase requires personalized-mindmap.html")
    else:
        html = mindmap.read_text(encoding="utf-8")
        lowered = html.lower()
        if "<!doctype html>" not in lowered or "<style" not in lowered or "<script" not in lowered:
            errors.append("mindmap must be a complete single-file HTML document")
        for description, pattern in MINDMAP_NETWORK_CHECKS:
            if pattern.search(html):
                errors.append(
                    f"mindmap must be offline and self-contained; found {description}"
                )


def validate(root: Path, phase: str) -> list[str]:
    errors: list[str] = []
    state = validate_template(root, errors)
    if errors or phase == "template":
        return errors
    validate_compiled(root, state, errors)
    if errors or phase == "compiled":
        return errors
    validate_final(root, state, errors)
    return errors


def main() -> int:
    args = parse_args()
    root = args.course_root.expanduser().resolve()
    errors = validate(root, args.phase)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Course validation failed: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(f"Course validation passed ({args.phase}): {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
