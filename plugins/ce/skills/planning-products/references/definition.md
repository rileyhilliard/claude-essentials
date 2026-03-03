# Definition

Define who has the problem, what the problem actually is, and what job the feature is hired to do.

## Problem Statement

Formula: "[User type] struggles with [specific friction] when trying to [goal], resulting in [consequence]."

| Good | Bad |
|------|-----|
| "Data analysts spend 30+ minutes manually joining CSVs that share a key column" | "Users need better data tools" |
| "New developers abandon integration after 15 minutes because the auth flow has 7 steps" | "Onboarding needs improvement" |
| "Support teams can't search past conversations, so they re-ask questions customers already answered" | "We need better search" |

A good problem statement is specific enough that you could hand it to someone unfamiliar with the project and they'd understand what's broken.

## User Personas (Lightweight)

Skip the 10-page marketing persona. Keep it tight.

| Element | Include | Skip |
|---------|---------|------|
| Who they are | Role, experience level, context | Demographics, hobbies |
| What they're doing | Task, workflow, environment | Life story |
| What frustrates them | Specific friction points | General complaints |
| What success looks like | Observable outcome | Feelings |

### Technical vs Non-Technical Users

When a feature serves both audiences, plan for each:

| Aspect | Technical user | Non-technical user |
|--------|---------------|-------------------|
| Explains via | How it works | What it does for them |
| Trusts through | Transparency, control | Simplicity, results |
| Frustration source | Lack of control, magic | Complexity, jargon |
| Success metric | Time to working integration | Task completed without help |
| Documentation need | API reference, examples | Guided walkthroughs |

## Jobs to Be Done (JTBD)

Format: "When [situation], I want to [motivation], so I can [expected outcome]."

Every feature addresses three dimensions:

| Dimension | Question | Example |
|-----------|----------|---------|
| Functional | What task are they completing? | "Export my data as CSV" |
| Emotional | How do they want to feel? | "Confident I'm not losing data" |
| Social | How do they want to appear? | "Like someone who has their act together" |

The emotional and social jobs often matter more for adoption than the functional one. A feature that works perfectly but makes users feel stupid will fail.

### Writing Job Statements

**Good:** "When I'm onboarding a new team member, I want to share my workspace configuration so I can get them productive in minutes instead of days."

**Bad:** "Users want to share configurations." (No situation, no motivation, no outcome.)

## Assumptions Log

Track what you believe vs what you've validated. Every product plan is built on assumptions. The dangerous ones are the ones you don't realize you're making.

| Assumption | Evidence | Confidence | How to validate |
|------------|----------|------------|-----------------|
| Users want self-serve onboarding | 60% of support tickets are onboarding questions | High | Prototype test with 5 users |
| Teams larger than 10 need role-based access | Competitor analysis (3/5 have RBAC) | Medium | Customer interviews |
| Developers prefer CLI over dashboard | Assumption, no data | Low | Survey existing users |

High confidence assumptions proceed. Low confidence assumptions that are Type 1 decisions need validation before the spec is finalized. Low confidence assumptions that are Type 2 decisions can ship and learn.
