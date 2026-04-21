---
name: waha-docker-vps
description: Deploy WAHA (WhatsApp HTTP API) dengan Docker Compose di VPS Linux. Includes credential configuration gotchas, engine selection (WEBJS vs NOWEB), webhook setup, and troubleshooting.
tags: [whatsapp, waha, docker, webhook, n8n]
related_skills: [baileys-whatsapp-gateway, evolution-api-whatsapp-gateway]
---

# WAHA Docker Deployment di VPS

## Persiapan

```bash
mkdir -p /opt/ai-whatsapp-bot
cd /opt/ai-whatsapp-bot
```

## Docker Compose Stack

```yaml
version: "3.8"

services:
  n8n:
    image: n8nio/n8n:latest
    restart: always
    ports:
      - "5678:5678"
    volumes:
      - ./n8n_data:/home/node/.n8n
    environment:
      - N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
      - N8N_SECURE_COOKIE=false
      - WEBHOOK_URL=http://localhost:5678
    user: "1000:1000"
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 5

  waha:
    image: devlikeapro/waha:latest
    restart: always
    ports:
      - "3001:3000"
    volumes:
      - ./waha_data:/app/.waha
      - /dev/shm:/dev/shm
    environment:
      # ENGINE: WEBJS atau NOWEB (lihat panduan di bawah)
      - WHATSAPP_DEFAULT_ENGINE=WEBJS
      - WAHA_SESSION_MODE=http
      - WAHA_ENABLE_SYNC=false
      - WAHA_DOCKER=true
      # CREDENTIALS - WAHA 2026.4.2 MENOLAK password lemah!
      - WAHA_API_KEY=your_api_key_here
      - WAHA_DASHBOARD_USERNAME=your_username
      - WAHA_DASHBOARD_PASSWORD=YourSecurePassword123!
      - WHATSAPP_SWAGGER_USERNAME=your_username
      - WHATSAPP_SWAGGER_PASSWORD=YourSecurePassword123!
      # WEBHOOK (hanya berfungsi dengan NOWEB engine)
      - WAHA_WEBHOOK_URL=https://your-n8n.cloud/webhook/whatsapp
      - WAHA_WEBHOOK_EVENTS=message.any
    tmpfs:
      - /tmp
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 5
```

## Engine Selection Guide

### WEBJS Engine
- **Default**, tidak perlu QR scan jika sudah ada sesi tersimpan
- **TIDAK mendukung webhook events** - error: `"The method is not implemented by 'WEBJS' engine"`
- Cocok jika hanya perlu kirim pesan (send-only)
- n8n harus polling secara periodik ke `/api/sessions/:session/chats`

### NOWEB Engine
- **Butuh QR scan** untuk connect WhatsApp
- **Mendukung webhook events** (message.any, message.text, dll.)
- Webhook URL dikonfigurasi saat start session
- QR code tersedia via API: `GET /api/:session/auth/qr`

## Setup Langkah demi Langkah

### 1. Deploy dengan WEBJS (tanpa webhook)
```bash
cd /opt/ai-whatsapp-bot
docker-compose up -d
# Cek logs
docker logs ai-whatsapp-bot_waha_1
```

### 2. Verifikasi Auth
```bash
# API Key auth
curl -H "X-Api-Key: your_api_key" http://localhost:3001/api/server/version

# Basic Auth (dashboard)
curl -u your_username:YourSecurePassword123! http://localhost:3001/
```

### 3. Jika Butuh Webhook → Switch ke NOWEB
```bash
docker-compose down
# Edit docker-compose.yml: ubah WHATSAPP_DEFAULT_ENGINE=NOWEB
# Hapus waha_data agar bersih
rm -rf waha_data
docker-compose up -d
```

