---
name: ui-ux-pro-max
description: "UI/UX design intelligence untuk web dan mobile.包含50+ styles, 161 color palettes, 57 font pairings, 161 product types, 99 UX guidelines, dan 25 chart types across 10 stacks (React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui, HTML/CSS). Trigger: plan, build, create, design, implement, review, fix, improve, optimize, enhance, refactor UI/UX code."
---

# UI/UX Pro Max - Design Intelligence

Comprehensive design guide untuk web dan mobile applications. Terdapat 50+ styles, 161 color palettes, 57 font pairings, 161 product types, 99 UX guidelines, dan 25 chart types. Database searchable dengan priority-based recommendations.

## Trigger Conditions

Skill ini **HARUS** digunakan ketika task melibatkan:

- Mendesain halaman baru (Landing Page, Dashboard, Admin, SaaS, Mobile App)
- Membuat atau refactor UI components (buttons, modals, forms, tables, charts, dll)
- Memilih color schemes, typography systems, spacing standards, atau layout systems
- Review UI code untuk user experience, accessibility, atau visual consistency
- Mengimplementasikan navigation structures, animations, atau responsive behavior
- Membuat product-level design decisions (style, information hierarchy, brand expression)
- Improving perceived quality, clarity, atau usability of interfaces

## Rule Priorities

| Priority | Category | Impact | Domain | Must Have | Anti-Patterns |
|----------|----------|--------|--------|-----------|---------------|
| 1 | Accessibility | CRITICAL | `ux` | Contrast 4.5:1, Alt text, Keyboard nav, Aria-labels | Removing focus rings, Icon-only buttons without labels |
| 2 | Touch & Interaction | CRITICAL | `ux` | Min 44×44px, 8px+ spacing, Loading feedback | Hover-only reliance, Instant state changes |
| 3 | Performance | HIGH | `ux` | WebP/AVIF, Lazy loading, CLS < 0.1 | Layout thrashing, Cumulative Layout Shift |
| 4 | Style Selection | HIGH | `style` | Match product type, Consistency, SVG icons | Mixing flat & skeuomorphic randomly |
| 5 | Layout & Responsive | HIGH | `ux` | Mobile-first, Viewport meta, No horizontal scroll | Horizontal scroll, Fixed px widths |
| 6 | Typography & Color | MEDIUM | `typography`, `color` | Base 16px, Line-height 1.5, Semantic tokens | Text < 12px body, Gray-on-gray |
| 7 | Animation | MEDIUM | `ux` | 150-300ms, Motion conveys meaning | Decorative-only animation |
| 8 | Forms & Feedback | MEDIUM | `ux` | Visible labels, Error near field | Placeholder-only label |
| 9 | Navigation Patterns | HIGH | `ux` | Predictable back, Bottom nav ≤5 | Overloaded nav, Broken back |
| 10 | Charts & Data | LOW | `chart` | Legends, Tooltips, Accessible colors | Color-only meaning |

## Quick Commands

### Search Database

```bash
python3 ~/.hermes/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain> [-n <max_results>]
```

### Domain Search Options

| Domain | Use For | Example |
|--------|---------|---------|
| `product` | Product type recommendations | SaaS, e-commerce, portfolio |
| `style` | UI styles, effects | glassmorphism, minimalism, dark |
| `typography` | Font pairings, Google Fonts | elegant, playful, modern |
| `color` | Color palettes by product | saas, healthcare, beauty |
| `landing` | Page structure, CTA | hero, testimonial, pricing |
| `chart` | Chart types, libraries | trend, comparison, pie |
| `ux` | Best practices, anti-patterns | animation, accessibility |
| `google-fonts` | Individual font lookup | sans serif, variable |
| `react` | React/Next.js performance | memo, rerender, bundle |
| `web` | App interface guidelines | accessibilityLabel, safe areas |

### Generate Design System

```bash
python3 ~/.hermes/skills/ui-ux-pro-max/scripts/search.py "<product_type> <industry>" --design-system [-p "Project Name"]
```

### Persist Design System

```bash
python3 ~/.hermes/skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name"
```

### Stack Search

```bash
python3 ~/.hermes/skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack <stack>
```

Available stacks: `html-tailwind`, `react`, `nextjs`, `astro`, `vue`, `nuxtjs`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`

## Quick Reference

### Accessibility (CRITICAL)
- `color-contrast` - Min 4.5:1 ratio (large text 3:1)
- `focus-states` - Visible focus rings 2-4px
- `alt-text` - Descriptive alt for meaningful images
- `aria-labels` - aria-label for icon-only buttons
- `keyboard-nav` - Tab order matches visual order
- `form-labels` - Use label with for attribute
- `reduced-motion` - Respect prefers-reduced-motion
- `heading-hierarchy` - Sequential h1→h6

### Touch & Interaction (CRITICAL)
- `touch-target-size` - Min 44×44pt / 48×48dp
- `touch-spacing` - Min 8px gap between targets
- `loading-buttons` - Disable during async, show spinner
- `error-feedback` - Clear error messages near problem
- `tap-delay` - Use touch-action: manipulation
- `haptic-feedback` - Use for confirmations (don't overuse)

### Typography & Color (MEDIUM)
- `line-height` - 1.5-1.75 for body text
- `line-length` - 65-75 chars per line
- `font-pairing` - Match heading/body personalities
- `color-semantic` - Use semantic tokens, not raw hex
- `color-dark-mode` - Desaturated/lighter tonal variants

### Animation (MEDIUM)
- `duration-timing` - 150-300ms micro-interactions
- `transform-performance` - Use transform/opacity only
- `easing` - ease-out entering, ease-in exiting
- `reduced-motion` - Respect prefers-reduced-motion

### Forms (MEDIUM)
- `input-labels` - Visible label, not placeholder-only
- `error-placement` - Error below related field
- `submit-feedback` - Loading → success/error state
- `inline-validation` - Validate on blur, not keystroke

## Example Workflow

**Request:** "Buatkan landing page untuk SaaS product"

```bash
# 1. Generate design system
python3 ~/.hermes/skills/ui-ux-pro-max/scripts/search.py "saas software tool" --design-system -p "SaaS Product"

# 2. Get landing page structure
python3 ~/.hermes/skills/ui-ux-pro-max/scripts/search.py "hero social-proof pricing" --domain landing

# 3. Get style options
python3 ~/.hermes/skills/ui-ux-pro-max/scripts/search.py "minimal modern saas" --domain style

# 4. Get typography
python3 ~/.hermes/skills/ui-ux-pro-max/scripts/search.py "modern professional" --domain typography
```

## Data Files Location

- `~/.hermes/skills/ui-ux-pro-max/data/` - CSV databases (products, styles, colors, typography, ux-guidelines, charts, dll)
- `~/.hermes/skills/ui-ux-pro-max/scripts/` - Python search engine (BM25 + regex)
- `~/.hermes/skills/ui-ux-pro-max/templates/` - Template files
