import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_update", ROOT / "hooks/check_update.py")
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class CheckUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = ROOT / ".test-tmp" / uuid.uuid4().hex
        self.plugin_dir = self.temp / "plugin"
        self.state_dir = self.temp / "state"
        self.plugin_dir.mkdir(parents=True)
        self.addCleanup(self.cleanup)
        env = patch.dict(
            os.environ,
            {
                "PLUGIN_DATA": str(self.state_dir),
                "PLUGIN_ROOT": str(self.plugin_dir),
                "PROJECTDOC_NO_UPDATE_CHECK": "0",
            },
        )
        env.start()
        self.addCleanup(env.stop)
        self.write_manifest("0.5.0")

    def cleanup(self):
        target = self.temp.resolve()
        if target.parent != (ROOT / ".test-tmp").resolve():
            raise RuntimeError("Unexpected cleanup target")
        updater._rmtree(target)

    def write_manifest(self, version, *, relative=".antigravity-plugin/plugin.json", repo=updater.DEFAULT_REPO_URL):
        path = self.plugin_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"name": "projectdoc", "version": version, "repository": repo}),
            encoding="utf-8",
        )

    def test_update_available_injects_user_markdown_and_writes_cache(self):
        with (
            patch.object(updater, "fetch_remote_sha", return_value="abc123") as mock_sha,
            patch.object(updater, "fetch_remote_version", return_value="0.6.0") as mock_ver,
        ):
            result = updater.handle({"hookEventName": "SessionStart"}, now=1000.0)

        mock_sha.assert_called_once()
        mock_ver.assert_called_once()
        step = result["injectSteps"][0]["systemMessage"]
        self.assertEqual(step["systemMessage"], "")
        markdown = step["metadata"]["user_markdown"]
        self.assertIn("0.5.0", markdown)
        self.assertIn("0.6.0", markdown)
        self.assertIn(f"agy plugin install {updater.DEFAULT_REPO_URL}", markdown)

        cache = json.loads((self.state_dir / "update-check.json").read_text(encoding="utf-8"))
        self.assertEqual(cache["checked_at"], 1000.0)
        self.assertEqual(cache["remote_sha"], "abc123")
        self.assertEqual(cache["remote_version"], "0.6.0")

    def test_ttl_hit_within_two_hours_skips_remote_calls(self):
        with (
            patch.object(updater, "fetch_remote_sha", return_value="abc123"),
            patch.object(updater, "fetch_remote_version", return_value="0.6.0"),
        ):
            updater.handle({"hookEventName": "SessionStart"}, now=1000.0)

        with (
            patch.object(updater, "fetch_remote_sha", side_effect=AssertionError("should not fetch")) as mock_sha,
            patch.object(updater, "fetch_remote_version", side_effect=AssertionError("should not fetch")),
        ):
            cached = updater.handle({"hookEventName": "SessionStart"}, now=1000.0 + updater.TTL_SECONDS - 1)

        mock_sha.assert_not_called()
        self.assertIn("0.6.0", cached["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"])

        with (
            patch.object(updater, "fetch_remote_sha", return_value="def456") as mock_sha_expired,
            patch.object(updater, "fetch_remote_version", return_value="0.7.0") as mock_ver_expired,
        ):
            refreshed = updater.handle({"hookEventName": "SessionStart"}, now=1000.0 + updater.TTL_SECONDS)

        mock_sha_expired.assert_called_once()
        mock_ver_expired.assert_called_once()
        self.assertIn("0.7.0", refreshed["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"])

    def test_expired_ttl_with_unchanged_sha_skips_manifest_fetch(self):
        with (
            patch.object(updater, "fetch_remote_sha", return_value="abc123"),
            patch.object(updater, "fetch_remote_version", return_value="0.6.0"),
        ):
            updater.handle({"hookEventName": "SessionStart"}, now=1000.0)

        with (
            patch.object(updater, "fetch_remote_sha", return_value="abc123") as mock_sha,
            patch.object(updater, "fetch_remote_version", side_effect=AssertionError("should reuse cached version")),
        ):
            result = updater.handle({"hookEventName": "SessionStart"}, now=1000.0 + updater.TTL_SECONDS + 10)

        mock_sha.assert_called_once()
        self.assertIn("0.6.0", result["injectSteps"][0]["systemMessage"]["metadata"]["user_markdown"])
        cache = json.loads((self.state_dir / "update-check.json").read_text(encoding="utf-8"))
        self.assertEqual(cache["checked_at"], 1000.0 + updater.TTL_SECONDS + 10)

    def test_version_comparison_handles_equal_local_ahead_and_multi_digit(self):
        self.assertTrue(updater.is_newer("0.10.0", "0.9.0"))
        self.assertFalse(updater.is_newer("0.9.0", "0.10.0"))
        self.assertFalse(updater.is_newer("0.6.0", "0.6.0"))
        self.assertFalse(updater.is_newer("invalid", "0.6.0"))

        self.write_manifest("0.6.0")
        with (
            patch.object(updater, "fetch_remote_sha", return_value="abc123"),
            patch.object(updater, "fetch_remote_version", return_value="0.6.0"),
        ):
            self.assertEqual(updater.handle({"hookEventName": "SessionStart"}, now=1000.0), {})

    def test_remote_failure_fails_open_without_overwriting_cache(self):
        with (
            patch.object(updater, "fetch_remote_sha", return_value="abc123"),
            patch.object(updater, "fetch_remote_version", return_value="0.6.0"),
        ):
            updater.handle({"hookEventName": "SessionStart"}, now=1000.0)

        with patch.object(updater, "fetch_remote_sha", return_value=None):
            result = updater.handle({"hookEventName": "SessionStart"}, now=1000.0 + updater.TTL_SECONDS + 5)

        self.assertEqual(result, {})
        cache = json.loads((self.state_dir / "update-check.json").read_text(encoding="utf-8"))
        self.assertEqual(cache["checked_at"], 1000.0)
        self.assertEqual(cache["remote_version"], "0.6.0")

    def test_opt_out_and_other_events_return_empty(self):
        with patch.dict(os.environ, {"PROJECTDOC_NO_UPDATE_CHECK": "1"}):
            with patch.object(updater, "fetch_remote_sha", side_effect=AssertionError("should not fetch")):
                self.assertEqual(updater.handle({"hookEventName": "SessionStart"}), {})
        with patch.object(updater, "fetch_remote_sha", side_effect=AssertionError("should not fetch")):
            self.assertEqual(updater.handle({"hookEventName": "PreInvocation"}), {})

    def test_flattened_plugin_json_manifest_supported(self):
        shutil.rmtree(self.plugin_dir / ".antigravity-plugin")
        self.write_manifest("0.5.0", relative="plugin.json")
        with (
            patch.object(updater, "fetch_remote_sha", return_value="abc123"),
            patch.object(updater, "fetch_remote_version", return_value="0.6.0"),
        ):
            result = updater.handle({"hookEventName": "SessionStart"}, now=1000.0)
        self.assertIn("injectSteps", result)

    def test_invalid_stdin_fails_open_via_subprocess(self):
        process = subprocess.run(
            [sys.executable, str(ROOT / "hooks/check_update.py")],
            input="not-json",
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(json.loads(process.stdout), {})

    @unittest.skipUnless(shutil.which("git"), "Git unavailable")
    def test_git_fetch_reads_manifest_from_remote_main(self):
        origin = self.temp / "origin"
        origin.mkdir()
        git_env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        }
        subprocess.run(["git", "init", "-q", "-b", "main", str(origin)], check=True, env=git_env)
        manifest = origin / ".antigravity-plugin/plugin.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({"name": "projectdoc", "version": "0.9.0"}), encoding="utf-8")
        subprocess.run(["git", "-C", str(origin), "add", "."], check=True, env=git_env)
        subprocess.run(["git", "-C", str(origin), "commit", "-q", "-m", "init"], check=True, env=git_env)

        sha = updater.fetch_remote_sha(str(origin))
        self.assertIsNotNone(sha)
        self.assertEqual(len(sha), 40)
        self.assertEqual(updater.fetch_remote_version(str(origin)), "0.9.0")


if __name__ == "__main__":
    unittest.main()
