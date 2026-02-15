---
description: Comprehensive code review using the code-reviewer agent
argument-hint: "[instructions]"
allowed-tools: Bash, Task, AskUserQuestion
---

Invoke the ce:code-reviewer agent to perform a comprehensive code review.

**If `$ARGUMENTS` is provided:**

- Use the instructions from the user.

**If `$ARGUMENTS` is empty:**

Steps:

1. Check git status to see if there are uncommitted changes
2. Check current branch name
3. Determine what to review:
   - If uncommitted changes exist: Review uncommitted changes
   - If no uncommitted changes exist:
     - Check if on a feature branch (not main/master/develop)
     - Suggest reviewing all changes in current branch against main (or upstream branch)
     - Check the changed files via `git diff --name-only $([ "$(git rev-parse --abbrev-ref HEAD)" = "main" ] && echo "HEAD^" || echo "main...HEAD")`
     - Ask user what should be reviewed
4. Invoke the ce:code-reviewer agent with appropriate instructions

## Post-Review Workflow

After the code-reviewer agent completes:

1. **If APPROVE:** Report the review summary. Done.

2. **If REQUEST CHANGES:**

   a. Extract all Critical and Important issues into a checklist:
   ```
   Review Findings - [branch/scope]:
   - [ ] [CRITICAL] file.ts:123 - Description
   - [ ] [IMPORTANT] file.ts:456 - Description
   ```

   b. Ask the user how to proceed using `AskUserQuestion`:
   - "Fix all issues now" (recommended - fix everything the reviewer found)
   - "Show the full review, I'll handle it"

   c. If fixing: work through the checklist, marking items complete as resolved. After all targeted items are fixed, re-run the code-reviewer agent to verify the fixes don't introduce new issues.
