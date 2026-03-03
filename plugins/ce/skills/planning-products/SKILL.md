---
name: planning-products
description: Defines product features from a PM perspective before technical planning begins. Use when scoping new features, writing product specs, defining user problems, choosing what to build, researching existing patterns, or bridging the gap between strategy and implementation. Covers JTBD analysis, competitive research, UX/DX experience definition, and scope negotiation for consumer, B2B, and developer tool products.
---

# Planning Products

**Core principle:** Define the problem worth solving and the experience worth building before deciding how to build it. Research what exists, understand who needs it, scope what matters.

## Planning Phase

Load the relevant reference based on where you are in the planning process:

| Phase | Load | File |
|-------|------|------|
| Researching market, competitors, existing patterns | **Discovery** | `references/discovery.md` |
| Framing the problem, users, and jobs to be done | **Definition** | `references/definition.md` |
| Defining how the feature should feel (UX or DX) | **Experience** | `references/experience.md` |
| Drawing scope boundaries, MVP, phasing | **Scoping** | `references/scoping.md` |
| Writing the actual product spec document | **Template** | `references/feature-spec-template.md` |

Start with **Discovery** when beginning from scratch. Start with **Definition** when the problem is already understood. Load **Experience** alongside either when the feature has significant interaction design. Load **Scoping** when you need to cut.

---

## The Planning Sequence

```
Discovery → Definition → Experience → Scoping → [Hand off]
    ↓           ↓            ↓           ↓
 Research    Problem      How it      What's in
 & patterns  & users      feels       & what's out
```

Not always linear. Discovery can reframe the problem. Experience constraints can force scope changes. Scoping can send you back to discovery. But this is the default order.

---

## Product Type Adjustments

Different products need different emphasis. Adjust the planning weight:

| Product type | Heavy on | Light on | Key question |
|-------------|----------|----------|--------------|
| Consumer (B2C) | Experience, discovery | Formal definition | "Would I use this?" |
| B2B / Enterprise | Definition, scoping | Visual polish | "Does this solve a workflow?" |
| Developer tools | DX experience, API ergonomics | Marketing polish | "Is this the obvious API?" |
| Internal tools | Scoping, definition | Discovery | "Does this save time?" |
| Platform / API | Definition, experience (DX) | Consumer UX | "Is this composable?" |

---

## Universal Principles

### Start with the customer's problem, not your solution

You are not designing features. You are solving problems for specific people. If you can't name the person and their frustration, you're not ready to plan.

### Research before inventing

Before designing something new, find out what already exists. Users have expectations shaped by other products. Meeting those expectations is usually better than surprising people with novelty. Novelty costs learning; familiarity is free.

### Hypothesis-driven, not conviction-driven

Frame decisions as hypotheses that could be wrong. "We believe [user] will [behavior] because [evidence]." If you can't state the evidence, it's a guess. Guesses are fine as long as you know they're guesses.

### Type 1 vs Type 2 decisions

| Decision type | Characteristics | Planning rigor |
|---------------|-----------------|----------------|
| Type 1 (one-way door) | Hard to reverse, high switching cost | Full discovery + definition |
| Type 2 (two-way door) | Easy to change, low cost to undo | Lightweight spec, ship and learn |

Most product decisions are Type 2. Don't over-plan reversible choices.

### Define success before building

Every feature needs measurable success criteria before work begins. Not vanity metrics. Outcomes tied to the user problem you're solving.

| Bad metric | Good metric |
|-----------|-------------|
| "Page views" | "% of users who complete the core task" |
| "API calls" | "Time to first successful integration" |
| "DAU" | "Users who return within 7 days" |

---

## Anti-Patterns

| Pattern | Problem |
|---------|---------|
| Solution-first planning ("Let's build X") | Skips problem validation, builds the wrong thing |
| Feature lists without user stories | No context for why, impossible to prioritize |
| Copying competitors without understanding why | Imports their problems along with their solutions |
| "Users" as a monolith (no persona distinction) | Different users need different things |
| Scope that only grows, never shrinks | Ship date slides, value dilutes |
| Planning without research | Invents patterns users already know differently |
| Perfecting the spec before testing assumptions | Spec fiction, not product planning |
| DX as afterthought ("devs will figure it out") | Developers are users too, bad DX kills adoption |

---

## Handoff Points

This skill's output feeds into other skills:

- **Technical implementation:** `Skill(ce:writing-plans)` takes the product spec and produces task breakdowns with agent grouping
- **UI/UX craft:** `Skill(ce:design)` takes the experience requirements and produces the visual implementation
- **Architecture decisions:** `Skill(ce:architecting-systems)` takes the technical constraints from the spec and produces system design
- **Strategy context:** `Skill(ce:strategy-writer)` operates upstream, informing the "why this, why now" that feeds into discovery

**Writing tone for specs and product docs:** Use `Skill(ce:writer)` with The PM persona.
