# Feature Spec Template

Use this template for product feature definitions. The output feeds into `Skill(ce:writing-plans)` for technical task breakdown and `Skill(ce:design)` for UI implementation.

**Save to:** `**/specs/YYYY-MM-DD-<feature-name>.md`

---

## Document Structure

```markdown
# [Feature Name]

> **Status:** DRAFT | REVIEW | APPROVED
> **Author:** [Name]
> **Date:** [Date]

## TL;DR

[2-3 sentences. What is this feature, who is it for, and why are we building it now?]

## Problem

### Who

[Target user persona(s). Role, context, experience level. Keep it tight.]

### What

[The specific problem. Use the format: "[User] struggles with [friction] when [goal],
resulting in [consequence]."]

### Evidence

[How do we know this is real? Data, research, support tickets, competitive pressure.
If evidence is thin, say so and note what validation is planned.]

### Why Now

[What changed that makes this the right time? New data, market shift, dependency
unblocked, strategic priority.]

## Solution

### Jobs to Be Done

When [situation], I want to [motivation], so I can [expected outcome].

- **Functional:** [What task is completed]
- **Emotional:** [How the user wants to feel]

### Core Experience

[Describe the experience, not the implementation. What does the user do? What do they
see? How does it feel?]

#### Entry Point

[How do users discover/access this feature?]

#### Happy Path

1. User does X
2. System responds with Y
3. User sees Z

#### Error States

| Error | User sees | Recovery |
|-------|-----------|----------|
| [Error 1] | [Message/state] | [Action available] |

### What This Is NOT

[Explicit scope boundaries. What are we deliberately not building?]

- Not X (that's a separate feature)
- Not Y (deferred to v2)

## Research

### Competitive Patterns

[How do comparable products handle this? What do users already expect?]

| Product | Approach | Strength | Weakness |
|---------|----------|----------|----------|
| [Comp 1] | [How they do it] | [What works] | [What doesn't] |
| [Comp 2] | [How they do it] | [What works] | [What doesn't] |

### User Expectations

[Based on research, what patterns will users expect? Where can we meet expectations
vs. where should we break new ground?]

## Scope

### Must Have (v1)

- [ ] [Capability 1]
- [ ] [Capability 2]

### Should Have (v1 if time, otherwise v1.1)

- [ ] [Capability 3]

### Won't Have (this version)

- [ ] [Capability 4] - [Why deferred]

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| [Outcome metric] | [Specific target] | [How to measure] |
| [Adoption metric] | [Specific target] | [How to measure] |

## Assumptions and Risks

| Assumption | Confidence | Validation plan |
|------------|-----------|-----------------|
| [Belief 1] | High/Med/Low | [How to verify] |

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk 1] | H/M/L | H/M/L | [Action] |

## Open Questions

- [ ] [Question 1 - who answers, by when]
- [ ] [Question 2]
```

---

## Handoff Notes Section

Add this section at the bottom of every spec. It maps the spec to what downstream skills expect.

```markdown
## Handoff

### For Technical Planning (ce:writing-plans)

Extract these fields for the implementation plan:

**Problem:** [Copy from Problem > What section]
**Goal:** [Restate TL;DR as the desired end state]
**Scope:** [Copy Must Have list + Won't Have boundaries]
**Success Criteria:** [Copy from Success Criteria table]

Technical constraints: [Performance requirements, integrations, compatibility]
Dependencies: [External services, other features, infrastructure]

### For Design (ce:design)

Experience qualities: [2-3 qualities from experience definition]
Reference products: [Competitor patterns to match or improve on]
Key interactions: [Entry point, core action, feedback moments]
```

---

## Writing Tips

**TL;DR:** Write this last. If you can't summarize in 3 sentences, the scope is too broad.

**Problem section:** This is the most important part. If the problem isn't clear and evidenced, the rest of the spec is fiction.

**Solution section:** Describe the experience, not the implementation. "User uploads a file and sees results in 2 seconds" not "Use streaming multipart upload with S3 presigned URLs."

**Scope section:** The "Won't Have" list is as important as the "Must Have" list.

**Research section:** Even lightweight competitive research prevents reinventing worse versions of existing patterns.

**Length:** 2-4 pages for most features. If you need more, you're probably covering too much for a single spec.
