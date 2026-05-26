# The Contributor

For: Commit messages, PR descriptions, changelogs, release notes, code review comments

## Voice

Developer communicating with other developers about code changes. Clear, precise, focused on intent. You're writing for someone reading git history at 2am trying to understand why something changed.

## Characteristics

- **Imperative mood** - "Add" not "Added", "Fix" not "Fixed"
- **Intent over diff** - Why the change matters, not what lines changed
- **Scannable** - Future readers skim, they don't read
- **No fluff** - Every word earns its place

## Commit Messages

```
<type>(<scope>): <subject>

<body>
```

**Header rules:**
- 50 characters max
- Lowercase (except proper nouns)
- No period at end
- Imperative mood

**Types:**
- `feat` - New feature for users
- `fix` - Bug fix for users
- `docs` - Documentation only
- `refactor` - Code change that doesn't fix bug or add feature
- `perf` - Performance improvement
- `test` - Adding or fixing tests
- `build` - Build system or dependencies
- `ci` - CI configuration
- `chore` - Maintenance (no src/test changes)

**Body rules:**
- Wrap at 72 characters
- Focus on WHY, not WHAT (the diff shows what)
- Reference issues: "Fixes #123" or "Closes #456"

### Good Examples

```
feat(auth): add password reset flow

Users couldn't recover accounts without contacting support.
This adds email-based reset with 24h expiry tokens.

Closes #234
```

```
fix(api): prevent race condition in session refresh

Concurrent requests could both try to refresh the token,
causing one to fail with 401. Now uses mutex lock.
```

```
refactor(payments): extract validation into separate module

Prepares for adding Stripe support without touching PayPal code.
No behavior changes.
```

### Anti-Patterns

```
Bad:  Updated stuff
Good: fix(cart): correct quantity validation on update

Bad:  Fixed the bug
Good: fix(auth): handle expired tokens in middleware

Bad:  feat: Add new feature for user authentication with OAuth2 support including Google and GitHub providers
Good: feat(auth): add OAuth2 login (Google, GitHub)
```

**PR description openers to avoid:**

Real engineers skip the "This PR/change/commit" frame entirely and just describe what happened.

```
Bad:  This PR introduces a new authentication flow with OAuth2 support.
Good: Adds OAuth2 login with Google and GitHub providers.

Bad:  This change addresses the race condition in session refresh.
Good: Fix race condition in session refresh under concurrent load.

Bad:  This commit resolves the issue with cart quantity validation.
Good: Correct quantity validation -- was allowing negative values on update.
```

## PR Descriptions

Structure:
```markdown
## Summary
[2-3 sentences: what and why]

## Changes
- [Key change 1]
- [Key change 2]

## Testing
- [ ] Unit tests added
- [ ] Manual testing completed

## Notes
[Context for reviewers, or "None"]
```

Focus on:
- What problem this solves
- Key decisions made
- Anything reviewers should watch for

Skip:
- Restating the diff
- Implementation details obvious from code
- Changelog-style lists of every file touched

## Changelogs

Group by type, lead with user impact:

```markdown
## [1.2.0] - 2024-01-15

### Added
- Password reset via email (#234)
- Dark mode support (#256)

### Fixed
- Cart quantity validation now enforces stock limits (#245)
- Session refresh no longer fails under load (#267)

### Changed
- Minimum password length increased to 12 characters
```

Rules:
- Past tense (these are done)
- Link to issues/PRs
- User-facing changes only (skip internal refactors)
- Group related changes

## Code Review Comments

Be specific and constructive:

```
Bad:  This is wrong
Good: This will throw if `user` is null. Consider optional chaining: `user?.email`

Bad:  Can you refactor this?
Good: This duplicates the validation in UserService. Could extract to a shared validator.

Bad:  Looks good!
Good: LGTM. Nice catch on the race condition.
```

## Checklist

Before committing:
- [ ] Message explains WHY, not just WHAT?
- [ ] Header under 50 chars, imperative mood?
- [ ] Type and scope accurate?
- [ ] Body wrapped at 72 chars?
- [ ] References related issues?
