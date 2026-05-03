# Context Budget Discipline

Four-tier model for managing context window degradation during long, multi-step workflows. The model defines when to act, how to act, and what to preserve — critical for orchestrating complex agent runs.

Adapted from the GSD (Get Shit Done) project's context discipline reference — MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)).

## The four tiers

### Tier 1: PEAK (0–30% context used)

**Behavior:** No action needed. Context is abundant. Use full depth.

**Rules:**
- Read depth: full context window
- No pruning
- No summaries
- No abstractions

### Tier 2: GOOD (31–50% context used)

**Behavior:** Begin light pruning. Preserve core structure.

**Rules:**
- Read depth: full context window
- Prune only non-essential artifacts (e.g., verbose logs, duplicate output)
- Preserve full task text, plan structure, and code
- No summaries

### Tier 3: DEGRADING (51–70% context used)

**Behavior:** Actively manage context. Prune aggressively.

**Rules:**
- Read depth: 50% of context window
- Prune: remove redundant or low-signal artifacts (e.g., repeated debug prints, long error traces)
- Summarize: generate one-sentence summaries for each task or file
- Preserve: task list, file paths, and critical code
- Use `context-budget-discipline.md` reference to guide pruning

### Tier 4: POOR (>70% context used)

**Behavior:** Emergency mode. Stop and checkpoint.

**Rules:**
- Read depth: 25% of context window
- Prune: remove all non-essential content — keep only task list, file paths, and minimal code
- Summarize: generate a full summary of all completed tasks and state
- **Abort:** If any action is required that would exceed the window, stop immediately, checkpoint current state, and report the reason

## How to use this in a skill

When you design a workflow that spans multiple subagent invocations, long review loops, or complex artifact generation, **monitor context usage** and **act at the appropriate tier**.

Use the `references/context-budget-discipline.md` file to guide pruning and summarization decisions. Load it when the run will consume significant context (e.g., >5 tasks, 10+ file changes, long test runs).

## Example — a long orchestration with context management

```
[Start] Read plan: 20 tasks
[PEAK] Tier 1: Read full plan, extract tasks

[Task 1] Dispatch implementer
[GOOD] Tier 2: Full context, no pruning
[Revision] Reviewer: PASS
[Task 2] Dispatch implementer
[GOOD] Tier 2: Full context
[Revision] Reviewer: PASS

... (tasks 3–10)

[Task 11] Dispatch implementer
[DEGRADING] Tier 3: Context at 65%
- Prune: remove verbose logs
- Summarize: one-sentence summary of each task
- Use context-budget-discipline.md to guide pruning

[Task 12] Dispatch implementer
[POOR] Tier 4: Context at 73%
- Prune: keep only task list, file paths, minimal code
- Summarize: full summary of completed tasks
- **Abort:** Stop execution, checkpoint, report "context window exceeded"
```

## Why this matters

Without context discipline, long workflows silently degrade. The agent stops understanding the plan, produces incomplete code, and fails without warning. This model makes degradation visible and actionable.

## Further reading

- **`references/gates-taxonomy.md`** — The four canonical gate types (Pre-flight, Revision, Escalation, Abort) with behavior, recovery, and examples. Load when designing or reviewing any workflow that has validation checkpoints — use the vocabulary explicitly so each gate has defined entry, failure behavior, and resumption rules.

Both references adapted from gsd-build/get-shit-done (MIT © 2025 Lex Christopherson).