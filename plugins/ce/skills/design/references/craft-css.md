# Craft Details

## The 4px Grid

All spacing uses a 4px base:
- `4px` - micro (icon gaps)
- `8px` - tight (within components)
- `12px` - standard (related elements)
- `16px` - comfortable (section padding)
- `24px` - generous (between sections)
- `32px` - major separation

## Symmetrical Padding

TLBR must match. If top is 16px, all sides are 16px.

```css
/* Good */
padding: 16px;
padding: 12px 16px; /* Only when horizontal needs more room */

/* Bad */
padding: 24px 16px 12px 16px;
```

## Border Radius

Stick to 4px grid. Pick a system:
- Sharp: 4px, 6px, 8px
- Soft: 8px, 12px
- Minimal: 2px, 4px, 6px

## Depth Strategies

Choose ONE approach:

**Borders-only (flat):** Clean, technical. Just subtle borders, no shadows.

```css
--border: rgba(0, 0, 0, 0.08);
border: 0.5px solid var(--border);
```

**Single shadow:** Soft lift.

```css
--shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
```

**Layered shadows:** Premium, dimensional.

```css
--shadow-layered:
  0 0 0 0.5px rgba(0, 0, 0, 0.05),
  0 1px 2px rgba(0, 0, 0, 0.04),
  0 2px 4px rgba(0, 0, 0, 0.03),
  0 4px 8px rgba(0, 0, 0, 0.02);
```

## Typography

- Headlines: 600 weight, -0.02em tracking
- Body: 400-500 weight
- Labels: 500 weight, slight positive tracking for uppercase
- Scale: 11px, 12px, 13px, 14px (base), 16px, 18px, 24px, 32px

## Monospace for Data

Numbers, IDs, codes, timestamps in monospace. Use `tabular-nums` for columns.

## Iconography

Use **Phosphor Icons** (`@phosphor-icons/react`). If removing an icon loses no meaning, remove it.

## Animation

- 150ms for micro-interactions
- 200-250ms for larger transitions
- Easing: `cubic-bezier(0.25, 1, 0.5, 1)`
- No spring/bouncy effects

## Color Hierarchy

Four levels: foreground → secondary → muted → faint.

Color only for meaning: status, action, error, success. Gray builds structure.

## Isolated Controls

Never use native form elements (`<select>`, `<input type="date">`). Build custom components.

Custom select triggers: `display: inline-flex` with `white-space: nowrap`.

## Dark Mode

- Borders over shadows (shadows less visible)
- Desaturate semantic colors
- Same hierarchy, inverted values

## Anti-Patterns

Never:
- Dramatic drop shadows (`box-shadow: 0 25px 50px...`)
- Large border radius (16px+) on small elements
- Asymmetric padding without reason
- Pure white cards on colored backgrounds
- Thick borders (2px+) for decoration
- Spring/bouncy animations
- Multiple accent colors
