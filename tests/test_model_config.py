"""Tests for the layered model configuration system."""

from __future__ import annotations

import unittest

from execution.schemas import (
    ALL_MODEL_FIELDS,
    MODEL_PRESETS,
    ROLE_GROUPS,
    BuildConfig,
    ExecutionConfig,
    resolve_models,
)


# ---------------------------------------------------------------------------
# resolve_models() unit tests
# ---------------------------------------------------------------------------


class TestResolveModels(unittest.TestCase):
    def test_defaults_match_balanced_preset(self):
        """No preset/groups/overrides should produce balanced defaults."""
        result = resolve_models(preset=None, models=None, explicit_fields={})
        balanced = MODEL_PRESETS["balanced"]
        for field in ALL_MODEL_FIELDS:
            group = next(g for g, fs in ROLE_GROUPS.items() if field in fs)
            self.assertEqual(result[field], balanced[group], f"{field} mismatch")

    def test_preset_turbo_all_haiku(self):
        result = resolve_models(preset="turbo", models=None, explicit_fields={})
        for field in ALL_MODEL_FIELDS:
            self.assertEqual(result[field], "haiku", f"{field} should be haiku")

    def test_preset_thorough_all_sonnet(self):
        result = resolve_models(preset="thorough", models=None, explicit_fields={})
        for field in ALL_MODEL_FIELDS:
            self.assertEqual(result[field], "sonnet", f"{field} should be sonnet")

    def test_preset_quality(self):
        result = resolve_models(preset="quality", models=None, explicit_fields={})
        for field in ROLE_GROUPS["planning"]:
            self.assertEqual(result[field], "opus", f"{field} should be opus")
        for field in ROLE_GROUPS["coding"]:
            self.assertEqual(result[field], "opus", f"{field} should be opus")
        for field in ROLE_GROUPS["orchestration"]:
            self.assertEqual(result[field], "sonnet", f"{field} should be sonnet")
        for field in ROLE_GROUPS["lightweight"]:
            self.assertEqual(result[field], "haiku", f"{field} should be haiku")

    def test_preset_fast(self):
        result = resolve_models(preset="fast", models=None, explicit_fields={})
        for field in ROLE_GROUPS["planning"]:
            self.assertEqual(result[field], "sonnet")
        for field in ROLE_GROUPS["coding"]:
            self.assertEqual(result[field], "sonnet")
        for field in ROLE_GROUPS["orchestration"]:
            self.assertEqual(result[field], "haiku")
        for field in ROLE_GROUPS["lightweight"]:
            self.assertEqual(result[field], "haiku")

    def test_group_override(self):
        result = resolve_models(
            preset=None,
            models={"planning": "opus"},
            explicit_fields={},
        )
        for field in ROLE_GROUPS["planning"]:
            self.assertEqual(result[field], "opus", f"{field} should be opus")
        # Other groups stay at balanced defaults
        for field in ROLE_GROUPS["coding"]:
            self.assertEqual(result[field], "sonnet")
        for field in ROLE_GROUPS["lightweight"]:
            self.assertEqual(result[field], "haiku")

    def test_individual_override_wins(self):
        result = resolve_models(
            preset="fast",
            models=None,
            explicit_fields={"coder_model": "opus"},
        )
        self.assertEqual(result["coder_model"], "opus")
        # Other coding fields still from preset
        self.assertEqual(result["qa_model"], "sonnet")

    def test_layered_all_three(self):
        """Preset + group override + individual override all interacting."""
        result = resolve_models(
            preset="fast",  # planning=sonnet, coding=sonnet, orch=haiku, light=haiku
            models={"orchestration": "sonnet"},  # override orch back to sonnet
            explicit_fields={"pm_model": "opus"},  # override one planning field
        )
        self.assertEqual(result["pm_model"], "opus")  # individual wins
        self.assertEqual(result["architect_model"], "sonnet")  # from preset
        self.assertEqual(result["replan_model"], "sonnet")  # group override
        self.assertEqual(result["qa_synthesizer_model"], "haiku")  # from preset

    def test_invalid_preset_raises(self):
        with self.assertRaises(ValueError):
            resolve_models(preset="nonexistent", models=None, explicit_fields={})

    def test_invalid_group_raises(self):
        with self.assertRaises(ValueError):
            resolve_models(preset=None, models={"badgroup": "opus"}, explicit_fields={})


# ---------------------------------------------------------------------------
# BuildConfig tests
# ---------------------------------------------------------------------------