### 4. Start Session dengan NOWEB
```bash
# Start session + webhook
curl -X POST http://localhost:3001/api/sessions/default/start \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: your_api_key" \
  -d '{
    "webhookUrl": "https://your-n8n.cloud/webhook/whatsapp",
    "webhookEvents": ["message.any"]
  }'

# Cek status
curl -H "X-Api-Key: your_api_key" http://localhost:3001/api/sessions/default
# Status: SCAN_QR_CODE → scanning → WORKING
```

### 5. Ambil QR Code
```bash
curl -H "X-Api-Key: your_api_key" http://localhost:3001/api/default/auth/qr -o /tmp/waha_qr.png
```

## Important Gotchas

### WAHA Menolak Password Lemah
WAHA versi 2026.4.2 (CORE) **menolak** password seperti `admin`, `password`, `123456`. Gunakan password kuat:
- Minimal 8 karakter
- Kombinasikan huruf besar, huruf kecil, angka, simbol
- Contoh: `SumoPodSecure2026!`

### Session Config Selalu Null
Meskipun webhook diset via API PUT, session config sering tetap `null` di response. Ini tidak berarti webhook tidak bekerja - cek dengan mengirim pesan test.

### WAHA CORE Tidak Ada `/api/webhooks` Endpoint
Endpoint `/api/webhooks` tidak tersedia di WAHA CORE. Webhook harus melalui session-level events API.

### WAHA Mengabaikan .env File di Volume
WAHA tidak membaca file `.env` yang ditaruh di volume `waha_data`. SELALU gunakan environment variables di docker-compose.yml untuk credentials.

### WAHA Webhook via Global Environment Variable (NOWEB ONLY)
Untuk NOWEB engine, webhook URL BISA diset via environment variable di docker-compose.yml:

```yaml
environment:
  - WHATSAPP_DEFAULT_ENGINE=NOWEB
  - WAHA_WEBHOOK_URL=https://your-n8n.cloud/webhook/whatsapp
  - WAHA_WEBHOOK_EVENTS=message.any,message
```

Event types yang tersedia: `message.any`, `message.text`, `message.image`, `message.audio`, dll.

Session config akan tetap `null` di response API - ini NORMAL dan tidak berarti webhook tidak bekerja. Tes dengan kirim pesan.

## Troubleshooting

### Login Dashboard Gagal
1. WAHA mungkin generate random password jika environment tidak dibaca dengan benar
2. Hapus waha_data: `rm -rf waha_data`
3. Pastikan password cukup kuat (bukan "admin"/"password")
4. Restart: `docker-compose down && docker-compose up -d`

### WEBJS Engine Webhook Tidak Bekerja
WEBJS engine tidak support webhook events. Ini **bukan bug** - memang desainnya.
- Solusi: Switch ke NOWEB engine
- Atau: Gunakan polling dari n8n ke `/api/sessions/:session/chats`

### QR Code Endpoint 404
Pastikan menggunakan nama session yang benar (default). Endpoint:
```
GET /api/default/auth/qr
```
Bukan `/api/sessions/default/auth/qr`.

### Instance Sudah Terhubung (WORKING) tapi Webhook Tidak Trigger
1. Pastikan engine = NOWEB (WEBJS tidak support events)
2. Pastikan webhookUrl diset saat start session
3. Cek n8n workflow trigger URL benar
4. Kirim pesan test dari HP lain

## Maintenance Commands

```bash
# Restart
cd /opt/ai-whatsapp-bot && sudo docker-compose restart

# Logs
sudo docker logs -f ai-whatsapp-bot_waha_1

# Stop
cd /opt/ai-whatsapp-bot && sudo docker-compose down

# Reset completely
cd /opt/ai-whatsapp-bot && sudo docker-compose down && sudo rm -rf waha_data n8n_data && sudo docker-compose up -d
```

## Credential Summary

| Service | URL | Username | Password |
|---------|-----|----------|----------|
| WAHA Dashboard | http://VPS_IP:3001 | (set via env) | (set via env) |
| WAHA API Key | Header: `X-Api-Key` | - | (set via env) |
| n8n | http://VPS_IP:5678 | - | first-run setup |
