# Experience Definition

Define the experience *requirements* before the experience *implementation*. This isn't UI design (that's `Skill(ce:design)`). This is what the user's journey looks like, what moments matter, and what qualities the feature needs to embody.

The output here feeds into `Skill(ce:design)` for visual implementation and `Skill(ce:writing-plans)` for technical implementation.

## User Journey Moments

Map the experience as a sequence of moments, not a list of capabilities:

| Moment | Define | Example |
|--------|--------|---------|
| Entry | How does the user discover/access this? | Link in sidebar, CLI command, API endpoint |
| First impression | What do they see and understand immediately? | Empty state with clear CTA, help text, example data |
| Core action | What's the primary thing they do? | Upload a file, run a query, configure a setting |
| Feedback | How do they know it worked? | Success message, visible result, confirmation |
| Recovery | What happens when something goes wrong? | Error message, undo option, retry path |
| Return | Why and how do they come back? | Bookmarkable URL, recent items, notification |

Not every feature needs all six. A background process might only need Entry, Feedback, and Recovery.

## Experience Qualities

Pick 2-3 qualities this feature should embody. These guide design and technical decisions downstream.

| Quality | Feels like | When to pick |
|---------|-----------|-------------|
| Fast | Results before you finish thinking | Performance-critical features, search, real-time |
| Obvious | No instructions needed | Consumer products, broad audience, onboarding |
| Powerful | "I can do anything with this" | Power users, developer tools, advanced features |
| Safe | "I can't break anything" | Data operations, destructive actions, admin tools |
| Guided | "I know what to do next" | Complex workflows, onboarding, multi-step processes |
| Transparent | "I can see what's happening" | Background processes, AI features, long-running ops |

Qualities in tension require a conscious tradeoff. "Powerful" and "Obvious" often conflict. "Fast" and "Safe" can too. Name the tradeoff explicitly.

## DX Experience (Developer Tools)

When building for developers, the experience IS the API/CLI/SDK. These need the same careful planning as any user-facing feature.

### API Ergonomics

| Principle | What it means |
|-----------|---------------|
| Obvious defaults | Zero-config path works for 80% of cases |
| Progressive complexity | Simple things simple, complex things possible |
| Predictable naming | If `getUser` exists, `getTeam` works the same way |
| Fast feedback | Errors are immediate, specific, and actionable |
| Copy-paste friendly | Examples work when pasted without editing |

### CLI Ergonomics

| Principle | What it means |
|-----------|---------------|
| Verb-noun pattern | `create project`, `list users`, `delete token` |
| Useful help text | Shows examples, not just flag descriptions |
| Sensible defaults | Flags override defaults, not replace them |
| Dual output | Human-readable by default, `--json` for piping |
| Progressive disclosure | Common flags visible, advanced flags in `--help` |

### SDK Ergonomics

| Principle | What it means |
|-----------|---------------|
| Type-safe | Good autocomplete, catches mistakes at compile time |
| Actionable errors | Tell you what to do, not just what went wrong |
| Documented examples | Every public method has a working example |
| Idiomatic | Follows the conventions of the target language |

## Handoff Readiness

The experience definition is ready to hand off when:

- [ ] Entry point is clear (how users get here)
- [ ] Core action is defined (what they do)
- [ ] Feedback loop is specified (how they know it worked)
- [ ] Error states are covered (what happens when it doesn't)
- [ ] Experience qualities are chosen (2-3 from the table)
- [ ] DX requirements are specified (if developer-facing)

Hand off to `Skill(ce:design)` for visual implementation. Hand off to `Skill(ce:writing-plans)` for technical task breakdown.
