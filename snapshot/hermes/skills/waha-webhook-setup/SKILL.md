---
name: waha-webhook-setup
description: Setup and troubleshoot WAHA (WhatsApp HTTP API) webhook integration with n8n. Covers credential requirements, WEBJS engine limitations, and polling alternatives.
category: n8n
---

# WAHA Webhook Setup with n8n

## Important Discovery: WEBJS Engine Limitation

**WAHA CORE with WEBJS engine does NOT support webhook events.** When attempting to register webhooks:

```
"The method is not implemented by 'WEBJS' engine"
```

This means `POST /api/default/events` and similar webhook registration approaches will fail.

## WAHA Credential Requirements (2026.4.2+)

WAHA latest version **rejects weak passwords** like `admin`, `password123`. It ignores `WAHA_DASHBOARD_PASSWORD` env var and generates random credentials instead.

**Required password format:**
- Min 8 characters
- Mix of uppercase + lowercase + numbers + symbols
- Not in common password list

**Working example:**
```yaml
environment:
  - WAHA_DASHBOARD_USERNAME=adminsumo
  - WAHA_DASHBOARD_PASSWORD=SumoPodSecure2026!
  - WHATSAPP_SWAGGER_USERNAME=adminsumo
  - WHATSAPP_SWAGGER_PASSWORD=SumoPodSecure2026!
```

## API Endpoints (WAHA CORE)

Base auth: `-H "X-Api-Key: YOUR_API_KEY"`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/server/status` | GET | Server status |
| `/api/server/version` | GET | Version info |
| `/api/server/environment` | GET | All env vars (passwords masked) |
| `/api/sessions` | GET | List all sessions |
| `/api/sessions/default` | GET/PUT | Get/update default session |
| `/api/sessions/default/chats` | GET | Get chats (for polling) |

## Workaround: n8n Polling Approach

Since WEBJS doesn't support webhooks, use n8n to poll WAHA periodically:

1. Create n8n workflow with **Schedule Trigger** (e.g., every 30 seconds)
2. **HTTP Request** node calls `GET http://WAHA_HOST:3001/api/sessions/default/chats`
3. Process messages in n8n workflow

## Quick Test Commands

```bash
# Test API key auth
curl -H "X-Api-Key: sumopod123" http://localhost:3001/api/server/version

# Get sessions
curl -H "X-Api-Key: sumopod123" http://localhost:3001/api/sessions

# Get specific session
curl -H "X-Api-Key: sumopod123" http://localhost:3001/api/sessions/default
```

## Known Working Credentials (Example)

```
API Key: sumopod123
Username: adminsumo
Password: SumoPodSecure2026!
URL: http://43.157.205.89:3001
```
