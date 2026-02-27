---
name: drafting-tsds
description: Creates Draft Technical Specification Documents for exploring solution spaces before implementation. Use when evaluating multiple architectural approaches, designing complex systems with uncertainty, or proposing technical changes that require stakeholder buy-in and option analysis.
---

# Drafting Technical Specification Documents

Draft TSDs are PROPOSAL documents for exploring solution spaces before committing to implementation. They help you generate options, stress-test ideas, and converge on a recommendation with explicit reasoning.

**When to use this skill:**
- Multiple viable approaches exist and you need to compare them
- Significant risk or uncertainty in the design
- Cross-team coordination or stakeholder buy-in required
- Architectural decisions with long-term impact

**When NOT to use this skill:**
- Decision is already made (use ADR instead)
- Solution is obvious (just implement it)
- Need to document how to build something (use implementation plan)

---

## Reference Selection

Load references based on what you need:

| Need... | Load | File |
|---------|------|------|
| Template structure and section guidance | **Template** | `references/template.md` |
| 5-step exploration process (problem → context → options → stress-test → recommend) | **Exploration** | `references/exploration.md` |
| When to use, quality standards, anti-patterns | **Best Practices** | `references/best-practices.md` |

Load **Template** first to understand the structure. Then load **Exploration** to guide the process. Reference **Best Practices** for quality checks and decision-making guidance.

---

## Core Principles

### Progressive Disclosure

Structure information in layers:

1. **TL;DR:** Problem and proposed direction (2-3 sentences)
2. **Problem & Context:** What we're solving and why
3. **Options:** Multiple approaches with pros/cons
4. **Recommendation:** Clear choice with explicit reasoning
5. **Details:** Architecture, risks, implementation plan

Readers should understand the gist in 30 seconds and dive deeper as needed.

### Exploration Over Advocacy

Generate at least 3 options. Honestly evaluate pros and cons. Don't present strawmen to make your favorite option look good.

The goal is to explore the solution space, not to lobby for a pre-determined answer.

### Tradeoff Transparency

Every option has downsides. Name them explicitly. Readers trust you more when you acknowledge what you're giving up.

```markdown
Good:
**Option A: Microservices**
- Pros: Independent deployment, isolated failures
- Cons: Distributed debugging harder, team has no experience

Bad:
**Option A: Microservices**
This is the best approach for maximum flexibility.
```

### Decision-Oriented

Every Draft TSD should lead to a clear recommendation. Document the reasoning so future readers understand WHY you chose this path.

---

## When to Use: Decision Table

| Situation | Use This | Not That |
|-----------|----------|----------|
| Exploring multiple architectural options | **Draft TSD** | ADR (too final) |
| Decision already made, documenting rationale | ADR | Draft TSD |
| Explaining how to implement | Implementation plan | Draft TSD |
| Tracking open questions during design | **Draft TSD** | Ticket comments |
| Strategic business direction | Strategy memo | Draft TSD |

**Rule of thumb:** If asking "Should we?", use Draft TSD. If asking "How do we?", use implementation plan.

---

## Exploration Workflow Summary

### 1. Define the Problem

Nail down:
- What's broken or missing?
- Who's impacted?
- What's the business impact?
- Why now?

**Output:** 2-3 sentence problem statement

Example:
> Users abandon checkout when payment processing takes more than 3 seconds. Synchronous payment gateway calls timeout 8% of the time during peak hours. This costs us $X/month in lost conversions.

### 2. Gather Context

Collect:
- Technical constraints (architecture, stack, performance requirements)
- Team constraints (expertise, time, resources)
- User constraints (workflows, migration paths)
- Organizational constraints (dependencies, approvals)

**Output:** Context section answering "What's the current state?" and "What constraints must we respect?"

### 3. Generate Options

Brainstorm at least 3 distinct approaches. Techniques:
- Start with extremes (simplest vs most robust)
- Vary one dimension at a time (sync vs async, push vs pull)
- Look for prior art (how do others solve this?)
- Ask "what if we didn't solve this at all?"

**Output:** 3+ options, each with core idea, how it works, pros, cons, effort estimate

### 4. Stress-Test Ideas

Play devil's advocate. For each option, ask:
- What happens under 10x load?
- What are the failure modes?
- How easy is this to debug?
- What's the learning curve?
- What integration challenges exist?
- What edge cases break this?

**Output:** "What Could Go Wrong" section for each option

### 5. Converge on Recommendation

Weigh options against:
- Does it solve the problem?
- Can we build it?
- Can we maintain it?
- What are the risks?
- What's the opportunity cost?

**Output:** Clear recommendation with WHY + honest acknowledgment of what you're giving up

For detailed guidance on each step, load `references/exploration.md`.

---

## Writing Guide Summary

### Document Structure

Follow the template in `references/template.md`:

1. **Header:** Status, author, date, TL;DR
2. **Problem & Context:** What triggers this work?
3. **Goals & Non-Goals:** Scope boundaries
4. **Proposed Solution:** High-level approach + architecture
5. **Options Considered:** Alternatives with tradeoffs
6. **Implementation Plan:** Phases, dependencies, testing
7. **Risks & Mitigations:** What could go wrong
8. **Success Metrics:** How we'll know it worked
9. **Open Questions:** Tracked with owners and deadlines

### Writing Tips

