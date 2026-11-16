# Design slop

Contents: the two tests, eyebrows and kickers, where uppercase labels are fine, the pattern catalog, and reviewing a page.

Design slop is what a model produces when it averages instead of choosing. Asked for a section, it emits the most common answer from shadcn and Tailwind marketing pages: a tracked-out uppercase label, a heading, a subheading that paraphrases the heading, three identical rounded cards, a sparkle icon, a gradient. None of it is ugly, but readers have learned to read it as "nobody designed this."

The cause is at the page level. A model builds each section on its own, so every section gets the same anatomy and the same visual weight, and nothing is left for emphasis. Decide once per page what matters most, and let only that section carry the weight.

The repo's design tokens and style guide come first. This file covers the structural and copy patterns that stay generic even when every token is correct.

## The two tests

The deletion test: delete the element. If nothing is lost, it was decoration. Run it on eyebrows, subheadings, icons, badges, dots and cards, and on every kicker and sub in a section header before shipping.

The 25% zoom test: zoom out until the text is unreadable. If you can't tell which section matters most, the page has no hierarchy, usually because every section has the same box, padding and header stack. Vary the container by the section's job: one is a full-bleed chart, one a dense table, one a single sentence and a link.

## Eyebrows, kickers and overlines

The most common tell is a three-line stack above every section: a kicker, the heading, and a sub that restates the heading.

```
OUR APPROACH
How it works
See how the pieces fit together.
```

The kicker says nothing the heading doesn't, and the reader parses three lines to get one.

An eyebrow earns its place only when it adds a fact the heading lacks:

| Legitimate | Example |
|---|---|
| Category on a listing card | `Case study`, `Guide` |
| Status or recency | `Updated March 2026`, `FY2024`, `Beta` |
| Audience | `For data teams` |
| A real step in a sequence the reader follows | `Step 2 of 4` |
| A navigational label under a deliberately broad headline | `Pricing` above `Pay for what you use` |

An eyebrow is slop when it is:

- a paraphrase, synonym or one-item category for the heading below it (`FAQ` over "Frequently asked questions")
- on every section of the page, so it stops being a signal
- a mood word or marketing phrase rather than a fact (`THE BIG PICTURE`, `WHY IT WORKS`)
- numbered (`01`, `02`) when the sections aren't steps the reader performs in order
- marked up as a heading (`<h2>`, `<h3>`) instead of a `<span>` or `<p>`

Hold the sub line to the same test. Keep it only when it adds a scope, a number, a constraint or a caveat.

The default section header in app UI is a heading, an optional one-line sub with real content, and an action slot, with no kicker. On a long page, signal weight with the heading's size and the section's container, not a label.

## Where uppercase labels are fine

Small tracked uppercase text (`text-[10px] uppercase tracking-wider text-muted-foreground`) is slop when it labels a section and fine when it labels a field:

- table column headers
- form group labels inside a control panel or settings dialog
- the label under a KPI value
- a sidebar group label in a nav or picker (`Recent`, `Views`)
- a compact status or kind badge (`Beta`, `SQL`, `Published`)

A field label sits next to a value or control and names it. A section kicker sits above a heading and names what the heading already names.

## Pattern catalog

The grep column is a starting point for an audit of a Tailwind codebase. Every hit needs the deletion test, not a blanket rewrite.

### Typography and labeling

| Pattern | Looks like | Grep | Instead |
|---|---|---|---|
| Kicker above every h2 | `uppercase tracking-*` span right before an `<h2>` | `rg -B2 -A4 "uppercase" --glob '*.tsx'`, then check for an adjacent heading | Drop it, or make it carry a fact |
| Sub that restates the heading | muted paragraph under an h2 that says the same thing | read the pairs | Delete it, or make it a constraint |
| Uppercase as decoration | `uppercase` on prose, nav labels, button text, section names | `rg "uppercase"` | Sentence case, with weight and size for hierarchy |
| Numbered sections that aren't steps | `01 / 02 / 03` mono pills | `rg "\b0[1-9]\b" --glob '*.tsx'` | Remove the number unless order matters |
| One italic serif word in a headline | `font-serif italic` on a single span | `rg "font-serif"` | One type style per headline |

### Layout and structure

