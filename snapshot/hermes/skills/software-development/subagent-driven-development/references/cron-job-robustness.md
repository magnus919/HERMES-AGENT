---
name: cron-job-robustness
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Cron Job Robustness: Avoiding Truncation and Timeout Failures

## Key Principles

1. **Separate data collection from synthesis** — never combine them in one task. Collect all raw data first, save to file, then use that file as input for the synthesis phase.
2. **Use `artifacts` field** in cron config to explicitly list all generated files (e.g., `data/2026-05-07-08-00-00.json`, `logs/scraper-2026-05-07.log`). This enables auditability and recovery.
3. **Set explicit timeouts** for data collection tasks. If a task exceeds its timeout, fail early and log the failure.
4. **Handle missing or failed data sources gracefully** — log the error, but don't crash the entire job. Use fallbacks if available.
5. **Log all source URLs and timestamps** for traceability.

## Example Configuration

```yaml
name: morning-digest
schedule: '0 8 * * *'
script: 'scripts/collect-data.sh'
artifacts:
  - data/2026-05-07-08-00-00.json
  - logs/scraper-2026-05-07.log
timeout: 300
```

## Why This Works

- Prevents output truncation: data collection and synthesis are separate steps.
- Enables debugging: if synthesis fails, you can inspect the collected data.
- Supports audit: all artifacts are tracked and versioned.
- Improves reliability: if one source fails, others can still succeed.

## Related Skills

- `subagent-driven-development`: Use this skill to orchestrate the two-stage workflow.
- `hermes-agent-skill-authoring`: Use the `artifacts` field in SKILL.md for cron jobs.
- `cron-timeout-safe-research-digests`: For advanced cron-based research and digest jobs.

## Source

Based on the failed `nightly-ai-web-scan` job (ID: 5e591a7be711) on 2026-05-07, where output was truncated due to combining data collection and synthesis in a single task. The fix was to separate the workflow into two stages and use the `artifacts` field to track generated files.