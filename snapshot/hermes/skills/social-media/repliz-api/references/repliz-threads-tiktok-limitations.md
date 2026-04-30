# Repliz API: Threads & TikTok Integration Limitations

## Key Facts
- Repliz supports **TikTok** and **X/Twitter** accounts.
- Repliz **does not support Instagram or Threads** accounts directly.
- A TikTok account connected to Repliz **cannot be used for Threads** operations.
- `repliz-api threads profile` and `repliz-api threads posts` will return `400: account_not_threads` for any non-Threads account.

## Workarounds
- To access Threads, connect a dedicated Threads account to Repliz via the Repliz dashboard.
- To access Instagram, use a third-party tool or API (e.g., `instagram-scraper`, `graph-api`) and integrate via a custom skill.

## Verification
```bash
repliz-api account list --page 1 --limit 1
repliz-api account get <ACCOUNT_ID>
```
Check the `type` field: only `threads`, `tiktok`, or `twitter` are supported.

## Note
This limitation is not a bug — it is a design constraint of the Repliz Public API. No token or credential can bypass it.