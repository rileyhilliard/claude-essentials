# Craft Details (Tailwind)

Design philosophy from SKILL.md expressed through Tailwind primitives. This isn't a Tailwind tutorial. It's how to make the design principles concrete in a Tailwind codebase.

## Tailwind's Default Bias

Tailwind's defaults are heavily represented in AI training data. Using them without customization produces the "AI slop" aesthetic: `bg-indigo-500` buttons, `text-gray-600` body text, `rounded-lg shadow-md` cards on `bg-gray-50`. Every AI-generated landing page looks like this.

**Before writing any components**, customize `tailwind.config` with your product's design tokens (see Color Hierarchy and Border Radius sections below). The goal is that your Tailwind classes map to your design system, not Tailwind's generic defaults.

Don't reach for: `bg-indigo-*`, `bg-violet-*`, `bg-purple-*` unless the product's design direction specifically calls for it. Don't default to `rounded-lg` on everything. Don't use `shadow-md` as your only elevation.

## The 4px Grid in Tailwind

Tailwind's spacing scale already uses 4px increments. Map the design grid directly:

| Design intent | Tailwind class | Value |
|---|---|---|
| Micro (icon gaps) | `gap-1` | 4px |
| Tight (within components) | `gap-2`, `p-2` | 8px |
| Standard (related elements) | `gap-3`, `p-3` | 12px |
| Comfortable (section padding) | `gap-4`, `p-4` | 16px |
| Generous (between sections) | `gap-6`, `p-6` | 24px |
| Major separation | `gap-8`, `p-8` | 32px |

Stay on the grid. Avoid `p-5` (20px) and `p-7` (28px) unless you have a specific reason. They break the 4px rhythm.

## Symmetrical Padding

```html
<!-- Good: symmetrical -->
<div class="p-4">
<div class="px-4 py-3"> <!-- Only when horizontal needs more room -->

<!-- Bad: asymmetric noise -->
<div class="pt-6 pr-4 pb-3 pl-4">
```

## Depth Strategy

Commit to one approach per product. Don't mix.

**Borders-only (flat):** Use `divide-` and `border` utilities with low-opacity custom colors.

```html
<div class="border border-black/[0.08] rounded-lg">
```

**Subtle shadow:** Tailwind's `shadow-sm` is close but often too heavy. Prefer a custom shadow in `tailwind.config`:

```js
// tailwind.config
theme: {
  extend: {
    boxShadow: {
      'subtle': '0 1px 3px rgba(0, 0, 0, 0.08)',
      'layered': '0 0 0 0.5px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.04), 0 2px 4px rgba(0,0,0,0.03), 0 4px 8px rgba(0,0,0,0.02)',
    }
  }
}
```

Then use `shadow-subtle` or `shadow-layered` consistently. Don't reach for `shadow-lg` or `shadow-xl`.

## Color Hierarchy with Custom Properties

Tailwind's default palette is too broad. Define a constrained palette in your config using semantic names:

```js
// tailwind.config
theme: {
  extend: {
    colors: {
      fg: {
        DEFAULT: 'var(--fg)',           // foreground
        secondary: 'var(--fg-secondary)', // secondary text
        muted: 'var(--fg-muted)',       // muted text
        faint: 'var(--fg-faint)',       // faintest text
      },
      surface: {
        DEFAULT: 'var(--surface)',
        raised: 'var(--surface-raised)',
      },
      accent: 'var(--accent)',
    }
  }
}
```

This gives you `text-fg`, `text-fg-secondary`, `text-fg-muted`, `bg-surface`, `bg-surface-raised`, `text-accent`. Four levels of contrast, one accent. Gray builds structure, color only for meaning.

## Typography

Use Tailwind's font-size utilities but constrain the scale:

```html
<!-- Headlines -->
<h1 class="text-2xl font-semibold tracking-tight">
<h2 class="text-lg font-semibold tracking-tight">

<!-- Body -->
<p class="text-sm text-fg-secondary">

<!-- Labels -->
<span class="text-xs font-medium uppercase tracking-wide text-fg-muted">

<!-- Data -->
<span class="font-mono text-sm tabular-nums">
```

`tracking-tight` on headlines, `tracking-wide` on uppercase labels. `tabular-nums` on any column of numbers.

## Border Radius

Pick a system in your config and use it everywhere:

```js
// Sharp product (dev tools, terminals)
borderRadius: { sm: '4px', DEFAULT: '6px', lg: '8px' }

// Soft product (collaborative, friendly)
borderRadius: { sm: '6px', DEFAULT: '8px', lg: '12px' }
```

Then stick to `rounded-sm`, `rounded`, `rounded-lg`. Don't freestyle with `rounded-2xl` or `rounded-3xl` on small elements.

## Dark Mode

Use Tailwind's `dark:` variant with CSS custom properties:

```html
<div class="border border-black/[0.08] dark:border-white/[0.1]">
<div class="bg-surface dark:bg-surface shadow-subtle dark:shadow-none dark:border dark:border-white/[0.06]">
```

Key shifts: borders replace shadows, semantic colors desaturate, same hierarchy with inverted values.

## Animation

Use Tailwind's `transition` and `duration` utilities:

```html
<!-- Micro-interactions: 150ms -->
<button class="transition-colors duration-150">

<!-- Larger transitions: 200-300ms -->
<div class="transition-all duration-200 ease-out">
```

Avoid `duration-500`, `duration-700`, or anything `bounce`/`spring`-related.

## Class Organization

When a component has many utilities, group them by concern:

```html
<div class="
  flex items-center gap-3        <!-- layout -->
  p-4 rounded-lg                 <!-- box model -->
  bg-surface border border-black/[0.08]  <!-- surface -->
  text-sm text-fg-secondary      <!-- typography -->
  transition-colors duration-150 <!-- motion -->
">
```

This isn't about line breaks in production (use Prettier). It's about thinking in layers: layout, box model, surface, typography, motion.

## Anti-Patterns

| Avoid | Why | Instead |
|---|---|---|
| `shadow-lg`, `shadow-xl`, `shadow-2xl` | Too dramatic for UI components | Custom `shadow-subtle` or `shadow-layered` |
| `rounded-full` on rectangles | Looks unintentional | `rounded-lg` max |
| `p-1 md:p-3 lg:p-6` at every breakpoint | Over-responsive, inconsistent feel | Pick one padding, adjust at one breakpoint max |
| `text-blue-500`, `text-green-400` everywhere | Color without semantic meaning | Semantic tokens: `text-accent`, `text-success` |
| `animate-bounce`, `animate-spin` for UI | Decorative motion | `transition-*` with short durations |
| Mixing `gap-*` with margin hacks | Inconsistent spacing model | Use `gap-*` exclusively for flex/grid layouts |
