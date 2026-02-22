---
name: configuring-claude
description: Best practices for writing Claude Code skills, rules, and CLAUDE.md instructions. Use when creating SKILL.md files, authoring .claude/rules, writing CLAUDE.md project or user instructions, or configuring Claude behavior for a project or team.
---

# Configuring Claude

**Core principle:** The context window is a shared resource. Every token in your skill or rule competes with conversation history, other skills, and the user's actual request. Write the minimum instructions needed to change Claude's behavior from its defaults.

## Topic Selection

Load the relevant reference based on what you're configuring:

| Configuring... | Load | File |
|----------------|------|------|
| Skills (SKILL.md files, plugin skills) | **Skills** | `references/skills.md` |
| Rules, CLAUDE.md, memory | **Rules & Memory** | `references/rules-and-memory.md` |

Load both when creating a plugin that includes skills alongside project-level rules.

---

## Universal Principles

These apply whether you're writing a skill, a rule file, or CLAUDE.md instructions.

### Assume competence

Only add context Claude doesn't already have. Challenge each piece:
- "Does Claude need this explanation?"
- "Can I assume Claude knows this?"
- "Does this paragraph justify its token cost?"

| Good (~50 tokens) | Bad (~150 tokens) |
|---|---|
| "Use pdfplumber for text extraction" + code snippet | "PDF (Portable Document Format) files are a common format..." then background, then library comparison, then code |

### Be concrete

Specific instructions produce consistent behavior. Vague guidance produces inconsistent results.

| Concrete | Vague |
|----------|-------|
| `Run python scripts/validate.py --input {file}` | "Validate the data before proceeding" |
| "Use 2-space indentation, single quotes" | "Format code properly" |
| "Queries return in under 100ms" | "Robust performance" |

### Lead with the critical stuff

Put the most important rules first. Structure content so the highest-priority instructions appear early: opening paragraph, first table, first section heading. Bury critical rules in paragraph 4 and they'll get less attention.

### Use tables for decisions

Tables scan faster than prose. Use them for comparisons, decision trees, when-to-use logic, and anti-pattern lists. Reserve prose for reasoning and context that doesn't fit tabular format.

### Match freedom to fragility

Not every instruction needs the same level of specificity. Match it to how much damage a wrong choice causes.

| Freedom | Use when | Example |
|---------|----------|---------|
| **High** (text guidance) | Multiple valid approaches, context-dependent | Code review process, documentation style |
| **Medium** (templates/pseudocode) | Preferred pattern exists, some variation OK | Report generation, API response format |
| **Low** (exact commands) | Fragile operations, consistency critical | Database migrations, deployment scripts |

### Write in third person

Skill descriptions and rule content get injected into system prompts. Inconsistent point-of-view causes discovery problems.

- Good: "Processes Excel files and generates reports"
- Bad: "I can help you process Excel files"
- Bad: "You can use this to process Excel files"

---

## Anti-Patterns

| Pattern | Problem |
|---------|---------|
| Over-explaining basics Claude already knows | Wastes tokens, dilutes the instructions that matter |
| Vague descriptions ("Helps with projects") | Claude can't determine when to activate the skill |
| Deeply nested references (A -> B -> C) | Claude partially reads files past one level deep |
| Time-sensitive info ("After August 2025...") | Becomes silently wrong, use "current" vs "deprecated" sections |
| Multiple options without a default | Adds decision burden instead of reducing it |
| Instructions buried in prose paragraphs | Critical rules get missed, use headers and tables |
| Inconsistent terminology (mixing "endpoint", "URL", "route") | Confuses Claude about whether these are distinct concepts |
| Em dashes, emojis, corporate speak in instructions | Leaks into Claude's output style |

---

## Cross-References

- **Writing tone and style for config content:** Load `Skill(ce:writer)` with The Engineer persona for technical docs, or The Educator persona for tutorials and onboarding guides.
- **Documenting systems:** Load `Skill(ce:documenting-systems)` when the config involves creating README files, API docs, or architecture documentation.
