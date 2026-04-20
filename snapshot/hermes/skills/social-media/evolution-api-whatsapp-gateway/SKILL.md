---
name: evolution-api-whatsapp-gateway
description: Deploy Evolution API WhatsApp gateway dengan Docker Compose, PostgreSQL, Redis, dan Apache reverse proxy di VPS Linux. Untuk integrasi dengan n8n cloud via webhook.
---

# Evolution API WhatsApp Gateway Deployment

## Persiapan Environment

Evolution API v2.x **wajib** menggunakan **PostgreSQL** + **Redis** (bukan MySQL/SQLite).

### Install dependensi
```bash
apt update && apt install postgresql postgresql-contrib redis-server docker-compose -y
```

### Setup PostgreSQL
```bash
sudo -u postgres psql << 'EOF'
CREATE DATABASE evolution_api;
CREATE USER evolution WITH ENCRYPTED PASSWORD 'evo_pass123';
GRANT ALL PRIVILEGES ON DATABASE evolution_api TO evolution;
\c evolution_api
GRANT ALL ON SCHEMA public TO evolution;
ALTER DATABASE evolution_api OWNER TO evolution;
EOF
```

### Setup Redis (listen on all interfaces)
```bash
sudo sed -i 's/^bind 127.0.0.1 ::1/bind 0.0.0.0 ::1/' /etc/redis/redis.conf
sudo systemctl restart redis-server
redis-cli ping  # should return PONG
```

## Docker Compose Stack

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:16-alpine
    container_name: evolution-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: evolution_api
      POSTGRES_USER: evolution
      POSTGRES_PASSWORD: evo_pass123
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
    networks:
      - evolution-net

  redis:
    image: redis:7-alpine
    container_name: evolution-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - ./redis-data:/data
    networks:
      - evolution-net

  evolution-api:
    image: atendai/evolution-api:latest
    container_name: evolution-api
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:8080"
    environment:
      - AUTHENTICATION_API_KEY=evolution-secret-key
      - DATABASE_PROVIDER=POSTGRES
      - DATABASE_CONNECTION_URI=postgresql://evolution:evo_pass123@postgres:5432/evolution_api
      - CACHE_REDIS_ENABLED=true
      - CACHE_REDIS_URI=redis://redis:6379
      - WEBHOOK_GLOBAL_ENABLED=true
      - LOG_LEVEL=ERROR
      - TZ=Asia/Jakarta
    volumes:
      - ./evolution-data:/evolution
    depends_on:
      - postgres
      - redis
    networks:
      - evolution-net

networks:
  evolution-net:
    driver: bridge
```

## Setup Instance WhatsApp

### 1. Buat instance
```bash
curl -s -X POST "http://localhost:8080/instance/create" \
  -H "Content-Type: application/json" \
  -H "apikey: evolution-secret-key" \
  -d '{"instanceName":"whatsapp-stok","integration":"WHATSAPP-BAILEYS","qrcode":true}'
```

### 2. Cek status koneksi
```bash
curl -s "http://localhost:8080/instance/connectionState/whatsapp-stok" \
  -H "apikey: evolution-secret-key"
```

State values:
- `close` = not initialized
- `connecting` = Baileys running, waiting for QR scan
- `open` = WhatsApp connected

### 3. Ambil QR Code
```bash
curl -s "http://localhost:8080/instance/connect/whatsapp-stok" \
  -H "apikey: evolution-secret-key"
# Jika return {"count":0} = QR belum di-scan atau expired
```

### 4. Scan QR dengan WhatsApp
1. Buka `http://VPS_IP:8080/manager/` di browser
2. Scan QR dengan WhatsApp → Pengaturan → Perangkat Tertaut → Tambah Perangkat

## Endpoint API Penting

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/instance/connect/{instance}` | Ambil QR code |
| GET | `/instance/connectionState/{instance}` | Cek status koneksi |
| POST | `/instance/create` | Buat instance baru |
| DEL | `/instance/delete/{instance}` | Hapus instance |
| POST | `/message/sendText/{instance}` | Kirim pesan text |
| POST | `/webhook/set/{instance}` | Set webhook |

## Kirim Pesan

```bash
curl -X POST "http://localhost:8080/message/sendText/whatsapp-stok" \
  -H "Content-Type: application/json" \
  -H "apikey: evolution-secret-key" \
  -d '{"number":"628xxxxxxxxxx","text":"Pesan balasan"}'
```

## Set Webhook ke n8n Cloud

```bash
curl -X POST "http://localhost:8080/webhook/set/whatsapp-stok" \
  -H "Content-Type: application/json" \
  -H "apikey: evolution-secret-key" \
  -d '{"enabled":true,"url":"https://n8n.cloud/webhook/whatsapp-stok","webhookByEvents":true,"webhookBase64":false}'
```

## Apache Reverse Proxy

```bash
a2enmod proxy proxy_http ssl rewrite headers proxy_wstunnel
```

```apache
<VirtualHost *:80>
    ServerName wa.domain.com
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/

    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} =websocket [NC]
    RewriteRule ^/?(.*)$ ws://127.0.0.1:8080/$1 [P,L]
    RewriteCond %{HTTP:Upgrade} !=websocket [NC]
    RewriteRule ^/?(.*)$ http://127.0.0.1:8080/$1 [P,L]
</VirtualHost>
```

## Troubleshooting

### {"count":0} pada QR endpoint
- Instance belum di-scan atau session expired
- Recreate instance dan scan ulang segera

### Instance state "connecting" tapi tidak bisa scan
- Hapus: `DELETE /instance/delete/{instance}`
- Buat ulang instance
- QR expire dalam ~60 detik

### Webhook tidak trigger
- Pastikan instance state = "open"
- Cek `docker logs evolution-api`

## Data Persistent

Semua data di `./evolution-data/` - jangan hapus atau session akan hilang.

## Restart Otomatis

Dengan `restart: unless-stopped` semua service auto restart setelah reboot.

## Format Nomor

Gunakan format Indonesia: `628xxxxxxxxxx` (kode negara 62, tanpa +)
