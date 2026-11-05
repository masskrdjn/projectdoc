# ProjectDoc

English · [Français](README.md)

ProjectDoc helps Codex keep project documentation short and useful. It creates
missing documentation and updates affected explanations as the project changes.
Someone new to the project can see what it does and how to get started without
reading the code first.

ProjectDoc is for Codex. Install it from the private GitHub repository
[masskrdjn/projectdoc](https://github.com/masskrdjn/projectdoc).

## Install in Codex

You need Codex desktop with plugin and hook support, Git, and Python 3.10 or
later available as `python`. The GitHub account used by Git needs access to
the private repository. Set up that connection first if needed; keep access
tokens out of commands and project files.

From any directory, add the GitHub marketplace and install ProjectDoc:

```powershell
codex plugin marketplace add https://github.com/masskrdjn/projectdoc.git --ref main
codex plugin add projectdoc@projectdoc
```

Restart Codex, open the plugin directory, and check that **ProjectDoc** is
enabled. Review and approve its two hooks, which run at the start and end of a
task. The automatic check requires that approval. Then start a new task in the
project you want to work on.

These steps follow the [official Codex plugin guide](https://developers.openai.com/plugins/build/plugins).
For a new version, update the marketplace and plugin in the plugin manager,
restart Codex, and approve the hooks again if they changed.

## Use ProjectDoc

Ask Codex in English or French. No language setting is needed. Codex replies in
your language and keeps existing documents in theirs, unless you request a
different language. If the project has no documentation, Codex uses the language
of your request, falling back to English when unclear. Plugin labels are in English.

1. Codex finds the relevant documentation before development.
2. It makes the change and creates or updates the explanations people need.
3. If project files changed without a documentation update, ProjectDoc requests
   one more review before Codex finishes.

An internal fix may leave the documentation accurate. In that case, Codex can
briefly explain why no update is needed.

For a standalone documentation review, invoke the `maintain-project-docs`
skill directly. With no specified scope, it covers the whole project and
creates a README if there is no documentation. If documentation already
exists, it reviews pending Git changes and reports on each area of work.
Name a feature or file to limit the review.

If no check appears, open **Settings > Hooks** in Codex and follow the
[hook troubleshooting steps](docs/maintenance.en.md#troubleshoot-the-hooks).

## Where to find project documentation

ProjectDoc uses your existing layout. For a new project, it starts here:

| Location | What belongs there |
| --- | --- |
| `README.md` | Project purpose, quick start, and links. |
| `docs/` | Details that need their own page. |
| `docs/assets/` | SVG diagrams, when useful. |
| `AGENTS.md` and `.agents/` | Instructions and resources for Codex. |

Every page should be reachable from the README. Mermaid or SVG diagrams are
optional. Use them where they help, with a short explanation in text.

## Work on ProjectDoc

Read the [maintenance guide](docs/maintenance.en.md) for how the plugin works and
what it can check. From the repository root, run:

```powershell
python -m unittest discover -s tests -v
```
