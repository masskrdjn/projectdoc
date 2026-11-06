"""Sync shared ProjectDoc files into the standalone Claude Code plugin."""

from pathlib import Path
from shutil import copyfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/projectdoc-claude"
SHARED_FILES = ("hooks/documentation.py", "skills/maintain-project-docs/SKILL.md")


if __name__ == "__main__":
    for name in SHARED_FILES:
        target = PLUGIN / name
        target.parent.mkdir(parents=True, exist_ok=True)
        copyfile(ROOT / name, target)
