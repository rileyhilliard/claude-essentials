# Discovery

Research what exists before designing what's next. Users have expectations. Meet them or consciously break them.

## Research Inputs

Discovery requires inputs. These come from the user, from available tools (WebSearch, WebFetch, MCP servers), or from existing project knowledge. If web tools aren't available, ask the user to provide the research or gather it together.

### What to gather

| Source | Look for |
|--------|----------|
| Competitor products (3-5) | Common patterns, interaction models, terminology |
| G2/Capterra/app store reviews | Complaints, requested features, praise patterns |
| Stack Overflow / GitHub issues | Developer pain points (for dev tools) |
| Reddit, HN, Twitter/X | Unfiltered user sentiment, workarounds people build |
| Internal support/sales tickets | What customers ask for vs what they need |
| Existing analytics | Current usage patterns, drop-off points, popular paths |

Don't need all of these. Pick the 2-3 most relevant for the product type.

## Research Workflow

1. **Identify the space** - What category does this feature live in? What products do users already use for this job?
2. **Map existing patterns** - How do 3-5 comparable products handle this? What's the common UX/DX pattern users already know?
3. **Find the gaps** - Where do existing solutions fall short? What frustrations exist?
4. **Validate the opportunity** - Is the gap real or are users satisfied? Check forums, reviews, support tickets.
5. **Document the patterns** - Record what you found so the rest of the planning process can reference it.

## Competitive Analysis (Feature-Level)

This is lightweight, feature-level competitive review, not the deep market analysis that `Skill(ce:strategy-writer)` handles.

| What to capture | Why |
|----------------|-----|
| How competitors name the feature | Users expect this terminology |
| Default behavior / happy path | The baseline users compare against |
| What's missing or complained about | Your opportunity |
| Pricing/access model | Affects scope and positioning |

Focus on 3-5 direct comparisons. Don't boil the ocean.

## Pattern Documentation

Record patterns using this format:

> "Users expect [pattern] because [products A, B, C] all do it this way."

When breaking from established patterns, document why explicitly. The burden of proof is on novelty.

### Pattern types worth documenting

| Type | Example |
|------|---------|
| Interaction pattern | "Users expect drag-and-drop reordering in list views" |
| Naming convention | "Every competitor calls this 'workspaces,' not 'projects'" |
| Default behavior | "Auto-save is expected; manual save feels broken" |
| Information architecture | "Settings are always accessible from a top-right avatar menu" |
| DX pattern | "Every comparable CLI uses `init` for project setup" |

## Anti-Patterns

| Pattern | Problem |
|---------|---------|
| Skipping research ("we know our users") | You know your assumptions, not your users |
| Research paralysis (analyzing 20 competitors) | Pick 3-5, move on |
| Copying without understanding | Imports their mistakes along with their solutions |
| Only looking at direct competitors | Adjacent products shape expectations too |
| Treating competitor gaps as automatic opportunities | The gap might exist for a good reason |
