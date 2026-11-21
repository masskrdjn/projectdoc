#!/usr/bin/env python3
"""Antigravity SessionStart hook: check for ProjectDoc plugin updates with a 2-hour TTL.

Read-only check against the plugin's Git repository using existing Git credentials.
Never modifies project files, calls a model, or sends user/project data.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import time

DEFAULT_REPO_URL = "https://github.com/masskrdjn/projectdoc"
TTL_SECONDS = 2 * 60 * 60
GIT_TIMEOUT_SECONDS = 5
MANIFEST_CANDIDATES = (".antigravity-plugin/plugin.json", "plugin.json")


def plugin_root() -> Path:
    configured = os.environ.get("PLUGIN_ROOT")
    if configured:
        candidate = Path(configured)
        if candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parents[1]


def _normalize_repo_url(raw: object) -> str:
    url = raw.get("url") if isinstance(raw, dict) else raw
    if not isinstance(url, str):
        return DEFAULT_REPO_URL
    cleaned = url.strip().rstrip("/")
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    if not cleaned.startswith("https://"):
        return DEFAULT_REPO_URL
    return cleaned


def read_local_manifest(root: Path) -> tuple[str, str] | None:
    for relative in MANIFEST_CANDIDATES:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if not isinstance(data, dict):
            return None
        version = data.get("version")
        if not isinstance(version, str) or not version.strip():
            return None
        return version.strip(), _normalize_repo_url(data.get("repository"))
    return None


def parse_version(value: str) -> tuple[int, ...] | None:
    cleaned = value.strip()
    if cleaned.startswith(("v", "V")):
        cleaned = cleaned[1:]
    parts = cleaned.split(".")
    if not parts or any(not part.isascii() or not part.isdigit() for part in parts):
        return None
    return tuple(int(part) for part in parts)


def is_newer(remote: str, local: str) -> bool:
    remote_parts = parse_version(remote)
    local_parts = parse_version(local)
    if remote_parts is None or local_parts is None:
        return False
    width = max(len(remote_parts), len(local_parts))
    remote_padded = remote_parts + (0,) * (width - len(remote_parts))
    local_padded = local_parts + (0,) * (width - len(local_parts))
    return remote_padded > local_padded


def _is_link(path: Path) -> bool:
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def cache_path() -> Path | None:
    base = Path(os.environ.get("PLUGIN_DATA") or (Path(tempfile.gettempdir()) / "antigravity-projectdoc"))
    base.mkdir(parents=True, exist_ok=True)
    if _is_link(base):
        return None
    path = base / "update-check.json"
    if _is_link(path):
        return None
    return path


def load_cache(path: Path) -> dict | None:
    if not path.is_file() or _is_link(path):
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def save_cache(path: Path, data: dict) -> None:
    # Atomic write prevents partial reads and avoids following an existing symlink.
    handle, temp = tempfile.mkstemp(dir=path.parent, prefix=".projectdoc-update-")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=True)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def _git_env() -> dict[str, str]:
    # Never prompt interactively inside a hook.
    return {**os.environ, "GIT_TERMINAL_PROMPT": "0"}


def _rmtree(path: Path) -> None:
    def _clear_readonly(func, target, _exc):
        os.chmod(target, stat.S_IWRITE)
        func(target)

    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_clear_readonly)
    else:
        shutil.rmtree(path, onerror=_clear_readonly)


def fetch_remote_sha(git_url: str) -> str | None:
    try:
        output = subprocess.check_output(
            ["git", "ls-remote", git_url, "refs/heads/main"],
            stderr=subprocess.DEVNULL,
            timeout=GIT_TIMEOUT_SECONDS,
            env=_git_env(),
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    first_line = output.strip().splitlines()[:1]
    if not first_line:
        return None
    sha = first_line[0].split()[0]
    return sha if sha else None


def fetch_remote_version(git_url: str) -> str | None:
    temp_dir = Path(tempfile.mkdtemp(prefix="projectdoc-update-"))
    env = _git_env()
    try:
        subprocess.run(
            ["git", "init", "-q", str(temp_dir)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=GIT_TIMEOUT_SECONDS,
            env=env,
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(temp_dir), "fetch", "-q", "--depth", "1", "--filter=blob:none", git_url, "refs/heads/main"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=GIT_TIMEOUT_SECONDS,
            env=env,
            check=True,
        )
        for relative in MANIFEST_CANDIDATES:
            result = subprocess.run(
                ["git", "-C", str(temp_dir), "show", f"FETCH_HEAD:{relative}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=GIT_TIMEOUT_SECONDS,
                env=env,
                text=True,
            )
            if result.returncode != 0:
                continue
            data = json.loads(result.stdout)
            if isinstance(data, dict) and isinstance(data.get("version"), str) and data["version"].strip():
                return data["version"].strip()
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    finally:
        if temp_dir.exists():
            _rmtree(temp_dir)
    return None


def resolve_remote_version(
    repo_url: str, cache: dict | None, now: float
) -> tuple[str | None, dict | None]:
    if cache and cache.get("repo_url") == repo_url:
        checked_at = cache.get("checked_at")
        if isinstance(checked_at, (int, float)) and 0 <= now - checked_at < TTL_SECONDS:
            cached_version = cache.get("remote_version")
            return (cached_version if isinstance(cached_version, str) else None), None

    git_url = repo_url if repo_url.endswith(".git") else f"{repo_url}.git"
    remote_sha = fetch_remote_sha(git_url)
    if not remote_sha:
        return None, None

    if (
        cache
        and cache.get("repo_url") == repo_url
        and cache.get("remote_sha") == remote_sha
        and isinstance(cache.get("remote_version"), str)
        and cache["remote_version"].strip()
    ):
        remote_version = cache["remote_version"].strip()
    else:
        remote_version = fetch_remote_version(git_url)
        if not remote_version:
            return None, None

    updated = {
        "checked_at": now,
        "remote_sha": remote_sha,
        "remote_version": remote_version,
        "repo_url": repo_url,
    }
    return remote_version, updated


def update_notice(local_version: str, remote_version: str, repo_url: str) -> dict:
    markdown = (
        f"**ProjectDoc**: update available (`{local_version}` -> `{remote_version}`). "
        f"Update with `agy plugin install {repo_url}`."
    )
    return {
        "injectSteps": [
            {
                "systemMessage": {
                    "systemMessage": "",
                    "metadata": {"user_markdown": markdown},
                }
            }
        ]
    }


def handle(event: dict, *, now: float | None = None, root: Path | None = None) -> dict:
    if os.environ.get("PROJECTDOC_NO_UPDATE_CHECK") == "1":
        return {}
    name = event.get("hookEventName")
    if name is not None and name != "SessionStart":
        return {}
    manifest = read_local_manifest(root or plugin_root())
    if manifest is None:
        return {}
    local_version, repo_url = manifest
    current_time = time.time() if now is None else now
    path = cache_path()
    cache = load_cache(path) if path is not None else None
    remote_version, updated_cache = resolve_remote_version(repo_url, cache, current_time)
    if updated_cache is not None and path is not None:
        try:
            save_cache(path, updated_cache)
        except OSError:
            pass
    if remote_version and is_newer(remote_version, local_version):
        return update_notice(local_version, remote_version, repo_url)
    return {}


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError("event too large")
        event = json.loads(raw) if raw.strip() else {}
        if not isinstance(event, dict):
            raise ValueError("invalid event")
        output = handle(event)
    except (OSError, ValueError, TypeError, subprocess.SubprocessError):
        output = {}
    print(json.dumps(output, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
