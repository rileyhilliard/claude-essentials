# Scoping

Scope is the art of saying "not yet" without saying "never." Good scoping protects the team from building too much and protects users from waiting too long.

## Must / Should / Could / Won't

| Category | Definition | Rule |
|----------|-----------|------|
| Must | Feature doesn't work without it | Ship-blocking |
| Should | Expected by most users | Next iteration if not v1 |
| Could | Nice to have, adds polish | Only if time allows |
| Won't (this version) | Explicitly deferred | Write it down so it's not forgotten |

The "Won't" category is the most valuable. Explicit exclusions prevent scope creep better than priority lists. Unwritten exclusions become expectations.

## Scope Pressure Test

For each "must have" item, ask:

1. **What happens if we ship without it?** If the answer is "nothing bad," it's not a must.
2. **Can users work around the absence?** If yes, it's a "should."
3. **Will we lose users/deals without it?** Need specific examples, not hypothetical scenarios.

## MVP vs V1 vs Full Vision

| Phase | Goal | Scope |
|-------|------|-------|
| MVP | Validate the hypothesis | Minimum functionality to test if users want this |
| V1 | Useful to real users | Core job done well, rough edges acceptable |
| Full vision | Competitive and polished | Complete feature set, optimized experience |

Not everything needs an MVP phase. Type 2 decisions with high confidence can skip to V1.

## Phasing Decisions

When splitting across releases, each phase must deliver user value, not just technical progress.

| Good phasing | Bad phasing |
|-------------|-------------|
| Phase 1: Manual import, Phase 2: Auto-sync | Phase 1: Build sync engine, Phase 2: Add UI |
| Phase 1: Single-player, Phase 2: Collaboration | Phase 1: Real-time infrastructure, Phase 2: Features |
| Phase 1: Basic CRUD, Phase 2: Bulk operations | Phase 1: Data model, Phase 2: Everything else |

The test: could you demo Phase 1 to a user and they'd find it useful? If not, it's a foundation, not a phase.

## Scope Negotiation

When stakeholders push for more scope:

1. **Show the tradeoff explicitly** - "Adding X means shipping 3 weeks later or cutting Y"
2. **Propose phasing** - "X in v1, Y in v1.1"
3. **Ask which user problem they're solving** - Often reveals the real priority behind the request
4. **Distinguish Type 1 from Type 2** - "We can add this later without rework" defuses urgency

## Anti-Patterns

| Pattern | Problem |
|---------|---------|
| "MVP" that takes 6 months | It's not minimal |
| Phase 1 with no user value | You're building a foundation, not a product |
| Scope grows but timeline doesn't | Something will break (usually quality) |
| Everything is "must have" | Nothing is prioritized |
| No explicit "won't have" list | Scope creep has no guardrails |
