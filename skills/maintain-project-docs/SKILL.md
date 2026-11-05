---
name: maintain-project-docs
description: Create or update concise project documentation when implementing features, fixing bugs, or changing setup, configuration, interfaces or architecture. Also use for project documentation and handover requests.
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
