---
name: n8n-whatsapp-stok-logic
description: Setup WhatsApp auto-reply cek stok via n8n + Google Sheets (logic-based, NO AI Agent)
triggers: [whatsapp, n8n, inventory, google-sheets, logic-only]
---

# n8n WhatsApp Stok Checker (Logic-Based)

## Overview
WhatsApp auto-reply untuk cek stok barang menggunakan n8n + Google Sheets. **NO AI Agent** - pure logic untuk pencarian dan format reply. User: Master Faris, wholesale business, Bahasa Indonesia.

## Architecture
```
[WhatsApp Message] → [n8n WhatsApp Trigger] → [Read Google Sheets] → [JavaScript Logic] → [Send Reply]
```

## Prerequisites

### 1. Google Service Account (REQUIRED)
- Project: `gen-lang-client-0736302311`
- Service Account: `n8n-bot-stok-wa@gen-lang-client-0736302311.iam.gserviceaccount.com`
- Service Account JSON file with VALID private key

### ⚠️ CRITICAL: Private Key Validation
When copying Service Account JSON:
- Private key MUST be mathematically valid (RSA validation)
- Common error: `dmq1 not congruent to d` = corrupted key during copy-paste
- Fix: Download JSON directly from Google Cloud Console, never copy-paste the key
- Verify with: `openssl rsa -in key.pem -check -noout`

### 2. Google Sheets Setup
Upload Excel to Google Sheets:
```python
import gspread
from google.oauth2.service_account import Credentials
import openpyxl

# Auth with service account JSON file
SERVICE_ACCOUNT_FILE = '/path/to/service-account.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Create spreadsheet
spreadsheet = client.create('Daftar Barang Grosir - Inventory')
sheet = spreadsheet.sheet1
sheet.title = 'Stok Barang'

# Read Excel and upload
wb = openpyxl.load_workbook('Daftar_Barang_Grosir.xlsx', data_only=True)
# ... upload headers and data ...

# Share publicly (anyone with link can read)
spreadsheet.share('', perm_type='anyone', role='reader')
```

### 3. WhatsApp Number
- Target: `6285959572483`
- Use `n8n-nodes-base.whatsAppTrigger` or webhook from WhatsApp bridge

## n8n Workflow Nodes

### Node 1: WhatsApp Trigger
- Type: `n8n-nodes-base.whatsAppTrigger` or generic webhook
- Path: `whatsapp-stok`
- Extract: `chatId`, `body` (message text)

### Node 2: Google Sheets (Read Inventory)
- Method: `GET`
- URL: `https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{SHEET_NAME}!A:Z`
- Authentication: Google Service Account (OAuth2 API Key)

### Node 3: JavaScript Code (Search Logic)
```javascript
// Search inventory for matching items
const message = $input.first().json.body.toLowerCase();
const sheetData = $input.first().json.values || [];
const headers = sheetData[0];
const data = sheetData.slice(1);

// Search by nama barang (case-insensitive, partial match)
const results = data.filter(row => {
  const nama = String(row[2] || '').toLowerCase(); // Nama Barang column
  return nama.includes(message) || message.includes(nama);
});

// Format response
if (results.length === 0) {
  return { json: { chatId: $input.first().json.chatId, reply: 'Maaf, barang tidak ditemukan.' } };
}

const formatRupiah = (num) => 'Rp ' + parseInt(num).toLocaleString('id-ID');
const items = results.slice(0, 5).map(row => {
  const stok = parseInt(row[7]) || 0;  // Stok column
  const minStok = parseInt(row[8]) || 0; // Min Stok column
  const warning = stok <= minStok ? '\n⚠️ STOK HAMPIR HABIS!' : '';
  return `${row[2]}\nStok: ${stok} ${row[4]}\nHarga: ${formatRupiah(row[6])}${warning}`;
}).join('\n\n');

return {
  json: {
    chatId: $input.first().json.chatId,
    reply: `Hasil pencarian:\n\n${items}`
  }
};
```

### Node 4: Send WhatsApp Reply
- Method: POST
- URL: `http://localhost:3000/send` (WhatsApp bridge) OR WhatsApp node directly
- Body: `{ "chatId": "{{ $json.chatId }}", "message": "{{ $json.reply }}" }`

## Excel/Google Sheets Format
| A: Kode | B: Nama | C: Kategori | D: Satuan | E: Harga Beli | F: Harga Jual | G: Stok | H: Min Stok |
Expected column indices in code: Kode=0, Nama=2, Satuan=4, HargaJual=6, Stok=7, MinStok=8

## Key Notes
- User said "jangan menyuruh saya" - handle everything autonomously
- NO AI Agent - pure JavaScript logic for speed and reliability
- Show ONLY: nama barang, stok, harga jual, low stock warning
- NEVER show harga beli in responses
- All file operations should use n8n nodes or Google Sheets API, NOT local VPS files

## Common Issues

### "Invalid private key" error
→ Service account JSON key is corrupted. Download fresh JSON from Google Cloud Console.

### Google Sheets returns empty values
→ Use `data_only=True` when reading Excel with openpyxl before uploading
→ Or use `value_input_option='RAW'` when updating Google Sheets

### WhatsApp not receiving replies
→ Check webhook URL is accessible from n8n
→ Verify WhatsApp bridge is running on port 3000

### WhatsApp Bridge: Port 3000 EADDRINUSE or QR not generating
The bridge crashes or won't restart — follow this exact sequence:
```bash
# 1. Kill ALL bridge processes
pkill -f "whatsapp-bridge" 2>/dev/null; sleep 2

# 2. Verify port is free
lsof -i :3000  # should return empty

# 3. Start fresh (run in background)
cd /home/ubuntu/.hermes/hermes-agent && \
  node scripts/whatsapp-bridge/bridge.js \
    --port 3000 \
    --session ~/.hermes/whatsapp/session \
    --mode bot \
    --webhook-url "https://azmiariffaris.app.n8n.cloud/webhook/whatsapp-stok" \
    > ~/.hermes/whatsapp-bridge.log 2>&1 &

# 4. Wait and check QR
sleep 3 && cat ~/.hermes/whatsapp-bridge.log | grep QR
```

QR code is saved to: `/home/ubuntu/whatsapp_qr.png`
WhatsApp bridge log: `~/.hermes/whatsapp-bridge.log`
Process session ID for monitoring: `proc_c00f5365caf9` (example — check actual PID)
