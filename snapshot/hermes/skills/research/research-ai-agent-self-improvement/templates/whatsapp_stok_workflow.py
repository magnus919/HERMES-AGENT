import subprocess
import json
import os

token = os.environ.get('N8N_MCP_TOKEN', '')

workflow_code = r'''
import { workflow, trigger, node  from '@n8n/workflow-sdk';

// 1. Define webhook trigger
const webhookTrigger = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: { name: 'WhatsApp Webhook', parameters: { httpMethod: 'POST', path: 'whatsapp-stok', responseMode: 'responseNode' }, position: [250, 300] },
  output: [{ id: 1, type: 'main' ]
});

// 2. Extract data
const extractData = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: { name: 'Extract Data', parameters: { mode: 'manual', duplicateItem: false, assignments: { items: [{ id: 'chatId', name: 'chatId', value: '={{ $json.body.chatId }', type: 'string' }, { id: 'body', name: 'body', value: '={{ $json.body.body }', type: 'string' }]  }, position: [450, 300] },
  output: [{ id: 1, title: 'Item 1' ]
});

// 3. Read inventory JSON
const readInventory = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: { name: 'Read Inventory', parameters: { jsCode: "const fs = require('fs');\nconst inventory = JSON.parse(fs.readFileSync('/home/ubuntu/inventory.json', 'utf8'));\nreturn [{ json: { inventory }];" }, position: [650, 300] },
  output: [{ id: 1, title: 'Item 1' ]
});

// 4. AI Agent
const aiAgent = node({
  type: '@n8n/n8n-nodes-langchain.agent',
  version: 3.1,
  config: { name: 'AI Agent', parameters: { model: 'gpt-4', subnodes: {}, systemMessage: 'Anda adalah asisten stok toko grosir yang membantu pelanggan cek stok barang. Anda akan menerima data inventori dan pertanyaan pelanggan. Carilah barang yang dimaksud dan jawab dengan format: Nama barang, Stok, Harga Jual (Rp X). HANYA sebutkan HARGA JUAL, TIDAK boleh harga beli. Jika barang tidak ditemukan, jawab: "Maaf, barang tidak ada di inventori kami". Jika stok rendah, tambahkan: "STOK HAMPIR HABIS!". Bahasa Indonesia, singkat dan jelas.', textInput: '={{ $json.body }' }, position: [850, 300] },
  output: [{ id: 1, title: 'Item 1' ]
});

// 5. Send reply via HTTP
const sendReply = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.4,
  config: { name: 'Send Reply', parameters: { method: 'POST', url: 'http://localhost:3000/send', sendHeaders: true, headerParameters: { parameters: [{ name: 'Content-Type', value: 'application/json' }] }, sendBody: true, bodyParameters: { parameters: [{ name: 'chatId', value: '={{ $json.chatId }' }, { name: 'message', value: '={{ $json.text }' }]  }, position: [1050, 300] },
  output: [{ id: 1, title: 'Item 1' ]
});

// 6. Respond to webhook
const respondWebhook = trigger({
  type: 'n8n-nodes-base.respondToWebhook',
  version: 1.5,
  config: { name: 'Respond', parameters: { respondWith: 'json', responseBody: '{"status": "ok"}' }, position: [1250, 300] },
  output: [{ id: 1, type: 'main' ]
});

// 7. Compose workflow
export default workflow('whatsapp-stok-checker', 'AI Chat WhatsApp - Cek Stok')
  .add(webhookTrigger)
  .to(extractData)
  .to(readInventory)
  .to(aiAgent)
  .to(sendReply)
  .to(respondWebhook);
'''

# Call create_workflow_from_code
result = subprocess.run([
    'curl', '-s', '-X', 'POST',
    'https://azmiariffaris.app.n8n.cloud/mcp-server/http',
    '-H', 'Content-Type: application/json',
    '-H', f'Authorization: Bearer {token}',
    '-H', 'Accept: application/json, text/event-stream',
    '-d', json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": "create_workflow_from_code", "arguments": {
            "code": workflow_code,
            "name": "AI Chat WhatsApp - Cek Stok",
            "description": "Workflow untuk auto-reply cek stok barang via WhatsApp. Baca inventory dari JSON, AI Agent proses pertanyaan, balas via WhatsApp bridge."
        },
        "id": 1
    }),
    '--max-time', '60'
], capture_output=True, text=True)

# Parse response
for line in result.stdout.split('\n'):
    if line.startswith('data: '):
        data = json.loads(line[6:])
        if 'result' in data:
            content = data['result'].get('content', [{])[0].get('text', '')
            parsed = json.loads(content)
            print(json.dumps(parsed, indent=2))
        elif 'error' in data:
            print('ERROR:', json.dumps(data['error'], indent=2))
