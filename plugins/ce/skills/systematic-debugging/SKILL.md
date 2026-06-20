---
name: systematic-debugging
description: Debugging framework that finds root causes before proposing fixes. Use when investigating bugs, errors, unexpected behavior, failed tests, or when previous fixes haven't worked.
---

# Systematic Debugging

**If 3+ fixes have failed:** Stop fixing symptoms. Question the architecture. The bug may be a design problem, not a code problem.

**For multi-component systems:** Add diagnostic logging at each component boundary before proposing fixes. See [references/debugging-techniques.md](references/debugging-techniques.md) for instrumentation patterns (binary search, git bisect, minimal reproduction, strategic logging, differential analysis).

**For log-heavy investigations:** Use `Skill(reading-logs)` for efficient analysis.

## Reporting Format

```markdown
## Root Cause
[1-3 sentences explaining underlying issue]
Located in: `file.ts:123`

## What Was Wrong
[Specific problem - mutation, race condition, missing validation, etc.]

## The Fix
[Changes made and why they address root cause]

## Verification
- [x] Bug reproduced and confirmed fixed
- [x] Existing tests pass
- [x] Added regression test
```
