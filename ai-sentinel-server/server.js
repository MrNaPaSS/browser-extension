const WebSocket = require('ws');
require('dotenv').config();

/**
 * NMNH SENTINEL BRIDGE - Relay Server v1.2.0
 * Bidirectional Hub for Extension and AI Agent
 */

const wss = new WebSocket.Server({ port: 3001 });
let extensionSocket = null;
let agentSocket = null;

const pendingExtensionRequests = new Map(); // Requests from Extension to Agent
const pendingAgentRequests = new Map();     // Requests from Agent to Extension

wss.on('connection', (ws) => {
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data);
      
      // --- HANDSHAKE ---
      if (msg.id === 'AUTH_EXT') {
        extensionSocket = ws;
        console.log('[SENTINEL] Provider: Extension connected ✅');
        return;
      }
      if (msg.id === 'AUTH_AGENT') {
        agentSocket = ws;
        console.log('[SENTINEL] Brain: AI Agent connected ✅');
        return;
      }

      // --- ROUTING: RESPONSES ---
      // 1. Response intended for Extension
      if (pendingExtensionRequests.has(msg.id)) {
        const { resolve } = pendingExtensionRequests.get(msg.id);
        pendingExtensionRequests.delete(msg.id);
        resolve(msg.data);
        return;
      }

      // 2. Response intended for Agent (or Bridge Internal)
      if (pendingAgentRequests.has(msg.id)) {
        const { resolve } = pendingAgentRequests.get(msg.id);
        pendingAgentRequests.delete(msg.id);
        resolve(msg.data);
        return;
      }

      // --- ROUTING: REQUESTS ---
      // 1. Request from Extension (e.g. GET_SIGNAL)
      if (msg.type === 'GET_SIGNAL') {
        handleExtensionRequest(ws, msg);
      }
      // 2. Request from Agent (e.g. GET_CONTEXT, EXECUTE_TRADE)
      else if (msg.type === 'GET_CONTEXT' || msg.type === 'EXECUTE_TRADE') {
        handleAgentRequest(ws, msg);
      }

    } catch (e) {
      console.error('[SENTINEL] Bridge Router Error:', e.message);
    }
  });

  ws.on('close', () => {
    if (extensionSocket === ws) extensionSocket = null;
    if (agentSocket === ws) agentSocket = null;
    console.log('[SENTINEL] Client disconnected');
  });
});

async function handleExtensionRequest(ws, msg) {
  if (!agentSocket) {
    ws.send(JSON.stringify({ id: msg.id, error: 'AI Agent not connected to bridge' }));
    return;
  }
  console.log(`[SENTINEL] Relay: Extension -> Agent [${msg.type}]`);
  try {
    const data = await new Promise((resolve, reject) => {
      pendingExtensionRequests.set(msg.id, { resolve, reject });
      agentSocket.send(JSON.stringify(msg));
      setTimeout(() => {
        if (pendingExtensionRequests.has(msg.id)) {
          pendingExtensionRequests.delete(msg.id);
          reject(new Error('AI Agent Timeout'));
        }
      }, 15000);
    });
    ws.send(JSON.stringify({ id: msg.id, data }));
  } catch (err) {
    ws.send(JSON.stringify({ id: msg.id, error: err.message }));
  }
}

async function handleAgentRequest(ws, msg) {
  if (!extensionSocket) {
    ws.send(JSON.stringify({ id: msg.id, error: 'Extension not connected' }));
    return;
  }
  console.log(`[SENTINEL] Relay: Agent -> Extension [${msg.type}]`);
  try {
    const data = await new Promise((resolve, reject) => {
      pendingAgentRequests.set(msg.id, { resolve, reject });
      extensionSocket.send(JSON.stringify(msg));
      setTimeout(() => {
        if (pendingAgentRequests.has(msg.id)) {
          pendingAgentRequests.delete(msg.id);
          reject(new Error('Extension Timeout'));
        }
      }, 15000);
    });
    ws.send(JSON.stringify({ id: msg.id, data }));
  } catch (err) {
    ws.send(JSON.stringify({ id: msg.id, error: err.message }));
  }
}

console.log('[SENTINEL] RELAY HUB v1.2.0 Active on Port 3001');
