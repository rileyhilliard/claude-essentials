# Skill Authoring

Best practices for creating Claude Code skills, synthesized from Anthropic's official documentation and patterns proven across 20+ production skills.

## File Structure

```
your-skill-name/
├── SKILL.md          # Required - main instructions
├── references/       # Optional - detailed docs (loaded on demand)
├── scripts/          # Optional - executable code
└── assets/           # Optional - templates, fonts, icons
```

- `SKILL.md` must be exactly this casing (not `skill.md`, not `SKILL.MD`)
- No `README.md` inside the skill folder
- All documentation goes in `SKILL.md` or `references/`

## Naming

| Rule | Example |
|------|---------|
| Gerund form preferred | `writing-tests`, `managing-databases`, `configuring-claude` |
| Kebab-case only | `notion-project-setup` not `NotionProjectSetup` |
| Max 64 characters | Keep it descriptive but concise |
| No reserved words | Cannot contain "claude" or "anthropic" |
| Match folder name | Folder `writing-tests/` -> name: `writing-tests` |

## Description

The description is how Claude decides whether to load your skill. It's the most important field.

**Formula:** `[What it does] + [When to use it] + [Key capabilities]`

**Constraints:** Max 1024 characters, no XML angle brackets, third person only.

| Quality | Example |
|---------|---------|
| Good | "Writes behavior-focused tests using Testing Trophy model with real dependencies. Use when writing tests, choosing test types, or avoiding anti-patterns like testing mocks." |
| Good | "Guides database architecture decisions for PostgreSQL, DuckDB, and Parquet. Use when designing schemas, choosing storage strategies, or optimizing queries." |
| Bad | "Helps with testing." |
| Bad | "Creates sophisticated multi-page documentation systems." (no triggers) |

Include specific phrases users might say and mention relevant file types or technologies.

## Progressive Disclosure

Skills use three levels to minimize token usage:

| Level | What | When loaded | Token cost |
|-------|------|-------------|------------|
| **1. Frontmatter** | name + description | Always (system prompt at startup) | Always paid |
| **2. SKILL.md body** | Full instructions | When Claude thinks skill is relevant | Paid on activation |
| **3. Reference files** | Detailed docs, examples | When Claude navigates to them | Paid on demand |

This means your description carries the most weight per token. Get it right.

## Body Structure

Proven pattern from existing skills:

1. **Core principle** - Bold opener establishing the "why" (1-2 sentences)
2. **Topic/decision table** - Routes to references based on the task at hand
3. **Universal principles** - Rules that apply regardless of subtopic
4. **Anti-patterns** - Table of common mistakes and why they fail
5. **Cross-references** - Links to complementary skills

**Size targets:**
- SKILL.md: Under 500 lines / ~4000 words (Anthropic recommends 500 lines max)
- Reference files: 20-120 lines each, focused on one subtopic
- Keep references one level deep from SKILL.md (no reference-to-reference chains)

## Degrees of Freedom

Match instruction specificity to the task's fragility:

**High freedom** (multiple valid approaches):
```markdown
## Code Review
1. Analyze code structure and organization
2. Check for potential bugs or edge cases
3. Suggest improvements for readability
```

**Low freedom** (fragile, must be exact):
```markdown
## Database Migration
Run exactly: `python scripts/migrate.py --verify --backup`
Do not modify the command or add flags.
```

Provide a sensible default when multiple approaches exist. "Use pdfplumber for extraction. For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."

## Testing

### Trigger testing

Run 10-20 test queries that should activate your skill. Track hit rate.

```
Should trigger:
- "Help me write a new skill for project management"
- "Create CLAUDE.md rules for our team"

Should NOT trigger:
- "What's the weather?"
- "Help me write Python code"
```

### Iteration signals

| Signal | Diagnosis | Fix |
|--------|-----------|-----|
| Skill never loads automatically | Description too vague or missing triggers | Add specific trigger phrases and key terms |
| Skill loads for unrelated queries | Description too broad | Add scope boundaries, be more specific |
| Claude doesn't follow instructions | Instructions buried or too verbose | Put critical rules first, use tables, move detail to references |
| Inconsistent results across sessions | Ambiguous language | Replace "make sure to validate properly" with exact validation steps |

## YAML Frontmatter Reference

**Required fields:**
```yaml
---
name: skill-name          # kebab-case, max 64 chars
description: What and when  # max 1024 chars, no XML tags
---
```

**Optional fields:**
```yaml
license: MIT                    # For open-source skills
compatibility: "Claude Code"    # Environment requirements (max 500 chars)
metadata:                       # Custom key-value pairs
  author: Your Name
  version: 1.0.0
  mcp-server: server-name
```

**Security:** No XML angle brackets (`<` or `>`) in frontmatter. Frontmatter appears in Claude's system prompt, so malicious content could inject instructions.
