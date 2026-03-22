/**
 * NMNH Trading Robot — Background Service Worker v2.1.2 FINAL
 */
import { ULTRA_CONFIG } from './config.js';

// --- CONFIGURATION ---
// Replace with your actual remote server IP or Ngrok URL (e.g. 'http://1.2.3.4:8081')
const BOT_API_URL = 'http://213.21.240.78:8081'; 

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
    this.ws = new WebSocket(`wss://socket.polygon.io/${type}`);

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
      // Only log if not already handled by onclose
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
  dailyPnl: 0,
  session: { wins: 0, losses: 0, processed: [] },
  aiSignals: [], // Added for Persistence
  sessionStartBalance: 0,
  sessionStartTime: 0,
  lastUpdate: Date.now(),
  isVerified: false,
  signalLockUntil: 0,
};

const massive = new MassiveWS(ULTRA_CONFIG.MASSIVE_API_KEY);

function updateGlobalPrice(price) {
  appState.price = price;
  appState.lastUpdate = Date.now();
  chrome.tabs.query({}, (tabs) => {
    tabs.forEach(tab => {
      chrome.tabs.sendMessage(tab.id, {
        type: 'PRICE_UPDATE',
        payload: { price: price, asset: appState.asset }
      }).catch(() => { });
    });
  });
}

function broadcastSessionUpdate() {
  broadcastToAll({ 
    type: 'SESSION_UPDATE', 
    payload: { 
      ...appState.session, 
      dailyPnl: appState.dailyPnl,
      isTrading: appState.isTrading,
      aiSignals: appState.aiSignals,
      sessionStartBalance: appState.sessionStartBalance,
      sessionStartTime: appState.sessionStartTime,
      timeoutEndTime: appState.timeoutEndTime,
      signalLockUntil: appState.signalLockUntil
    } 
  });
}

/* ─── Storage & Lifecycle ─────────────────────── */
chrome.storage.local.get(['ultra_verified', 'nmnh_state'], (result) => {
  if (result.ultra_verified) {
    appState.isVerified = true;
    console.log('[NMNH] Verification Restored from Storage ✅');
  }
  
  if (result.nmnh_state) {
    console.log('[NMNH] Restoring state from storage...');
    // Carefully merge state to avoid losing references
    Object.assign(appState, result.nmnh_state);
    
    // Ensure lock is still valid if extension restarted
    if (appState.signalLockUntil && Date.now() < appState.signalLockUntil) {
      console.log(`[NMNH] Active signal lock restored until: ${new Date(appState.signalLockUntil).toLocaleTimeString()}`);
    }
  }
  
  massive.connect();
});

