# VPS GUI Interaction Protocol

## Rules
- All VPS operations must be performed via GUI/browser/remote desktop — never via terminal.
- Simulate human behavior: use mouse and keyboard actions (click, type, scroll, etc.).
- Use `browser_navigate`, `browser_click`, `browser_type`, `browser_scroll`, `browser_press`, and `browser_vision`.
- Never use `terminal` or `ssh` commands.

## Common Actions
- `browser_navigate(url)` — open a new page
- `browser_snapshot()` — capture current screen
- `browser_click(ref="@e5")` — click an element by reference
- `browser_type(ref="@e3", text="hello")` — type into an input
- `browser_scroll(direction="down")` — scroll the page
- `browser_press(key="Enter")` — press a key
- `browser_vision(question="What is on this page?")` — analyze visual content

## Verification
- Always run `browser_snapshot()` after navigation.
- Use `browser_vision` to confirm state (e.g., 'Is the dashboard loaded?').
- If a page fails to load, retry with a 5-second delay.

## Pitfalls
- Do not assume the browser is ready immediately after `browser_navigate`.
- Do not use `terminal` for any VPS operation.
- Do not rely on text-only parsing — use `browser_vision` for visual confirmation.

> 🔥 This protocol is mandatory for all VPS interactions. Violation is not allowed.