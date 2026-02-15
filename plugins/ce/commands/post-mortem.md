---
description: Review a session or task to assess execution and extract improvements
argument-hint: "[what to review]"
allowed-tools: Read, Grep, Glob, Skill, AskUserQuestion
---

Review the current session (or the specified task/context) and identify what we can learn from it.

Load the post-mortem skill for guidance: `Skill(ce:post-mortem)`

**If `$ARGUMENTS` is provided:**
- Use the specified context to focus the review.

**If `$ARGUMENTS` is empty:**
- Review the current conversation/session.
- Walk through what was attempted, what happened, and where friction occurred.