// --- Verification Logic ---
async function verifyUID(uid) {
  try {
    console.log(`[NMNH] Verifying UID: ${uid} via Bot API...`);
    // Added controller to handle timeouts
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000);

    const response = await fetch(`${BOT_API_URL}/verify?uid=${uid}`, {
      headers: { 'ngrok-skip-browser-warning': 'true' },
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
    
    const result = await response.json();
    console.log('[NMNH] Verification Result:', result);
    
    if (result.verified) {
      appState.isVerified = true;
      await chrome.storage.local.set({ 
        'ultra_verified': true,
        'nmnh_verified_uid': uid 
      });
      return true;
    }
    return false;
  } catch (e) {
    if (e.name === 'AbortError') {
      console.error('[NMNH] Verification TIMEOUT: Server is not responding on port 8081');
    } else {
      console.error('[NMNH] Verification FAILED (Network/CORS/MixedContent):', e.message);
      console.log('%c[NMNH] TIP: Ensure port 8081 is open on your server firewall!', 'color: #fbbf24; font-weight: bold;');
    }
    return false;
  }
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'VERIFY_UID') {
    verifyUID(msg.payload.uid).then(isVerified => {
      sendResponse({ isVerified });
      // Broadcast update to all tabs
      chrome.tabs.query({}, (tabs) => {
        tabs.forEach(tab => {
          chrome.tabs.sendMessage(tab.id, { 
            type: 'STATE_UPDATED', 
            payload: { isVerified } 
          }).catch(() => {});
        });
      });
    });
    return true; // Keep channel open for async
  }
  
  if (msg.type === 'GET_STATE') {
    sendResponse({ 
      status: 'SUCCESS', 
      data: {
        ...appState.session,
        dailyPnl: appState.dailyPnl,
        isTrading: appState.isTrading,
        aiSignals: appState.aiSignals,
        sessionStartBalance: appState.sessionStartBalance,
        sessionStartTime: appState.sessionStartTime,
        timeoutEndTime: appState.timeoutEndTime,
        signalLockUntil: appState.signalLockUntil
      }
    });
  } else if (msg.type === 'UPDATE_MARKET') {
    if (msg.payload.balance !== undefined) {
      appState.balance = msg.payload.balance;
      if (appState.isTrading && (!appState.sessionStartBalance || appState.sessionStartBalance === 0)) {
        appState.sessionStartBalance = msg.payload.balance;
      }
    }
    if (msg.payload.asset) {
      if (appState.asset !== msg.payload.asset) {
        appState.asset = msg.payload.asset;
        massive.setAsset(msg.payload.asset);
      }
    }
    chrome.storage.local.set({ nmnh_state: appState });
  } else if (msg.type === 'TRADE_DETECTED_CLOSE') {
    if (!appState.session) appState.session = { wins: 0, losses: 0, processed: [] };
    if (!appState.session.processed) appState.session.processed = [];

    const sig = msg.payload.sig;

    if (sig) {
      if (appState.session.processed.includes(sig)) {
        return;
      }
    }

    if (msg.payload.result === 'WIN') {
      appState.session.wins++;
    } else if (msg.payload.result === 'LOSS') {
      appState.session.losses++;
    }
    
    if (msg.payload.pnl !== undefined) {
      appState.dailyPnl = (appState.dailyPnl || 0) + msg.payload.pnl;
    }
    
    if (sig) appState.session.processed.push(sig);
    if (appState.session.processed.length > 1000) appState.session.processed.shift();

    console.log(`[NMNH] Trade detected: ${msg.payload.result}, wins=${appState.session.wins}, losses=${appState.session.losses}`);
    chrome.storage.local.set({ nmnh_state: appState });
    broadcastSessionUpdate();
    sendResponse({ status: 'ACK' });
  } else if (msg.type === 'START_TRADING') {
    appState.isTrading = true;
    if (!appState.session) appState.session = { wins: 0, losses: 0, processed: [] };
    appState.session.wins = 0;
    appState.session.losses = 0;
    appState.session.processed = []; 
    
    appState.aiSignals = [];
    appState.consecutiveLosses = 0;
    appState.timeoutEndTime = 0;
    appState.sessionStartTime = Date.now();
    appState.sessionStartBalance = appState.balance || 0;
    chrome.storage.local.set({ nmnh_state: appState });
    broadcastSessionUpdate();
    sendResponse({ status: 'ACK' });
  } else if (msg.type === 'STOP_TRADING') {
    appState.isTrading = false;
    appState.sessionStartTime = null;
    chrome.storage.local.set({ nmnh_state: appState });
    broadcastSessionUpdate();
    sendResponse({ status: 'ACK' });
  } else if (msg.type === 'DECREMENT_STATS') {
    if (!globalThis.lastDecrementTime) globalThis.lastDecrementTime = 0;
    const now = Date.now();
    if (now - globalThis.lastDecrementTime < 2000) {
      sendResponse({ status: 'IGNORED' });
      return;
    }
    globalThis.lastDecrementTime = now;

    if (appState.session && appState.session.losses > 0) {
      appState.session.losses--;
      chrome.storage.local.set({ nmnh_state: appState });
      broadcastSessionUpdate();
    }
    sendResponse({ status: 'ACK' });
  } else if (msg.type === 'RESET_SESSION') {
    if (appState.session) {
      appState.session.wins = 0;
      appState.session.losses = 0;
      appState.session.processed = []; 
    }
    appState.dailyPnl = 0;
    appState.aiSignals = []; 
    chrome.storage.local.set({ nmnh_state: appState });
    broadcastSessionUpdate();
    sendResponse({ status: 'ACK' });

  } else if (msg.type === 'REQUEST_AI_SIGNAL') {
    console.log('[NMNH] REQUEST_AI_SIGNAL received in background. Payload keys:', Object.keys(msg.payload || {}));
    if (msg.payload && msg.payload.chartData) {
      console.log('[NMNH] ChartData found, length:', msg.payload.chartData.length);
    } else {
      console.error('[NMNH] ChartData MISSING from payload!');
    }
    handleSignalRequest(sendResponse, msg.payload || {});
    return true; // async
  } else if (msg.type === 'CAPTURE_FULL_TAB') {
    captureTabAsBase64().then(sendResponse).catch(() => sendResponse(null));
    return true;
  } else if (msg.type === 'VERIFY_ACADEMY_USER') {
    callBridge('VERIFY_ACADEMY_USER', msg.payload).then(sendResponse).catch(err => {
      console.error('[NMNH] Verification Relay Error:', err.message);
      sendResponse({ status: 'ERROR', message: err.message });
    });
    return true;
  }
  return true;
});

