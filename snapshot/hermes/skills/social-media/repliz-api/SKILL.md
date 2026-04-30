---
name: repliz-api
description: Use Repliz Public API for accounts, schedules, and queue replies via a local CLI wrapper authenticated with Basic Auth credentials stored in ~/.hermes/.env.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Repliz, API, Social Media, Scheduling, Queue, Basic Auth]
---

# Repliz API

Use this skill when the user wants Hermes to interact with the Repliz Public API.

## What this skill provides

A local CLI helper and wrapper command for:
- listing and reading connected accounts
- listing, reading, creating, and deleting schedules
- listing and reading queue items
- replying to queue comments
- reading Threads profile and post data by reusing the connected Threads account token stored in Repliz

## Credential source

This skill expects these variables in `~/.hermes/.env`:

- `REPLIZ_ACCESS_KEY`
- `REPLIZ_SECRET_KEY`
- `REPLIZ_BASE_URL` (default `https://api.repliz.com`)

Authentication is HTTP Basic Auth against the Repliz Public API.

## Commands

Prefer the wrapper command:

```bash
repliz-api account list --page 1 --limit 10
repliz-api account get ACCOUNT_ID
repliz-api schedule list --page 1 --limit 10
repliz-api schedule get SCHEDULE_ID
repliz-api schedule create --file ~/.hermes/skills/social-media/repliz-api/templates/text-post.json
repliz-api schedule delete SCHEDULE_ID
repliz-api queue list --page 1 --limit 10
repliz-api queue get QUEUE_ID
repliz-api queue reply QUEUE_ID --text "Terima kasih, kami akan bantu cek dulu."
repliz-api threads profile ACCOUNT_ID
repliz-api threads posts ACCOUNT_ID --limit 5
repliz-api threads post ACCOUNT_ID POST_ID
```

Fallback direct script path:

```bash
python ~/.hermes/skills/social-media/repliz-api/scripts/repliz_api.py account list --page 1 --limit 10
```

## Input methods for schedule creation

Exactly one of the following is required:
- `--file payload.json`
- `--data '{...json...}'`
- `--stdin`

## Rules

1. Read-only operations can be run directly.
2. Mutating operations (`schedule create`, `schedule delete`, `queue reply`) should only be run when the user explicitly asks for that action.
3. Never print or expose the stored access key or secret key.
4. If the API returns an error, report the HTTP status and parsed response body.
5. `account get` responses may include account token fields. Never echo raw token values to the user. Treat them as secrets and redact them immediately in any summaries or logs.
6. The `threads` commands work only for Repliz accounts whose `type` is `threads` and that contain a usable access token.
7. The `threads` commands call the Threads Graph API with the token retrieved from Repliz. Do not print the raw token.
8. Use ISO 8601 timestamps for `scheduleAt`.

## Templates

The template files in `templates/` are safe starting points for schedule creation.

## Verification

```bash
repliz-api account list --page 1 --limit 1
repliz-api account get ACCOUNT_ID
```

A valid configuration should return JSON from the API instead of an auth error.

## Pitfalls

- The public docs are hosted at `https://api.repliz.com/public` but the actual API base is `https://api.repliz.com`.
- The API uses HTTP Basic Auth, not bearer tokens.
- Repliz public Swagger currently documents account/schedule/queue only; the `threads` wrapper commands are a convenience layer that reuses the Threads access token from the connected Repliz account to call the Threads Graph API directly.
- `schedule create` requires a full JSON payload matching the documented schema.
- **Threads & TikTok Limitation**: Repliz does not support Instagram or Threads accounts for TikTok accounts. `repliz-api threads profile` and `repliz-api threads posts` will return `400: account_not_threads` for any non-Threads account. See `references/repliz-threads-tiktok-limitations.md` for details.
