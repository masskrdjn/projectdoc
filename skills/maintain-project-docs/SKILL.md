---
name: maintain-project-docs
description: Create or update concise project documentation during development or handover. Invoke on its own to document an undocumented project or review pending changes. Specify a scope to limit the review.
---

# Accessible project documentation

Write for someone who is new to the project or taking it over. Help them
understand what it does, get started, and find their next step without reading
the code. Use plain words and short sentences. Explain necessary technical terms
on first use. Leave out filler, file inventories, and accounts of the work session.

## Language

Reply in the language of the user's request or conversation. The language of
this skill does not set the response language. No language selection is needed.

For documentation, follow an explicit user request, then any project language
rules. Otherwise keep each existing document in its language. Write new pages
in the language of the surrounding documentation. If the project has no
documentation, use the user's language, with English as a fallback when it is
unclear. If the project already maintains translations, update the affected
versions together. Do not create new translations unless asked.

For example, an English request to change a French project gets an English
reply and French documentation updates. A new project requested in English
gets an English README unless the user or project specifies another language.

## Before and after development

Before editing, find the documentation entry point and read the affected pages.
Follow the project's instructions and existing structure. After development,
compare the documentation with the delivered behavior and verified commands.
Update only the affected explanations: usage, setup, configuration, interfaces,
how it works, or what someone needs to take over.

If documentation is missing, create a root README.md even for a small change.
Use the code and available evidence; identify important gaps without inventing
working procedures. If an internal fix leaves existing explanations accurate,
say briefly why no documentation change is needed. Do not edit accurate pages
just to satisfy the check.

## Standalone documentation review

When the user asks for a documentation review or invokes this skill on its own,
first locate the existing reader documentation and establish the scope. If the
user names a feature, file, or other boundary, follow it.

If the user gives no scope and the project has no reader documentation, review
the project as a whole, even if there are pending changes. Use its structure,
configuration and entry points to identify its purpose, main components and
workflows. Create a root README covering prerequisites, setup and ordinary
usage. Add detail pages where needed.

For a project with existing reader documentation and no explicit scope, review
all pending Git changes, including changes already present before the request.
Use `git status --short --untracked-files=all`
to inventory them, `git diff` and `git diff --cached` to inspect unstaged and
staged changes, and read relevant non-ignored untracked files directly.
The current branch name does not narrow the review. With a clean working tree,
review the current documentation against the project; only use commit history
as a review range when the user asks for it.

Before editing, group the changes by behavior and check the existing docs for
each group. Update explanations that are missing or out of date. A group may
already be covered or may have no effect on readers; do not edit docs for those
groups just to show activity. Leave the underlying changes alone.

Before finishing, account for every group in scope: say what you updated, what
needed no update and why, and what you could not verify. Editing one page does
not complete the review if other groups still need to be checked.

When this skill is loaded for a development task or a hook reminder, review the
documentation affected by that task. Unrelated pending work is outside that
review unless the user includes it.

## Placement and navigation

- Keep existing locations, including a documentation site or custom directory.
  Avoid duplicate sources of truth and unnecessary moves.
- Default to README.md for the entry point: purpose, quick start, and links to
  further help. A single page is enough for a simple project.
- Use docs/ when a topic needs a separate page. Link each page from the README
  or an index and provide a route back. Prefer versioned relative links.
- Use AGENTS.md for Codex instructions and .agents/ for agent resources.
- For handover, include the essential commands, settings, and dependencies.
  Explain maintenance decisions or limitations when they are otherwise unclear.

## Useful diagrams

Add a diagram when it makes a workflow, relationship, or flow of data easier
to follow than a short paragraph. Use plain labels and few elements.

Choose Mermaid for a simple diagram when the reading surface can render it.
Choose a local SVG for precise layout, export, or readers without Mermaid.
Store SVGs under docs/assets/ or the existing equivalent, add descriptive alt
text, and keep them free of scripts and external resources. Provide a short
text explanation in either case. Avoid maintaining two copies of one diagram.

## Final check

Read it as a newcomer: are the purpose, first step, and links clear? Do the
examples match the change? Check the relevant links and commands when possible.
Render diagrams using the project's existing tools if available; otherwise
mention that rendering was not verified. Do not copy secrets or personal data.
Do not publish documents or change sharing permissions.

The hook reminds Codex to review documentation and compares file changes.
It cannot judge the text. If it requests a continuation, complete the review
and finish, mentioning any actual limits.
