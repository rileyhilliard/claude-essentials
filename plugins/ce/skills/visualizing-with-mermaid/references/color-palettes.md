# Color Palette Guide

**Use a consistent, limited palette.** Don't use every color Mermaid offers. Choose colors based on your target environment (light mode, dark mode, or both).

## Contents

- [Choosing the Right Palette](#choosing-the-right-palette)
- [Light Mode Palette](#light-mode-palette)
- [Dark Mode Palette](#dark-mode-palette)
- [Universal Colors](#universal-colors-work-in-both-modes)
- [Color Usage Best Practices](#color-usage-best-practices)

## Choosing the Right Palette

**Light Mode**: Use when diagrams will be viewed on white/light backgrounds (documentation, presentations, printed materials)

**Dark Mode (Default)**: Use when diagrams will be viewed on dark backgrounds (dark-themed IDEs, terminal output, dark documentation themes)

**Universal**: Some colors work reasonably well in both modes but may need stroke adjustments

## Light Mode Palette

### Semantic Status Colors

Use these for states, alerts, and status indicators:

- **Success/Active**: `fill:#10b981,stroke:#059669,stroke-width:2px` (green)
- **Error/Critical**: `fill:#ef4444,stroke:#dc2626,stroke-width:2px` (red)
- **Warning/Attention**: `fill:#f59e0b,stroke:#d97706,stroke-width:2px` (amber)
- **Info/Secondary**: `fill:#3b82f6,stroke:#2563eb,stroke-width:2px` (blue)
- **Neutral/Inactive**: `fill:#e5e7eb,stroke:#6b7280,stroke-width:2px` (gray)

### Layer/Grouping Colors

Use pastels for subgraph backgrounds:

- **Frontend**: `fill:#dbeafe,stroke:#3b82f6,stroke-width:2px` (light blue)
- **Backend**: `fill:#dcfce7,stroke:#10b981,stroke-width:2px` (light green)
- **Infrastructure**: `fill:#f3e8ff,stroke:#a855f7,stroke-width:2px` (light purple)
- **External**: `fill:#fef3c7,stroke:#f59e0b,stroke-width:2px` (light yellow)
- **Data**: `fill:#fce7f3,stroke:#ec4899,stroke-width:2px` (light pink)

### Text Colors

- **Primary text**: `#1f2937` (dark gray, not pure black)
- **Secondary text**: `#6b7280` (medium gray)
- **On dark fills**: `#ffffff` (white - use only on dark status colors)

### Link/Arrow Colors

- **Default**: `#6b7280` (medium gray)
- **Primary path**: `#10b981` (green)
- **Error path**: `#ef4444` (red)

## Dark Mode Palette

### Semantic Status Colors

Use slightly muted colors with lighter strokes for better visibility:

- **Success/Active**: `fill:#065f46,stroke:#10b981,stroke-width:2px,color:#d1fae5` (dark green fill, light text)
- **Error/Critical**: `fill:#7f1d1d,stroke:#ef4444,stroke-width:2px,color:#fee2e2` (dark red fill, light text)
- **Warning/Attention**: `fill:#78350f,stroke:#f59e0b,stroke-width:2px,color:#fef3c7` (dark amber fill, light text)
- **Info/Secondary**: `fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#dbeafe` (dark blue fill, light text)
- **Neutral/Inactive**: `fill:#374151,stroke:#9ca3af,stroke-width:2px,color:#e5e7eb` (dark gray fill, light text)

### Layer/Grouping Colors

Use darker backgrounds with brighter strokes:

- **Frontend**: `fill:#1e3a8a,stroke:#60a5fa,stroke-width:2px` (dark blue)
- **Backend**: `fill:#14532d,stroke:#34d399,stroke-width:2px` (dark green)
- **Infrastructure**: `fill:#581c87,stroke:#c084fc,stroke-width:2px` (dark purple)
- **External**: `fill:#78350f,stroke:#fbbf24,stroke-width:2px` (dark amber)
- **Data**: `fill:#831843,stroke:#f472b6,stroke-width:2px` (dark pink)

### Text Colors

- **Primary text**: `#f9fafb` (off-white, not pure white)
- **Secondary text**: `#d1d5db` (light gray)
- **On light fills**: `#1f2937` (dark gray - rare in dark mode)

### Link/Arrow Colors

- **Default**: `#9ca3af` (light gray)
- **Primary path**: `#34d399` (bright green)
- **Error path**: `#f87171` (bright red)

## Universal Colors (Work in Both Modes)

These colors have good contrast in both light and dark environments:

### Semantic Colors (with appropriate text)

- **Success**: `fill:#059669,stroke:#10b981,stroke-width:2px,color:#ffffff` (medium green)
- **Error**: `fill:#dc2626,stroke:#ef4444,stroke-width:2px,color:#ffffff` (medium red)
- **Warning**: `fill:#d97706,stroke:#f59e0b,stroke-width:2px,color:#000000` (medium amber)
- **Info**: `fill:#2563eb,stroke:#3b82f6,stroke-width:2px,color:#ffffff` (medium blue)

**Note**: Universal colors sacrifice some visual softness for compatibility. Prefer mode-specific palettes when possible.

## Color Usage Best Practices

### Do:

- **Limit to 5 colors per diagram at most (3-4 is typical)** - More creates visual chaos
- **Use semantic meaning** - Blue for frontend, green for success, red for errors
- **Ensure sufficient contrast** - Test with contrast checkers (WCAG AA: 4.5:1 for text)
- **Use consistent colors** - Same color should mean the same thing across diagrams
- **Include stroke colors** - Strokes define boundaries and improve readability

### Don't:

- **Use pure black (#000000)** in light mode - Too harsh, use `#1f2937` instead
- **Use pure white (#ffffff)** in dark mode - Too bright, use `#f9fafb` instead
- **Mix light and dark mode colors** - Choose one palette and stick to it
- **Use low-contrast combinations** - Light yellow on white, dark blue on black, etc.
- **Rely only on color** - Use shapes, labels, and patterns for accessibility
