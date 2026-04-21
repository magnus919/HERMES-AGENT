---
name: design-system
description: "Design token architecture: three-layer tokens (primitive→semantic→component), CSS variables, spacing/typography scales, component specs, slide generation. Use untuk design tokens, systematic design, brand-compliant presentations."
---

# Design System

Token architecture, component specifications, systematic design, slide generation.

## When to Use

- Design token creation (primitive, semantic, component layers)
- Component state definitions (default, hover, active, disabled, focus)
- CSS variable systems
- Spacing/typography scales
- Design-to-code handoff
- Tailwind theme configuration
- Slide/presentation generation

## Token Architecture

### Three-Layer Structure

```
Primitive (raw values)
       ↓
Semantic (purpose aliases)
       ↓
Component (component-specific)
```

**Example:**
```css
/* Primitive */
--color-blue-600: #2563EB;

/* Semantic */
--color-primary: var(--color-blue-600);

/* Component */
--button-bg: var(--color-primary);
```

## Quick Commands

### Generate Tokens
```bash
node ~/.hermes/skills/ui-ux-pro-max/scripts/generate-tokens.cjs --config tokens.json -o tokens.css
```

### Validate Usage
```bash
node ~/.hermes/skills/ui-ux-pro-max/scripts/validate-tokens.cjs --dir src/
```

### Embed Tokens
```bash
node ~/.hermes/skills/ui-ux-pro-max/scripts/embed-tokens.cjs --input tokens.css --output embedded.css
```

### Generate Slide
```bash
python3 ~/.hermes/skills/ui-ux-pro-max/scripts/generate-slide.py --topic "<topic>" --layout <layout>
```

### Search Slides
```bash
python3 ~/.hermes/skills/ui-ux-pro-max/scripts/search-slides.py "<query>" [-n <max_results>]
```

## Reference Files

| Topic | File |
|-------|------|
| Token Architecture | `references/token-architecture.md` |
| Primitive Tokens | `references/primitive-tokens.md` |
| Semantic Tokens | `references/semantic-tokens.md` |
| Component Tokens | `references/component-tokens.md` |
| Component Specs | `references/component-specs.md` |
| States & Variants | `references/states-and-variants.md` |
| Tailwind Integration | `references/tailwind-integration.md` |

## Component Spec Pattern

| Property | Default | Hover | Active | Disabled |
|----------|---------|-------|--------|----------|
| Background | primary | primary-dark | primary-darker | muted |
| Text | white | white | white | muted-fg |

## Design Tokens Starter Template

`templates/design-tokens-starter.json` - Base template for generating design tokens

## Slide Data

- `data/slide-layouts.csv` - Layout options
- `data/slide-strategies.csv` - Strategy guide
- `data/slide-layout-logic.csv` - Layout decision logic
- `data/slide-typography.csv` - Typography for slides
- `data/slide-color-logic.csv` - Color logic for slides
- `data/slide-backgrounds.csv` - Background options
- `data/slide-copy.csv` - Copy patterns
- `data/slide-charts.csv` - Chart types for slides