async function handleSignalRequest(sendResponse, payload) {
  try {
    // REMOVED LOCK CHECK for manual developer/user testing to avoid "BLOCK" UI
    /*
    if (Date.now() < appState.signalLockUntil) {
       ...
    }
    */
    console.log('[NMNH] Starting signal generation process (Manual Trigger)...');
    const context = await getActiveTabContext();
    const asset = context.asset || 'EUR/USD';
    const isOTC = asset.toUpperCase().includes('OTC');

    console.log(`[NMNH] Signal Request for: ${asset}`);
    try {
      let screenshot = payload.chartData;
      if (!screenshot) screenshot = await captureTabAsBase64();

      if (screenshot) {
        const visualSignal = await analyzeImageWithAI(screenshot, asset, payload.timeframe || '1m');
        
        if (visualSignal) {
          console.log('[NMNH] Visual AI Success:', visualSignal.decision);
          
          if (!appState.aiSignals) appState.aiSignals = [];
          appState.aiSignals.unshift({
            asset: asset,
            type: visualSignal.decision,
            conf: Math.round(visualSignal.confidence * 100),
            timestamp: Date.now()
          });
          appState.aiSignals = appState.aiSignals.slice(0, 3);
          
          applySignalLock(visualSignal.duration);

          sendResponse({ 
            status: 'SUCCESS', 
            data: visualSignal, 
            isVisual: true,
            screenshot: screenshot 
          });
          return;
        } else {
          console.warn('[NMNH] Visual AI returned NULL - check API Response logs above');
        }
      } else {
        console.error('[NMNH] FAILED to obtain any screenshot! Skipping Visual AI.');
      }
    } catch (vErr) {
      console.error('[NMNH] Visual AI CRITICAL ERROR:', vErr.message, vErr.stack);
    }

    // 2. Fallback to OTC (Local) or Forex (Finnhub)
    if (isOTC) {
      console.log('[NMNH] Falling back to Local Analysis...');
      const localSignal = await getLocalSignalFromTab();
      
      // Short cooldown for local to let user try AI again soon
      applySignalLock(0.25); 
      
      sendResponse({ status: 'SUCCESS', data: localSignal, isVisual: false });
      return;
    }

    const symbol = mapAssetToFinnhub(asset);
    const token = ULTRA_CONFIG.FINNHUB_API_KEY;

    try {
      console.log(`[NMNH] Fetching Finnhub signal for: ${symbol}`);
      const apiController = new AbortController();
      const apiTimeout = setTimeout(() => apiController.abort(), 6000);
      const response = await fetch(`https://finnhub.io/api/v1/scan/technical-indicator?symbol=${symbol}&resolution=1&token=${token}`, { signal: apiController.signal });
      clearTimeout(apiTimeout);
      const data = await response.json();

      if (data && data.technicalAnalysis) {
        const { signal, count } = data.technicalAnalysis;
        const diff = Math.abs(count.buy - count.sell);
        let duration = 3;
        if (signal.includes('strong')) duration = Math.random() > 0.5 ? 1 : 2;
        else if (diff > 8) duration = 3;
        else duration = Math.random() > 0.5 ? 4 : 5;

        const decision = signal.toUpperCase().includes('BUY') ? 'BUY' : 
                         signal.toUpperCase().includes('SELL') ? 'SELL' : 'WAIT';

        const finalSignal = { 
          decision, 
          reason: `Finnhub: ${signal} (B:${count.buy} S:${count.sell})`,
          confidence: Math.min(0.95, 0.6 + (diff / 20)),
          duration
        };

        applySignalLock(finalSignal.duration);

        sendResponse({ 
          status: 'SUCCESS', 
          data: finalSignal
        });
        return;
      }
    } catch (apiErr) {
      console.warn('[NMNH] Finnhub AI failed, falling back to Local:', apiErr.message);
    }

    const fallbackSignal = await getLocalSignalFromTab();
    applySignalLock(fallbackSignal.duration);
    sendResponse({ status: 'SUCCESS', data: fallbackSignal });

  } catch (err) {
    if (err.message.includes('Extension context invalidated')) return;
    console.error('[NMNH] Signal Logic Error:', err.message);
    sendResponse({ status: 'ERROR', message: err.message });
  }
}

