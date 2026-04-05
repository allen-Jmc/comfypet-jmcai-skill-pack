import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "skills" / "comfypet-jmcai-skill" / "jmcai_skill.py"

SPEC = importlib.util.spec_from_file_location("jmcai_skill", MODULE_PATH)
jmcai_skill = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(jmcai_skill)


class JmcaiSkillConfigTests(unittest.TestCase):
    def write_config(self, directory: str, payload: dict) -> Path:
        path = Path(directory) / "config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_load_config_clamps_stale_min_bridge_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self.write_config(
                tmpdir,
                {
                    "bridge_url": "http://bridge-host:32100",
                    "min_bridge_version": "1.1.0",
                },
            )

            config = jmcai_skill.load_config(str(config_path))

        self.assertEqual(config["bridge_url"], "http://bridge-host:32100")
        self.assertEqual(config["min_bridge_version"], "1.2.0")
        self.assertTrue(
            any("lower than the hard minimum 1.2.0" in warning for warning in config[jmcai_skill.CONFIG_WARNINGS_KEY])
        )

    def test_write_normalized_config_file_adds_missing_min_bridge_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self.write_config(
                tmpdir,
                {
                    "bridge_url": "http://bridge-host:32100",
                    "upload_timeout_ms": 90000,
                },
            )

            written = jmcai_skill.write_normalized_config_file(config_path)
            on_disk = json.loads(config_path.read_text(encoding="utf-8"))

        self.assertEqual(written["min_bridge_version"], "1.2.0")
        self.assertEqual(on_disk["min_bridge_version"], "1.2.0")
        self.assertEqual(on_disk["upload_timeout_ms"], 90000)

    def test_write_normalized_config_file_replaces_invalid_min_bridge_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self.write_config(
                tmpdir,
                {
                    "bridge_url": "http://bridge-host:32100",
                    "min_bridge_version": "abc",
                },
            )

            initial = jmcai_skill.load_config(str(config_path))
            written = jmcai_skill.write_normalized_config_file(config_path)
            reloaded = jmcai_skill.load_config(str(config_path))

        self.assertTrue(
            any("is invalid" in warning for warning in initial[jmcai_skill.CONFIG_WARNINGS_KEY])
        )
        self.assertEqual(written["min_bridge_version"], "1.2.0")
        self.assertEqual(reloaded["min_bridge_version"], "1.2.0")
        self.assertEqual(reloaded[jmcai_skill.CONFIG_WARNINGS_KEY], [])

    def test_higher_min_bridge_version_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self.write_config(
                tmpdir,
                {
                    "bridge_url": "http://bridge-host:32100",
                    "min_bridge_version": "1.3.0",
                },
            )

            written = jmcai_skill.write_normalized_config_file(config_path)
            reloaded = jmcai_skill.load_config(str(config_path))

        self.assertEqual(written["min_bridge_version"], "1.3.0")
        self.assertEqual(reloaded["min_bridge_version"], "1.3.0")
        self.assertEqual(reloaded[jmcai_skill.CONFIG_WARNINGS_KEY], [])

    def test_doctor_uses_effective_min_bridge_version_and_surfaces_warning(self) -> None:
        config = jmcai_skill.normalize_config_payload(
            {
                "bridge_url": "http://bridge-host:32100",
                "min_bridge_version": "1.1.0",
            }
        )
        workflow_payload = {
            "workflows": [
                {
                    "id": "demo-workflow",
                    "name": "Demo",
                    "summary": "Demo workflow",
                    "description": "Demo workflow",
                    "schema": [{"alias": "prompt_1", "type": "string"}],
                    "input_modalities": ["text"],
                    "output_modalities": ["image"],
                    "default_target_id": "default-target",
                    "available_targets": [
                        {
                            "id": "default-target",
                            "name": "Default target",
                            "type": "desktop",
                            "available": True,
                        }
                    ],
                }
            ]
        }

        with mock.patch.object(
            jmcai_skill,
            "request_json",
            side_effect=[
                {"bridge_version": "1.1.0", "desktop_app": "JMCAI", "capabilities": []},
                workflow_payload,
            ],
        ):
            result = jmcai_skill.doctor_command(config)

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["min_bridge_version"], "1.2.0")
        self.assertTrue(
            any("Configured min_bridge_version '1.1.0'" in warning for warning in result["warnings"])
        )
        self.assertTrue(
            any("Bridge version 1.1.0 is lower than required 1.2.0" in problem for problem in result["problems"])
        )

    def test_write_normalized_config_file_matches_install_flow_regression_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self.write_config(
                tmpdir,
                {
                    "bridge_url": "http://bridge-host:32100",
                    "request_timeout_ms": 20000,
                    "min_bridge_version": "1.1.0",
                },
            )

            jmcai_skill.write_normalized_config_file(config_path)
            reloaded = jmcai_skill.load_config(str(config_path))
            on_disk = json.loads(config_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk["bridge_url"], "http://bridge-host:32100")
        self.assertEqual(on_disk["request_timeout_ms"], 20000)
        self.assertEqual(on_disk["min_bridge_version"], "1.2.0")
        self.assertEqual(reloaded["min_bridge_version"], "1.2.0")


if __name__ == "__main__":
    unittest.main()
