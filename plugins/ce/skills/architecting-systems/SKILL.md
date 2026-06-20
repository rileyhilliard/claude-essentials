---
name: architecting-systems
description: Guides clean, scalable system architecture during the build phase. Use when designing modules, defining boundaries, structuring projects, managing dependencies, or preventing tight coupling and brittleness as systems grow.
---

# Architecting Systems

**Core principle:** Small decisions made early compound into either clean systems or massive technical debt. Get the structure right and the system stays maintainable as it grows. Get it wrong and every change gets harder.

## Topic Selection

Load the relevant reference based on what you're working on:

| Working on... | Load | File |
|---------------|------|------|
| Layers, vertical slices, file organization | **Structure** | `references/structure.md` |
| Interfaces, dependency inversion, contracts | **Coupling** | `references/coupling.md` |
| Bounded contexts, API design, module boundaries | **Boundaries** | `references/boundaries.md` |
| Async patterns, race conditions, queues | **Concurrency** | `references/concurrency.md` |
| Logging, health checks, metrics, tracing | **Observability** | `references/observability.md` |

Load multiple references when the task spans topics. For most greenfield work, start with **Structure** and **Coupling**.

---

## Core Principles (All Topics)

### Complexity budget

Every architectural decision has a complexity cost. Spend that budget where it matters.

| Worth the complexity | Not worth it |
|---------------------|--------------|
| Separation between domains that change independently | Abstracting code that only has one implementation |
| Event-driven for genuinely async workflows | Event-driven for simple request-response flows |
| Caching for measured performance bottlenecks | Caching "just in case" |
| Microservices for teams that deploy independently | Microservices for a small team's monolith |

**The rule:** Don't add indirection until you need it. Premature abstraction is as costly as premature optimization. Two similar code blocks are better than a wrong abstraction.

---

## Quick Reference

| Problem | Response |
|---------|----------|
| "Where does this code go?" | If the answer isn't obvious, the structure needs work |
| "Changing X requires touching Y" | Missing boundary between X and Y |
| "This module does too many things" | Split along separate reasons to change |
| "We can't test this in isolation" | Hidden dependencies; inject them instead |
| "New devs take weeks to be productive" | Conventions are too weak or too novel |
| "Every PR touches 10 files" | Feature code is scattered; colocate it |
| "The shared folder keeps growing" | Boundaries are in the wrong place |

**Writing architecture documents?** This skill covers how to build. For how to write about it (ADRs, design docs, tradeoff analyses), load `Skill(writer)` and use The Architect persona.
