---
name: design
description: Enforces precise, minimal design for dashboards and admin interfaces. Use when building SaaS UIs, data-heavy interfaces, or any product needing Jony Ive-level craft.
---

# Design Principles

**Core philosophy:** Every interface should look designed by a team that obsesses over 1-pixel differences. Not stripped, _crafted_. And designed for its specific context.

## Avoid AI Sameness

AI-generated UIs have a recognizable "median of the internet" feel. Polished but generic, like everything was designed by the same committee. Break out of that by making deliberate choices instead of reaching for defaults.

**AI default patterns to actively avoid:**

| AI default | Why it happens | Do this instead |
|---|---|---|
| Indigo/purple gradients | Tailwind's `bg-indigo-500` saturated training data | Choose an accent color that fits the product's emotional job |
| Inter or system fonts everywhere | Statistically safest choice | Pick typography that matches the product personality (see Choose Typography below) |
| Three-column icon grid | Every SaaS landing page template uses this | Vary card layouts by content type. Metric cards, feature cards, and testimonial cards should look different from each other |
| Centered hero + CTA button | The default starting point for every landing page | Consider what the user actually needs first. Maybe it's a dense dashboard, a split layout, or content-forward with no hero at all |
| Uniform border-radius on everything | `rounded-lg` applied without thinking | Pick a radius system and vary it by component role (sharp for data, softer for interactive) |
| White/light gray background + subtle shadow cards | The safest possible surface treatment | Commit to a depth strategy that matches the product (see Depth Strategy below) |
| Decorative gradients on hero sections | Looks "modern" without communicating anything | If using gradients, make them functional (show hierarchy, direct attention) not decorative |

**The test:** If you swapped your brand name with a competitor's and the design still works, it's too generic. Something about the color foundation, typography, spacing rhythm, or layout density should feel specific to _this_ product.

**Controlled imperfection creates character.** Perfect symmetry and uniform spacing everywhere reads as machine-generated. Human-designed interfaces have intentional asymmetry: a sidebar slightly narrower than expected, a headline that breaks the grid for emphasis, whitespace that breathes unevenly to create visual rhythm. These are deliberate choices, not sloppiness.

## Design Direction (REQUIRED)

**Before writing code, commit to a direction.** Don't default. Think about what this specific product needs to feel like.

### Think About Context

- **What does this product do?** A finance tool needs different energy than a creative tool.
- **Who uses it?** Power users want density. Occasional users want guidance.
- **What's the emotional job?** Trust? Efficiency? Delight? Focus?
- **What would make this memorable?** Every product has a chance to feel distinctive.

### Choose a Personality

| Direction | Feel | When to Use |
|-----------|------|-------------|
| Precision & Density | Tight spacing, monochrome, info-forward | Power users who live in the tool. Linear, Raycast, terminal aesthetics. |
| Warmth & Approachability | Generous spacing, soft shadows, friendly | Products that want to feel human. Notion, Coda, collaborative tools. |
| Sophistication & Trust | Cool tones, layered depth, gravitas | Products handling money or sensitive data. Stripe, Mercury. |
| Boldness & Clarity | High contrast, dramatic negative space | Modern, decisive products. Vercel, minimal dashboards. |
| Utility & Function | Muted palette, functional density | Work matters more than chrome. GitHub, developer tools. |
| Data & Analysis | Chart-optimized, technical but accessible | Analytics, metrics, business intelligence. |

Pick one. Or blend two. But commit to a direction that fits the product.

### Choose Foundation

**Color foundation** (don't default to warm):
- Warm (creams, warm grays): approachable, comfortable, human
- Cool (slate, blue-gray): professional, trustworthy, serious
- Pure neutrals (true grays): minimal, bold, technical
- Tinted (slight color cast): distinctive, memorable, branded

**Light or dark?** Dark feels technical, focused, premium. Light feels open, approachable, clean. Choose based on context.

**Accent color:** ONE that means something. Blue = trust. Green = growth. Orange = energy. Violet = creativity.

### Choose Layout

- **Dense grids** for information-heavy interfaces where users scan and compare
- **Generous spacing** for focused tasks where users need to concentrate
- **Sidebar nav** for multi-section apps with many destinations
- **Top nav** for simpler tools with fewer sections

### Choose Typography

- **System fonts**: fast, native, invisible (utility-focused products)
- **Geometric sans** (Geist, Inter): modern, clean, technical
- **Humanist sans** (SF Pro, Satoshi): warmer, more approachable
- **Monospace influence**: technical, developer-focused, data-heavy

## Card Layouts

**Internal layouts should vary by content.** A metric card doesn't have to look like a plan card doesn't have to look like a settings card. One might have a sparkline, another an avatar stack, another a progress ring.

**Surface treatment stays consistent:** same border weight, shadow depth, corner radius, padding scale.

## Isolated Controls

**Never use native form elements for styled UI.** Native `<select>`, `<input type="date">` render OS-native elements that cannot be styled. Build custom components.

Custom select triggers: `display: inline-flex` with `white-space: nowrap` to keep text and icons on same row.

## Navigation Context

Screens need grounding:
- Navigation (sidebar or top)
- Location indicator (breadcrumbs, active state)
- User context (who's logged in)

When building sidebars, consider using same background as main content. Linear, Vercel use subtle border for separation rather than different backgrounds.

## Dark Mode

- **Borders over shadows**: Shadows less visible on dark backgrounds
- **Adjust semantic colors**: Desaturate for dark backgrounds
- **Same hierarchy, inverted values**

## Anti-Patterns

Never:
- Dramatic drop shadows (`0 25px 50px...`)
- Large radius (16px+) on small elements
- Asymmetric padding without reason
- Pure white cards on colored backgrounds
- Thick borders (2px+) for decoration
- Spring/bouncy animations
- Multiple accent colors
- Motion without purpose

## The Standard

Different products want different things. A dev tool wants precision and density. A collaborative product wants warmth and space. A financial product wants trust and sophistication.

**Same quality bar, context-driven execution.**

## Implementation

Detect which styling approach the project uses, then load the matching reference:

| Project uses | Load |
|---|---|
| Vanilla CSS, CSS Modules, styled-components, or no Tailwind | [references/craft-css.md](references/craft-css.md) |
| Tailwind CSS | [references/craft-tailwind.md](references/craft-tailwind.md) |

If unclear, check for `tailwind.config` or `@tailwind` directives in the project. Default to CSS if neither is found.
