# Architecture Clarity Investigation

Investigate cases where code was hard to understand, things were in unexpected places, or the overall system structure made the task harder than it needed to be.

Load `Skill(ce:architecting-systems)` for guidance on structure, coupling, boundaries, concurrency, and observability patterns. Use its reference files for targeted architectural context.

## What to Look For

**Discoverability problems** - Hard to find things:
- Related code scattered across distant directories
- No clear module boundaries (everything reaches into everything)
- Utility functions buried in unrelated files
- No index or barrel exports to surface what a module provides

**Naming problems** - Names don't communicate purpose:
- Generic names (utils, helpers, common, misc) that hide what's inside
- Inconsistent naming across similar concepts
- File names that don't match their primary export
- Directory names that don't reflect their domain

**Responsibility confusion** - Unclear where things belong:
- Multiple places that could reasonably own a piece of logic
- Business logic mixed into transport/presentation layers
- Shared state that makes it unclear who owns what
- Circular dependencies that reveal tangled responsibilities

**Unexpected patterns** - Inconsistency across the codebase:
- Same problem solved differently in different modules
- Some areas follow a pattern, others don't
- Configuration approaches vary across services
- Error handling is different everywhere

## Root Cause Questions

For each clarity issue:
1. Would a new developer (or agent) find this without being told where to look?
2. Is the current structure an intentional design or organic accumulation?
3. Does the module/directory structure match the domain model?
4. Would a refactor here pay for itself across future sessions?

## Typical Actions

- Refactor to colocate related code
- Rename files/directories to communicate purpose
- Add architecture docs (even a paragraph in README helps)
- Establish and document conventions for where types of code live
- Extract tangled responsibilities into clear modules
- Add CLAUDE.md notes about non-obvious architectural decisions
