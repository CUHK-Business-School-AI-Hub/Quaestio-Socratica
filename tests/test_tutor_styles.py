from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "quaestio-socratica"
STARTER = ROOT / "starter-course"
DEMO = ROOT / "demo" / "reliable-ai-workflows"


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_script(
    "quaestio_validate_course", SKILL_ROOT / "scripts" / "validate_course.py"
)
initializer = load_script(
    "quaestio_init_course", SKILL_ROOT / "scripts" / "init_course.py"
)


class TutorStyleContractTests(unittest.TestCase):
    def test_style_contract_keeps_common_teaching_boundaries(self) -> None:
        contract = (
            SKILL_ROOT / "references" / "tutor-styles.md"
        ).read_text(encoding="utf-8")
        for expected in (
            "## Friendly (`friendly`, default)",
            "## Strict (`strict`)",
            "## Humorous (`humorous`)",
            "direct explanation",
            "`forced_skip`",
            "A joke never replaces a correction",
            "When style and pedagogy conflict, the teaching contract wins.",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, contract)

    def test_all_explicit_styles_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = Path(temporary) / "learner-profile.md"
            for style in ("friendly", "strict", "humorous"):
                with self.subTest(style=style):
                    profile.write_text(
                        f"# Learner profile\n\n- Fixed tutor style: {style}\n",
                        encoding="utf-8",
                    )
                    errors: list[str] = []
                    fields = validator.read_learner_profile(profile, errors)
                    self.assertEqual(errors, [])
                    self.assertEqual(fields["Fixed tutor style"], style)

    def test_missing_style_defaults_to_friendly_for_old_workspaces(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = Path(temporary) / "learner-profile.md"
            profile.write_text(
                "# Learner profile\n\n- Fixed tutor mode: course-mentor\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            fields = validator.read_learner_profile(profile, errors)
            self.assertEqual(errors, [])
            self.assertEqual(fields["Fixed tutor style"], "friendly")

    def test_invalid_explicit_style_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            course = Path(temporary) / "course"
            shutil.copytree(STARTER, course)
            profile = course / "learner" / "learner-profile.md"
            text = profile.read_text(encoding="utf-8")
            profile.write_text(
                text.replace(
                    "- Fixed tutor style: friendly",
                    "- Fixed tutor style: sarcastic",
                ),
                encoding="utf-8",
            )
            errors = validator.validate(course, "template")
            self.assertTrue(
                any("invalid Fixed tutor style" in error for error in errors),
                errors,
            )

    def test_starter_template_contract_passes(self) -> None:
        self.assertEqual(validator.validate(STARTER, "template"), [])

    def test_initializer_embeds_default_style_and_style_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "initialized-course"
            initialized, skipped = initializer.initialize(
                destination,
                mode="self",
                title="Questioning styles",
            )
            self.assertEqual(skipped, [])
            profile = initialized / "learner" / "learner-profile.md"
            self.assertIn(
                "- Fixed tutor style: friendly",
                profile.read_text(encoding="utf-8"),
            )
            self.assertTrue(
                (
                    initialized
                    / ".agents"
                    / "skills"
                    / "quaestio-socratica"
                    / "references"
                    / "tutor-styles.md"
                ).is_file()
            )
            self.assertEqual(validator.validate(initialized, "template"), [])

    def test_distributed_runtime_files_match_canonical_skill(self) -> None:
        relative_files = [
            "SKILL.md",
            "references/artifact-contracts.md",
            "references/course-compiler.md",
            "references/teaching-runtime.md",
            "references/tutor-modes.md",
            "references/tutor-styles.md",
            "scripts/validate_course.py",
        ]
        embedded_roots = [
            STARTER / ".agents" / "skills" / "quaestio-socratica",
            DEMO / ".agents" / "skills" / "quaestio-socratica",
        ]
        for embedded_root in embedded_roots:
            for relative in relative_files:
                with self.subTest(root=embedded_root, relative=relative):
                    self.assertEqual(
                        (SKILL_ROOT / relative).read_bytes(),
                        (embedded_root / relative).read_bytes(),
                    )


if __name__ == "__main__":
    unittest.main()
