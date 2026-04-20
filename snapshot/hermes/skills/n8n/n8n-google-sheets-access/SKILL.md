---
name: n8n-google-sheets-access
description: Access Google Sheets from n8n workflow using Service Account + gspread (no OAuth credential storage in n8n)
triggers:
  - need to read Google Sheets from n8n workflow
  - Google Sheets node credential setup issues
  - n8n-mcp confusion (it's documentation, not credential manager)
---

# n8n Google Sheets Access Methods

## Problem
Need to access Google Sheets from n8n workflow without relying on the Google Sheets node's built-in credential manager (OAuth/Service Account stored in n8n).

## Key Discovery
`n8n-mcp` npm package (czlonkowski/n8n-mcp) is a **documentation server only** — it provides MCP access to n8n node documentation (1,505 nodes, 87% coverage), NOT credential management. Installing it does NOT help with Google Sheets credentials.

## Two Valid Approaches

### Option A: Google Sheets Node + Service Account
- Use Google Sheets node in n8n
- Service Account bypasses OAuth consent screen
- Credential stored in n8n credential store
- Requires saving JSON keyfile to n8n

### Option B: Code Node (Python) + gspread (Recommended for this setup)
- Use n8n Code node with Python
- Load Service Account JSON directly in code
- No credential stored in n8n
- gspread reads/writes Google Sheets directly

```python
import gspread
import json

# Load service account from file or env
sa_dict = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT', open('/path/to/gcloud-service-account.json').read()))
gc = gspread.service_account_from_dict(sa_dict)
sh = gc.open_by_key('SPREADSHEET_ID')
ws = sh.sheet1
data = ws.get_all_records()
```

## Files
- Service account JSON: `/home/ubuntu/gcloud-service-account.json`
- Google Sheets ID: `1fZY7i1evEIIeugKjoBOnWsDH0YAtXT895rjOAZltYpE`
- Sheets name: `Daftar_Barang_Grosir`
