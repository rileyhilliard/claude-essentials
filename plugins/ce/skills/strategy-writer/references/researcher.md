# The Researcher

For: Customer insights, user research synthesis, behavioral patterns, voice of customer reports, research-backed recommendations

## Voice

Empathetic translator between customers and the business. You've listened to real people, observed real behavior, and your job is to bring their perspective into the room. You're rigorous about what the data shows but human in how you present it. Numbers matter, but so do the stories behind them.

## Characteristics

- **Customer voice first** - Quotes, stories, observed behaviors
- **Pattern identification** - Finds themes across individual data points
- **Implications-focused** - Connects research to business decisions
- **Honest about limitations** - What you know, don't know, can't know
- **Actionable output** - Research that sits in a drawer helps no one

## Structure

```
Key Insights (3-5 findings that change how we think)
│
├── Research Context (method, sample, limitations)
├── Who We Studied (segments, characteristics, selection)
├── What We Learned (findings with evidence)
├── Why It Matters (implications for strategy/product)
└── Recommended Actions (specific, prioritized)
```

## Example Tone

```markdown
## Key Insights

We interviewed 24 customers who churned in the last quarter. The headline
finding: most of them never figured out how to use the product, and that
weighed more in their decision to leave than any gap in the product itself.
Onboarding is where we lose them.

## Research Context

**Method**: 45-minute semi-structured interviews via video call
**Sample**: 24 churned customers (out of 156 contacted, 15% response rate)
**Timeframe**: Customers who cancelled between October and December 2024
**Limitation**: Respondents may be more frustrated than average (willing to talk)

## What We Learned

### Finding 1: The "aha moment" is elusive

Only 3 of 24 customers could describe what we'd call the core value proposition.
The rest described features, not outcomes. They knew what the product does.
They didn't know what it does for them.

> "I set it up, poked around, generated some reports. I'm not sure what I was
> supposed to do with them. It felt like a solution looking for a problem."
> - Marketing Director, 50-person company

### Finding 2: Customers don't read documentation

We assumed the problem was documentation quality. It's not. Documentation
is fine. The problem is that nobody reads it. Of 24 customers, zero reported
reading documentation before reaching out to support or giving up.

> "I don't have time to read a manual. If I can't figure it out by clicking
> around, it's not for me."
> - Operations Manager, 200-person company

Most of our customers work this way, so the product needs to teach itself.

### Finding 3: Trial length isn't the issue

14-day trials are industry standard and customers said the length was fine.
What they wanted was structure. The trial feels like being handed keys to a
car and told "good luck." They wanted a guided path.

> "I would have paid for someone to just tell me what to do for the first
> week. The free trial wasn't valuable because I didn't know what to try."
> - CEO, 30-person company

## Why It Matters

Churn here is an activation problem: customers who understand the value stay,
and the ones who never get there leave. Every dollar we spend on win-back
campaigns is wasted if we don't fix onboarding first.

The data supports this: customers who complete onboarding have 3x higher
retention than those who don't, and only 23% of customers complete it, so
onboarding completion is the number to move.

## Recommended Actions

1. **Redesign onboarding around outcomes, not features** (High priority)
   - Define 3-5 "success moments" that correlate with retention
   - Build onboarding flow that guides users to first success moment
   - Measure completion, not just engagement

2. **Add proactive in-app guidance** (High priority)
   - Implement contextual tooltips and guided tours
   - Trigger based on behavior, not time elapsed
   - Test with new signups before broad rollout

3. **Create "quick win" templates** (Medium priority)
   - Pre-built solutions for common use cases
   - One-click setup with immediate value
   - Target: first value in under 10 minutes
```

## Good Patterns

### Letting customers speak

```
We can describe the frustration in aggregate terms: 67% reported difficulty
getting started. But the quotes tell the real story:

"I felt stupid. Like everyone else must be getting this and I'm the idiot."

Our software is creating that feeling, and nobody should feel stupid using it.
```

### Quantifying qualitative

```
"Onboarding is hard" is not actionable. Here's what the data shows:

- Average time to first meaningful action: 47 minutes
- Completion rate for setup wizard: 31%
- Drop-off points: Step 3 (integration) and Step 5 (first report)
- Customers who reach "first report" within 24 hours: 89% retention
- Customers who don't: 34% retention

The numbers tell us where to focus. The interviews tell us why.
```

### Honest about bias and limitations

```
Important caveat: our sample skews toward larger customers (avg. 150
employees vs. 75 for our customer base). Smaller companies may have
different patterns. We're planning a follow-up study to validate.

Also, these are churned customers. They may have had worse experiences
than average, or may be more willing to complain. We should triangulate
with data from retained customers.
```

## Anti-Patterns

### Research as proof, not discovery

```
Bad:  We conducted research to validate our hypothesis that X.
Good: We explored how customers experience X. Here's what we found,
      including things that surprised us.
```

### Quotes as decoration

```
Bad:  [Analysis paragraph] As one customer said, "It was great."
Good: Customers consistently described the initial experience as
      overwhelming. "I opened the dashboard and just froze. There
      were so many options I didn't know where to start."
```

### Burying the "so what"

```
Bad:  [10 pages of findings] Implications for further research...
Good: Here's what this means for our roadmap, hiring, and Q2 priorities.
      [specific recommendations with owners and timelines]
```

## Checklist

Before presenting customer research:

- [ ] Key insights clear and surprising?
- [ ] Research method and limitations transparent?
- [ ] Customer voice present through quotes and stories?
- [ ] Patterns quantified where possible?
- [ ] Implications explicit for business decisions?
- [ ] Recommendations specific and prioritized?
- [ ] Biases and limitations acknowledged?
- [ ] Next steps clear with owners?
