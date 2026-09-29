---
name: systematic-debugging
description: Debugging framework that finds root causes before proposing fixes. Use when investigating bugs, errors, unexpected behavior, failed tests, or when previous fixes haven't worked.
---

If the current repo has its own rules/skills covering this topic (check .claude/rules/ and repo CLAUDE.md), those take precedence — apply this skill only where they're silent.

# Systematic Debugging

**If 3+ fixes have failed:** Stop fixing symptoms. Question the architecture. The bug may be a design problem, not a code problem.

**For multi-component systems:** Add diagnostic logging at each component boundary before proposing fixes. See [references/debugging-techniques.md](references/debugging-techniques.md) for instrumentation patterns (binary search, git bisect, minimal reproduction, strategic logging, differential analysis).

**For large or multi-file log investigations:** Delegate to the `@ce:log-reader` agent for efficient analysis. Not needed for a single short stack trace.

## Reporting Format

```markdown
## Root Cause
[The underlying issue, briefly]
Located in: `file.ts:123`

## What Was Wrong
[Specific problem - mutation, race condition, missing validation, etc.]

## The Fix
[Changes made and why they address root cause]

## Verification
[How the fix was confirmed - e.g. reran the failing test, reproduced and retested manually]
```
