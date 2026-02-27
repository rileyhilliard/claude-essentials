---
description: Create a lightweight draft TSD from rough ideas or well-formed topics
argument-hint: "<topic-or-rough-idea>"
allowed-tools: Read, Grep, Glob, Write, AskUserQuestion, Skill, Task
---

Create a draft technical specification document (TSD) from: `$ARGUMENTS`

## Workflow

1. **DETECT**: Analyze $ARGUMENTS to determine if rough idea or well-formed topic
2. **IF ROUGH IDEA**: Run exploration workflow (context gathering, option generation, devils-advocate critique)
3. **IF WELL-FORMED**: Skip to drafting with appropriate skills
4. **WRITE DRAFT TSD**: Create structured document with exploration insights
5. **OPTIONAL**: Devils-advocate review of complete draft (ask user if desired)

## Well-Formed Detection Heuristics

Topic is **well-formed** if it contains ALL of the following:

- **Specific technology/vendor**: OAuth2, Stripe, Postgres, React, GraphQL, etc.
- **Action verb**: migrate, implement, refactor, replace, add, remove, update, etc.
- **Target system/component**: external API, admin dashboard, checkout flow, webhook handler, etc.

**Examples:**

| Input | Classification | Reason |
|-------|---------------|---------|
| "Migrate external API from JWT to OAuth2 with PKCE" | ✅ Well-formed | Has tech (OAuth2/JWT), action (migrate), target (external API) |
| "Implement rate limiting on Stripe webhook handler" | ✅ Well-formed | Has tech (Stripe), action (implement), target (webhook handler) |
| "better error handling" | ❌ Rough idea | No specific tech, no target system |
| "improve auth" | ❌ Rough idea | No action verb (what kind of improvement?), vague |
| "add GraphQL caching" | ❌ Rough idea | Has tech and action, but no target system (which API?) |

**User overrides:**

- `--skip-exploration` flag: Force direct drafting even for rough ideas
- User confirmation: If detected as rough idea, ask: "This looks like a rough idea. Run exploration workflow? [Y/n]"

## Exploration Workflow (For Rough Ideas)

### STEP 1: Load Context Skills

Load the drafting skill:

```
Skill(ce:drafting-tsds)
```

Auto-detect and load domain skills (see Domain Skill Auto-Detection section below).

Auto-detect and load architecture topics (see Architecture Topic Auto-Detection section below).

### STEP 2: Gather Context with AskUserQuestion

Ask via `AskUserQuestion` (allow "I don't know" responses):

**Required questions** (cannot proceed without):

1. What's the current state? What's broken or insufficient?
2. Who is affected by this problem? (users, team, business)

**Helpful questions** (improve quality but not blocking):

3. What constraints exist? (performance, compatibility, timeline, team size)
4. What have you tried already? What didn't work?
5. How will you know if this is successful? (metrics, behaviors)

**Handling incomplete answers:**

- "I don't know constraints" → Proceed, note assumption in TSD Context section
- "Not sure who's affected" → Ask follow-up: "Is this user-facing or internal?"
- No success criteria → Generate options anyway, surface as open question
- User skips all questions → Fail gracefully: "I need at least the problem description and who's affected to explore solutions"

### STEP 3: Generate Solution Options (2-4 viable approaches)

Use loaded skills (domain skills, architecture skills) to generate **2-4 distinct, viable solution options**.

**Generation strategies:**

1. **Spectrum approach**: Vary along one dimension (minimal patch → full rewrite)
2. **Tradeoff approach**: Different optimization targets (fast to implement vs long-term quality)
3. **Technology approach**: Different tech stacks (existing tools vs new library vs custom build)
4. **Scope approach**: Different problem boundaries (fix this case vs fix root cause)

**Quality checks for each option:**

- Can we actually build this with current team/timeline? (viable)
- Does it solve the stated problem? (complete)
- Is it meaningfully different from other options? (distinct)
- Would someone genuinely choose this? (not a strawman)

### STEP 4: Run Devils-Advocate Critique

For each solution option, spawn the devils-advocate agent:

```
Task(ce:devils-advocate) with structured context:

"Review this solution option for a technical specification.

OPTION: {
  "number": 1,
  "title": "Option 1: Centralized Error Middleware",
  "description": "Implement Express middleware that catches all errors...",
  "approach": "Single error handler in gateway layer",
  "tradeoffs": "Centralized but less granular control"
}

PROBLEM CONTEXT: {problem from user}
CONSTRAINTS: {constraints from user or "Unknown"}
SUCCESS CRITERIA: {criteria from user or "To be determined"}

Look for:
- Unstated assumptions
- Missing edge cases
- Hidden complexity
- Failure modes
- Second-order effects"
```

**Parse agent output** and incorporate into option analysis:

- **Critical Issues** → Add to TSD "Open Questions" as blocking items
- **Concerns** → Add to option's "Tradeoffs" with prefix "⚠️ Risk:"
- **Questions** → Add to TSD "Open Questions" as non-blocking items

