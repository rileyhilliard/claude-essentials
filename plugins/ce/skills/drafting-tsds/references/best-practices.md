# Best Practices for Draft TSDs

Draft Technical Specification Documents serve a specific purpose: exploring solution spaces before committing to implementation. This guide covers when to use them, quality standards, and common pitfalls.

---

## When to Use Draft TSDs

### Good Fit

Draft TSDs work best when:

- **Multiple viable approaches exist:** You need to compare options before choosing
- **Significant risk or uncertainty:** The solution isn't obvious and mistakes are costly
- **Cross-team coordination required:** Others need to understand and buy into the approach
- **Architectural decisions with long-term impact:** Choices that are hard to reverse
- **Exploration before commitment:** You're in the design phase, not ready for implementation

### Examples

- Designing a new API with multiple integration patterns
- Choosing between monolith and microservices for a new feature
- Evaluating build vs buy for complex functionality
- Planning a data migration strategy across multiple systems
- Architecting an event-driven system with many moving parts

### Poor Fit

Draft TSDs are overkill when:

- **Solution is obvious:** No real options to evaluate
- **Problem is well-understood:** Existing patterns apply cleanly
- **Change is low-risk and reversible:** Easy to pivot if wrong
- **Time pressure:** Need to ship now, iterate later
- **Exploratory spike:** Better to prototype first, document after

### Examples

- Adding a CRUD endpoint following existing patterns
- Fixing a bug with clear root cause
- Implementing a feature with established framework conventions
- Making cosmetic UI changes
- Updating dependencies with clear migration guides

---

## Decision Tree: What to Use

| Situation | Use This | Not That |
|-----------|----------|----------|
| Exploring solution space with multiple options | **Draft TSD** | Architecture Decision Record (too final) |
| Documenting a decision already made | Architecture Decision Record (ADR) | Draft TSD (decision is final) |
| Explaining how to build something | Implementation Plan / Developer Guide | Draft TSD (design is settled) |
| Tracking open questions and options | Draft TSD | Ticket comments (lacks structure) |
| Proposing a strategic direction | Strategy Memo (use `Skill(ce:strategy-writer)`) | Draft TSD (not technical spec) |
| Explaining architecture to new team members | Architecture Docs / System Overview | Draft TSD (proposal format wrong) |

**Rule of thumb:** If you're still asking "Should we?" use a Draft TSD. If you're asking "How do we?" use an implementation plan or developer guide.

---

## Quality Standards

### Structure

A good Draft TSD has:

- **Clear problem statement:** 2-3 sentences explaining what we're solving and why
- **Explicit scope boundaries:** Goals AND non-goals
- **Multiple options:** At least 3 distinct approaches with honest pros/cons
- **Recommendation with reasoning:** Not just "Option A wins" but WHY
- **Risks and mitigations:** What could go wrong and how we'll address it
- **Success metrics:** How we'll know if this worked

### Clarity

- **Scannable:** Readers should grok the structure and find relevant sections quickly
- **Concrete:** Specific examples, not abstract handwaving
- **Diagram-supported:** Architecture and data flows shown visually
- **Jargon-free:** Explain terms; don't assume everyone knows the same vocabulary

### Completeness

- **Context included:** Enough background for new readers to understand the problem
- **Tradeoffs explicit:** What we're gaining and what we're giving up
- **Open questions tracked:** With owners and deadlines
- **Related work linked:** ADRs, design docs, code, research

### Length

- **Main document: 6-12 pages**
  - Shorter risks missing important details
  - Longer risks readers skipping it entirely
- **Move details to appendices** if they clutter the main narrative
- **Link to related docs** rather than duplicating content

---

## Writing Tips

### Start with the TL;DR

Write the 2-3 sentence summary FIRST. If you can't articulate the problem and direction concisely, you're not ready to write the full doc.

### Use tables for comparisons

Prose is for narrative. Tables are for side-by-side evaluation.

```markdown
Good:
| Option | Build Time | Maintenance | Scalability |
|--------|------------|-------------|-------------|
| A      | 2 weeks    | Low         | High        |
| B      | 3 days     | High        | Low         |

Bad:
Option A takes 2 weeks to build and has low maintenance but scales well.
Option B is faster to build at 3 days but requires more maintenance and
doesn't scale as well...
```

### Show, don't tell

Every architectural claim needs a diagram or concrete example.

```markdown
Bad:
The system uses event-driven architecture for decoupling.

Good:
When an order is placed, the Order Service emits an OrderCreated event.
The Payment Service subscribes to this event and processes payment
asynchronously. This decouples checkout from payment processing.

[Include sequence diagram showing the flow]
```

### Be honest about downsides

Every option has tradeoffs. Readers trust you more when you acknowledge them.

```markdown
Good:
**Option A: Microservices**

Pros:
- Independent deployment
- Isolated failure domains

Cons:
- Distributed debugging is harder (need tracing infrastructure)
- Network overhead adds latency
- Team has no experience operating microservices

Bad:
**Option A: Microservices**

This is the best approach because it provides maximum flexibility
and scalability.
```

### Name the decision-maker

