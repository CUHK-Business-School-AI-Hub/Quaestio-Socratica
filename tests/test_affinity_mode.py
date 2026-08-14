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
AFFINITY_HEADER = (
    "tutor_id,tutor_name,affinity,route_stage,last_checkpoint,notes\n"
)


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_script(
    "quaestio_validate_affinity", SKILL_ROOT / "scripts" / "validate_course.py"
)
initializer = load_script(
    "quaestio_init_affinity", SKILL_ROOT / "scripts" / "init_course.py"
)


class AffinityModeContractTests(unittest.TestCase):
    def make_course(
        self,
        temporary: str,
        *,
        mode: str = "affinity",
        opt_in: str = "yes",
        rows: str = "T01,Lin,0,acquaintance,,initial cast\n",
    ) -> Path:
        course = Path(temporary) / "course"
        shutil.copytree(STARTER, course)

        status = course / "course" / "course-status.md"
        status.write_text(
            status.read_text(encoding="utf-8").replace(
                "- Tutor mode: unselected", f"- Tutor mode: {mode}"
            ),
            encoding="utf-8",
        )

        profile = course / "learner" / "learner-profile.md"
        text = profile.read_text(encoding="utf-8")
        if "- Affinity adult opt-in:" in text:
            text = text.replace("- Affinity adult opt-in: no", f"- Affinity adult opt-in: {opt_in}")
        else:
            text += f"\n- Affinity adult opt-in: {opt_in}\n"
        profile.write_text(text, encoding="utf-8")

        (course / "learner" / "affinity.csv").write_text(
            AFFINITY_HEADER + rows,
            encoding="utf-8",
        )
        return course

    def test_affinity_contract_preserves_consent_and_teaching_independence(self) -> None:
        contract = (SKILL_ROOT / "references" / "affinity-mode.md").read_text(
            encoding="utf-8"
        )
        for expected in (
            "at least 18 and opt in",
            "exactly one heart to at most one tutor",
            "never removes hearts",
            "answer correctness",
            "requesting explanation",
            "friendship or light-romance epilogue",
            "must not claim real consciousness",
            "The ordinary teaching contract always wins.",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, contract)

    def test_affinity_accepts_one_to_three_valid_tutors(self) -> None:
        valid_rows = {
            1: "T01,Lin,0,acquaintance,,initial cast\n",
            2: (
                "T01,Lin,1,trust,CP01,chose archive route\n"
                "T02,Mara,2,fondness,CP02,chose field route\n"
            ),
            3: (
                "T01,Lin,1,trust,CP01,chose archive route\n"
                "T02,Mara,2,fondness,CP02,chose field route\n"
                "T03,Soren,3,route-ready,CP03,chose studio route\n"
            ),
        }
        for count, rows in valid_rows.items():
            with self.subTest(count=count), tempfile.TemporaryDirectory() as temporary:
                course = self.make_course(temporary, rows=rows)
                self.assertEqual(validator.validate(course, "template"), [])

    def test_affinity_rejects_missing_adult_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            course = self.make_course(temporary, opt_in="no")
            errors = validator.validate(course, "template")
            self.assertTrue(any("adult opt-in" in error for error in errors), errors)

    def test_affinity_rejects_zero_or_more_than_three_tutors(self) -> None:
        invalid_rows = {
            "zero": "",
            "four": (
                "T01,Lin,0,acquaintance,,\n"
                "T02,Mara,0,acquaintance,,\n"
                "T03,Soren,0,acquaintance,,\n"
                "T04,Ivo,0,acquaintance,,\n"
            ),
        }
        for name, rows in invalid_rows.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                course = self.make_course(temporary, rows=rows)
                errors = validator.validate(course, "template")
                self.assertTrue(any("one to three tutors" in error for error in errors), errors)

    def test_affinity_rejects_invalid_row_contracts(self) -> None:
        invalid_rows = {
            "bad_id": "mentor-one,Lin,0,acquaintance,,\n",
            "duplicate_id": (
                "T01,Lin,0,acquaintance,,\n"
                "T01,Mara,1,trust,CP01,duplicate\n"
            ),
            "bad_value": "T01,Lin,4,route-ready,CP01,too high\n",
            "stage_mismatch": "T01,Lin,2,trust,CP01,mismatch\n",
            "missing_checkpoint": "T01,Lin,1,trust,,missing checkpoint\n",
            "bad_checkpoint": "T01,Lin,1,trust,chapter-one,bad checkpoint\n",
        }
        for name, rows in invalid_rows.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                course = self.make_course(temporary, rows=rows)
                self.assertNotEqual(validator.validate(course, "template"), [])

    def test_non_affinity_mode_rejects_dormant_affinity_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            course = self.make_course(temporary, mode="course-mentor")
            errors = validator.validate(course, "template")
            self.assertTrue(any("outside affinity mode" in error for error in errors), errors)

    def test_old_non_affinity_workspace_without_affinity_file_stays_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            course = Path(temporary) / "legacy-course"
            shutil.copytree(STARTER, course)
            affinity = course / "learner" / "affinity.csv"
            if affinity.exists():
                affinity.unlink()
            self.assertEqual(validator.validate(course, "template"), [])

    def test_initializer_includes_empty_affinity_state_and_runtime_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "initialized-course"
            initialized, skipped = initializer.initialize(
                destination,
                mode="self",
                title="Affinity mode",
            )
            self.assertEqual(skipped, [])
            self.assertEqual(
                (initialized / "learner" / "affinity.csv").read_text(
                    encoding="utf-8"
                ),
                AFFINITY_HEADER,
            )
            self.assertTrue(
                (
                    initialized
                    / ".agents"
                    / "skills"
                    / "quaestio-socratica"
                    / "references"
                    / "affinity-mode.md"
                ).is_file()
            )
            self.assertEqual(validator.validate(initialized, "template"), [])

    def test_affinity_runtime_files_match_all_distributions(self) -> None:
        relative_files = [
            "SKILL.md",
            "references/affinity-mode.md",
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
