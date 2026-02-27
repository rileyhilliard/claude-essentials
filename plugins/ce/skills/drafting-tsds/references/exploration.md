# Exploration Workflow

Draft TSDs are about exploring the solution space before committing to implementation. This workflow guides you through generating options, stress-testing ideas, and converging on a recommendation.

---

## Overview

The exploration process has five steps:

1. **Define the Problem** - Understand what we're solving and why
2. **Gather Context** - Collect constraints, requirements, and existing patterns
3. **Generate Options** - Brainstorm multiple approaches without judgment
4. **Stress-Test Ideas** - Play devil's advocate to find weaknesses
5. **Converge on Recommendation** - Choose the best path forward with explicit reasoning

---

## STEP 1: Define the Problem

### Questions to Answer

Before exploring solutions, nail down the problem:

- **What's broken or missing?** Be specific. "Performance is bad" is vague. "Database queries take 5s under peak load" is concrete.
- **Who's impacted?** End users? Internal teams? Downstream systems?
- **What's the business impact?** Lost revenue? Poor experience? Team velocity? Security risk?
- **What triggers this work NOW?** Why not next quarter? What changed?

### Output

A crisp problem statement that fits in 2-3 sentences:

> Users abandon checkout when payment processing takes more than 3 seconds. Currently, synchronous payment gateway calls block the entire flow and timeout 8% of the time during peak hours. This costs us $X/month in lost conversions.

### Common Mistakes

- **Solution disguised as problem:** "We need microservices" is not a problem statement
- **Multiple problems bundled:** If you're solving 3 things, split them or prioritize
- **Vague impact:** Quantify where possible

---

## STEP 2: Gather Context

### What to Collect

**Technical constraints:**
- Existing architecture patterns in the codebase
- Technology stack and framework conventions
- Performance requirements (latency, throughput, uptime)
- Data residency, security, compliance requirements
- Integration points with external systems

**Team constraints:**
- Who will build this?
- What's their expertise?
- How much time is available?
- What support will they need?

**User constraints:**
- How do users currently accomplish this task?
- What workflows break if we change the interface?
- What's the migration path for existing data or behavior?

**Organizational constraints:**
- Does this require cross-team coordination?
- Are there dependencies on other roadmap items?
- What approvals or reviews are needed?

### Sources

- **Codebase exploration:** Read existing implementations, patterns, conventions
- **Documentation:** ADRs, design docs, runbooks
- **Data:** Analytics, logs, performance metrics
- **People:** Talk to domain experts, users, operators

### Output

A context section that answers:
- What's the current state?
- What constraints must we respect?
- What patterns should we follow (or break)?

---

## STEP 3: Generate Options

### Brainstorming Phase

Generate at least 3 distinct approaches. Don't judge yet. Don't commit yet. Just explore the possibility space.

**Techniques:**

**1. Start with extremes**
- What's the absolute simplest approach (even if it doesn't scale)?
- What's the most robust, enterprise-grade solution (even if it's overkill)?
- Now explore the middle ground

**2. Vary one dimension at a time**
- Synchronous vs async
- Push vs pull
- Monolith vs distributed
- Build vs buy
- Generic vs specialized

**3. Look for prior art**
- How do similar companies solve this?
- What does the framework/library recommend?
- What patterns exist elsewhere in the codebase?

**4. Ask "what if we didn't solve this at all?"**
- Can we eliminate the problem instead of fixing it?
- Can we work around it?
- What's the cost of doing nothing?

### Option Template

For each option, document:

```markdown
## Option A: [Name]

**Core idea:** [One sentence]

**How it works:** [2-3 paragraphs]

**Pros:**
- [What makes this attractive]

**Cons:**
- [What makes this risky or costly]

**Effort estimate:** [Rough sizing: days, weeks, months]
```

### Common Mistakes

- **Stopping at 2 options:** "Do X or don't do X" is not exploration
- **Strawman options:** Don't include bad options just to make your favorite look good
- **Attachment to first idea:** The first solution is rarely the best one

---

## STEP 4: Stress-Test Ideas

Now play devil's advocate. For each option, ask:

### Performance Questions

- What happens under 10x current load?
- What's the slowest operation in this design?
- Where are the bottlenecks?
- Can we scale horizontally or are we locked to vertical scaling?

### Reliability Questions

- What are the failure modes?
- How do we detect failures?
- How do we recover?
- What's the blast radius if this component fails?

### Maintainability Questions

