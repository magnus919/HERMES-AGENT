---
name: design
description: "Comprehensive design skill: brand identity, logo generation, corporate identity program (CIP), HTML presentations, banner design, icon design, social photos. Actions: design logo, create CIP, generate mockups, build slides, design banner, generate icon, create social photos, brand identity, design system. Platforms: Facebook, Twitter, LinkedIn, YouTube, Instagram, Pinterest, TikTok, Threads, Google Ads."
---

# Design

Unified design skill: brand, tokens, UI, logo, CIP, slides, banners, social photos, icons.

## Sub-Skill Routing

| Task | Sub-skill | Details |
|------|-----------|---------|
| Brand identity, voice, assets | `brand` | Brand guidelines & voice |
| Design tokens, systematic design | `design-system` | Token architecture, component specs |
| Tailwind, shadcn/ui styling | `ui-styling` | UI component styling |
| Logo design, AI generation | `design` | 55 logo styles with prompts |
| Corporate identity program | `design` | 50 CIP deliverables |
| Presentations, pitch decks | `slides` | HTML slide generation |
| Social/ads/web/print banners | `banner-design` | 22 banner styles |
| Icon design, SVG generation | `design` | 15 icon styles |

## Reference Files

- `references/logo-design.md` - Logo design patterns
- `references/logo-style-guide.md` - Style guidelines
- `references/logo-prompt-engineering.md` - AI prompt engineering
- `references/logo-color-psychology.md` - Color psychology
- `references/icon-design.md` - Icon design guide
- `references/cip-design.md` - CIP design patterns
- `references/cip-style-guide.md` - CIP style guidelines
- `references/cip-prompt-engineering.md` - CIP prompt engineering
- `references/cip-deliverable-guide.md` - Deliverables guide
- `references/slides.md` - Slide creation
- `references/slides-create.md` - How to create slides
- `references/slides-strategies.md` - Slide strategies
- `references/slides-layout-patterns.md` - Layout patterns
- `references/slides-copywriting-formulas.md` - Copywriting
- `references/slides-html-template.md` - HTML template
- `references/social-photos-design.md` - Social photo design
- `references/banner-sizes-and-styles.md` - Banner reference
- `references/design-routing.md` - Task routing guide

## Data Files

- `data/logo/styles.csv` - 55 logo styles
- `data/logo/colors.csv` - Color psychology data
- `data/logo/industries.csv` - Industry-specific logos
- `data/cip/styles.csv` - CIP styles
- `data/cip/industries.csv` - CIP industries
- `data/cip/mockup-contexts.csv` - Mockup contexts
- `data/cip/deliverables.csv` - 50 deliverables
- `data/icon/styles.csv` - 15 icon styles

## Quick Commands

### Generate Logo
```bash
python3 ~/.hermes/skills/ui-ux-pro-max/scripts/search.py "<style> <industry> logo" --domain prompt
```

### Generate Banner Sizes
```bash
# See banner-sizes-and-styles.md reference
```

### Generate Slides
```bash
python3 skills/design-system/scripts/generate-slide.py --topic "<topic>" --layout <layout>
```
