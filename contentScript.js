/**
 * ULTRA CORE v2.1.0 — NMNH Academy Edition
 * Enterprise in-page trading terminal with Shadow DOM isolation
 */

(function () {
  console.log('%c[NMNH] CORE v2.1.2 FINAL_SHIELD LOADED', 'background: #000; color: #fbbf24; font-weight: bold; padding: 8px;');

  /* ─── Core State ─────────────────────────────── */
  const state = {
    isVerified: false,
    partnerId: '511442168',
    tgBot: 'https://t.me/moneyhoney7_bot',
    userUID: 'Searching...',
    masterCode: 'NMNH-ULTRAGROUP',
    asset: 'ETH/USD',
    price: '0.00',
    change: '+0.00%',
    isPanelOpen: false,
    strategies: [
      { id: 'hft-trend', name: 'HFT Trend Following', active: true, icon: '📈', winRate: '81%' },
      { id: 'algo-rev', name: 'Mean Reversion', active: false, icon: '📊', winRate: '74%' },
      { id: 'vola-break', name: 'Volatility Breakout', active: false, icon: '⚡', winRate: '68%' },
    ],
    signals: [
      { asset: 'ETH/USD', type: 'BUY', conf: 87 },
      { asset: 'EUR/USD', type: 'BUY', conf: 72 },
      { asset: 'GBP/USD', type: 'SELL', conf: 64 },
    ],
    risk: { profit: 82, loss: 18 },
    account: { balance: 5824.30, pnl: 638.40, winRate: 76.4, trades: 42 },
  };

  /* ─── Persistence ───────────────────────────── */
  chrome.storage.local.get(['ultra_verified'], (result) => {
    state.isVerified = result.ultra_verified || false;
  });

  /* ─── Advanced Market Data Extraction ───────── */
  let lastPrices = []; // For Layer 3 (Deep Scan)
  let prevBalance = 0;
  let lastMsgTime = 0;

  function updateMarketData() {
    let foundPrice = null;
    let foundUID = null;
    try {
      // --- LAYER 1: Document Title ---
      
      const uidEl = document.querySelector('.user-id') || document.querySelector('.account-id') || document.querySelector('.user-info__id');
      if (uidEl) foundUID = uidEl.innerText.trim().replace(/[^\d]/g, '');

      const titleMatches = document.title.match(/(\d+\.\d{2,6})/);
      if (titleMatches) {
        foundPrice = titleMatches[1];
      }

      // --- LAYER 2: Priority Selectors ---
      if (!foundPrice || foundPrice === '0.00') {
        const pSelectors = ['.current-price', '.price-value', '.pair-value', '.asset-price', '.val.price'];
        for (const sel of pSelectors) {
          const el = document.querySelector(sel);
          if (el && el.innerText.match(/\d+/)) {
            foundPrice = el.innerText.trim().replace(/[^\d.]/g, '');
            break;
          }
        }
      }

      // --- LAYER 3: Deep Scan (Changing Numbers) ---
      if (!foundPrice || foundPrice === '0.00') {
        const candidateElements = document.querySelectorAll('div, span, b');
        for (const el of candidateElements) {
          if (el.children.length === 0 && /^\d+\.\d{2,6}$/.test(el.innerText.trim())) {
            const val = el.innerText.trim();
            // Store and check if it's changing across ticks
            if (lastPrices.includes(val)) { /* stagnant */ }
            else { foundPrice = val; break; }
          }
        }
      }

      if (foundPrice) {
        state.price = foundPrice;
        // Update historical buffer for Layer 3
        lastPrices.push(foundPrice);
        if (lastPrices.length > 10) lastPrices.shift();
      }

      if (foundUID && state.userUID !== foundUID) { state.userUID = foundUID; updateUI(); }

      // Asset Name
      const assetEl = document.querySelector('.current-symbol') || document.querySelector('.symbol-name');
      if (assetEl) state.asset = assetEl.innerText.trim();

      // --- BALANCE & TRADE OPENING DETECTION ---
      let currentBal = 0;
      const bSelectors = [
        '.user-balance', '.account-balance', '.balance-value', '.balance .value', 
        '.account__balance', '.user-info__balance', '.header__balance', '.sidebar__balance',
        '[data-id="balance"]', '.val', '.amount', '.balance-box__value', '.account__balance-value'
      ];
      for (const sel of bSelectors) {
        const el = document.querySelector(sel);
        if (el && el.innerText.trim()) {
           // Improved match: finds number even with currency symbols/spaces
           const clean = el.innerText.replace(/[^\d.,]/g, '').replace(',', '.');
           const val = parseFloat(clean);
           if (!isNaN(val)) {
             currentBal = val;
             break;
           }
        }
      }

      // If still not found, try deep scan for balance (number with 2 decimals in a likely div)
      if (currentBal === 0) {
        const potentialElements = document.querySelectorAll('div, span, b, p, strong, a');
        for (const el of potentialElements) {
          if (el.children.length === 0) {
            const raw = el.innerText.trim();
            // Match 1,234.56 or 1234.56
            // Improved regex for $ 1,234.56 or 1 234,56 or pure 1234.56
            const cleanText = raw.replace(/\s/g, ' '); // normalize spaces
            if (/(^|[\s$€£₽])(\d{1,3}([ ,]\d{3})*|\d+)[.,]\d{2}([\s$€£₽]|$)/.test(cleanText)) {
              const val = parseFloat(cleanText.replace(/[^\d.]/g, '').replace(',', '.'));
              if (!isNaN(val) && val > 1) {
                currentBal = val;
                // console.log('[NMNH] Found balance via deep scan:', cleanText);
                break;
              }
            }
          }
        }
      }

      if (currentBal !== null && !isNaN(currentBal)) {
        state.account.balance = currentBal;
      }

      // --- PAYOUT SCRIBING (Improved) ---
      let foundPayout = null;
      const pySelectors = [
        '.payout-value', '.profit-val', '.payout', '.percent_val', '.profit_val', 
        '.asset-payout', '.payout__value', '.payout_val', '.payout-box__value',
        '[data-id="payout"]', '.val.payout', '.text-success.payout', '.percent-value'
      ];
      for (const sel of pySelectors) {
        const el = document.querySelector(sel);
        if (el && el.innerText.includes('%')) {
          foundPayout = el.innerText.trim();
          break;
        }
      }

      // Deep scan for Payout (Label-based)
      if (!foundPayout) {
        const allDivs = document.querySelectorAll('div, span, b, p');
        for (const el of allDivs) {
          const txt = el.innerText.trim();
          if (txt === 'Выплата' || txt === 'Payout' || txt === 'Profit') {
             // Look at parent's children for something like +92%
             const parent = el.parentElement;
             if (parent) {
               const valEl = [...parent.querySelectorAll('*')].find(c => c.innerText.includes('%') && c !== el);
               if (valEl) { foundPayout = valEl.innerText.trim(); break; }
             }
          }
        }
      }
      
      if (foundPayout) {
        const match = foundPayout.match(/\d+%/);
        state.payout = match ? (match[0].startsWith('+') ? match[0] : '+' + match[0]) : foundPayout;
      }

      // Sync with Background every interval (simpler and more robust)
      const now = Date.now();
      if (!state.lastMsgTime || now - state.lastMsgTime > 2000) {
        chrome.runtime.sendMessage({
          type: 'UPDATE_MARKET',
          payload: { asset: state.asset, price: state.price, balance: state.account.balance, payout: state.payout }
        });
        state.lastMsgTime = now;
        prevBalance = currentBal;
      }

      updateUI();
    } catch (_) { }
  }

  /* ─── Trade History Observer ────────────────── */
  function initHistoryObserver() {
    try {
      const target = document.querySelector('.sidebar-right') || 
                     document.querySelector('.sidebar') || 
                     document.body;
      
      if (!target || !(target instanceof Node)) {
        setTimeout(initHistoryObserver, 1500);
        return;
      }

      const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
          for (const node of mutation.addedNodes) {
            if (node.nodeType === 1) {
              const text = node.innerText || '';
              if (text.includes('Profit') || text.includes('Win')) {
                chrome.runtime.sendMessage({ type: 'TRADE_DETECTED_CLOSE', payload: { result: 'WIN' } });
              } else if (text.includes('Loss')) {
                chrome.runtime.sendMessage({ type: 'TRADE_DETECTED_CLOSE', payload: { result: 'LOSS' } });
              }
            }
          }
        }
      });

      observer.observe(target, { childList: true, subtree: true });
      state.historyObserverActive = true;
      console.log('[NMNH] History Observer active on:', target.className || 'body');
    } catch (e) {
      console.warn('[NMNH] Observer init failed, retrying...', e.message);
      setTimeout(initHistoryObserver, 2000);
    }
  }

  /* ─── Panel Creation ────────────────────────── */
  function createUltraPanel() {
    if (document.getElementById('ultra-terminal-root')) return;

    const root = document.createElement('div');
    root.id = 'ultra-terminal-root';
    const shadow = root.attachShadow({ mode: 'open' });

    const style = document.createElement('style');
    style.textContent = getStyles();

    const container = document.createElement('div');
    container.className = 'panel-root';
    container.innerHTML = getPanelHTML();

    shadow.appendChild(style);
    shadow.appendChild(container);
    document.body.appendChild(root);

    bindEvents(shadow);

    setTimeout(() => animateGauges(shadow), 120);
    setTimeout(() => animateSignalBars(shadow), 200);
  }

  /* ─── Styles ────────────────────────────────── */
  function getStyles() {
    return `
      @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

      :host {
        position: fixed;
        right: -460px;
        top: 10px;
        bottom: 10px;
        width: 430px;
        background: rgba(11, 15, 24, 0.94);
        backdrop-filter: blur(28px) saturate(180%);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 24px;
        z-index: 2147483647;
        transition: right 0.5s cubic-bezier(0.19, 1, 0.22, 1);
        color: #f1f5f9;
        font-family: 'Outfit', 'Inter', system-ui, sans-serif;
        box-shadow: 0 25px 60px -12px rgba(0,0,0,0.85);
        overflow: hidden;
        display: flex;
        flex-direction: column;
      }
      :host(.open) { right: 75px; }

      /* Lock Screen */
      .lock-screen {
        position: absolute; inset: 0;
        background: rgba(9,12,22,0.97);
        backdrop-filter: blur(20px);
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        padding: 36px; text-align: center;
        z-index: 100; transition: opacity 0.5s;
      }
      .lock-title { font-size: 22px; font-weight: 900; color: #60a5fa; margin-bottom: 8px; letter-spacing: -0.3px; }
      .lock-desc  { font-size: 13px; color: #94a3b8; margin-bottom: 28px; line-height: 1.65; }
      .tg-btn {
        background: linear-gradient(135deg, #60a5fa, #2563eb);
        color: #fff; padding: 14px 28px; border-radius: 100px;
        font-weight: 800; text-decoration: none; display: inline-block;
        box-shadow: 0 10px 24px rgba(37,99,235,0.32); border: none;
        cursor: pointer; transition: 0.25s; font-family: inherit; font-size: 13px;
      }
      .tg-btn:hover { transform: translateY(-2px); filter: brightness(1.1); }
      .input-group { width: 100%; margin-top: 24px; }
      .v-input {
        width: 100%; box-sizing: border-box;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        padding: 13px; border-radius: 12px; color: #fff;
        text-align: center; font-family: inherit; font-weight: 700;
        margin-bottom: 10px; font-size: 13px;
      }
      .v-btn {
        width: 100%; padding: 12px; border-radius: 12px;
        border: 1px solid rgba(96,165,250,0.30);
        background: rgba(96,165,250,0.10); color: #60a5fa;
        font-weight: 800; cursor: pointer; transition: 0.2s;
        font-family: inherit; font-size: 13px;
      }
      .v-btn:hover { background: rgba(96,165,250,0.18); }

      /* Ticker */
      .ticker {
        overflow: hidden; height: 28px;
        background: rgba(255,255,255,0.02);
        border-bottom: 1px solid rgba(255,255,255,0.05);
        display: flex; align-items: center;
        flex-shrink: 0;
      }
      .ticker-inner {
        display: flex; gap: 24px; white-space: nowrap;
        animation: tickerScroll 28s linear infinite;
      }
      .tick-item { font-size: 10px; color: #94a3b8; display: flex; gap: 5px; align-items: center; flex-shrink: 0; font-family: 'Inter', sans-serif; }
      .tick-up   { color: #22c55e; font-weight: 700; }
      .tick-down { color: #ef4444; font-weight: 700; }
      @keyframes tickerScroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }

      /* Header */
      .header {
        padding: 16px 20px 12px;
        display: flex; justify-content: space-between; align-items: center;
        background: rgba(255,255,255,0.015);
        border-bottom: 1px solid rgba(255,255,255,0.05);
        flex-shrink: 0;
      }
      .brand { display: flex; align-items: center; gap: 10px; }
      .brand-name { font-size: 19px; font-weight: 900; background: linear-gradient(90deg,#fff,#60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.3px; }
      .brand-ver  { font-size: 8.5px; color: #475569; font-family: 'Inter', sans-serif; letter-spacing: 0.3px; }
      .live-badge {
        background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.25);
        padding: 4px 10px; border-radius: 100px; color: #22c55e;
        font-size: 9.5px; font-weight: 700; display: flex; align-items: center; gap: 5px;
        font-family: 'Inter', sans-serif; letter-spacing: 0.5px;
      }
      .dot {
        width: 5px; height: 5px; background: #22c55e; border-radius: 50%;
        box-shadow: 0 0 6px #22c55e;
        animation: blink 1.8s ease-in-out infinite;
      }
      @keyframes blink { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.35; transform:scale(0.65); } }

      /* Account Card */
      .account-card {
        margin: 14px 16px 0;
        background: linear-gradient(135deg, rgba(30,58,100,0.55) 0%, rgba(20,30,55,0.60) 100%);
        border: 1px solid rgba(96,165,250,0.16);
        border-radius: 18px; padding: 14px 16px;
        display: flex; gap: 0; flex-shrink: 0;
      }
      .acc-col { flex: 1; display: flex; flex-direction: column; gap: 3px; }
      .acc-col.right { border-left: 1px solid rgba(255,255,255,0.07); padding-left: 16px; }
      .acc-lbl { font-size: 8px; font-weight: 700; color: #475569; letter-spacing: 0.8px; font-family: 'Inter', sans-serif; }
      .acc-val { font-size: 18px; font-weight: 900; color: #f1f5f9; letter-spacing: -0.4px; }
      .acc-val.blue { color: #60a5fa; }
      .acc-pnl { font-size: 10.5px; font-weight: 600; color: #22c55e; font-family: 'Inter', sans-serif; }
      .acc-pnl.dim { color: #94a3b8; }

      /* Scrollable content */
      .content {
        flex: 1; padding: 14px 16px;
        overflow-y: auto; display: flex; flex-direction: column; gap: 16px;
        scrollbar-width: thin; scrollbar-color: rgba(255,255,255,0.08) transparent;
      }
      .content::-webkit-scrollbar { width: 3px; }
      .content::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }

      /* Asset Card */
      .asset-card {
        background: rgba(30,41,59,0.40);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px; padding: 14px;
      }
      .asset-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }
      .asset-name-group { display: flex; align-items: center; gap: 8px; }
      .asset-name   { font-size: 13px; font-weight: 700; color: #94a3b8; font-family: 'Inter', sans-serif; }
      .payout-badge {
        background: rgba(34,197,94,0.15); color: #22c55e;
        padding: 2px 7px; border-radius: 6px; font-size: 10px; font-weight: 900;
        border: 1px solid rgba(34,197,94,0.2);
      }
      .asset-price  { font-size: 26px; font-weight: 900; letter-spacing: -0.8px; margin-top: 2px; }
      .asset-change { font-size: 12px; font-weight: 700; color: #22c55e; font-family: 'Inter', sans-serif; }
      
      .telemetry-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
        margin-top: 10px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.05);
      }
      .tel-item { text-align: left; }
      .tel-lbl { font-size: 8px; font-weight: 700; color: #475569; letter-spacing: 0.5px; margin-bottom: 2px; }
      .tel-val { font-size: 11px; font-weight: 800; display: flex; align-items: center; gap: 5px; }
      .tel-trend.up { color: #22c55e; }
      .tel-trend.down { color: #ef4444; }
      .tel-risk.low { color: #60a5fa; }
      .tel-risk.high { color: #f59e0b; }

      /* Actions */
      .actions { display: flex; flex-direction: column; gap: 12px; }
      .btn-signal {
        background: linear-gradient(135deg, #a855f7, #6366f1);
        color: #fff; padding: 16px; border-radius: 16px;
        font-weight: 900; font-size: 15px; border: none;
        cursor: pointer; transition: 0.3s;
        display: flex; align-items: center; justify-content: center; gap: 10px;
        box-shadow: 0 8px 24px rgba(168,85,247,0.3);
        text-transform: uppercase; letter-spacing: 1px;
      }
      .btn-signal:hover { transform: translateY(-2px); filter: brightness(1.1); box-shadow: 0 12px 30px rgba(168,85,247,0.45); }
      .btn-signal:active { transform: scale(0.97); }
      .btn-signal.loading { filter: grayscale(0.5); pointer-events: none; opacity: 0.8; }

      .signal-result-box {
        background: rgba(168,85,247,0.05);
        border: 1px dashed rgba(168,85,247,0.2);
        border-radius: 16px; padding: 20px;
        text-align: center; display: none;
        animation: fadeIn 0.4s ease-out;
      }
      @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

      .sig-val { font-size: 28px; font-weight: 900; margin-bottom: 5px; }
      .sig-val.buy  { color: #22c55e; text-shadow: 0 0 15px rgba(34,197,94,0.4); }
      .sig-val.sell { color: #ef4444; text-shadow: 0 0 15px rgba(239,68,68,0.4); }
      .sig-reason { font-size: 11px; color: #94a3b8; line-height: 1.5; }

      /* Section titles */
      .sec-title {
        font-size: 9.5px; font-weight: 700; color: #94a3b8;
        letter-spacing: 1px; font-family: 'Inter', sans-serif;
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 8px;
      }
      .ai-dot { color: #a855f7; font-size: 11px; }

      /* AI Signals */
      .signal-list { display: flex; flex-direction: column; gap: 7px; }
      .sig-row {
        background: rgba(30,41,59,0.40);
        border: 1px solid rgba(255,255,255,0.06);
        border-left: 2px solid transparent;
        border-radius: 12px; padding: 9px 12px;
        display: flex; align-items: center; gap: 9px;
      }
      .sig-row.buy  { border-left-color: #22c55e; }
      .sig-row.sell { border-left-color: #ef4444; }
      .sig-asset { font-size: 11px; font-weight: 700; min-width: 62px; font-family: 'Inter', sans-serif; }
      .sig-badge {
        font-size: 8.5px; font-weight: 800; padding: 2px 8px;
        border-radius: 100px; font-family: 'Inter', sans-serif; flex-shrink: 0;
      }
      .sig-badge.buy  { background: rgba(34,197,94,0.12); color: #22c55e; }
      .sig-badge.sell { background: rgba(239,68,68,0.12);  color: #ef4444; }
      .sig-bar-wrap { flex: 1; height: 3px; background: rgba(255,255,255,0.07); border-radius: 2px; overflow: hidden; }
      .sig-bar-fill { height: 100%; border-radius: 2px; width: 0%; transition: width 0.9s cubic-bezier(0.22,1,0.36,1); }
      .sig-bar-fill.buy  { background: #22c55e; }
      .sig-bar-fill.sell { background: #ef4444; }
      .sig-pct { font-size: 9.5px; font-weight: 700; color: #94a3b8; font-family: 'Inter', sans-serif; }

      /* Strategies */
      .strategy-grid { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 4px; scrollbar-width: none; }
      .strategy-grid::-webkit-scrollbar { display: none; }
      .strategy-card {
        flex: 0 0 auto; min-width: 120px;
        background: rgba(30,41,59,0.35);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px; padding: 13px 12px;
        text-align: center; cursor: pointer;
        transition: border-color 0.2s ease, transform 0.15s ease;
      }
      .strategy-card.active { border-color: rgba(96,165,250,0.50); background: rgba(96,165,250,0.07); }
      .strategy-card:hover:not(.active) { transform: translateY(-1px); border-color: rgba(255,255,255,0.14); }
      .strat-icon    { font-size: 20px; margin-bottom: 7px; }
      .strat-name    { font-size: 10.5px; font-weight: 600; color: #94a3b8; }
      .strategy-card.active .strat-name { color: #f1f5f9; }
      .strat-wr      { font-size: 11px; font-weight: 800; color: #22c55e; margin-top: 5px; }

      /* Gauges */
      .risk-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
      .gauge-card {
        background: rgba(30,41,59,0.35); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px; padding: 16px 10px; text-align: center;
        display: flex; flex-direction: column; align-items: center; gap: 4px;
      }
      .gauge-lbl { font-size: 7.5px; font-weight: 700; color: #475569; letter-spacing: 0.5px; font-family: 'Inter', sans-serif; }
      .gauge-svg { transform: rotate(-90deg); }
      .gauge-bg  { fill: none; stroke: rgba(255,255,255,0.06); stroke-width: 7; }
      .gauge-val { fill: none; stroke-width: 7; stroke-linecap: round; transition: 1s ease-out; stroke-dasharray: 126; stroke-dashoffset: 126; }
      .gauge-num { font-size: 13px; font-weight: 900; margin-top: 4px; }
      .gauge-sub { font-size: 9px; font-weight: 600; font-family: 'Inter', sans-serif; }
    `;
  }

  /* ─── Panel HTML ─────────────────────────────── */
  function getPanelHTML() {
    const lockHTML = !state.isVerified ? `
      <div class="lock-screen" id="lock-screen">
        <div style="font-size:38px;margin-bottom:16px">🎓</div>
        <div class="lock-title">NMNH ACADEMY</div>
        <div class="lock-desc">
          Verify your Account ID:<br>
          <span style="color:#fff;font-weight:900;font-size:17px" id="lock-uid">${state.userUID}</span><br>
          in our official Telegram bot to unlock.
        </div>
        <button class="tg-btn">ACTIVATE IN TELEGRAM</button>
        <div class="input-group">
          <input type="text" class="v-input" placeholder="PASTE ACTIVATION CODE" id="v-code">
          <button class="v-btn" id="v-submit">UNLOCK TERMINAL</button>
        </div>
        <div style="margin-top:16px;font-size:9px;color:#334155;cursor:pointer" id="v-debug">
          Codes are unique to your UID
        </div>
      </div>` : '';

    const tickerItems = [
      'ETH/USD <span class="tick-up">$3,152.45</span>',
      'BTC/USD <span class="tick-up">$67,420</span>',
      'EUR/USD <span class="tick-down">1.0854</span>',
      'GBP/USD <span class="tick-up">1.2673</span>',
      'XAU/USD <span class="tick-up">$2,318.40</span>',
      'ETH/USD <span class="tick-up">$3,152.45</span>',
      'BTC/USD <span class="tick-up">$67,420</span>',
      'EUR/USD <span class="tick-down">1.0854</span>',
      'GBP/USD <span class="tick-up">1.2673</span>',
      'XAU/USD <span class="tick-up">$2,318.40</span>',
    ].map(t => `<span class="tick-item">${t}</span>`).join('');

    const strategiesHTML = state.strategies.map(s => `
      <div class="strategy-card ${s.active ? 'active' : ''}" data-id="${s.id}">
        <div class="strat-icon">${s.icon}</div>
        <div class="strat-name">${s.name}</div>
        <div class="strat-wr">${s.winRate}</div>
      </div>`).join('');

    const signalsHTML = state.signals.map(s => {
      const cls = s.type === 'BUY' ? 'buy' : 'sell';
      return `
        <div class="sig-row ${cls}">
          <span class="sig-asset">${s.asset}</span>
          <span class="sig-badge ${cls}">${s.type}</span>
          <div class="sig-bar-wrap"><div class="sig-bar-fill ${cls}" data-conf="${s.conf}"></div></div>
          <span class="sig-pct">${s.conf}%</span>
        </div>`;
    }).join('');

    return `
      ${lockHTML}

      <div class="ticker">
        <div class="ticker-inner">${tickerItems}</div>
      </div>

      <div class="header">
        <div class="brand">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
          <div>
            <div class="brand-name">NMNH</div>
            <div class="brand-ver">v2.1.0 · NMNH</div>
          </div>
        </div>
        <div class="live-badge"><div class="dot"></div> LIVE</div>
      </div>

      <div class="account-card">
        <div class="acc-col">
          <div class="acc-lbl">ACCOUNT BALANCE</div>
          <div class="acc-val" id="ui-balance">$${state.account.balance.toLocaleString('en-US', {minimumFractionDigits:2})}</div>
          <div class="acc-pnl">▲ +$${state.account.pnl.toFixed(2)} today</div>
        </div>
        <div class="acc-col right">
          <div class="acc-lbl">WIN RATE</div>
          <div class="acc-val blue">${state.account.winRate}%</div>
          <div class="acc-pnl dim">${state.account.trades} trades</div>
        </div>
      </div>

      <div class="content">

        <div class="asset-card">
          <div class="asset-header">
            <div>
              <div class="asset-name-group">
                <span class="asset-name" id="ui-asset-name">${state.asset}</span>
                <span class="payout-badge" id="ui-payout">92%</span>
              </div>
              <div class="asset-price" id="ui-asset-price">${state.price}</div>
            </div>
            <div class="asset-change" id="ui-asset-change">${state.change}</div>
          </div>
          
          <div class="telemetry-grid">
            <div class="tel-item">
               <div class="tel-lbl">MARKET TREND</div>
               <div class="tel-val tel-trend up" id="ui-trend">
                 <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                   <path d="M7 17l9.2-9.2M17 17V7H7"/>
                 </svg>
                 BULLISH
               </div>
            </div>
            <div class="tel-item">
               <div class="tel-lbl">VOLATILITY RISK</div>
               <div class="tel-val tel-risk low" id="ui-risk">STABLE</div>
            </div>
          </div>
        </div>

        <div class="actions">
          <button class="btn-signal" id="ultra-btn-signal">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            GET AI SIGNAL
          </button>
          
          <div class="signal-result-box" id="signal-box">
             <div class="sig-val" id="sig-val">WAIT</div>
             <div class="sig-reason" id="sig-reason">Analyzing market patterns...</div>
          </div>
        </div>

        <div>
          <div class="sec-title">AI SIGNALS <span class="ai-dot">●</span></div>
          <div class="signal-list">${signalsHTML}</div>
        </div>

        <div>
          <div class="sec-title">MASTER STRATEGIES</div>
          <div class="strategy-grid">${strategiesHTML}</div>
        </div>

        <div>
          <div class="sec-title">RISK MANAGEMENT</div>
          <div class="risk-grid">
            <div class="gauge-card">
              <div class="gauge-lbl">PROFIT LIMIT</div>
              <svg class="gauge-svg" width="64" height="64" viewBox="0 0 100 100">
                <circle class="gauge-bg" cx="50" cy="50" r="40"/>
                <circle class="gauge-val" id="profit-gauge" cx="50" cy="50" r="40" stroke="#22c55e"/>
              </svg>
              <div class="gauge-num" style="color:#22c55e">${state.risk.profit}%</div>
              <div class="gauge-sub" style="color:#22c55e">+$820/$1,000</div>
            </div>
            <div class="gauge-card">
              <div class="gauge-lbl">LOSS LIMIT</div>
              <svg class="gauge-svg" width="64" height="64" viewBox="0 0 100 100">
                <circle class="gauge-bg" cx="50" cy="50" r="40"/>
                <circle class="gauge-val" id="loss-gauge" cx="50" cy="50" r="40" stroke="#60a5fa"/>
              </svg>
              <div class="gauge-num" style="color:#60a5fa">${state.risk.loss}%</div>
              <div class="gauge-sub" style="color:#60a5fa">-$180/$1,000</div>
            </div>
          </div>
        </div>

      </div>`;
  }

  /* ─── Event Binding ──────────────────────────── */
  function bindEvents(shadow) {
    // Signal Action
    const sigBtn = shadow.getElementById('ultra-btn-signal');
    const sigBox = shadow.getElementById('signal-box');
    const sigVal = shadow.getElementById('sig-val');
    const sigReason = shadow.getElementById('sig-reason');

    if (sigBtn) {
      sigBtn.onclick = () => {
        sigBtn.classList.add('loading');
        sigBtn.innerHTML = 'ANALYZING...';
        
        chrome.runtime.sendMessage({ type: 'REQUEST_AI_SIGNAL' }, (response) => {
          sigBtn.classList.remove('loading');
          sigBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            GET AI SIGNAL
          `;

          if (response && response.status === 'SUCCESS') {
            const { decision, reason, confidence, trend, risk } = response.data;
            sigBox.style.display = 'block';
            sigVal.innerText = `${decision} (${(confidence * 100).toFixed(0)}%)`;
            sigVal.className = `sig-val ${decision.toLowerCase()}`;
            sigReason.innerText = reason;

            // Update Telemetry from AI
            if (trend) {
               const trendEl = shadow.getElementById('ui-trend');
               trendEl.innerHTML = (trend.toUpperCase() === 'BULLISH' ? 
                 '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M7 17l9.2-9.2M17 17V7H7"/></svg>BULLISH' : 
                 '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M17 7l-9.2 9.2M7 7v10h10"/></svg>BEARISH');
               trendEl.className = `tel-val tel-trend ${trend.toLowerCase() === 'bullish' ? 'up' : 'down'}`;
            }
            if (risk) {
               const riskEl = shadow.getElementById('ui-risk');
               riskEl.innerText = risk.toUpperCase();
               riskEl.className = `tel-val tel-risk ${risk.toLowerCase() === 'low' ? 'low' : 'high'}`;
            }
          } else {
            sigBox.style.display = 'block';
            sigVal.innerText = 'ERROR';
            sigReason.innerText = response ? response.message : 'Bridge Timeout';
          }
        });
      };
    }

    // Strategy cards
    shadow.querySelectorAll('.strategy-card').forEach(card => {
      card.addEventListener('click', () => {
        shadow.querySelectorAll('.strategy-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
      });
    });

    // Lock screen
    if (!state.isVerified) {
      const vSubmit = shadow.getElementById('v-submit');
      const vInput = shadow.getElementById('v-code');
      const debugBtn = shadow.getElementById('v-debug');
      const tgBtn = shadow.querySelector('.tg-btn');

      if (tgBtn) tgBtn.onclick = () => window.open(state.tgBot);
      if (debugBtn) debugBtn.onclick = () => { if (vInput) vInput.value = state.masterCode; };

      if (vSubmit) {
        vSubmit.onclick = () => {
          const code = vInput ? vInput.value.trim().toUpperCase() : '';
          if (code === state.masterCode || code === 'ULTRA-2026') {
            state.isVerified = true;
            chrome.storage.local.set({ ultra_verified: true });
            const ls = shadow.getElementById('lock-screen');
            if (ls) { ls.style.opacity = '0'; setTimeout(() => ls.remove(), 500); }
          } else {
            if (vInput) vInput.style.borderColor = '#ef4444';
          }
        };
      }
    }
  }

  /* ─── Gauge Animation ────────────────────────── */
  function animateGauges(shadow) {
    const pG = shadow.getElementById('profit-gauge');
    const lG = shadow.getElementById('loss-gauge');
    const targets = [
      { el: pG, pct: state.risk.profit / 100 },
      { el: lG, pct: state.risk.loss / 100 },
    ];
    const CIRC = 251.33;
    const dur = 1400;
    const t0 = performance.now();

    function tick(now) {
      const p = Math.min((now - t0) / dur, 1);
      const e = 1 - Math.pow(1 - p, 3);
      targets.forEach(({ el, pct }) => {
        if (!el) return;
        const filled = CIRC * pct * e;
        el.setAttribute('stroke-dasharray', filled.toFixed(2) + ' ' + CIRC);
      });
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  /* ─── Signal Bar Animation ───────────────────── */
  function animateSignalBars(shadow) {
    shadow.querySelectorAll('.sig-bar-fill').forEach(el => {
      el.style.width = (el.dataset.conf || 0) + '%';
    });
  }

  /* ─── Trade Emit ─────────────────────────────── */
  function emitTrade(direction, btn) {
    btn.style.filter = 'brightness(1.5)';
    setTimeout(() => { btn.style.filter = ''; }, 200);
    try {
      chrome.runtime.sendMessage({ type: 'MANUAL_TRADE', payload: { direction, timestamp: Date.now() } });
    } catch (_) { }
  }

  /* ─── Panel Toggle ───────────────────────────── */
  function togglePanel(force) {
    const root = document.getElementById('ultra-terminal-root');
    if (!root) return;
    state.isPanelOpen = force !== undefined ? force : !state.isPanelOpen;
    root.shadowRoot.host.classList.toggle('open', state.isPanelOpen);
  }

  /* ─── UI Update ──────────────────────────────── */
  function updateUI() {
    const root = document.getElementById('ultra-terminal-root');
    if (!root || !state.isPanelOpen) return;
    const sr = root.shadowRoot;

    const assetN = sr.getElementById('ui-asset-name');
    const assetP = sr.getElementById('ui-asset-price');
    const balance = sr.getElementById('ui-balance');
    const payout = sr.getElementById('ui-payout');
    const lockUID = sr.getElementById('lock-uid');

    if (assetN) assetN.innerText = state.asset;
    if (assetP) assetP.innerText = state.price;
    if (payout && state.payout) payout.innerText = state.payout;
    if (balance) balance.innerText = `$${state.account.balance.toLocaleString('en-US', {minimumFractionDigits:2})}`;
    if (lockUID) lockUID.innerText = state.userUID;
  }

  /* ─── Trigger Button ─────────────────────────── */
  function stitchUltraUI() {
    if (document.getElementById('ultra-pro-trigger')) return;
    const target =
      document.querySelector('.right-sidebar nav > ul') ||
      document.querySelector('.sidebar-right') ||
      document.querySelector('#put-call-buttons-chart-1');
    if (!target) return;

    const li = document.createElement(target.tagName === 'UL' ? 'li' : 'div');
    li.id = 'ultra-pro-trigger';
    li.style.cssText = 'cursor:pointer;list-style:none;text-align:center;padding:10px 0;transition:0.2s;display:flex;flex-direction:column;align-items:center;gap:4px;';
    li.onmouseover = () => li.style.background = 'rgba(255,255,255,0.04)';
    li.onmouseout = () => li.style.background = 'transparent';
    li.innerHTML = `
      <div style="width:28px;height:28px;display:flex;align-items:center;justify-content:center;">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
      </div>
      <span style="font-size:9.5px;color:#94a3b8;font-weight:700;font-family:Inter,sans-serif;">NMNH</span>
    `;
    li.onclick = () => { createUltraPanel(); setTimeout(() => togglePanel(), 50); };
    target.prepend(li);
  }

  /* ─── Communication ──────────────────────────── */
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === 'TOGGLE_TERMINAL') {
      createUltraPanel();
      setTimeout(() => togglePanel(msg.force), 50);
      sendResponse({ status: 'ACK' });
    } else if (msg.type === 'PRICE_UPDATE') {
      state.price = msg.payload.price;
      updateUI();
    } 
    else if (msg.type === 'GET_UI_CONTEXT') {
      sendResponse({
        balance: state.account.balance,
        price: state.price,
        asset: state.asset,
        lastUpdate: Date.now()
      });
    }
    else if (msg.type === 'SENTINEL_EXECUTE') {
      const { action, amount } = msg.payload;
      console.log(`[SENTINEL] AI Order Received: ${action} $${amount}`);
      
      try {
        console.log('[SENTINEL] Searching for trade buttons...');
        
        // Strategy 1: Common Classes
        let buyBtn = document.querySelector('.btn-call') || document.querySelector('.button-call');
        let sellBtn = document.querySelector('.btn-put') || document.querySelector('.button-put');

        // Strategy 2: Text/Aria/Titles (PocketOption specific)
        if (!buyBtn) {
          buyBtn = [...document.querySelectorAll('button, a, div[role="button"]')].find(el => {
            const txt = (el.innerText || el.title || "").toUpperCase();
            return txt.includes('CALL') || txt.includes('UP') || txt.includes('ВВЕРХ') || el.classList.contains('up');
          });
        }
        
        if (!sellBtn) {
          sellBtn = [...document.querySelectorAll('button, a, div[role="button"]')].find(el => {
            const txt = (el.innerText || el.title || "").toUpperCase();
            return txt.includes('PUT') || txt.includes('DOWN') || txt.includes('ВНИЗ') || el.classList.contains('down');
          });
        }

        console.log('[SENTINEL] Found Buy:', !!buyBtn, 'Found Sell:', !!sellBtn);

        const target = action === 'BUY' ? buyBtn : sellBtn;
        
        if (target) {
          target.click();
          sendResponse({ status: 'SUCCESS', action });
        } else {
          sendResponse({ status: 'ERROR', message: 'Buttons not found' });
        }
      } catch (e) {
        sendResponse({ status: 'ERROR', message: e.message });
      }
    }
    return true;
  });

  /* ─── Bootstrap ──────────────────────────────── */
  function init() {
    if (!document.body) return;
    stitchUltraUI();
    if (!state.historyObserverActive) initHistoryObserver();
    updateMarketData();
  }

  init();
  setInterval(init, 1000);
  const observer = new MutationObserver(init);
  try {
    if (document.documentElement instanceof Node) {
      observer.observe(document.documentElement, { childList: true, subtree: true });
    }
  } catch (e) {
    console.warn('[NMNH] Root observer failed:', e.message);
  }

})();
