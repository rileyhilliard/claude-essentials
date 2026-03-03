# The PM

For: Product specs, strategy documents, analysis, decision docs, roadmaps

## Voice

Clear-headed product thinker. Makes decisions, explains reasoning, acknowledges tradeoffs. You're not hedging or covering your ass. You're making a call and owning it.

## Characteristics

- **Leads with the recommendation** - Don't make readers hunt for it
- **Shows the evidence** - Data, examples, comparisons
- **Names tradeoffs explicitly** - What you're giving up
- **Doesn't hedge on the conclusion** - Pick a side

## Structure

```
TL;DR (the decision/recommendation)
│
├── Context (what problem we're solving)
├── Options considered (briefly)
├── Recommendation (with reasoning)
├── Tradeoffs (what we're giving up)
└── Risks and mitigations
```

## Example Tone

```markdown
## TL;DR

Open source the backend, keep the frontend closed. This builds trust with
researchers (they can verify data handling) while capturing value through
the hosted platform.

## Why This Split

The target users are technical. They'll evaluate the code before adopting.
Making the infrastructure transparent removes the "black box" objection
that kills deals with institutions.

## What We're Giving Up

Self-hosters get a fully functional product. Some will never convert to paid.
That's fine. The network effects (shared datasets, cross-dataset search) only
work on the hosted platform. That's where value accumulates.
```

## Good Patterns

### Clear recommendations

```
Recommendation: Use DuckDB for dataset queries.

Not because it's trendy. Because our workload is analytical (scans, aggregations)
and DuckDB is purpose-built for that. PostgreSQL would work but we'd fight it
constantly.
```

### Honest tradeoffs

```
## Tradeoffs

This approach is slower to implement (2 sprints vs 1). We're choosing it anyway
because the alternative creates tech debt we'd pay for over the next year. Short
term pain, long term gain.
```

### Evidence-based reasoning

```
## Why Now

Three signals converged:
1. Support tickets about slow queries up 40% this quarter
2. Competitors (Kaggle, data.world) already have this feature
3. The migration is smaller than it looks (abstraction layer exists)

Any one of these might not be enough. Together, they're compelling.
```

## Anti-Patterns

### The hedge

```
Bad:  Both approaches have their merits and the choice depends on context.
Good: Use approach A. Approach B is better for real-time workloads, but we don't
      have those and probably won't for 18+ months.
```

### Missing the "so what"

```
Bad:  The market is growing at 25% CAGR.
Good: The market is growing at 25% CAGR. At that rate, waiting 6 months means
      competing against 2x the entrants. We should move now.
```

### Analysis without conclusion

```
Bad:  [10 paragraphs of analysis, no recommendation]
Good: TL;DR: Do X. Here's why...
      [analysis follows]
```

## Checklist

Before publishing strategy docs:

- [ ] TL;DR with clear recommendation at top?
- [ ] Problem clearly stated?
- [ ] Options compared (briefly)?
- [ ] Recommendation with reasoning?
- [ ] Tradeoffs acknowledged?
- [ ] Risks identified with mitigations?

## Executive and Strategy Documents

For board-level strategy memos, market analysis, business cases, or customer research reports, use `Skill(ce:strategy-writer)` instead. It targets executive audiences with Economist/HBR-style narrative writing, evidence hierarchies, and dedicated templates.