async function getLocalSignalFromTab() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tabs[0]) throw new Error('No active tab');
  return new Promise((resolve, reject) => {
    chrome.tabs.sendMessage(tabs[0].id, { type: 'GET_LOCAL_SIGNAL' }, (resp) => {
      if (chrome.runtime.lastError) reject(new Error(chrome.runtime.lastError.message));
      else if (resp && resp.status === 'SUCCESS') resolve(resp.data);
      else reject(new Error('Local analysis failed'));
    });
  });
}

async function captureTabAsBase64() {
  return new Promise((resolve, reject) => {
    chrome.tabs.captureVisibleTab(null, { format: 'jpeg', quality: 80 }, (dataUrl) => {
      if (chrome.runtime.lastError) reject(new Error(chrome.runtime.lastError.message));
      else resolve(dataUrl);
    });
  });
}

async function analyzeImageWithAI(base64, asset, timeframe) {
  const apiKey = ULTRA_CONFIG.OPENROUTER_API_KEY;
  const model = "google/gemini-2.0-flash-001";
  
  // Ensure base64 has correct prefix for OpenRouter
  const finalBase64 = base64.startsWith('data:') ? base64 : `data:image/jpeg;base64,${base64}`;

  const prompt = `Analyze this ${timeframe} trading chart for ${asset}. 
  Identify the current trend, key support/resistance levels, and recent candlestick patterns.
  Provide a trading signal: BUY, SELL, or WAIT.
  Provide an optimal duration for a binary options trade (1-5 minutes).
  Provide a confidence score (0.0 to 1.0).
  IMPORTANT: Return ONLY a JSON object in this format:
  {
    "decision": "BUY",
    "duration": 2,
    "confidence": 0.85,
    "reason": "Clear bullish pin bar at support level, upward momentum confirmed."
  }`;

  console.log('[NMNH] OpenRouter Fetch START...', { model, asset, timeframe, imgLen: finalBase64.length });

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 12000);

    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://nmnh.academy",
        "X-Title": "NMNH Trading Robot"
      },
      signal: controller.signal,
      body: JSON.stringify({
        model: model,
        messages: [
          {
            role: "user",
            content: [
              { type: "text", text: prompt },
              { type: "image_url", image_url: { url: finalBase64 } }
            ]
          }
        ]
      })
    });
    clearTimeout(timeoutId);

    console.log('[NMNH] OpenRouter HTTP Status:', response.status);
    const data = await response.json();
    
    if (!response.ok) {
      console.error('[NMNH] OpenRouter Error Data:', JSON.stringify(data));
      return null;
    }
    
    if (data && data.choices && data.choices[0]) {
      const text = data.choices[0].message.content;
      console.log('[NMNH] AI Raw Text received.');
      const match = text.match(/\{[\s\S]*\}/);
      if (match) {
        try {
          const parsed = JSON.parse(match[0]);
          console.log('[NMNH] AI Parsed Signal:', parsed.decision, parsed.duration, 'min');
          return parsed;
        } catch (e) {
          console.error('[NMNH] AI JSON Parse Error:', e.message, text);
        }
      } else {
        console.warn('[NMNH] No JSON found in AI response:', text);
      }
    } else {
      console.error('[NMNH] AI Response empty or malformed.');
    }
  } catch (err) {
    console.error('[NMNH] OpenRouter Physical Fetch Error:', err.message);
  }
  return null;
}

