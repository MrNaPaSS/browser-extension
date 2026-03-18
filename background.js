/**
 * NMNH Trading Robot — Background Service Worker v2.1.2 FINAL
 */
import { ULTRA_CONFIG } from './config.js';

console.log('%c[NMNH] Background v2.1.2 FINAL_SHIELD LOADED', 'background: #000; color: #fbbf24; font-weight: bold; padding: 4px;');

/* ─── Massive.com WebSocket Manager ──────────────── */
class MassiveWS {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.ws = null;
    this.authenticated = false;
    this.currentAsset = 'ETH/USD';
    this.currentType = 'crypto';
    this.reconnectTimer = null;
  }

  connect(type = 'crypto') {
    if (this.ws) {
      this.ws.onclose = null; // Prevent recursion
      this.ws.close();
    }
    this.currentType = type;
    console.log(`[NMNH] Connecting to Massive.com (${type})...`);
    
    // Attempting the most stable endpoint
    this.ws = new WebSocket(`wss://socket.massive.com/${type}`);

    this.ws.onopen = () => {
      console.log(`[NMNH] WS (${type}) Opened. Authenticating...`);
      // Massive authentication usually requires the key as a direct string or in an auth action
      // Massive.com authentication (alternative formats common)
      this.ws.send(JSON.stringify({ action: 'auth', params: [this.apiKey] }));
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (!Array.isArray(data)) return;

        data.forEach(msg => {
          if (msg.ev === 'status' && msg.status === 'auth_success') {
            this.authenticated = true;
            console.log(`[NMNH] WS (${type}) Authenticated ✅`);
            this.subscribe(this.currentAsset);
          }
          else if (msg.ev === 'XT' || msg.ev === 'C') { 
            // Handle Crypto Trade (XT) or Forex Quote (C)
            const price = (msg.p || msg.a);
            if (price) updateGlobalPrice(price.toFixed(2));
          }
        });
      } catch (e) {
        console.warn('[NMNH] WS Msg Error:', e.message);
      }
    };

    this.ws.onclose = (event) => {
      console.warn(`[NMNH] WS (${type}) Closed (Code: ${event.code}). Reconnecting in 5s...`);
      this.authenticated = false;
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = setTimeout(() => this.connect(this.currentType), 5000);
    };

    this.ws.onerror = (err) => {
      console.error(`[NMNH] WS (${type}) Socket Error`);
    };
  }

  setAsset(asset) {
    this.currentAsset = asset;
    const isCrypto = asset.includes('/') && !asset.includes('EUR') && !asset.includes('GBP') && !asset.includes('USD') && asset !== 'ETH/USD';
    // Logic check: if it's pairs like BTC/USD it might be crypto, but EUR/USD is definitely forex
    const newType = (asset.includes('EUR') || asset.includes('GBP') || asset.includes('JPY')) ? 'forex' : 'crypto';
    
    if (this.currentType !== newType) {
      console.log(`[NMNH] Switching cluster to: ${newType}`);
      this.connect(newType);
    } else if (this.authenticated) {
      this.subscribe(asset);
    }
  }

  subscribe(symbol) {
    if (!this.ws || !this.authenticated) return;
    console.log(`[NMNH] Subscribing to: ${symbol}`);
    this.ws.send(JSON.stringify({ action: 'subscribe', params: symbol }));
  }
}

// Global state
let appState = {
  isConnected: true,
  isTrading: false,
  asset: 'ETH/USD',
  price: '0.00',
  balance: 0,
  lastUpdate: Date.now(),
};

const massive = new MassiveWS(ULTRA_CONFIG.MASSIVE_API_KEY);

function updateGlobalPrice(price) {
  appState.price = price;
  appState.lastUpdate = Date.now();
  
  // Sync with tabs
  chrome.tabs.query({}, (tabs) => {
    tabs.forEach(tab => {
      chrome.tabs.sendMessage(tab.id, { 
        type: 'PRICE_UPDATE', 
        payload: { price: price, asset: appState.asset } 
      }).catch(() => {});
    });
  });

  // Sync with Bridge (Sentinel)
  if (bridgeSocket && bridgeSocket.readyState === WebSocket.OPEN) {
    // We don't spam the bridge with every tick unless requested, 
    // but the bridge can ask for context.
  }
}