Who has final say? If it's unclear, the doc will sit in limbo.

```markdown
## Decision Authority

- **Technical decision:** Backend team lead (after review with arch team)
- **Product decision:** PM (defines success metrics and user impact)
- **Timeline:** Engineering manager (balances with other roadmap items)
```

---

## Common Anti-Patterns

### 1. The Fait Accompli

**Symptom:** Draft TSD with only one option presented as "the solution"

**Why it's bad:** You're not exploring; you're lobbying. If the decision is made, write an ADR instead.

**Fix:** Generate at least 2 alternative approaches and honestly evaluate them.

---

### 2. The Strawman Parade

**Symptom:** Three options where two are obviously terrible

**Why it's bad:** Readers see through it. You lose credibility.

**Fix:** If you genuinely can't find viable alternatives, document WHY other approaches don't work. Make it a teaching moment, not theater.

---

### 3. The Architecture Astronaut

**Symptom:** Over-engineered solution with buzzwords like "hexagonal CQRS event-sourced microservices"

**Why it's bad:** Complexity has a cost. If you can't explain why each layer is necessary, it's probably not.

**Fix:** Start simple. Add complexity only when you can justify it with concrete benefits.

---

### 4. The Analysis Paralysis

**Symptom:** 30-page document covering every edge case and contingency

**Why it's bad:** No one reads it. Perfection is the enemy of progress.

**Fix:** Document the 80% solution. Move edge cases to appendices. Ship and iterate.

---

### 5. The Handwave

**Symptom:** Critical details marked as "TBD" or "We'll figure this out during implementation"

**Why it's bad:** If the hard parts are unsolved, you haven't de-risked the design.

**Fix:** Spike the risky unknowns BEFORE writing the draft TSD. If you can't prototype, at least research and document what you learned.

---

### 6. The Scope Creep

**Symptom:** Proposal that solves 5 problems simultaneously

**Why it's bad:** Risk multiplies. Impossible to review or approve.

**Fix:** Split into phases. Ship the core, iterate on the rest. Or split into multiple docs.

---

### 7. The Missing Context

**Symptom:** Assumes readers know the domain, codebase, and history

**Why it's bad:** New team members or cross-functional stakeholders can't follow.

**Fix:** Include a "Current State" section. Link to relevant code and docs. Explain acronyms.

---

### 8. The Disappearing Doc

**Symptom:** Draft TSD written, then never revisited or updated

**Why it's bad:** Decisions get made in Slack or meetings, doc becomes stale, no record of what was decided or why.

**Fix:** Update the doc as you learn. When the decision is made, mark it "Approved" and link to any follow-up work.

---

## Collaboration Best Practices

### Share Early

Don't wait for perfection. Share a rough draft and gather feedback. Early input is cheaper than late course-correction.

### Async-Friendly

Structure the doc so people can read and comment on their own time. Don't require everyone in a room at once.

### Explicit Review Process

Define:
- Who needs to review (required vs optional)
- What you need from them (approval, feedback, awareness)
- Timeline (when do you need responses)

### Capture Decisions

When feedback leads to changes, document WHY:

```markdown
## Change Log

**2025-02-15:** Switched from Option A to Option B based on feedback from
Platform team. Concern: Option A introduces Redis as a new dependency, and
we're trying to reduce operational complexity this quarter.
```

### Close the Loop

When the decision is final:
1. Update the doc status to "Approved"
2. Archive rejected options (don't delete; useful for future reference)
3. Create implementation tickets or detailed design docs
4. Link from the draft TSD to follow-up work

---

## Maintenance and Lifecycle

### During Exploration

- Status: "Draft"
- Update freely as you learn
- Mark sections with "[Needs review]" or "[Open question]"
- Share widely, gather feedback

### During Review

- Status: "In Review"
- Incorporate feedback
- Resolve open questions
- Clarify ambiguities

### After Decision

- Status: "Approved"
- Lock the document (no more major changes)
- Create follow-up tasks or detailed design docs
- Link to implementation work

### When Superseded

- Status: "Superseded by [link]"
- Don't delete; keep as historical record
- Explain briefly why the new approach replaced this one

---

## Checklist: Before Sharing

- [ ] **TL;DR** at the top with problem and proposed direction?
- [ ] **Problem statement** clear and specific?
- [ ] **Goals and non-goals** explicitly listed?
- [ ] **At least 3 options** documented with honest pros/cons?
- [ ] **Recommendation** with explicit reasoning?
- [ ] **Risks and mitigations** identified?
- [ ] **At least one diagram** showing architecture or data flow?
- [ ] **Success metrics** defined?
- [ ] **Open questions** tracked with owners and deadlines?
- [ ] **Under 12 pages** (move details to appendices if longer)?
- [ ] **Reviewers identified** with clear timeline?

---

## Related Skills

- `Skill(ce:architecting-systems)` - Architecture principles for informed option generation
- `Skill(ce:writer)` with **The Architect** persona - Tone and structure for technical docs
- `Skill(ce:documenting-systems)` - General documentation best practices
- `Skill(ce:visualizing-with-mermaid)` - Creating architecture and flow diagrams