**Error handling:**

- If agent times out: Continue without critique, note in TSD
- If agent returns malformed output: Extract what's parseable, log warning
- If agent refuses to critique: Note "Option appears solid" in TSD

### STEP 5: Synthesize Findings

Use `Skill(ce:writer)` with The Architect persona to:

1. Present option summary to user
2. Highlight key tradeoffs and risks from devils-advocate
3. Ask user: "Should I draft the TSD with these insights? [Y/n]"

If user confirms, proceed to writing draft TSD.

## Domain Skill Auto-Detection

**Note:** This section shows how to auto-load domain-specific skills based on keywords in the user's input. The example uses Eucalyptus-specific skills (`euc-*`). Customize this scoring table for your organization's skills, or omit this section if you don't have domain skills to auto-load.

**Algorithm:**

1. Extract keywords from `$ARGUMENTS` (lowercase, normalize)
2. Score each skill by keyword relevance

**Example scoring (customize for your skills):**

```
graphql skill:
- +3 points: "graphql"
- +2 points: "apollo", "federation"
- +1 point: "gateway" AND ("api" OR "bff"), "resolver"

database skill:
- +3 points: "postgres", "postgresql", "sql"
- +2 points: "query", "index", "migration"
- +1 point: "database", "schema"

payments skill:
- +3 points: "stripe", "payment"
- +2 points: "checkout", "subscription"
- +1 point: "billing", "invoice"
```

3. **Load skills with score ≥ 3**

4. **If multiple skills score ≥ 3**:
   - Ask user: "I detected [X, Y, Z]. Load all of these? [Yes / Select specific ones / None]"

5. **If no skills score ≥ 3**:
   - Skip domain skill loading and proceed

**User override:**

- `--skills=skill-1,skill-2` flag for explicit skill selection

## Architecture Topic Auto-Detection

Detect architecture topics from keywords and load relevant sections from `Skill(ce:architecting-systems)`:

**Keyword mapping:**

| Keywords | Load Reference |
|----------|---------------|
| "error", "logging", "monitoring", "observability" | `references/observability.md` |
| "API design", "versioning", "breaking changes", "endpoint" | `references/boundaries.md` |
| "async", "queue", "pub/sub", "race condition", "concurrency" | `references/concurrency.md` |
| "module", "structure", "organization", "monorepo" | `references/structure.md` |
| "dependency", "coupling", "interface", "contract" | `references/coupling.md` |

Load the architecture skill with appropriate reference if keywords match.

## File Naming Convention

**Default path:** `docs/specs/drafts/YYYY-MM-DD-<topic-slug>.md`

**Slug generation rules:**

1. Lowercase input topic
2. Replace spaces with hyphens
3. Remove special characters (keep only alphanumeric + hyphens)
4. Truncate to max 60 characters if needed
5. Example: "Improve API Error Handling" → "improve-api-error-handling"

**Collision handling:**

- If file exists, append counter: `YYYY-MM-DD-<topic-slug>-2.md`
- Check up to 10 attempts
- If still colliding after 10 attempts, fail with error message

**Directory creation:**

- Create `docs/specs/drafts/` if it doesn't exist
- Warn user: "Creating new directory structure: docs/specs/drafts/"

**User override:**

- Accept full path as first argument: `/ce:draft-tsd path/to/custom-name.md <topic>`
- Validate path is within project (no `../` escapes outside project root)
- If path is outside project, fail with error

## Writing the Draft TSD

Once exploration is complete (or skipped for well-formed topics), write the draft TSD using:

- `Skill(ce:drafting-tsds)` for structure and template
- `Skill(ce:writer)` with The Architect persona for tone and style
- Loaded domain skills for technical accuracy
- Devils-advocate feedback incorporated into tradeoffs and open questions

**Ensure the draft includes:**

1. **Problem Statement**: What, why, who's affected, cost of status quo
2. **Context**: Background, constraints, requirements, why now
3. **Solution Options**: 2-4 options with approach, tradeoffs, edge cases
4. **Open Questions**: Blocking questions first, nice-to-knows last

**Target length:** 1-2 pages for draft (not exhaustive, ready for team review)

## Examples

| Command | Behavior |
|---------|----------|
| `/ce:draft-tsd improve API error handling` | Detects rough idea → runs exploration → asks questions → generates options → devils-advocate → drafts TSD |
| `/ce:draft-tsd Migrate external API from JWT to OAuth2` | Detects well-formed → loads relevant skills → drafts directly |
| `/ce:draft-tsd implement Stripe webhooks` | Detects rough (no target system) → asks for clarification → runs exploration |
| `/ce:draft-tsd --skip-exploration better auth` | Forces direct drafting despite rough input |
| `/ce:draft-tsd --skills=euc-go,euc-sql add database pooling` | Uses explicitly specified skills, skips auto-detection |
