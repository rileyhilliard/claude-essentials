# Anti-Patterns and Convention Divergence

Audit the session's output for code that works but diverges from established best practices, language conventions, or framework idioms. The goal is catching things that will cause confusion or problems down the road even if they function correctly today.

## What to Look For

**Language anti-patterns** - Code that fights the language:
- Ignoring language idioms (e.g., Go error handling with try/catch-style, Python without list comprehensions where appropriate, JS callbacks instead of async/await)
- Mutating data in languages/frameworks that expect immutability
- Stringly-typed values where enums or union types exist
- Manual resource management when the language has RAII, context managers, or defer
- Reimplementing standard library functionality

**Framework anti-patterns** - Fighting the framework instead of working with it:
- Bypassing the ORM to write raw SQL for simple queries (or vice versa for complex ones)
- Managing state outside the framework's state management system
- Direct DOM manipulation in a virtual DOM framework
- Ignoring framework lifecycle hooks and doing manual setup/teardown
- Custom routing/middleware when the framework provides it

**Error handling anti-patterns:**
- Swallowing errors silently (empty catch blocks, ignored return values)
- Using exceptions for control flow
- Returning boolean success/failure instead of propagating errors
- Catching broad exception types when specific ones are available
- Error messages that lose context about what actually went wrong

**Testing anti-patterns:**
- Testing implementation details instead of behavior
- Mocking everything instead of using real dependencies where practical
- Tests that pass when the feature is broken (false positives)
- Tests tightly coupled to internal structure that break on any refactor
- No assertion in the test (test that can't fail)

**Data handling anti-patterns:**
- N+1 queries in loops
- Loading entire datasets when only a subset is needed
- No pagination on endpoints that return collections
- Storing derived data that could be computed
- Missing database indexes on frequently queried columns

**Security anti-patterns:**
- Secrets in source code or config files committed to git
- User input used directly in queries, commands, or templates
- Overly permissive CORS, permissions, or access controls
- Missing rate limiting on public endpoints
- Authentication/authorization checks in the wrong layer

## How to Audit

For each piece of code produced during the session:

1. **Check against language conventions**: Does this follow idiomatic patterns for the language? Would a senior developer familiar with this language write it this way?

2. **Check against framework conventions**: Does this work with the framework or around it? Is it using the framework's built-in solutions?

3. **Check against project conventions**: Is this consistent with how the rest of the codebase handles the same concern? If it diverges, is there a good reason?

4. **Check against domain conventions**: For the specific domain (API design, database access, auth, etc.), does this follow well-established patterns?

## Root Cause Questions

For each anti-pattern found:
1. Was there a skill that should have guided this correctly? (e.g., `ce:handling-errors`, `ce:writing-tests`)
2. Is the anti-pattern isolated or is it a pattern across the codebase?
3. If it's codebase-wide, is it worth a refactoring task or just documenting the preferred pattern?
4. Could a linter rule or type constraint prevent this class of issue?

## Typical Actions

- Add linter rules that catch the specific anti-pattern
- Document the preferred pattern in CLAUDE.md or a project-specific skill
- Refactor the specific instance and add a test that validates the correct pattern
- Update relevant ce skills if they're missing guidance for this pattern
- Add type constraints that make the anti-pattern harder to express
