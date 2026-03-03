---
name: documentation
description: Create or improve documentation by routing to the right approach. Handles code comments (inline audit/cleanup), system docs (READMEs, API docs, architecture), and templates. Use when writing, auditing, or improving any form of documentation.
argument-hint: "<file-path-or-doc-type>"
---

# Documentation

Route documentation tasks to the right reference and execution path.

## Routing

Determine the task type from arguments and context, then load the matching reference:

| Signal | Task type | Load | Execute with |
|--------|-----------|------|--------------|
| Source file path (`.ts`, `.js`, `.py`, `.go`, `.rs`, etc.) | Code comments | [references/code-comments.md](references/code-comments.md) | `@ce:haiku` agent |
| Mentions "comments", "inline docs", "code comments" | Code comments | [references/code-comments.md](references/code-comments.md) | `@ce:haiku` agent |
| "Clean up comments" in a folder or unstaged changes | Code comments | [references/code-comments.md](references/code-comments.md) | `@ce:haiku` agent |
| Markdown file path (`.md`) | System docs | [references/systems.md](references/systems.md) | General subagent |
| Mentions README, API docs, architecture, `/docs/` | System docs | [references/systems.md](references/systems.md) | General subagent |
| Multi-file scope or new documentation | System docs | [references/systems.md](references/systems.md) | General subagent |
| Ambiguous | - | Ask user to clarify scope | - |

## Execution

### Code comments (delegate to `@ce:haiku`)

Pass these instructions when delegating:

1. Read target file(s) completely, identify language and patterns
2. Audit comments using the code-comments reference checklist
3. Apply fixes: remove unnecessary comments, rewrite unclear ones
4. Report changes: summarize removals, rewrites, and suggested refactors
5. For multi-file requests, find changed files via `git status -s` or scope to the folder specified

Scope: only inline code comments. If asked about markdown/README/docs content, switch to system docs path.

### System docs (spawn general subagent)

Pass these instructions when delegating:

**API Documentation:**
1. Read source files, types, route definitions, error handling paths
2. Plan structure using progressive disclosure layers from the systems reference
3. Write `{resource-name}.md` in `/docs/api/`
4. Cross-reference related endpoints and guides

**README Updates:**
1. Audit existing README.md, package.json, configs, entry points
2. Update: quick start within first 30 lines, installation, config, links to `/docs`
3. Verify all code examples are runnable

**Architecture Documentation:**
1. Read core modules, trace dependencies, identify design decisions
2. Document decisions focusing on WHY, not just WHAT
3. Add diagrams using `Skill(ce:visualizing-with-mermaid)` for flows
4. Write docs in `/docs/architecture/`

For writing style and tone, use `Skill(ce:writer)` with **The Engineer** persona.

### Location standards

| Doc Type | Location | Filename Pattern |
|----------|----------|------------------|
| Project overview | Root | `README.md` |
| API reference | `/docs/api/` | `{resource-name}.md` |
| Architecture | `/docs/architecture/` | `{topic}.md` |
| Guides/How-to | `/docs/guides/` | `{topic}.md` |

## Examples

| Input | Routes to |
|-------|-----------|
| `/documentation src/utils/auth.ts` | Code comments |
| `/documentation clean up comments in unstaged changes` | Code comments |
| `/documentation README` | System docs |
| `/documentation API docs for /users endpoint` | System docs |
| `/documentation architecture overview` | System docs |
