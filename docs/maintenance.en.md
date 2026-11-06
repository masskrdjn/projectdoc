# Maintain ProjectDoc

[Back to the README](../README.en.md) · [Français](maintenance.md)

The skill tells Codex how to write documentation. Two hooks, small programs
that Codex runs during a task, remind it of the rules and check for omissions.

| File | Purpose |
| --- | --- |
| `.codex-plugin/plugin.json` | Codex manifest: plugin name, version, and components. |
| `.agents/plugins/marketplace.json` | Plugin catalog supplied by the GitHub repository. |
| `AGENTS.md` | Coding, documentation, and version rules. |
| `CHANGELOG.md` | Changes by version. |
| `skills/maintain-project-docs/SKILL.md` | Writing and layout rules. |
| `hooks/hooks.json` | When Codex runs the checks. |
| `hooks/documentation.py` | File comparison and review requests. |
| `tests/test_documentation.py` | Tests for hook behavior. |

## Claude Code plugin

The catalog at `.claude-plugin/marketplace.json` installs the
`plugins/projectdoc-claude/` directory. That directory contains the Claude Code
manifest and hook configuration, plus copies of the shared script and skill.
Edit the originals at the repository root and run
`python scripts/sync_claude_plugin.py`. The tests check that the copies match.

Claude Code replaces the baseline at each prompt and consumes it at the stop
check. State is scoped to the project and session in `CLAUDE_PLUGIN_DATA/turns/`
or the temporary `claude-projectdoc/turns/` directory.

From the repository root, validate the catalog with `claude plugin validate .`
and load the local plugin with `claude --plugin-dir ./plugins/projectdoc-claude`.
In a disposable project, check both events in `/hooks`, request a code change,
and check that the plugin asks for a review at most once. See the
[Claude Code hooks reference](https://code.claude.com/docs/en/hooks).

## How the Codex checks work

At the start of a request (`UserPromptSubmit`), the first hook records file
fingerprints: values that change when file contents change. It gives Codex the
skill path and language rules. Codex uses the conversation and existing documents
to decide which language to write in. The script does not detect language, save
the request, or require a language setting.

Before Codex finishes (`Stop`), the second hook compares file fingerprints. If
files outside the documentation changed while documentation stayed the same or
is missing, it asks Codex to review the docs. A blank page or a diagram alone
does not count as readable documentation. The hook repeats the language rules
on a continuation and requests at most one continuation per task. The check
cannot tell whether the text is accurate; Codex still needs to read it.

## Standalone documentation review

If the project has no reader documentation and the user gives no scope, the
skill reviews the whole project and creates a README, even when Git has
pending changes.

If documentation exists and the user gives no scope, the skill reviews all
pending Git changes:
staged changes, unstaged changes, and untracked files Git does not ignore.
Codex identifies the affected behaviors and explains what it updated or why
no update was needed for each one. If the user names a specific area, the
review stays within it.

With a clean working tree and no explicit scope, the skill follows the
handover path from the README. It checks setup, key components and workflows,
and how to validate them. Where technical pages exist, it reads a sample and
checks which pages still describe the current project. The summary names the
pages read, what they cover, any limits, and why pages were edited, linked,
or left as they were.

The `Stop` hook remains a reminder for changes made during the turn. It does
not verify that the edited pages cover every affected behavior.

## Scope and limits

- In a Git repository, the check covers tracked files and new files Git does not
  ignore, starting from the repository root. It does not attribute existing
  changes to the current task. Work on a submodule in its own task.
- Without Git, run tasks from the project root. The check covers that directory
  and its subdirectories, skipping common dependency and cache directories.
  It does not follow links to files or directories.
- The check recognizes `.md`, `.mdx`, `.rst`, `.adoc` and files in `docs/`, `doc/`,
  `documentation/`, `guide/`, `guides/`, or `handbook/`. `AGENTS.md`,
  `AGENTS.override.md`, `SKILL.md`, hidden directories, and `skills/` do not count
  as reader documentation. The skill can still use other documentation locations.
- Each comparison is limited to 15,000 files or 128 MiB. Git commands time out
  after 8 seconds, and each hook after 20 seconds. If a check is unavailable,
  Codex should review the documentation itself.
- Changes made by another tool during the task can appear in the comparison.
  Changes outside a Codex task do not trigger a check on their own.

The hook does not edit source files, read conversations, call a model, or contact
a service. It stores file names, fingerprints, and timestamps for each task in
`PLUGIN_DATA/turns/`, or in `codex-projectdoc/turns/` under the temporary directory
when `PLUGIN_DATA` is unavailable. Completed tasks' state can be removed.

## Troubleshoot the hooks

In **Settings > Hooks**, check that both ProjectDoc hooks are listed and trusted.
To see their decisions, start Codex with `PROJECTDOC_DEBUG=1` in the launching
process's environment. Traces appear as Codex warnings and include no IDs,
paths, or file contents. Remove the variable and restart to turn them off.

In a disposable Git repository, prepare a tracked `.txt` file, then ask Codex
to add one trailing space without other edits. Look for `baseline saved` at the
start and `documentation review requested` at the end, followed by one
continuation. If `Stop` reports `no baseline`, check for the start trace in the
same turn. Warnings name missing fields. If no trace appears at all, check
hook approval and whether Codex can launch Python.

## Verify and release a change

Run `python -m unittest discover -s tests -v`. The tests cover new and changed
documentation, file deletion, read-only tasks, the single continuation limit,
Git exclusions, and checks with English and French requests.

An isolated installation of version 0.2.1 confirmed that Codex detects both
hooks. A full run in the desktop app still needs to be checked after approval.

To check the desktop workflow, follow the [Codex installation steps](../README.en.md#install-in-codex)
and approve the hooks. In a disposable project, request a new function and
check that Codex creates a README. Then request a change to how the function
is used and check that Codex updates the README. A request for an explanation
should leave the project files untouched.

To check the skill's scope, prepare three independent changes before starting
a new chat: a staged PDF change, an unstaged mail change, and an untracked
classification file. Make the mail and classification docs accurate and the
PDF docs outdated. Invoke the skill on its own: it should fix the PDF docs and
report on all three areas. Repeat on a copy with a request limited to PDFs:
only PDFs should be in the review summary.

To replay the CodeSlice AI case, prepare a clean test copy at commit
`5f15453` (version 1.6.0) and invoke the skill on its own without naming a file.
The scenario passes if the summary cites technical pages the assistant read,
places the 1.5.0 harness audit in the context of the 1.6.0 editing workflow,
and assesses how readers find guidance on architecture, editing, and validation.
Check that it distinguishes Node tests, checks in VS Code, offline simulations,
and evaluations with a real provider. The summary should explain each edit
location or why the existing pages are sufficient. Creating a file is optional.
This manual scenario checks whether the assistant follows the skill.

To check language behavior in Codex, install the plugin and approve its hooks.
Request the same small change in English and French in two projects without
documentation. Check that each reply and README use the language of its request.
Then make an English request in a project with French docs: the reply should be
in English and the documentation update in French. Python tests check the hook
logic; they do not verify how Codex writes the resulting documents.

Before each release, increment the version in both manifests
(`.codex-plugin/plugin.json` and `plugins/projectdoc-claude/.claude-plugin/plugin.json`).
Record the change in the [changelog](../CHANGELOG.md) as described in
[AGENTS.md](../AGENTS.md). Keep both guides aligned.

References: [Codex hooks](https://developers.openai.com/codex/hooks),
[plugin format](https://developers.openai.com/plugins/build/plugins), and
[AGENTS.md instructions](https://developers.openai.com/codex/guides/agents-md).