- How easy is this to debug in production?
- What operational complexity are we adding?
- How do we test this?
- What's the learning curve for new team members?

### Security Questions

- What are the attack surfaces?
- Where does sensitive data flow?
- What access controls are needed?
- What compliance requirements apply?

### Integration Questions

- What breaks for existing clients?
- How do we migrate existing data or behavior?
- What versioning strategy do we need?
- What dependencies does this create?

### Edge Case Questions

- What happens if inputs are invalid?
- What happens if external systems are down?
- What happens if requests arrive out of order?
- What happens during partial failures?

### Output

For each option, add a **"What Could Go Wrong"** section:

```markdown
## Option A: Event-Driven Processing

[... description ...]

**What Could Go Wrong:**
- **Debugging distributed flows:** Need OpenTelemetry to trace events across services
- **Event ordering:** Payments could process out of order; need sequence numbers
- **Event loss:** Pub/Sub guarantees at-least-once; need idempotency keys
- **Operational complexity:** Team has no experience running event-driven systems
```

### Common Mistakes

- **Only stress-testing options you don't like:** Be equally skeptical of your favorite
- **Handwaving concerns:** "We'll figure that out later" is not a mitigation
- **Ignoring operational reality:** If your team can't support it, it's the wrong choice

---

## STEP 5: Converge on Recommendation

### Selection Criteria

Weigh each option against:

1. **Does it solve the problem?** (Obvious but check: some solutions don't actually fix the issue)
2. **Can we build it?** (Skills, time, resources)
3. **Can we maintain it?** (Operational burden, debugging complexity)
4. **What are the risks?** (Known unknowns, acceptable?)
5. **What's the opportunity cost?** (What else could we build with this effort?)

### Decision Framework

Use a comparison table to make tradeoffs explicit:

| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| Solves problem | High | ✓ | ✓ | ~ |
| Low complexity | Med | ✗ | ✓ | ✓ |
| Team expertise | High | ~ | ✓ | ✗ |
| Time to ship | Med | ~ | ✓ | ✗ |
| Scales to 10x | Low | ✓ | ~ | ✓ |

Legend: ✓ Strong fit, ~ Acceptable, ✗ Poor fit

### Document the Reasoning

Don't just pick a winner. Explain WHY:

```markdown
## Recommendation: Option B (Job Queue)

We're choosing the job queue approach over event-driven or synchronous options because:

1. **Solves the immediate problem:** Decouples checkout from payment processing, eliminating timeouts
2. **Team can support it:** We already run Redis, and the team has experience with Sidekiq
3. **Right-sized complexity:** Event-driven is overkill for this use case; we don't need cross-service choreography
4. **Fast to ship:** 2-3 weeks vs 2-3 months for event infrastructure

**What we're giving up:**
- Won't scale to real-time event processing if requirements change (acceptable: not on roadmap)
- Adds Redis as a critical dependency (acceptable: already in use, operationally proven)
```

### Acknowledge Uncertainty

Call out open questions and how you'll address them:

```markdown
## Open Questions

- **Performance under peak load:** Need to load test queue throughput
  - **Owner:** Backend team
  - **Deadline:** Before implementation starts
  - **Plan:** Spin up staging environment with production-like traffic

- **Job retry strategy:** How many retries? What backoff?
  - **Owner:** Product team (needs to define UX for failed payments)
  - **Deadline:** Design review next week
```

### Common Mistakes

- **Ignoring the human factor:** The "best" solution is the one the team can actually ship and maintain
- **Perfectionism:** Waiting for perfect information means never shipping. Document assumptions and move forward.
- **Choosing based on what's interesting:** Pick what solves the problem, not what's fun to build

---

## Iteration and Refinement

Draft TSDs are living documents during the exploration phase:

- Share early, share often
- Incorporate feedback
- Update as you learn more
- Mark sections as "[Needs review]" or "[Open question]"

Once you converge on a decision:
- Mark status as "Approved"
- Archive rejected options (don't delete; useful for future reference)
- Create implementation tasks or detailed design docs

---

## When to Stop Exploring

You've explored enough when:

- ✓ You have at least 3 distinct options
- ✓ Each option has clear pros, cons, and risks documented
- ✓ You've stress-tested ideas with edge cases and failure modes
- ✓ Stakeholders have reviewed and provided input
- ✓ You have a clear recommendation with explicit reasoning
- ✓ Open questions have owners and target resolution dates

Don't over-index on completeness. Ship the 80% solution and iterate.