**Start with TL;DR:** If you can't articulate problem and direction in 2-3 sentences, you're not ready.

**Use tables for comparisons:** Prose is for narrative, tables for side-by-side evaluation.

**Show, don't tell:** Every architectural claim needs a diagram or concrete example.

**Be honest about downsides:** Acknowledge tradeoffs. Perfection doesn't exist.

**Name the decision-maker:** Who has final say? Prevents limbo.

### Diagrams

Use Mermaid diagrams to show:
- System components and relationships
- Data flow (request/response, events)
- Integration points
- Before/after architecture

For diagram guidance, use `Skill(ce:visualizing-with-mermaid)`.

---

## Quality Checklist

Before sharing a Draft TSD:

**Structure:**
- [ ] TL;DR at the top (2-3 sentences)
- [ ] Problem statement clear and specific
- [ ] Goals and non-goals explicitly listed
- [ ] At least 3 options documented with honest pros/cons
- [ ] Clear recommendation with explicit reasoning
- [ ] Risks and mitigations identified

**Content:**
- [ ] At least one architecture or data flow diagram
- [ ] Success metrics defined (measurable outcomes)
- [ ] Open questions tracked with owners and deadlines
- [ ] Related work linked (ADRs, design docs, code)

**Clarity:**
- [ ] Scannable structure (readers find sections quickly)
- [ ] Concrete examples (not abstract handwaving)
- [ ] Jargon explained (don't assume shared vocabulary)
- [ ] Under 12 pages (move details to appendices if longer)

**Process:**
- [ ] Reviewers identified with clear timeline
- [ ] Decision authority named (who has final say)

---

## Common Anti-Patterns

### The Fait Accompli
**Symptom:** Only one option presented as "the solution"
**Fix:** Generate at least 2 alternatives or explain why others don't work

### The Strawman Parade
**Symptom:** Three options where two are obviously terrible
**Fix:** If you can't find viable alternatives, make it a teaching moment, not theater

### The Architecture Astronaut
**Symptom:** Over-engineered with buzzwords ("hexagonal CQRS event-sourced microservices")
**Fix:** Start simple. Add complexity only with concrete justification

### The Analysis Paralysis
**Symptom:** 30-page document covering every edge case
**Fix:** Document the 80% solution. Move edge cases to appendices. Ship and iterate.

### The Handwave
**Symptom:** Critical details marked "TBD" or "We'll figure this out later"
**Fix:** Spike the risky unknowns BEFORE writing the draft. At minimum, research and document findings.

### The Scope Creep
**Symptom:** Proposal solving 5 problems simultaneously
**Fix:** Split into phases or separate documents

For more anti-patterns and fixes, load `references/best-practices.md`.

---

## Tone and Style

Use `Skill(ce:writer)` with **The Architect** persona for:
- Decision-oriented structure
- Explicit tradeoffs
- Diagram-supported explanations
- Clear recommendations

Key characteristics:
- Senior architect presenting to engineers
- Thought deeply, have clear recommendation, not hiding tradeoffs
- Explaining "why behind the why" so people can make good calls in edge cases

Example tone:
```markdown
## Why Option A?

Three things make this the right choice:
1. Payment-related deploys block the main release train 2-3x per sprint
2. PCI audit scope keeps expanding because payment logic touches shared tables
3. The team is big enough (4 engineers) to own a service independently

Any one of these might not justify the move. Together, they make a strong case.
```

---

## Document Lifecycle

### During Exploration
- **Status:** Draft
- Update freely as you learn
- Mark sections "[Needs review]" or "[Open question]"
- Share widely, gather feedback

### During Review
- **Status:** In Review
- Incorporate feedback
- Resolve open questions
- Clarify ambiguities

### After Decision
- **Status:** Approved
- Lock the document (no more major changes)
- Create follow-up tasks or detailed design docs
- Link to implementation work

### When Superseded
- **Status:** Superseded by [link]
- Don't delete; keep as historical record
- Explain briefly why new approach replaced this

---

## Related Skills

- `Skill(ce:architecting-systems)` - Architecture principles for informed option generation
- `Skill(ce:writer)` with **The Architect** persona - Tone and structure for technical docs
- `Skill(ce:documenting-systems)` - General documentation best practices
- `Skill(ce:visualizing-with-mermaid)` - Creating architecture and flow diagrams
- `Skill(ce:systematic-debugging)` - Root cause analysis when designing fixes
- `Skill(ce:strategy-writer)` - For strategic business documents (not technical specs)

---

## Quick Start

To create a Draft TSD:

1. **Load references:**
   ```
   Load references/template.md for structure
   Load references/exploration.md for process guidance
   ```

2. **Follow the exploration workflow:**
   - Define problem (2-3 sentence statement)
   - Gather context (constraints, current state)
   - Generate 3+ options (distinct approaches)
   - Stress-test (what could go wrong?)
   - Converge (recommend with reasoning)

3. **Use the template:**
   - Start with TL;DR
   - Fill in sections progressively
   - Use tables for option comparisons
   - Add diagrams for architecture
   - Track open questions

4. **Quality check:**
   - Run through checklist above
   - Share for feedback
   - Update based on learnings

5. **Finalize:**
   - Mark status as "Approved" when decided
   - Link to implementation work
   - Update as you learn during build phase
