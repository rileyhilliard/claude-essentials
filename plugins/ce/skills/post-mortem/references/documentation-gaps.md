# Documentation Gaps Investigation

Investigate cases where documentation was wrong, incomplete, or misleading, causing the agent to take wrong approaches or waste time. "Documentation" here means any `.md` file: READMEs, code comments, API docs, architecture docs, and inline documentation.

> **Note:** `.claude/` configuration files (CLAUDE.md, rules, skills, hooks) are also documentation, but they're actionable agent config. If the gap is in `.claude/` files, load `references/tooling-improvements.md` for guidance on fixing skills, hooks, commands, and agent configs.

## What to Look For

**Incorrect documentation** - Docs said one thing, reality was different:
- API docs described endpoints that don't exist or have different signatures
- README setup instructions are outdated
- Code comments describe behavior that no longer matches
- CLAUDE.md instructions conflict with actual project setup

**Missing documentation** - Key information isn't written down anywhere:
- No description of the overall architecture or module responsibilities
- Environment variables needed but not listed
- Database schema or migration process not documented
- Deployment process exists only as tribal knowledge

**Misleading documentation** - Technically correct but creates wrong mental models:
- Docs focus on happy path, hiding important edge cases
- Example code works but uses deprecated patterns
- README describes the ideal architecture, not the current state
- Naming conventions in docs differ from naming in code

## Root Cause Questions

For each gap:
1. Did the agent trust documentation that turned out to be stale?
2. Was there a single source of truth, or did conflicting docs exist?
3. If the docs were missing, where should they live? (README, docs/, inline comments, architecture doc)
4. Would the agent have found the right answer faster by reading code instead of docs?
5. Is this a documentation problem or an agent config problem? If the fix is updating `.claude/` files (skills, hooks, CLAUDE.md, rules), load `references/tooling-improvements.md` instead.

## Typical Actions

- Fix incorrect documentation with current behavior
- Add architecture overview to README or docs/
- Remove or update stale code comments
- Add "last verified" dates to critical documentation
- Document environment variables, setup steps, and migration processes
- Update inline code comments that describe behavior that no longer matches
