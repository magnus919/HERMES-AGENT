---
name: baileys-whatsapp-gateway
description: Setup WhatsApp gateway on VPS with QR display in terminal using Baileys v6
---

# Baileys WhatsApp Gateway on VPS

Setup a production-ready WhatsApp gateway on Linux VPS with QR code displayed in terminal SSH.

## When to Use

Set up a WhatsApp bridge/gateway that:
- Shows QR code in terminal (ASCII art) for scanning via WhatsApp Linked Devices
- Persists session across restarts
- Forwards inbound messages to a webhook (e.g., n8n cloud)
- Exposes HTTP endpoints for outbound messaging
- Runs as a PM2-managed service

## Stack

- **Library:** `@whiskeysockets/baileys` v6.x (NOT v7 — v7 has different QR emission behavior)
- **HTTP:** Express.js
- **QR Display:** `qrcode-terminal`
- **Process Manager:** PM2
- **Session:** `useMultiFileAuthState` (persistent, stored on disk)

## Critical Discovery: QR Event in Baileys v6

Baileys v6 does NOT emit QR via the `qr` event alone. QR code is delivered via the `connection.update` object:

```javascript
sock.ev.on('connection.update', (update) => {
    const { qr } = update;
    if (qr) {
        qrcodeTerminal.generate(qr, { small: false });
    }
});
```

Primary QR channel is `connection.update.qr`, not the `qr` event.

## Setup Steps

### 1. Install Dependencies

```bash
mkdir -p /home/ubuntu/wa-gateway && cd /home/ubuntu/wa-gateway
npm init -y
npm install @whiskeysockets/baileys@6.7.3 express qrcode qrcode-terminal @hapi/boom
```

Install PM2 globally if not present.

### 2. Main Server File (server.js)

Key architecture:
- Port 3000
- Session folder: `/home/ubuntu/wa-gateway/session`
- Use `useMultiFileAuthState` for session persistence
- Listen to both `qr` event AND `connection.update.qr`
- Endpoints: GET `/status`, GET `/qr`, GET `/reset`, POST `/send-message`
- Inbound: forward messages to configured webhook URL

### 3. PM2 Startup

```bash
pm2 start ecosystem.config.js
pm2 save
```

## Common Issues

### QR returns `{"count":0}` (Evolution API)
- Switch to Baileys — more reliable

### Puppeteer/Chrome ICU Error
- whatsapp-web.js needs Chrome with ICU data
- Use Baileys — it does NOT need a browser

### QR never appears, goes to "registration" mode
- Using Baileys v7.x — different auth flow
- Downgrade to v6.7.3: `npm install @whiskeysockets/baileys@6.7.3`

### Port Already in Use
```bash
ss -tlnp | grep 3000
```

## HTTP Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/status` | Gateway & WhatsApp status |
| GET | `/qr` | QR as base64 PNG |
| GET | `/reset` | Clear session & regenerate QR |
| POST | `/send-message` | Send `{to, message}` |

Auth: `X-API-Key` header or `?key=<API_KEY>`

## Session Persistence

Session stored at `/home/ubuntu/wa-gateway/session/`. Survives process restarts and reboots via PM2.

To reset session: delete contents of session folder, then `pm2 restart wa-gateway`

## Get QR from Terminal

```bash
pm2 logs wa-gateway --nostream 2>&1 | grep -A10 "SCAN"
```