function mapAssetToFinnhub(asset) {
  const clean = asset.replace(' OTC', '').replace('/', '').replace(' ', '').toUpperCase();
  const mapping = {
    'EURUSD': 'OANDA:EUR_USD',
    'GBPUSD': 'OANDA:GBP_USD',
    'USDJPY': 'OANDA:USD_JPY',
    'AUDUSD': 'OANDA:AUD_USD',
    'USDCAD': 'OANDA:USD_CAD',
    'USDCHF': 'OANDA:USD_CHF',
    'BTCUSD': 'BINANCE:BTCUSDT',
    'ETHUSD': 'BINANCE:ETHUSDT',
    'XAUUSD': 'OANDA:XAU_USD',
    'APPLE': 'AAPL',
    'AMAZON': 'AMZN',
    'TESLA': 'TSLA',
    'FACEBOOK': 'META',
    'MICROSOFT': 'MSFT',
    'GOOGLE': 'GOOGL',
    'NETFLIX': 'NFLX',
    'BOEING': 'BA',
    'INTEL': 'INTC',
    'VISA': 'V'
  };
  return mapping[clean] || `FX:${clean}`;
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
    // Silent fail if no bridge to avoid console spam
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

// Helper to apply signal lock and sync across components
function applySignalLock(durationMinutes) {
  const dur = parseInt(durationMinutes) || 1;
  appState.signalLockUntil = Date.now() + (dur * 60 * 1000);
  console.log(`[NMNH] Signal lock set for ${dur}m until: ${new Date(appState.signalLockUntil).toLocaleTimeString()}`);
  
  chrome.storage.local.set({ nmnh_state: appState });
  
  broadcastToAll({ 
    type: 'SESSION_UPDATE', 
    payload: { 
      ...appState.session, 
      aiSignals: appState.aiSignals, 
      sessionStartBalance: appState.sessionStartBalance,
      signalLockUntil: appState.signalLockUntil
    } 
  });
}

// Start bridge connection
connectToSentinelBridge();

// Helper to broadcast messages to popup AND all relevant tabs
function broadcastToAll(msg) {
  // 1. To Popup
  chrome.runtime.sendMessage(msg).catch(() => {});
  
  // 2. To all tabs matching PocketOption
  chrome.tabs.query({ url: ["*://*.pocketoption.com/*", "*://*.po.trade/*", "*://*.po.cash/*"] }, (tabs) => {
    tabs.forEach(tab => {
      chrome.tabs.sendMessage(tab.id, msg).catch(() => {});
    });
  });
}
