import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("documentation", ROOT / "hooks/documentation.py")
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


class DocumentationTests(unittest.TestCase):
    def setUp(self):
        self.temp = ROOT / ".test-tmp" / uuid.uuid4().hex
        self.root = self.temp / "project"
        self.root.mkdir(parents=True)
        self.addCleanup(self.cleanup)
        self.scope = patch.object(hook, "project_root", return_value=(self.root, False))
        self.scope.start()
        self.addCleanup(self.scope.stop)
        env = patch.dict(os.environ, {"PLUGIN_DATA": str(self.temp / "state")})
        env.start()
        self.addCleanup(env.stop)
        self.event = {"cwd": str(self.root), "session_id": "session", "turn_id": "turn"}

    def cleanup(self):
        target = self.temp.resolve()
        if target.parent != (ROOT / ".test-tmp").resolve():
            raise RuntimeError("Unexpected cleanup target")
        shutil.rmtree(target)

    def call(self, name, **extra):
        return hook.handle({**self.event, "hook_event_name": name, **extra})

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def start(self):
        self.assertIn("additionalContext", self.call("UserPromptSubmit")["hookSpecificOutput"])

    def assert_blocked(self):
        self.assertEqual(self.call("Stop")["decision"], "block")

    def test_read_only_needs_no_documents(self):
        self.start()
        self.assertIsNone(self.call("Stop"))

    def test_new_code_requires_documentation(self):
        self.start()
        self.write("main.py", "print('hello')")
        self.assert_blocked()

    def test_existing_unchanged_docs_require_review(self):
        self.write("README.md", "How to start")
        self.start()
        self.write("main.py", "print('hello')")
        self.assert_blocked()

    def test_created_documents_pass(self):
        self.start()
        self.write("main.py", "print('hello')")
        self.write("README.md", "Run python main.py")
        self.assertIsNone(self.call("Stop"))

    def test_updated_documents_pass(self):
        self.write("README.md", "Old usage")
        self.write("main.py", "old")
        self.start()
        self.write("main.py", "new")
        self.write("README.md", "New usage")
        self.assertIsNone(self.call("Stop"))

    def test_deleted_code_requires_review(self):
        self.write("main.py", "old")
        self.start()
        (self.root / "main.py").unlink()
        self.assert_blocked()

    def test_deleted_only_document_requires_creation(self):
        self.write("README.md", "Old usage")
        self.start()
        (self.root / "README.md").unlink()
        self.write("main.py", "new")
        self.assert_blocked()

    def test_empty_document_or_svg_alone_is_insufficient(self):
        self.start()
        self.write("main.py", "new")
        self.write("README.md", "  \n")
        self.write("docs/assets/map.svg", "<svg/>")
        self.assert_blocked()

    def test_agent_instructions_are_not_reader_docs(self):
        self.start()
        self.write("AGENTS.md", "Instructions")
        self.write("skills/a/SKILL.md", "Skill")
        self.assert_blocked()

    def test_continuation_is_bounded_even_without_runtime_flag(self):
        self.start()
        self.write("main.py", "new")
        self.assert_blocked()
        self.assertIsNone(self.call("Stop"))

    def test_runtime_continuation_flag_skips_check(self):
        self.assertIsNone(self.call("Stop", stop_hook_active=True))

    def test_separate_turns_have_separate_baselines(self):
        self.start()
        self.write("main.py", "new")
        self.event["turn_id"] = "another-turn"
        self.start()
        self.write("another.py", "another")
        self.assert_blocked()

    def test_missing_baseline_warns(self):
        self.assertIn("systemMessage", self.call("Stop"))

    def test_budget_exceeded_warns(self):
        with patch.object(hook, "MAX_FILES", 0):
            self.write("main.py", "new")
            result = self.call("UserPromptSubmit")
        self.assertIn("indisponible", result["hookSpecificOutput"]["additionalContext"])

    @unittest.skipUnless(shutil.which("git"), "Git unavailable")
    def test_git_ignores_generated_files_and_keeps_dirty_baseline(self):
        self.scope.stop()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.write(".gitignore", "generated/\n")
        self.write("main.py", "already dirty before Codex")
        self.start()
        self.write("generated/cache.bin", "irrelevant")
        self.assertIsNone(self.call("Stop"))
        self.write("main.py", "changed during the task")
        self.assert_blocked()

    def test_command_reads_json_and_returns_context(self):
        process = subprocess.run(
            [os.sys.executable, str(ROOT / "hooks/documentation.py")],
            input=json.dumps({**self.event, "hook_event_name": "UserPromptSubmit"}),
            text=True, capture_output=True, check=True,
            env={**os.environ, "TMP": str(self.temp), "TEMP": str(self.temp)},
        )
        self.assertEqual(json.loads(process.stdout)["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")


if __name__ == "__main__":
    unittest.main()
