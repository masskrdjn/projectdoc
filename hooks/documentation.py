#!/usr/bin/env python3
"""Codex hooks: capture a turn baseline, then request one documentation review.

No model calls, source writes, transcript parsing, or network access.
Only file names and content hashes are persisted in PLUGIN_DATA.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

SKILL = Path(__file__).resolve().parents[1] / "skills/maintain-project-docs/SKILL.md"
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".next", ".cache"}
DOC_DIRS = {"docs", "doc", "documentation", "guide", "guides", "handbook"}
TEXT_DOCS = {".md", ".mdx", ".rst", ".adoc"}
MAX_FILES = 15000
MAX_BYTES = 128 * 1024 * 1024
LANGUAGE_POLICY = (
    "Follow the user's conversation language for replies and explanations; "
    "the English wording of these internal instructions is not a language preference. "
    "For documentation, follow explicit user requirements, then project language rules. "
    "Otherwise preserve each document's language and match it for related new pages. "
    "If no documentation exists, use the user's language, falling back to English. "
    "If the project already maintains multiple languages, keep affected translations "
    "consistent. Do not add translations or a language selection step unless requested."
)
CONTEXT = (
    "ProjectDoc: for development tasks, read the skill at "
    f"{SKILL.as_posix()} before making changes. Find existing documentation, "
    "then create it if missing or update affected explanations before finishing. "
    "Keep its existing structure; default to README.md for the entry point and "
    "docs/ for details. Write for someone new to the project: plain words, short "
    "text, clear setup steps and easy navigation. Add Mermaid or SVG only when "
    "helpful, with a text explanation. An internal fix may need no documentation "
    "change: explain that briefly. Read-only tasks require no new files. "
    + LANGUAGE_POLICY
)


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], stderr=subprocess.DEVNULL, timeout=8
    )


def project_root(cwd: Path) -> tuple[Path, bool]:
    try:
        root = Path(os.fsdecode(git(cwd, "rev-parse", "--show-toplevel")).strip())
        return root.resolve(), True
    except (OSError, subprocess.SubprocessError):
        return cwd.resolve(), False


def is_doc(name: str) -> bool:
    path = Path(name)
    # Instructions are executable plugin/agent inputs, not reader documentation.
    if path.name.lower() in {"agents.md", "agents.override.md", "skill.md"}:
        return False
    if any(part.startswith(".") or part == "skills" for part in path.parts[:-1]):
        return False
    return path.suffix.lower() in TEXT_DOCS or any(
        part.lower() in DOC_DIRS for part in path.parts[:-1]
    )


def candidates(root: Path, use_git: bool):
    if use_git:
        names = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
        yield from sorted(set(os.fsdecode(item) for item in names.split(b"\0") if item))
    else:
        # Fallback for a new project with no Git repository. Never follow links.
        for directory, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in SKIP and not (Path(directory) / d).is_symlink())
            for name in sorted(files):
                yield (Path(directory) / name).relative_to(root).as_posix()


def snapshot(root: Path, use_git: bool) -> dict:
    result: dict = {"code": {}, "docs": {}, "readable_docs": False}
    total = 0
    count = 0
    for name in candidates(root, use_git):
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            continue
        path = root / relative
        if any(p in SKIP for p in relative.parts):
            continue
        # Also avoid traversing a linked parent, including Windows junctions.
        parents = [path, *list(path.parents)[:len(relative.parts) - 1]]
        if any(p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction()) for p in parents):
            continue
        if not path.is_file():
            continue
        count += 1
        total += path.stat().st_size
        if count > MAX_FILES or total > MAX_BYTES:
            raise ValueError("project exceeds the snapshot reading budget")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(65536), b""):
                digest.update(chunk)
        group = "docs" if is_doc(name) else "code"
        # Empty documents are not enough to establish documentation presence.
        if group == "docs" and path.stat().st_size == 0:
            continue
        result[group][relative.as_posix()] = digest.hexdigest()
        if group == "docs" and path.suffix.lower() in TEXT_DOCS:
            with path.open("rb") as stream:
                if stream.read(65536).strip():
                    result["readable_docs"] = True
    return result


def state_path(event: dict, root: Path) -> Path:
    session = event.get("session_id")
    turn = event.get("turn_id")
    if not isinstance(session, str) or not session or not isinstance(turn, str) or not turn:
        raise ValueError("missing session or turn identifier")
    base = Path(os.environ.get("PLUGIN_DATA") or (Path(tempfile.gettempdir()) / "codex-projectdoc"))
    base = base / "turns"
    base.mkdir(parents=True, exist_ok=True)
    if base.is_symlink() or (hasattr(base, "is_junction") and base.is_junction()):
        raise ValueError("linked state directory")
    key = hashlib.sha256(json.dumps([str(root), session, turn]).encode()).hexdigest()
    return base / f"{key}.json"


def save(path: Path, data: dict) -> None:
    # Replace rather than follow an existing state-file link. Isolate concurrent writes.
    handle, temp = tempfile.mkstemp(dir=path.parent, prefix=".projectdoc-")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=True)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def context(message: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": message}}


def handle(event: dict) -> dict | None:
    name = event.get("hook_event_name")
    if name not in {"UserPromptSubmit", "Stop"}:
        return None
    if name == "Stop" and event.get("stop_hook_active") is True:
        return None
    try:
        cwd = event.get("cwd")
        if not isinstance(cwd, str) or not Path(cwd).is_dir():
            raise ValueError("missing working directory")
        root, use_git = project_root(Path(cwd))
        path = state_path(event, root)
        if name == "UserPromptSubmit":
            before = snapshot(root, use_git)
            save(path, {"before": before, "created": time.time(), "blocked": False})
            return context(CONTEXT)
        if not path.is_file() or path.is_symlink():
            raise ValueError("turn baseline unavailable")
        state = json.loads(path.read_text(encoding="utf-8"))
        if state.get("blocked"):
            return None
        after = snapshot(root, use_git)
        before = state["before"]
        if before["code"] == after["code"]:
            return None
        if after["readable_docs"] and before["docs"] != after["docs"]:
            return None
        # Once per turn, even if a runtime omits stop_hook_active on continuation.
        state["blocked"] = True
        save(path, state)
        return {"decision": "block", "reason": (
            "ProjectDoc: project files changed during this task without a detected "
            "documentation update. Read the skill at " + SKILL.as_posix() +
            ". Review documentation now; create it if missing (README.md by default), "
            "or update only affected explanations. If existing documents remain "
            "accurate, briefly explain why no update is needed. Do not make "
            "artificial edits. Then finish; this check will not request a second "
            "continuation. " + LANGUAGE_POLICY
        )}
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        warning = ("ProjectDoc: automatic check unavailable; review documentation "
                   "using the skill. No automatic validation was completed. " + LANGUAGE_POLICY)
        if name == "UserPromptSubmit":
            return context(CONTEXT + "\n" + warning)
        return {"systemMessage": warning}


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError("event too large")
        event = json.loads(raw)
        if not isinstance(event, dict):
            raise ValueError("invalid event")
        output = handle(event)
    except (ValueError, TypeError):
        output = {"systemMessage": "ProjectDoc: invalid event; check not performed."}
    if output:
        print(json.dumps(output, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
