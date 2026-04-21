---
name: ui-styling
description: "UI styling skill: Tailwind CSS configuration, shadcn/ui components, font loading, canvas fonts. Use untuk component styling, Tailwind theme setup, shadcn/ui integration, responsive design."
---

# UI Styling

Tailwind CSS, shadcn/ui components, and UI styling best practices.

## When to Use

- Tailwind CSS configuration
- shadcn/ui component integration
- Component styling and theming
- Responsive design implementation
- Font loading and optimization
- Canvas/font generation

## Reference Files

- `references/tailwind-integration.md` - Tailwind setup and best practices
- `references/component-tokens.md` - Component token patterns

## Quick Commands

### Add shadcn/ui Component
```bash
python3 ~/.hermes/skills/ui-ux-pro-max/scripts/shadcn_add.py --component <component-name>
```

### Generate Tailwind Config
```bash
python3 ~/.hermes/skills/ui-ux-pro-max/scripts/tailwind_config_gen.py --tokens tokens.css --output tailwind.config.js
```

## Scripts

| Script | Purpose |
|--------|---------|
| `shadcn_add.py` | Add shadcn/ui component to project |
| `tailwind_config_gen.py` | Generate Tailwind config from tokens |
| `tailwind_config_gen.py --coverage` | Coverage report for UI components |

## Canvas Fonts

Pre-loaded canvas fonts available in `canvas-fonts/`:
- BigShoulders (Bold)
- Gloock (Regular)
- Lora (Regular)
- WorkSans (Regular)
- EricaOne
- NothingYouCouldDo

## Tailwind Best Practices

1. Use semantic token names in config
2. Support dark mode with `class` strategy
3. Use `@apply` sparingly
4. Keep config minimal, extend where needed
5. Use CSS variables for design tokens
6. Respect platform idioms (iOS/Android)
