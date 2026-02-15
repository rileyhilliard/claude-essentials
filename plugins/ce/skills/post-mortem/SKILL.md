---
name: post-mortem
description: Review a completed session to extract actionable improvements. Identifies DX friction, documentation gaps, architectural confusion, anti-patterns, process failures, and skill/config improvements. Uses progressive disclosure for targeted investigation types.
---

# Post-Mortem

Review a completed session or task to assess how it went and extract improvements. This covers both "how did we do" evaluation and "what can we learn" investigation.

## When to Use

After completing any non-trivial task or session. The goal is continuous improvement:
- **Routine review**: How smooth was execution? Where did friction occur?
- **Problem sessions**: Things took longer than expected, multiple corrections needed
- **Bug fixes**: What caused it and what would prevent it next time?
- **New patterns**: Something worked well that should be codified

## Investigation Types

Load the relevant reference based on what you're investigating:

| Situation | Load | File |
|-----------|------|------|
| Agent hit friction during execution (wrong files, bad assumptions, unclear conventions) | **DX Friction** | `references/dx-friction.md` |
| Documentation (READMEs, comments, API docs) was wrong, incomplete, or misleading | **Documentation Gaps** | `references/documentation-gaps.md` |
| Code was hard to understand or things were in unexpected places | **Architecture Clarity** | `references/architecture-clarity.md` |
| A bug was fixed but the root cause suggests a process gap | **Bug Prevention** | `references/bug-prevention.md` |
| Code works but diverges from best practices, idioms, or established conventions | **Anti-Patterns** | `references/anti-patterns.md` |
| Skills, hooks, commands, agents, or `.claude/` configs need updating | **Tooling Improvements** | `references/tooling-improvements.md` |

Load multiple references when the session spans investigation types.

## Core Process

Every post-mortem follows four steps regardless of investigation type.

### 1. Reconstruct What Happened

Walk through the session timeline. For each significant step, note:
- What was attempted
- What actually happened
- Where corrections were needed and why
- What went smoothly (worth noting what worked, not just what didn't)

Don't editorialize yet. Just document the sequence.

### 2. Assess Execution Quality

Evaluate how the session went overall:
- **Efficiency**: Did we take a direct path or wander? Where were the detours?
- **Accuracy**: Were initial approaches correct, or did we need multiple corrections?
- **Tooling fit**: Did skills, commands, and configs help or get in the way?
- **Communication**: Was intent clear between user and agent throughout?
- **Outcome**: Did we deliver what was asked for? Is it solid or just "works for now"?

Flag anything that felt harder than it should have been, even if it ultimately succeeded.

### 3. Identify Systemic Causes

For each friction point, ask: **"What would have prevented this?"**

Push past the first answer. "I should have read the file more carefully" is a symptom. "The file's name doesn't indicate what it contains" or "there's no convention documented for where this type of code lives" is a systemic cause.

**Good root causes** point to something fixable:
- A missing or misleading piece of documentation
- An architectural pattern that's inconsistent or undiscoverable
- A skill/config that gives wrong guidance
- A convention that exists but isn't written down
- A test gap that allowed a regression
- A workflow that worked well but isn't codified

**Bad root causes** are just descriptions of what went wrong:
- "I made a mistake"
- "The code was complex"
- "It took a while to figure out"

### 4. Propose Concrete Actions

Every finding should produce one of these:
- **Documentation update** - Fix incorrect docs, add missing docs, clarify ambiguous docs
- **Skill/config update** - Modify an existing skill or CLAUDE.md instruction
- **New skill/hook** - Create a new skill or hook to codify a pattern
- **Architecture improvement** - Refactor to make the system more discoverable
- **Test addition** - Add tests that would catch this class of issue
- **Codify a win** - Something that worked well should be made repeatable

Each action should have a specific file path and description of the change. Vague actions like "improve documentation" are not useful.

## Output Format

```markdown
## Session Post-Mortem

### What Happened
[Timeline of the session with key decision points]

### Execution Assessment
- **Outcome:** [What was delivered vs what was asked]
- **Efficiency:** [Direct path or detours? Where and why?]
- **What worked well:** [Patterns, skills, or approaches worth repeating]

### Findings

#### Finding 1: [Title]
**What happened:** [The friction or issue, stated factually]
**Root cause:** [The systemic issue underneath]
**Action:** [Specific change with file path]
**Priority:** [High/Medium/Low based on how often this would recur]

#### Finding 2: [Title]
...

### Summary
[1-2 sentences: biggest takeaway and what should change first]
```
