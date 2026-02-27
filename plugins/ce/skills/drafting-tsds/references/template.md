# Draft TSD Template

Use this structure for Draft Technical Specification Documents. This is a PROPOSAL format for exploring solutions before committing to implementation.

---

## Document Header

```markdown
# [Feature/System Name] - Draft Technical Specification

**Status:** Draft Proposal
**Author:** [Your Name]
**Date:** [YYYY-MM-DD]
**Related:** [Links to issues, PRs, parent docs]

**TL;DR (2-3 sentences):**
State the problem and the proposed direction. Readers should understand what this is about and where it's heading within 30 seconds.
```

---

## 1. Problem & Context

**What triggers this work?**

- What specific pain point, customer request, or technical limitation are you addressing?
- What happens if we don't solve this?
- What constraints are we working within (time, resources, compatibility)?

**Current state:**

Describe how things work today, including any relevant:
- User workflows
- System behavior
- Data flows
- Integration points

---

## 2. Goals & Non-Goals

### Goals

What this proposal aims to achieve. Be specific and measurable where possible.

Example:
- Enable users to X without Y
- Reduce latency for operation Z from 3s to under 500ms
- Support up to 10,000 concurrent operations

### Non-Goals

Explicitly list what this proposal does NOT solve. This prevents scope creep and sets expectations.

Example:
- Not addressing historical data migration (separate effort)
- Not optimizing for edge case W (< 0.1% of traffic)
- Not redesigning the entire subsystem (focused change only)

---

## 3. Proposed Solution

### High-Level Approach

Summarize the solution direction in 2-3 paragraphs before diving into details. Answer:
- What's the core idea?
- Why is this the right approach?
- What are the major components or phases?

### Architecture

Use diagrams to show:
- System components and their relationships
- Data flow (request/response patterns, event flows)
- Integration points with existing systems

```mermaid
[Include relevant architecture diagram]
```

**Key design decisions:**

For each major architectural choice, explain:
- **What** we're doing
- **Why** we're doing it this way
- **What alternatives** we considered
- **What tradeoffs** we're accepting

Example:

**Decision: Event-driven processing instead of synchronous calls**

- **Why:** Payment gateway timeouts currently block the entire checkout flow
- **Alternatives considered:** Circuit breakers (doesn't solve the blocking problem), job queues (adds delay)
- **Tradeoffs:** Added complexity in distributed debugging, eventual consistency requires optimistic UI updates

---

## 4. Options Considered

Document the alternatives you explored. This shows your thinking and helps future readers understand why you chose this path.

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **A: Proposed approach** | [Benefits] | [Drawbacks] | ✓ Recommended |
| **B: Alternative 1** | [Benefits] | [Drawbacks] | Not chosen: [reason] |
| **C: Alternative 2** | [Benefits] | [Drawbacks] | Not chosen: [reason] |

For the recommended option, dive deeper:

### Why Option A?

Explain the reasoning that led to this choice. Connect it to your goals and constraints.

### What are we giving up?

Be honest about the downsides. No solution is perfect. What problems does this approach NOT solve? What new complexity does it introduce?

---

## 5. Implementation Plan

### Phases

Break the work into logical phases. Each phase should deliver value or reduce risk.

**Phase 1: [Name]**
- Deliverables: [What ships]
- Success criteria: [How we know it worked]
- Estimated effort: [Rough sizing]

**Phase 2: [Name]**
- Deliverables: [What ships]
- Success criteria: [How we know it worked]
- Estimated effort: [Rough sizing]

### Key Technical Details

Address the critical implementation questions:

**Data model changes:**
- What tables/schemas change?
- Migration strategy?
- Backward compatibility?

**API changes:**
- New endpoints or modifications?
- Versioning strategy?
- Client impact?

**Dependencies:**
- What must happen first?
- What external teams or systems are involved?
- What can be parallelized?

**Testing strategy:**
- How do we verify correctness?
- What edge cases must we cover?
- Performance testing requirements?

---

## 6. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Risk description] | High/Med/Low | High/Med/Low | [How we'll address it] |

Be specific. "Performance issues" is too vague. "Database queries exceed 2s under peak load" is actionable.

---

## 7. Success Metrics

How will we know if this worked? Define measurable outcomes.

**Must-have:**
- [Metric 1 with target]: e.g., "95th percentile latency < 500ms"
- [Metric 2 with target]: e.g., "Zero data loss events"

**Nice-to-have:**
- [Metric 3 with target]: e.g., "50% reduction in support tickets related to X"

**Monitoring:**
- What alerts or dashboards do we need?
- What logs or traces should we capture?
- How do we debug issues in production?

---

## 8. Open Questions

List anything still undecided. Mark with owners and target resolution dates if possible.

- [ ] **Q:** [Question text]
  **Owner:** [Name]
  **Deadline:** [Date]
  **Status:** [Under investigation / Blocked on X / Resolved]

---

## 9. Appendices (Optional)

### A. Related Documents
- Links to ADRs, design docs, research
- Links to relevant code, prototypes, or spikes

### B. Technical Deep Dives
Move detailed implementation notes here if they clutter the main doc.

### C. Research Notes
External research, competitive analysis, or benchmarking data.

---

## Document Status

Track the lifecycle of this draft:

- **Draft:** Initial exploration and option generation
- **Review:** Gathering feedback from stakeholders
- **Approved:** Decision made, ready for implementation
- **Superseded:** Replaced by [link to newer doc]
