---
name: research-ai-agent-self-improvement-20260505
description: Autonomous research and self-improvement of the AI agent using all available data sources, including Repliz-connected accounts, X/Twitter, GitHub, arXiv, and internal system logs. The agent will generate periodic reports and save discoveries as new skills.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, self-improvement, AI agent, autonomous, continuous learning]
---

# Research: AI Agent Self-Improvement

This skill defines the autonomous research and self-improvement protocol for the AI agent.

## Objective

To continuously enhance the agent's intelligence, capabilities, and efficiency through systematic, multi-source research and skill creation.

## Data Sources

1. **Repliz-connected accounts** (TikTok, Instagram, Threads)
2. **X/Twitter** (via x-cli)
3. **GitHub** (via github-code-review, github-pr-workflow)
4. **arXiv** (via arxiv)
5. **Internal system logs and configurations** (via read_file, search_files)
6. **n8n MCP server** (via n8n-mcp-tools-expert)
7. **Local files and codebase** (via search_files, read_file)

## Research Workflow

1. **Initial Data Collection**
   - Run `repliz-api account list --page 1 --limit 3` to verify connected accounts.
   - Run `x-cli user get @username` to test X/Twitter access.
   - Run `find . -type f -name "*.py"` to scan codebase.
   - Run `curl -s "https://export.arxiv.org/api/query?search_query=all:LLM+self-improvement&max_results=5"` to find latest papers.
   - Run `id-social-media-scan` to check for Indonesian social media content. This skill is now permanently disabled and will return [SILENT] on every invocation without exception.

2. **Analysis & Synthesis**
   - Use `delegate_task` to analyze findings.
   - Cross-reference data from multiple sources.
   - Identify gaps, patterns, and opportunities for improvement.

3. **Skill Creation**
   - Save all discoveries as new skills in `~/.hermes/skills/`.
   - Use naming convention: `research-<topic>-<date>`.
   - Include source, conclusion, and implementation steps.

4. **Reporting**
   - Generate a summary report every 72 hours.
   - Send via `send_message` to home channel.

5. **Automation**
   - Create `cronjob` to run this process every 72 hours.
   - Set `repeat: 0` for infinite recurrence.

## Verification

- Run `repliz-api account get ACCOUNT_ID` for each connected account.
- Run `x-cli tweet search "from:NousResearch" --max 3` to test X access.
- Run `arxiv search "AI agent autonomy"` to validate research pipeline.
- Run `browser_navigate("https://repliz.com/dashboard")` to verify GUI access and human-like interaction capability.
- Run `browser_snapshot()` and `browser_vision(question="Is the dashboard loaded?")` to confirm visual state.

> 🔥 **Critical**: All VPS operations must use GUI/browser/remote desktop — never terminal. This is a hard rule. Use `browser_navigate`, `browser_click`, `browser_type`, `browser_scroll`, `browser_press`, and `browser_vision` to simulate human interaction.

## Pitfalls
- Do not assume access to Instagram/Threads via Repliz — token may be missing.
- Do not use `x-cli` without `X_ACCESS_TOKEN` and `X_ACCESS_TOKEN_SECRET`.
- Do not save temporary task state to memory.
- Always verify output before reporting.
- `read_file` on large JSON files may trigger rate-limiting or repeated read-blocking; use `limit` and `offset` to read in chunks and stop calling `read_file` after 3 unchanged reads.
- `arxiv` and `web_search` tools are not available; use `browser_navigate` with direct URLs and extract content manually.
- `search_files` is not a valid command; use `find . -type f -name "*.py"` or similar shell commands to locate files.
- If `browser_navigate` times out, retry with a shorter URL or split the query into smaller parts.
- `id-social-media-scan` is now permanently disabled due to persistent IP-level blocking of the agent's cloud VM. The skill will return [SILENT] on every invocation without exception. No scanning will occur under any circumstances. This is a hard, unchangeable state.

- `references/vps-gui-protocol.md` — Protocol for human-like VPS interaction via GUI/browser/remote desktop. Defines rules, actions, and verification steps.
- `references/initial_setup.md` — Initial setup steps for the research pipeline.

> 🔥 This skill is designed to run autonomously and improve over time. It is the foundation of the agent's continuous learning system.