class TestBuildConfig(unittest.TestCase):
    def test_backward_compat_flat(self):
        """Explicit flat fields still work without preset/models."""
        cfg = BuildConfig(pm_model="opus", coder_model="opus")
        resolved = cfg.resolved_models()
        self.assertEqual(resolved["pm_model"], "opus")
        self.assertEqual(resolved["coder_model"], "opus")
        # Non-explicit fields get balanced defaults
        self.assertEqual(resolved["architect_model"], "sonnet")
        self.assertEqual(resolved["qa_synthesizer_model"], "haiku")

    def test_preset_only(self):
        cfg = BuildConfig(preset="quality")
        resolved = cfg.resolved_models()
        self.assertEqual(resolved["pm_model"], "opus")
        self.assertEqual(resolved["coder_model"], "opus")
        self.assertEqual(resolved["replan_model"], "sonnet")
        self.assertEqual(resolved["qa_synthesizer_model"], "haiku")

    def test_preset_plus_individual_override(self):
        cfg = BuildConfig(preset="balanced", architect_model="opus")
        resolved = cfg.resolved_models()
        self.assertEqual(resolved["architect_model"], "opus")
        self.assertEqual(resolved["pm_model"], "sonnet")  # from preset

    def test_preset_plus_group_override(self):
        cfg = BuildConfig(preset="quality", models={"orchestration": "haiku"})
        resolved = cfg.resolved_models()
        self.assertEqual(resolved["pm_model"], "opus")  # from preset
        self.assertEqual(resolved["replan_model"], "haiku")  # from group override

    def test_default_config_matches_balanced(self):
        """BuildConfig() with no args should resolve identically to balanced preset."""
        default = BuildConfig().resolved_models()
        balanced = BuildConfig(preset="balanced").resolved_models()
        self.assertEqual(default, balanced)

    def test_to_execution_config_dict(self):
        cfg = BuildConfig(preset="quality")
        d = cfg.to_execution_config_dict()
        # Execution-level model fields should be resolved
        self.assertEqual(d["coder_model"], "opus")
        self.assertEqual(d["replan_model"], "sonnet")
        self.assertEqual(d["qa_synthesizer_model"], "haiku")
        # Planning-only fields should NOT be in the dict
        self.assertNotIn("pm_model", d)
        self.assertNotIn("architect_model", d)
        self.assertNotIn("tech_lead_model", d)
        self.assertNotIn("sprint_planner_model", d)
        self.assertNotIn("git_model", d)
        self.assertNotIn("verifier_model", d)
        # Non-model config should be present
        self.assertEqual(d["max_coding_iterations"], 5)
        self.assertTrue(d["enable_replanning"])

    def test_to_execution_config_dict_roundtrips(self):
        """The dict from to_execution_config_dict() should be valid for ExecutionConfig."""
        cfg = BuildConfig(preset="quality")
        d = cfg.to_execution_config_dict()
        exec_cfg = ExecutionConfig(**d)
        self.assertEqual(exec_cfg.coder_model, "opus")
        self.assertEqual(exec_cfg.qa_synthesizer_model, "haiku")


# ---------------------------------------------------------------------------
# ExecutionConfig tests
# ---------------------------------------------------------------------------


class TestExecutionConfig(unittest.TestCase):
    def test_execution_config_resolution(self):
        """ExecutionConfig(preset=...) should resolve fields on construction."""
        cfg = ExecutionConfig(preset="quality")
        self.assertEqual(cfg.coder_model, "opus")
        self.assertEqual(cfg.qa_model, "opus")
        self.assertEqual(cfg.replan_model, "sonnet")
        self.assertEqual(cfg.qa_synthesizer_model, "haiku")

    def test_execution_config_turbo(self):
        cfg = ExecutionConfig(preset="turbo")
        self.assertEqual(cfg.coder_model, "haiku")
        self.assertEqual(cfg.replan_model, "haiku")
        self.assertEqual(cfg.qa_synthesizer_model, "haiku")

    def test_execution_config_group_override(self):
        cfg = ExecutionConfig(models={"coding": "opus"})
        self.assertEqual(cfg.coder_model, "opus")
        self.assertEqual(cfg.qa_model, "opus")
        self.assertEqual(cfg.code_reviewer_model, "opus")
        # Orchestration stays default
        self.assertEqual(cfg.replan_model, "sonnet")

    def test_execution_config_no_preset_unchanged(self):
        """Without preset/models, fields stay at their declared defaults."""
        cfg = ExecutionConfig()
        self.assertEqual(cfg.coder_model, "sonnet")
        self.assertEqual(cfg.qa_synthesizer_model, "haiku")

    def test_execution_config_preset_plus_explicit(self):
        """Explicit field overrides preset even on ExecutionConfig."""
        cfg = ExecutionConfig(preset="turbo", coder_model="opus")
        self.assertEqual(cfg.coder_model, "opus")  # explicit wins
        self.assertEqual(cfg.qa_model, "haiku")  # from turbo preset


# ---------------------------------------------------------------------------
# Preset coverage
# ---------------------------------------------------------------------------


class TestPresetCoverage(unittest.TestCase):
    def test_all_presets_have_all_groups(self):
        for name, preset in MODEL_PRESETS.items():
            for group in ROLE_GROUPS:
                self.assertIn(group, preset, f"Preset {name!r} missing group {group!r}")

    def test_all_model_fields_in_exactly_one_group(self):
        seen: set[str] = set()
        for group, fields in ROLE_GROUPS.items():
            for field in fields:
                self.assertNotIn(field, seen, f"{field} in multiple groups")
                seen.add(field)
        self.assertEqual(seen, set(ALL_MODEL_FIELDS))


if __name__ == "__main__":
    unittest.main()
