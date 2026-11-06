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

    def test_claude_plugin_copies_are_in_sync(self):
        plugin = ROOT / "plugins/projectdoc-claude"
        for name in ("hooks/documentation.py", "skills/maintain-project-docs/SKILL.md"):
            with self.subTest(name=name):
                self.assertEqual((ROOT / name).read_bytes(), (plugin / name).read_bytes())

    def test_claude_hook_turns_without_turn_id(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        plugin = ROOT / "plugins/projectdoc-claude"
        env = {
            **os.environ,
            "CLAUDE_PLUGIN_DATA": str(self.temp / "claude-state"),
            "PROJECTDOC_DEBUG": "0",
        }

        def call(name, **extra):
            result = subprocess.run(
                [sys.executable, str(plugin / "hooks/documentation.py"), "--claude"],
                input=json.dumps({
                    "cwd": str(self.root),
                    "session_id": "claude-session",
                    "hook_event_name": name,
                    **extra,
                }),
                text=True, capture_output=True, check=True, env=env,
            )
            return json.loads(result.stdout) if result.stdout else {}

        context = call("UserPromptSubmit")["hookSpecificOutput"]
        self.assertEqual(context["hookEventName"], "UserPromptSubmit")
        self.assertIn((plugin / "skills").as_posix(), context["additionalContext"])
        self.write("main.py", "print('hello')")
        self.assertEqual(call("Stop")["decision"], "block")
        self.assertEqual(call("Stop", stop_hook_active=True), {})
        self.assertNotIn("decision", call("Stop"))

        call("UserPromptSubmit")
        self.assertEqual(call("Stop"), {})
        self.assertEqual(list((self.temp / "claude-state/turns").glob("*.json")), [])

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

    def test_missing_baseline_warns_without_blocking(self):
        result = self.call("Stop")
        self.assertIn("no baseline", result["systemMessage"])
        self.assertNotIn("decision", result)

    def test_missing_event_fields_warn_without_exposing_event_values(self):
        for name in ("UserPromptSubmit", "Stop"):
            for field in self.event:
                with self.subTest(name=name, field=field):
                    result = self.call(name, **{field: ""})
                    warning = result["systemMessage"]
                    self.assertIn(field, warning)
                    self.assertNotIn(str(self.root), warning)
                    self.assertNotIn("decision", result)

    def test_budget_exceeded_warns(self):
        with patch.object(hook, "MAX_FILES", 0):
            self.write("main.py", "new")
            result = self.call("UserPromptSubmit")
        self.assertIn("unavailable", result["hookSpecificOutput"]["additionalContext"])

    def test_english_and_french_requests_follow_the_same_checks(self):
        cases = [
            ("en", "Add a greeting", "Run python main.py for a greeting."),
            ("fr", "Ajoute un message d'accueil", "Lancer python main.py pour un message d'accueil."),
        ]
        for language, prompt, document in cases:
            with self.subTest(language=language):
                self.event["turn_id"] = language
                self.call("UserPromptSubmit", prompt=prompt)
                self.write("main.py", language)
                self.write("README.md", document)
                self.assertIsNone(self.call("Stop"))
                self.assertEqual((self.root / "README.md").read_text(encoding="utf-8"), document)
                state = hook.state_path(self.event, self.root).read_text(encoding="utf-8")
                self.assertNotIn(prompt, state)

    def test_english_request_does_not_rewrite_french_documents(self):
        document = "# Projet\nComment commencer : lancer python main.py."
        self.write("README.md", document)
        self.call("UserPromptSubmit", prompt="Fix the internal counter")
        self.write("main.py", "counter = 0")
        self.assert_blocked()
        self.assertEqual((self.root / "README.md").read_text(encoding="utf-8"), document)
        self.assertIsNone(self.call("Stop", stop_hook_active=True))

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

    @unittest.skipUnless(shutil.which("git"), "Git unavailable")
    def test_commands_share_baseline_and_trace_a_single_continuation(self):
        def run(name):
            process = subprocess.run(
                [os.sys.executable, str(ROOT / "hooks/documentation.py")],
                input=json.dumps({**self.event, "hook_event_name": name}),
                text=True, capture_output=True, check=True,
                env={**os.environ, "PROJECTDOC_DEBUG": "1"},
            )
            return json.loads(process.stdout)

        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.write("tmp_trigger.txt", "existing\n")
        start = run("UserPromptSubmit")
        self.assertEqual(start["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
        self.assertIn("baseline saved", start["systemMessage"])
        self.write("tmp_trigger.txt", "existing \n")
        stop = run("Stop")
        self.assertEqual(stop["decision"], "block")
        self.assertIn("documentation review requested", stop["systemMessage"])
        repeat = run("Stop")
        self.assertIn("review already requested", repeat["systemMessage"])
        self.assertNotIn("decision", repeat)


if __name__ == "__main__":
    unittest.main()
