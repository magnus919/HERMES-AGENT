/**
 * WhatsApp Gateway - Baileys Based
 * QR displayed in terminal, HTTP endpoints, n8n cloud integration
 */

const { default: makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const express = require('express');
const qrcodeTerminal = require('qrcode-terminal');
const QRCode = require('qrcode');
const { Boom } = require('@hapi/boom');

const PORT = parseInt(process.env.PORT || '3000');
const SESSION_FOLDER = process.env.SESSION_FOLDER || '/home/ubuntu/wa-gateway/session';
const N8N_WEBHOOK = process.env.N8N_WEBHOOK || 'https://azmiariffaris.app.n8n.cloud/webhook/whatsapp-stok';
const API_KEY = process.env.API_KEY || 'wa-gateway-secret-key';

let sock = null;
let qrBuffer = null;
let connectionState = 'disconnected';
let startTime = Date.now();

async function startSocket() {
    const { state, saveCreds } = await useMultiFileAuthState(SESSION_FOLDER);
    const { version } = await fetchLatestBaileysVersion();

    console.log(`[WA] Baileys v${version.join('.')} starting...`);

    sock = makeWASocket({
        auth: state,
        version,
        keepAliveIntervalMs: 30000,
        printQRInTerminal: false,
        defaultQueryTimeoutMs: 60000,
    });

    sock.ev.on('creds.update', saveCreds);

    // QR via connection.update (v6 primary channel)
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            console.log('\n========== SCAN QR INI DENGAN WHATSAPP ==========\n');
            qrcodeTerminal.generate(qr, { small: false });
            console.log('\nGET QR: http://43.157.205.89:' + PORT + '/qr');
            console.log('QR expires in 60s!\n');
            qrBuffer = qr;
            connectionState = 'waiting_scan';
        }

        if (connection === 'open') {
            console.log('[WA] WhatsApp connected!');
            qrBuffer = null;
            connectionState = 'connected';
        }

        if (connection === 'close') {
            const dc = lastDisconnect?.error instanceof Boom ? lastDisconnect.error.output?.statusCode : 0;
            const shouldReconnect = dc !== 401;
            console.log('[WA] Connection closed, reconnect:', shouldReconnect);
            qrBuffer = null;
            connectionState = shouldReconnect ? 'reconnecting' : 'disconnected';
            if (shouldReconnect) setTimeout(startSocket, 5000);
        }
    });

    // Also listen to qr event as backup
    sock.ev.on('qr', (qr) => {
        console.log('[WA] QR via event (backup)');
        qrcodeTerminal.generate(qr, { small: false });
        qrBuffer = qr;
        connectionState = 'waiting_scan';
    });

    // Inbound messages
    sock.ev.on('messages.upsert', async ({ messages }) => {
        for (const msg of messages) {
            if (msg.key.fromMe || !msg.message) continue;
            const from = msg.key.remoteJid;
            const body = msg.message?.conversation ||
                         msg.message?.extendedTextMessage?.text || '';
            const senderName = msg.pushName || '';

            console.log(`[WA] ${senderName}: ${body.substring(0, 50)}`);

            try {
                await fetch(N8N_WEBHOOK, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        webhookSource: 'wa-gateway',
                        from: from.replace('@s.whatsapp.net', ''),
                        fromName: senderName,
                        body: body,
                        timestamp: msg.messageTimestamp,
                        type: Object.keys(msg.message || {})[0],
                        id: msg.key.id,
                    })
                });
            } catch (err) {
                console.error('[WA] Forward error:', err.message);
            }
        }
    });
}

const app = express();
app.use(express.json());

function authMiddleware(req, res, next) {
    const key = req.headers['x-api-key'] || req.query.key;
    if (key === API_KEY) return next();
    res.status(401).json({ error: 'Unauthorized' });
}

app.get('/status', (req, res) => {
    res.json({ gateway: 'online', whatsapp: connectionState, connected: connectionState === 'connected', qrAvailable: qrBuffer !== null, uptime: Math.floor((Date.now() - startTime) / 1000) + 's' });
});

app.get('/qr', async (req, res) => {
    if (!qrBuffer) return res.status(404).json({ error: 'QR not available', status: connectionState });
    try {
        const dataUrl = await QRCode.toDataURL(qrBuffer, { margin: 2, scale: 8 });
        res.json({ status: connectionState, qr: dataUrl });
    } catch (err) { res.status(500).json({ error: err.message }); }
});

app.get('/reset', async (req, res) => {
    if (sock) { try { sock.end(); } catch (e) {} }
    qrBuffer = null; connectionState = 'disconnected';
    res.json({ message: 'Reset done, generating new QR...' });
    await startSocket();
});

app.post('/send-message', authMiddleware, async (req, res) => {
    if (connectionState !== 'connected' || !sock) return res.status(503).json({ error: 'WhatsApp not connected' });
    const { to, message } = req.body;
    if (!to || !message) return res.status(400).json({ error: 'Missing to or message' });

    let jid = to.replace(/[^0-9]/g, '');
    if (jid.startsWith('0')) jid = '62' + jid.substring(1);
    else if (!jid.startsWith('62')) jid = '62' + jid;
    jid = jid + '@s.whatsapp.net';

    try {
        const result = await sock.sendMessage(jid, { text: message });
        res.json({ success: true, id: result.key.id });
    } catch (err) { res.status(500).json({ error: err.message }); }
});

app.get('/', (req, res) => {
    res.json({ name: 'WhatsApp Gateway', status: connectionState, endpoints: ['GET /status', 'GET /qr', 'GET /reset', 'POST /send-message'] });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`WhatsApp Gateway running on port ${PORT}`);
    startSocket();
});

process.on('SIGINT', () => { if (sock) try { sock.end(); } catch (e) {} process.exit(0); });
process.on('SIGTERM', () => { if (sock) try { sock.end(); } catch (e) {} process.exit(0); });
