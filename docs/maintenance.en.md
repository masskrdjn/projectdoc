# Maintain ProjectDoc

[Back to the README](../README.en.md) · [Français](maintenance.md)

The skill tells Codex how to write documentation. Two hooks, small programs
that Codex runs during a task, remind it of the rules and check for omissions.

| File | Purpose |
| --- | --- |
| `plugin.json` | Plugin name, version, and components. |
| `.agents/plugins/marketplace.json` | Plugin catalog supplied by the GitHub repository. |
| `AGENTS.md` | Coding, documentation, and version rules. |
| `CHANGELOG.md` | Changes by version. |
| `skills/maintain-project-docs/SKILL.md` | Writing and layout rules. |
| `hooks/hooks.json` | When Codex runs the checks. |
| `hooks/documentation.py` | File comparison and review requests. |
| `tests/test_documentation.py` | Tests for hook behavior. |

## How the checks work

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

## Verify and release a change

Run `python -m unittest discover -s tests -v`. The tests cover new and changed
documentation, file deletion, read-only tasks, the single continuation limit,
Git exclusions, and checks with English and French requests.

To check language behavior in Codex, install the plugin and approve its hooks.
Request the same small change in English and French in two projects without
documentation. Check that each reply and README use the language of its request.
Then make an English request in a project with French docs: the reply should be
in English and the documentation update in French. Python tests check the hook
logic; they do not verify how Codex writes the resulting documents.

Before each release, increment the version in `plugin.json` and record the
change in `CHANGELOG.md` as described in `AGENTS.md`. Keep both guides aligned.

References: [Codex hooks](https://developers.openai.com/codex/hooks),
[plugin format](https://developers.openai.com/plugins/build/plugins), and
[AGENTS.md instructions](https://developers.openai.com/codex/guides/agents-md).
