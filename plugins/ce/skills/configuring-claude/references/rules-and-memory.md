# Rules and Memory

Best practices for CLAUDE.md files, `.claude/rules/`, and auto memory.

## Memory Hierarchy

More specific instructions take precedence over broader ones. All CLAUDE.md files in the directory hierarchy above the working directory load at launch. Files in child directories load on demand.

| Type | Location | Shared with | Use for |
|------|----------|-------------|---------|
| **Managed policy** | `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS) | All org users | Company-wide standards, security policies |
| **Project** | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team (via git) | Project architecture, coding standards, common commands |
| **Project rules** | `./.claude/rules/*.md` | Team (via git) | Modular, topic-specific guidelines |
| **User** | `~/.claude/CLAUDE.md` | Just you (all projects) | Personal preferences, tool shortcuts |
| **Local project** | `./CLAUDE.local.md` | Just you (this project) | Sandbox URLs, personal test data (auto-gitignored) |
| **Auto memory** | `~/.claude/projects/<project>/memory/` | Just you (per project) | Claude's own notes, patterns, debugging insights |

## Writing CLAUDE.md

### Be specific

| Good | Bad |
|------|-----|
| "Use 2-space indentation" | "Format code properly" |
| "Run `npm test -- --coverage` before commits" | "Make sure tests pass" |
| "Use PostgreSQL array columns for tags, not junction tables" | "Design the database well" |

### Structure for scanning

- Format each instruction as a bullet point
- Group related instructions under descriptive markdown headings
- Include frequently used commands (build, test, lint) to avoid repeated searches
- Document code style, naming conventions, and architectural patterns

### Imports

Pull in external files with `@path/to/file` syntax:

```markdown
See @README for project overview and @package.json for npm commands.

# Git Workflow
- Follow @docs/git-instructions.md
```

Relative paths resolve from the file containing the import. Max depth: 5 hops. Imports aren't evaluated inside code blocks.

### CLAUDE.local.md

For private project preferences that shouldn't be committed. Auto-added to `.gitignore`. Use for sandbox URLs, personal test data, individual workflow shortcuts.

For shared instructions across worktrees, use a home-directory import instead:
```markdown
# Individual Preferences
- @~/.claude/my-project-instructions.md
```

## Modular Rules (.claude/rules/)

Organize instructions into focused files instead of one large CLAUDE.md.

### Structure

```
.claude/rules/
├── code-style.md       # Formatting, naming conventions
├── testing.md          # Test patterns, coverage requirements
├── security.md         # Auth, input validation, secrets
├── frontend/
│   ├── react.md        # Component patterns
│   └── styles.md       # CSS conventions
└── backend/
    ├── api.md          # Endpoint design
    └── database.md     # Query patterns, migrations
```

All `.md` files are discovered recursively. Subdirectories for organization. Symlinks supported for sharing rules across projects.

### Path-specific rules

Scope rules to specific files using YAML frontmatter:

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "lib/**/*.ts"
---

# API Development Rules
- All endpoints must include input validation
- Use the standard error response format
```

Rules without a `paths` field apply unconditionally to all files. Use path-specific rules sparingly, only when rules genuinely apply to specific file types.

Supported glob patterns: `**/*.ts`, `src/**/*`, `*.md`, `src/components/*.tsx`, `src/**/*.{ts,tsx}`, `{src,lib}/**/*.ts`

## Auto Memory

Claude automatically saves useful context as it works. Located at `~/.claude/projects/<project>/memory/`.

```
memory/
├── MEMORY.md           # Index file (first 200 lines loaded at startup)
├── debugging.md        # Detailed debugging notes
├── api-conventions.md  # API design decisions
└── patterns.md         # Project patterns
```

**Key constraints:**
- Only the first 200 lines of `MEMORY.md` are loaded at startup
- Topic files are read on demand, not at startup
- Organize semantically by topic, not chronologically
- Keep `MEMORY.md` concise by moving detail into topic files

**What belongs in auto memory:** Project patterns confirmed across sessions, key architecture decisions, debugging insights, user workflow preferences.

**What doesn't:** Session-specific context, unverified conclusions, anything that duplicates CLAUDE.md.
