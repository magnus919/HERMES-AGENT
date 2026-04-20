---
name: n8n-whatsapp-ai-stok-agent
description: Setup WhatsApp AI Chat untuk cek stok barang via n8n + Google Sheets + AI Agent
triggers: [whatsapp, n8n, inventory, google-sheets, ai-agent]
---

# n8n WhatsApp AI Stok Agent

## Overview
Setup WhatsApp AI Chat untuk cek stok barang menggunakan n8n + Google Sheets + AI Agent.
User: Master Faris, wholesale business, Bahasa Indonesia.

## Architecture
```
[WhatsApp Message] → [n8n WhatsApp Trigger] → [Read Google Sheets] → [AI Agent] → [Send Reply]
```

## Prerequisites

### 1. WhatsApp
- Number: `6285959572483`
- Use `n8n-nodes-base.whatsAppTrigger` node

### 2. Google Sheets (Inventory)
- Upload Excel to Google Sheets
- Share as view-only link
- Or use Service Account JSON for full access
- Format kolom: Kode | Nama | Kategori | Satuan | Harga Beli | Harga Jual | Stok | Min Stok

### 3. AI Agent
- Nodes available in n8n:
  - `@n8n/n8n-nodes-langchain.agent` (v3.1)
  - `@n8n/n8n-nodes-langchain.openAi` (v2.1)
  - `@n8n/n8n-nodes-langchain.anthropic` (v1) - Claude
  - `@n8n/n8n-nodes-langchain.googleGemini` (v1.1)
- System prompt: Indonesian, show ONLY: nama barang, stok, harga jual, low stock warning. NEVER show harga beli.

## Key Notes
- User REJECTED VPS-based file reading (no `/home/ubuntu/inventory.json`)
- User wants 100% n8n with Google Sheets for auto-sync when Excel is edited
- User said "jangan pernah menyuruh saya untuk mengurus n8n" - handle everything autonomously
- AI Agent should be connected to Hermes (Assistant: Anindhita Berliana Putri)

## Workflow Structure
1. WhatsApp Trigger (incoming message)
2. Google Sheets node (read inventory)
3. AI Agent node (process query, format response)
4. WhatsApp node (send reply)

## Files
- `/home/ubuntu/Daftar_Barang_Grosir.xlsx` - Source inventory (upload to Google Sheets)
- n8n workflow ID: `W5OJ2DI3QvJACKJo` (old, needs update to use Google Sheets)