| Pattern | Looks like | Grep | Instead |
|---|---|---|---|
| Uniform section anatomy | five to nine sections, each kicker, h2, sub and grid | walk the page | Vary the container by job, with one dominant section |
| Three identical feature cards | `md:grid-cols-3` with three icon, title and blurb children | `rg "grid-cols-3"` | A list, a bento with one dominant tile, a table, or two columns |
| Everything in a bordered rounded card | `rounded-xl border p-5` around content you can't act on | `rg "rounded-xl border"` | Whitespace and proximity for grouping; cards only for units you can open, run or download |
| Nested cards | a card in a card in a panel | read the tree | Flatten to one level |
| Centered hero with two buttons | `text-center`, `text-5xl`, primary and ghost button pair | `rg "text-center"` in hero files | Asymmetry, a real product visual, one call to action |
| Stat tiles with unsourced numbers | a row of big numbers with small captions | `rg "tabular-nums" -B2 -A4` | Numbers in context, with provenance and a comparison |
| Mixed spacing scales | `p-3`, `p-7`, `mt-[37px]` on siblings | `rg "\[[0-9]+px\]"` | One scale per component family |

### Color and surface

| Pattern | Looks like | Grep | Instead |
|---|---|---|---|
| Gradient text, gradient borders, hero washes | `bg-clip-text`, a full-bleed `bg-gradient-to-b` behind a hero | `rg "bg-clip-text\|gradient"` | Flat text and borders, unless the gradient shows hierarchy or state |
| Glow | `shadow-[0_0_8px]`, glowing accent dots | `rg "shadow-\[0_0"` | Depth from luminance steps |
| Accent spread thin | `text-primary` on eyebrows, dots, icons, links and badges in one view | `rg "text-primary"` per file | Accent only on calls to action and interactive state |
| Colored left borders cycling through a palette | `border-l-4 border-emerald-500` per card | `rg "border-l-"` | An accent border only as consistent semantic status |
| Status colors without a status | ad hoc `text-emerald-400` for "good" | `rg "text-emerald"` | Status colors only for real states |

### Icons and decoration

| Pattern | Looks like | Grep | Instead |
|---|---|---|---|
| Sparkles for anything AI | `<Sparkles>` on buttons, callouts, titles | `rg "Sparkles"` | Name the action |
| Icon in a tinted square above every card title | `h-9 w-9 rounded-lg bg-primary/15` with an icon | `rg "place-items-center rounded-(md\|lg) bg-"` | Icons only where they tell two things apart |
| Icon in a circle above a centered page title | page header with a decorative icon | read the page headers | Title and sub, no icon |
| Accent dot before a label | `h-1.5 w-1.5 rounded-full bg-primary` | `rg "rounded-full\" aria-hidden"` | Nothing |
| A badge on every heading | `rounded-full px-3 py-1 text-xs uppercase` beside an h1 | `rg "rounded-full.*uppercase"` | Badges for real state only |
| Emoji as icons | emoji in labels or headings | `rg -P "[\x{1F300}-\x{1FAFF}]"` | The icon set, or text |
| Arrow after every link | `→` or `<ArrowRight>` on each card link | `rg "ArrowRight\|→"` | Links that look like links |

### Motion

| Pattern | Looks like | Grep | Instead |
|---|---|---|---|
| Reveal on everything | every element fades up with staggered delays | count motion attributes per file | Motion for feedback and continuity |
| Spring or bounce entrances | `bounce-in`, bouncy springs | `rg "bounc"` | None |
| Pulsing decorative dot | `animate-pulse` on something that isn't status | `rg "animate-pulse"` | Remove it |
| Hover scale | `hover:scale-105` | `rg "hover:scale"` | A background luminance change |

### Copy in the UI

| Pattern | Looks like | Instead |
|---|---|---|
| Weightless benefit words | Effortless, Seamless, Powerful, Unlock, Supercharge, Transform | A verb naming what happens |
| Formulaic h2 | "Everything you need to...", "Built for...", "Why choose...", "How it works" | Read only the h2s aloud; each should be unmistakably about this product |
| Mood-word kicker | THE BIG PICTURE, WHY IT WORKS | A fact, or nothing |
| "Anything, in plain English" | "Ask anything, in plain English" | Say what the reader can ask |

## Reviewing a page

1. Screenshot at 25% zoom and name the section that matters most. If you can't, fix the hierarchy before touching labels.
2. Read only the h2s in order. They should read as an argument about this page's content, not a list of headings that would fit any page.
3. For each section header, run the deletion test on the kicker, then on the sub. Keep what carries a fact.
4. Count cards. Each should be something the reader can act on; cards around prose are just containers.
5. Count accent uses (`text-primary`, glowing dots, tinted icon squares). One accent job per view.
6. Count icons. Each should tell apart two things that would otherwise be confused.
7. Check the grids. Three identical cards in a row means the content was fitted to a template, so ask what shape the content actually has.
