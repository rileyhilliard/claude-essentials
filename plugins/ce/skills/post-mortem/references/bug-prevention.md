# Bug Prevention Investigation

Investigate bugs that were fixed to determine whether the root cause suggests a process or structural gap that could prevent similar bugs in the future.

## What to Look For

**Test gaps** - The bug existed because nothing tested for it:
- No test coverage for the affected code path
- Tests existed but didn't cover the specific edge case
- Integration between components wasn't tested
- Test mocks hid the real behavior that caused the bug

**Type safety gaps** - The type system could have caught this:
- `any` types that allowed invalid data through
- Missing null checks that the type system should enforce
- API contracts not validated at boundaries
- Runtime type assumptions not enforced by the compiler

**Implicit coupling** - The bug came from unexpected dependencies:
- Changing A broke B because of a hidden connection
- Shared mutable state caused a race condition or stale data
- Configuration change had unintended side effects
- Import order or initialization order mattered but wasn't enforced

**Missing validation** - Bad data got further than it should:
- User input wasn't validated at the boundary
- API responses weren't checked before use
- Database queries returned unexpected shapes
- Environment variables were missing or malformed

## Root Cause Questions

For each bug:
1. Could a test have caught this before it shipped? What kind of test?
2. Could the type system have prevented this? What type change would help?
3. Was this a one-off or a pattern that could recur in other places?
4. Did a previous change introduce this? Would a regression test have caught it?

## Typical Actions

- Add regression test that reproduces the exact bug
- Add integration tests for component boundaries
- Tighten type definitions to make invalid states unrepresentable
- Add validation at system boundaries (API inputs, DB outputs)
- Add pre-commit or CI checks that would catch this class of bug
- Document the gotcha in CLAUDE.md if it's a recurring pattern