/* ─── Storage & Lifecycle ─────────────────────── */
chrome.storage.local.get(['nmnh_state'], (result) => {
  if (result.nmnh_state) {
    appState = { ...appState, ...result.nmnh_state };
    console.log('[NMNH] State loaded');
  }
  massive.connect(); 
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'GET_STATE') {
    sendResponse({ status: 'SUCCESS', data: appState });
  } else if (msg.type === 'UPDATE_MARKET') {
    if (msg.payload.balance !== undefined) appState.balance = msg.payload.balance;
    if (msg.payload.asset) {
       if (appState.asset !== msg.payload.asset) {
          appState.asset = msg.payload.asset;
          massive.setAsset(msg.payload.asset);
       }
    }
    chrome.storage.local.set({ nmnh_state: appState });
  } else if (msg.type === 'REQUEST_AI_SIGNAL') {
    handleSignalRequest(sendResponse);
    return true; // async
  }
  return true;
});

async function handleSignalRequest(sendResponse) {
  try {
    const context = await getActiveTabContext();
    const result = await callBridge('GET_SIGNAL', context);
    sendResponse({ status: 'SUCCESS', data: result });
  } catch (err) {
    sendResponse({ status: 'ERROR', message: err.message });
  }
}

async function getActiveTabContext() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tabs[0]) return appState;
  return new Promise(resolve => {
    chrome.tabs.sendMessage(tabs[0].id, { type: 'GET_UI_CONTEXT' }, (resp) => {
      resolve(resp || appState);
    });
  });
}

async function callBridge(type, payload) {
  if (!bridgeSocket || bridgeSocket.readyState !== WebSocket.OPEN) {
    throw new Error('Sentinel Bridge not connected');
  }
  return new Promise((resolve, reject) => {
    const id = Math.random().toString(36).substring(7);
    const handler = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id === id) {
        bridgeSocket.removeEventListener('message', handler);
        if (msg.error) reject(new Error(msg.error));
        else resolve(msg.data);
      }
    };
    bridgeSocket.addEventListener('message', handler);
    bridgeSocket.send(JSON.stringify({ id, type, payload }));
    setTimeout(() => { 
      bridgeSocket.removeEventListener('message', handler);
      reject(new Error('Bridge Timeout'));
    }, 15000);
  });
}

/* ─── Sentinel Bridge Integration ──────────────── */
let bridgeSocket = null;

function connectToSentinelBridge() {
  if (bridgeSocket) return;
  
  console.log('%c[SENTINEL] Connecting to local MCP bridge...', 'color: #fbbf24');
  bridgeSocket = new WebSocket('ws://localhost:3001');

  bridgeSocket.onopen = () => {
    console.log('%c[SENTINEL] Connected to bridge ✅', 'color: #22c55e; font-weight: bold;');
    // Handshake to identify as the extension provider
    bridgeSocket.send(JSON.stringify({ id: 'AUTH_EXT' }));
  };
  bridgeSocket.onclose = () => {
    bridgeSocket = null;
    setTimeout(connectToSentinelBridge, 5000);
  };
  bridgeSocket.onerror = () => {
    // Silent fail if no bridge
  };

  bridgeSocket.onmessage = async (event) => {
    try {
      const msg = JSON.parse(event.data);
      const { id, type, payload } = msg;

      console.log(`[SENTINEL] Bridge Request: ${type} (ID: ${id})`);

      if (type === 'GET_CONTEXT') {
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tabs[0]) {
          chrome.tabs.sendMessage(tabs[0].id, { type: 'GET_UI_CONTEXT' }, (resp) => {
            console.log(`[SENTINEL] Context Resp:`, !!resp);
            if (bridgeSocket) bridgeSocket.send(JSON.stringify({ id, data: resp || appState }));
          });
        } else {
          if (bridgeSocket) bridgeSocket.send(JSON.stringify({ id, data: appState }));
        }
      } 
      else if (type === 'EXECUTE_TRADE') {
        const tabs = await chrome.tabs.query({ url: "*://*.pocketoption.com/*" });
        const targetTab = tabs[0] || (await chrome.tabs.query({ active: true }))[0];
        
        if (targetTab) {
          console.log(`[SENTINEL] Sending EXECUTE to tab: ${targetTab.id}`);
          chrome.tabs.sendMessage(targetTab.id, { type: 'SENTINEL_EXECUTE', payload }, (resp) => {
            console.log(`[SENTINEL] Execute Resp:`, resp);
            if (bridgeSocket) bridgeSocket.send(JSON.stringify({ id, data: resp || { status: 'ERROR', message: 'No response from content script' } }));
          });
        } else {
          console.warn('[SENTINEL] No target tab for execution');
          if (bridgeSocket) bridgeSocket.send(JSON.stringify({ id, data: { status: 'ERROR', message: 'PocketOption tab not found' } }));
        }
      }
    } catch (e) {
      console.error('[SENTINEL] Bridge error:', e);
    }
  };
}

// Start bridge connection
connectToSentinelBridge();
