---
name: cron-timeout-safe-research-digests
description: Design and repair autonomous cron-based research/digest jobs so they finish reliably within Hermes cron time limits while staying honest, sourced, and useful.
triggers:
  - User wants scheduled research digests or monitoring jobs
  - A cron research job timed out or returned incomplete results
  - The task involves broad web/social scanning in an autonomous run
---

# Cron Timeout-Safe Research Digests

Use this skill when creating or fixing autonomous research cron jobs, especially when the job must gather current information, include sources, and run without user interaction.

## Why this skill exists

Cron runs are time-boxed and have no live user clarification. Broad prompts like “search Threads, Instagram, AI agents, Hermes, and general AI; learn everything; report fully” can exceed the cron timeout, especially when social/public sources are slow, JS-gated, or only partially accessible.

## Core pattern

Design the cron prompt to be explicitly bounded.

### Required constraints to include

1. Add a hard time budget
   - Example: `Finish within 7 minutes of work.`
   - Leave headroom under the cron timeout instead of using the full budget.

2. Cap the number of sources
   - Example: `Collect at most 6 total sources.`
   - Prefer fewer high-signal sources over broad coverage.

3. Limit slow/fragile source classes
   - For Threads/Instagram/public social pages: only check them if quickly accessible.
   - Example: `Check Threads and Instagram public content only if it is quickly accessible in under 2 minutes total; if access is limited, explicitly say so and move on.`

4. Define trusted fallback sources
   - Prefer official blogs, company announcements, GitHub repos/releases, arXiv, and reputable reporting.
   - Social sources should be optional, not blocking.

5. Force honesty and explicit uncertainty
   - Include directives such as:
     - `Never fabricate access, findings, or source details.`
     - `If something cannot be verified, say that clearly.`

6. Require a compact output structure
   - Recommended sections:
     1. `Ringkasan 5 poin terpenting hari ini`
     2. `Mengapa ini penting`
     3. `Sumber`
     4. `Apa yang belum bisa diverifikasi`

7. Keep the job read-only unless the user explicitly requested account actions
   - Add: `Do not post, like, comment, follow, or modify any account.`

## Repair procedure after a timeout

When a cron digest times out:

1. Inspect the job status with `cronjob(action='list', include_disabled=true)`.
2. Confirm the failing job ID, last status, and schedule.
3. Update the existing job instead of creating a duplicate when possible.
4. Shrink the prompt scope using the constraints above.
5. Update any companion jobs (for example, a morning digest that depends on the same style of research) so they use the same bounded approach.
6. Optionally trigger a manual rerun with `cronjob(action='run', job_id=...)` after the prompt is fixed.
7. Tell the user plainly that the previous failure was caused by timeout due to too-broad scope.

## Recommended prompt template

```text
At [time/frequency], produce a short, sourced [language] research brief about [topic].

Hard constraints to avoid timeout:
- Finish within 7 minutes of work.
- Do not attempt exhaustive research.
- Collect at most 6 total sources.
- Check [slow source classes] only if quickly accessible in under 2 minutes total; if access is limited, explicitly say so and move on.
- Prefer fast, reliable public sources such as official blogs, company announcements, GitHub repos/releases, arXiv, and reputable news.
- Never fabricate access, findings, or source details.
- If something cannot be verified, say that clearly.

Output format:
1) [top findings]
2) [why it matters]
3) Sources
4) What could not be verified

Behavior:
- Be honest and precise.
- Read-only research only.
- Prioritize recency and credibility over quantity.
```

## Signs the prompt is too broad

Reduce scope if the prompt includes several of these at once:
- multiple source ecosystems (social + web + academic + repo scanning)
- vague goals like “serap semua informasi” or “cover everything up to date”
- no source cap
- no time budget
- no fallback when social access is blocked
- no output size limit

## Notes learned from experience

- Threads/Instagram public research is especially risky in cron because access may be limited, login-gated, or slow.
- A concise, high-signal digest is more reliable than an exhaustive one.
- For recurring digests, pair a nightly collection brief with a morning delivery only if both prompts are individually bounded.
- Always preserve the user’s requirement for sources and honesty, even when reducing scope.
- Prefer machine-readable feeds and APIs over page scraping whenever possible. In practice, RSS/Atom/GitHub API endpoints are much faster and more reliable than browsing rendered pages during cron runs.
- Concrete fast-paths that worked well:
  - OpenAI News RSS: `https://openai.com/news/rss.xml` (the HTML news page may return 403 / Cloudflare challenge while RSS still works)
  - If the official article page is bot-blocked but the official RSS item is accessible, you may still report the item using the RSS title/description as the source — but explicitly say you could not verify the full article body.
  - GitHub release feeds: `https://github.com/<owner>/<repo>/releases.atom`
  - GitHub JSON APIs for releases/commits: `https://api.github.com/repos/<owner>/<repo>/releases` and `/commits`
  - For GitHub releases, request only a small page (`?per_page=1..3`) and locally extract the top bullets you need. Full release JSON can be extremely large and may overflow tool output budgets.
  - arXiv API for recent papers instead of site browsing
- For quick social checks, use the browser only as a time-boxed probe. If Threads/Instagram immediately show login walls or limited public visibility, record that explicitly and move on rather than spending the budget fighting access.
- Threads-specific fast path learned in practice: public access is uneven. Search result pages like `/search?q=...` and some direct post/profile URLs may still expose enough text/time metadata to extract a usable signal without login, while other accounts or clicks bounce to login. Prefer harvesting visible text from search/profile pages first; only open a direct post if you need to confirm wording or the canonical URL.
- Instagram-specific fast path learned in practice: public profile URLs often redirect straight to `/accounts/login/` in headless browsing. Treat that as an access limitation, not a challenge to bypass.
- On Threads, full post snapshots can be slower or time out more often than search/profile snapshots. When the search/profile page already shows the post text, timestamp, and canonical post link, that is usually enough for a bounded digest.
- A good under-7-minute workflow is: 1) pull 4-6 candidate feed/API sources, 2) extract the newest 1-2 items from each, 3) keep only the strongest 4-5 claims, 4) mention unverifiable areas instead of stretching coverage.
- If one combined job still times out, split it into multiple narrower jobs by source class instead of just trimming wording. A strong pattern is:
  1) social scan job (Threads/Instagram/public social only, local delivery)
  2) web scan job (official blogs/GitHub/arXiv/news only, local delivery)
  3) morning digest job (reads the newest local outputs from the scan jobs and sends one user-facing summary)
- When splitting jobs, stagger them rather than firing all at the same minute. Example: social at 23:05, web at 23:20, digest at 08:00.
- Use `deliver='local'` for intermediate collection jobs and `deliver='origin'` only for the final digest. This avoids spamming the user while still leaving artifacts the digest job can read.
- The morning digest prompt should explicitly inspect the newest files under `~/.hermes/cron/output/<job_id>/` for each feeder job, then synthesize verified findings. Tell it to admit when a feeder job failed or produced nothing.
- If you split a recurring job after a late-night failure, create a one-shot catch-up job for any new feeder that has not produced its first output yet. Then point the digest job at both the regular feeder directory and the catch-up job directory as fallback inputs.
- After manual `cronjob(action='run', ...)`, do not assume success from the accept response alone. Re-check `cronjob(action='list')`, recent sessions, or output files to confirm a real result was produced.
