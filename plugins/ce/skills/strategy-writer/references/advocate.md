# The Advocate

For: Business cases, investment justifications, resource requests, ROI analysis, go/no-go recommendations

## Voice

Persuasive but grounded. You're making a case for investment, but you're not a salesperson. Your credibility comes from intellectual honesty. You acknowledge risks, address counterarguments, and show your math. The reader should finish feeling confident in the recommendation, not manipulated into it.

## Characteristics

- **Clear ask upfront** - What you want, how much, by when
- **Customer-grounded ROI** - Benefits flow from solving customer problems
- **Honest risk assessment** - What could go wrong, how we'd know, what we'd do
- **Alternatives considered** - Shows you've thought it through
- **Concrete next steps** - Specific actions, owners, timelines

## Structure

```
The Ask (what, how much, why now)
│
├── Opportunity (customer problem, market size, our position)
├── Proposed Solution (what we'd build/buy/do)
├── Business Impact (revenue, cost, strategic value)
├── Investment Required (money, people, time)
├── Risks and Mitigations (what could go wrong)
├── Alternatives Considered (why not those)
└── Recommendation and Next Steps
```

## Example Tone

```markdown
## The Ask

Invest $2.4M over 18 months to build an AI-powered support system. Expected
outcome: 40% reduction in support costs ($8M annually) and improved customer
satisfaction (target: +15 NPS points).

## Why Now

Support costs grew 34% last year while revenue grew 18%. That's unsustainable.
We've been hiring to keep up, but labor markets are tight and training takes
6 months. Meanwhile, customers wait longer and satisfaction scores are dropping.

Our top three competitors launched AI support this year, and two of them are
seeing 50%+ deflection rates, which puts us behind on a technology that has
already proven itself.

## The Opportunity

Our support team handles 450,000 tickets annually. Analysis shows:

- 62% are questions answered in our documentation (poorly organized)
- 23% require account-specific lookup (AI can handle)
- 15% require human judgment or complex troubleshooting

That means 85% of tickets could be resolved or significantly accelerated
through AI. At our current cost of $45 per ticket, that's $17M in annual
support spend that could be reduced.

We're projecting 40% capture initially, scaling to 60% by year two. That's
conservative compared to industry benchmarks.

## Investment Required

| Category | Year 1 | Year 2 | Total |
|----------|--------|--------|-------|
| Engineering (3 FTE) | $900K | $600K | $1.5M |
| AI/ML infrastructure | $400K | $200K | $600K |
| Third-party tools | $200K | $100K | $300K |
| **Total** | **$1.5M** | **$900K** | **$2.4M** |

Payback period: 8 months after launch (month 14 of project).

## Risks

**Technology risk (Medium)**: AI hallucination could damage customer trust.
Mitigation: Start with low-risk queries, human review for edge cases, clear
escalation paths.

**Adoption risk (Medium)**: Customers might prefer humans. Mitigation: Offer
choice, measure satisfaction, iterate quickly.

**Competitive risk (High)**: Delay means falling further behind. Mitigation:
This proposal.

## Alternatives Considered

**Outsource support**: Cheaper short-term, but quality control issues and no
long-term cost reduction. Rejected.

**Hire more agents**: Doesn't solve the structural problem. Costs grow with
volume. Rejected.

**Buy vs. build**: Evaluated three vendors. Best option (Intercom) would cost
$1.8M annually and require significant integration work. Building gives us
more control and better long-term economics. Recommended: build.

## Recommendation

Approve $2.4M investment. Begin immediately with a 3-month proof of concept
focused on documentation-answerable queries. Full rollout in month 9.
```

## Good Patterns

### ROI grounded in customer benefit

```
The $8M in annual savings is the smaller part of the case. Every minute a
customer spends waiting for support is a minute they're considering
alternatives, so the larger return is retention and expansion revenue from
customers who feel supported.
```

### Honest uncertainty quantification

```
Our projections assume 40% ticket deflection. That's the conservative case.
Industry benchmarks suggest 50-60% is achievable. But we've also seen
implementations that stalled at 25% due to poor knowledge base quality.

Our knowledge base needs work. If we don't invest in content alongside
technology, we'll hit the low end of the range. The proposal includes
$200K for content remediation.
```

### Addressing the obvious counterargument

```
The natural objection is timing. We're launching a major product update in
Q3. Adding another initiative seems like too much.

Here's why I disagree: Support volume will spike after the product launch.
If we don't have AI support in place, we'll either miss SLAs or scramble
to hire contractors at premium rates. The right time to start was six
months ago. The second-best time is now.
```

## Anti-Patterns

### The hockey stick

```
Bad:  Revenue will grow 300% in year three based on our projections.
Good: Revenue could reach $X in year three if we hit targets. More likely
      range is $Y-$Z based on historical performance of similar initiatives.
      Here's what has to go right to hit the high end.
```

### Hiding the ask

```
Bad:  [15 pages of analysis] ...so we recommend an investment of $5M.
Good: We're requesting $5M to build X. Here's why it's worth it.
```

### Risk section as afterthought

```
Bad:  Risks: competitive, operational, financial. We have mitigation plans.
Good: The biggest risk is customer adoption. Here's the evidence that
      concerns me, how we'll measure early, and what we'll do if it's not
      working.
```

## Checklist

Before presenting business cases:

- [ ] Ask clear in first paragraph?
- [ ] Opportunity grounded in customer problem?
- [ ] Investment sized and categorized?
- [ ] ROI calculated with assumptions explicit?
- [ ] Risks assessed honestly with mitigations?
- [ ] Alternatives considered and dismissed with reasoning?
- [ ] Timeline realistic with dependencies identified?
- [ ] Next steps specific with owners?
