/**
 * ULTRA CORE v2.1.0 — NMNH Academy Edition
 * Enterprise in-page trading terminal with Shadow DOM isolation
 */

(function () {
  console.log('%c[NMNH] SCRIPT LOADING...', 'background: #000; color: #fbbf24; font-weight: bold; padding: 8px;');

  /* ─── Core State ─────────────────────────────── */
  const state = {
    isVerified: true,
    isAdmin: true,
    partnerId: '511442168',
    tgBot: 'https://t.me/moneyhoney7_bot',
    userUID: 'Searching...',
    masterCode: 'NMNH-ULTRAGROUP',
    asset: 'ETH/USD',
    price: '0.00',
    change: '+0.00%',
    historyObserverActive: false,
    isInitializing: false,
    strategies: [
      { id: 'hft-trend', name: 'HFT Trend Following', active: true, icon: '📈', winRate: '81%' },
      { id: 'algo-rev', name: 'Mean Reversion', active: false, icon: '📊', winRate: '74%' },
      { id: 'vola-break', name: 'Volatility Breakout', active: false, icon: '⚡', winRate: '68%' },
    ],
    signals: [], // Start empty as requested
    risk: { profit: 0, loss: 0 },
    account: { balance: 0, pnl: 0, winRate: 0, trades: 0, wins: 0, losses: 0, sessionStartBalance: 0 },
    tickerPrices: {},
    isGeneratingSignal: false, // For local UI state
    isTrading: false, // Global session state
    isPanelOpen: false, // Hidden by default — user opens via NMNH button
    profitAlertShown: false, // New flag for take-profit
    isAmountPercent: false, // Fixed vs 10% balance mode
    signalLockUntil: 0,
    isOTC: false
  };

  /* ─── Persistence ───────────────────────────── */
  chrome.storage.local.get(['ultra_verified', 'ultra_panel_open', 'ultra_start_trading', 'nmnh_state'], (result) => {
    state.isVerified = true; // Show by default
    
    // PRE-HYDRATE stats from storage BEFORE creating UI (prevents 0→real jump)
    if (result.nmnh_state) {
      const s = result.nmnh_state;
      if (s.session) {
        state.account.wins = s.session.wins || 0;
        state.account.losses = s.session.losses || 0;
        state.account.trades = (s.session.wins || 0) + (s.session.losses || 0);
        state.account.winRate = state.account.trades > 0 
          ? (state.account.wins / state.account.trades) * 100 : 0;
        // Pre-load processed trade sigs so parseTradeHistory doesn't re-count them!
        if (s.session.processed && Array.isArray(s.session.processed)) {
          s.session.processed.forEach(sig => processedTrades.add(sig));
        }
      }
      if (s.dailyPnl !== undefined) state.account.pnl = s.dailyPnl;
      if (s.balance !== undefined) state.account.balance = s.balance;
      if (s.sessionStartBalance !== undefined) state.account.sessionStartBalance = s.sessionStartBalance;
      if (s.isTrading !== undefined) state.isTrading = s.isTrading;
      if (s.aiSignals) state.signals = s.aiSignals;
    }
    
    // Create panel IMMEDIATELY — no setTimeout delay
    createUltraPanel();
    
    if (result.ultra_start_trading) {
      console.log('[NMNH] Auto-starting trading session...');
      chrome.runtime.sendMessage({ type: 'START_TRADING', payload: { mode: 'hft-trend' } });
      createSessionWindow();
      chrome.storage.local.set({ ultra_start_trading: false }); 
    }
  });

  chrome.storage.onChanged.addListener((changes) => {
    if (changes.ultra_verified) {
      state.isVerified = changes.ultra_verified.newValue;
      if (state.isVerified) {
        const root = document.getElementById('ultra-terminal-root');
        if (root && root.shadowRoot) {
           const tls = root.shadowRoot.getElementById('lock-screen');
           if (tls) {
             tls.style.opacity = '0';
             setTimeout(() => tls.remove(), 500);
           }
        }
      }
    }
  });

  /* ─── Asset → TradingView Symbol Converter ──── */


  /* ─── Advanced Market Data Extraction ───────── */
  let lastPrices = []; // Buffer for local TA (120 samples)
  const MAX_PRICE_HISTORY = 120;
  let prevBalance = 0;
  let lastMsgTime = 0;
  let tradeDetectionCooldown = 0; // debounce for balance-based trade detection

  function updateMarketData() {
    let foundPrice = null;
    let foundUID = null;
    try {
      // --- LAYER 1: Document Title ---

      // Revert target fallback to document.body for general queries
      const target = document.body;

      const uidEl = target.querySelector('.user-id') || 
                    target.querySelector('.account-id') || 
                    target.querySelector('.user-info__id') || 
                    target.querySelector('.js-hd[data-hd-show*="id"]') ||
                    target.querySelector('.js-hd');
      
      if (uidEl) {
        let raw = uidEl.innerText || uidEl.getAttribute('data-hd-show') || '';
        foundUID = raw.trim().replace(/[^\d]/g, '');
      }

      // Deep fallback for UID if still not found
      if (!foundUID) {
        const anyIdEl = [...document.querySelectorAll('div, span')].find(el => 
          el.innerText.toLowerCase().includes('id ') && /\d{5,}/.test(el.innerText)
        );
        if (anyIdEl) foundUID = anyIdEl.innerText.replace(/[^\d]/g, '');
      }

      const titleMatches = document.title.match(/(\d+\.\d{2,6})/);
      if (titleMatches) {
        foundPrice = titleMatches[1];
      }

      // --- LAYER 2: Priority Selectors ---
      if (!foundPrice || foundPrice === '0.00') {
        const pSelectors = [
          '.current-price', '.price-value', '.pair-value', '.asset-price', '.val.price',
          '.value__val', '.value-wrap', '.charts-value', '[class*="current-price"]',
          '[class*="price-value"]', '[class*="chart-price"]'
        ];
        for (const sel of pSelectors) {
          const el = document.querySelector(sel);
          if (el && el.innerText.match(/\d+/)) {
            foundPrice = el.innerText.trim().replace(/[^\d.]/g, '');
            break;
          }
        }
      }

      // --- LAYER 3: Deep Scan (price-like numbers) ---
      if (!foundPrice || foundPrice === '0.00') {
        const candidateElements = document.querySelectorAll('div, span, b, strong');
        for (const el of candidateElements) {
          if (el.children.length === 0 && /^\d+\.\d{2,6}$/.test(el.innerText.trim())) {
            foundPrice = el.innerText.trim();
            break;
          }
        }
      }

      if (foundPrice) {
        state.price = foundPrice;
        // Update historical buffer (1 sample per second)
        const pNum = parseFloat(foundPrice);
        if (!isNaN(pNum)) {
          lastPrices.push(pNum);
          if (lastPrices.length > MAX_PRICE_HISTORY) lastPrices.shift();
        }
      }

      if (foundUID && state.userUID !== foundUID) { 
        state.userUID = foundUID; 
        updateUI(); 
        // Trigger verification via background's HTTP endpoint
        if (!state.isVerified) {
          safeSendMessage({ type: 'VERIFY_UID', payload: { uid: foundUID } }, (res) => {
            if (res && res.isVerified) {
              state.isVerified = true;
              createUltraPanel();
            }
          });
        }
      }

      // Asset Name
      // Asset Name - Improved for PocketOption
      const assetEl = document.querySelector('.current-symbol') || 
                      document.querySelector('.symbol-name') || 
                      document.querySelector('.current-pair') ||
                      document.querySelector('.pair-name-container');
      if (assetEl) {
        const rawAsset = assetEl.innerText.trim();
        if (rawAsset && rawAsset !== state.asset) {
          state.asset = rawAsset;
          state.isOTC = rawAsset.toUpperCase().includes('OTC');
          updateUI();
        }
      }

      // --- BALANCE & TRADE OPENING DETECTION ---
      let currentBal = 0;
      const bSelectors = [
        '.user-balance', '.account-balance', '.balance-value', '.balance .value',
        '.account__balance', '.user-info__balance', '.header__balance', '.sidebar__balance',
        '[data-id="balance"]', '.balance-box__value', '.js-balance', '.account__balance-value',
        '.val', '.amount'
      ];
      for (const sel of bSelectors) {
        const el = document.querySelector(sel);
        if (el && el.innerText.trim()) {
          // Improved match: finds number even with currency symbols/spaces
          const clean = el.innerText.replace(/[^\d.,]/g, '').replace(',', '.');
          const val = parseFloat(clean);
          if (!isNaN(val) && val > 0) {
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
            const parent = el.parentElement;
            if (parent) {
              const children = [...parent.querySelectorAll('*')];
              const valEl = children.find(c => c.innerText.includes('%') && c !== el);
              if (valEl) { foundPayout = valEl.innerText.trim(); }
              // Also find dollar payout amount (e.g. "+$1.92")
              const dollarEl = children.find(c => /\+?\$[\d,.]+/.test(c.innerText.trim()) && c !== el);
              if (dollarEl) { state.payoutAmount = dollarEl.innerText.trim(); }
              if (foundPayout) break;
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
        safeSendMessage({
          type: 'UPDATE_MARKET',
          payload: { asset: state.asset, price: state.price, balance: state.account.balance, payout: state.payout }
        });
        state.lastMsgTime = now;
      }
      prevBalance = currentBal;

      updateUI();
    } catch (e) {
      console.warn('[NMNH] UI Stitch failed:', e.message);
    }
  }

  async function verifyUser(uid) {
    if (!uid) return;
    console.log(`[NMNH] Automating verification for UID: ${uid}`);
    chrome.runtime.sendMessage({ type: 'VERIFY_UID', payload: { uid } }, (response) => {
      if (response && typeof response.isVerified !== 'undefined') {
        state.isVerified = response.isVerified;
        updateUI();
      }
    });
  }

  /* ─── Real-Time Ticker Logic ────────────────── */
  // Start ticker updates removed as requested


  // --- Admin Loss Correction (Manual/Auto) ---
  window.nmnhTestDecrement = () => {
    console.log('[NMNH] Manual test decrement triggered...');
    safeSendMessage({ type: 'DECREMENT_STATS' });
  };

  document.addEventListener('click', (e) => {
    // Catch-all: find any element that has "Отмена" or "Cancel" in it or its direct children
    let x = e.target;
    while (x && x !== document.body) {
      const text = (x.innerText || x.textContent || '').trim();
      if (/^(Отмена|Cancel)$/i.test(text) || x.classList.contains('deal-cancel')) {
         console.log('%c[NMNH] Cancel Button Clicked!', 'background: #f43f5e; color: white; padding: 4px; font-weight: bold;');
         safeSendMessage({ type: 'DECREMENT_STATS' });
         
         // Visual feedback
         const oldBg = x.style.background;
         x.style.background = 'rgba(244, 63, 94, 0.5)';
         setTimeout(() => x.style.background = oldBg, 1000);
         break;
      }
      x = x.parentElement;
    }
  }, true);

  /* ─── Trade History Observer (with burst protection) ── */
  let lastTradeTime = 0;
  const TRADE_DEBOUNCE_MS = 2000;
  const processedTrades = new Set(); // Track unique trades to avoid double counting
  const pendingLosses = new Map(); // sig -> timestamp (hoisted for flushing)
  const DEAL_SELECTORS = '.deals-list__item-first, .deals-list__item-short, .deals-list__item, .deal-item, [class*="deal-item"], [class*="deals-list__item"], [class*="history-item"], .list-item, .deals-list > div';
  let sessionStartTime = 0;
  let sessionReadyForTrades = true;

  function getStaticSig(node) {
    // Deterministic signature: Timestamp + Asset + Investment + Payout
    const text = (node.innerText || node.textContent || '').trim().replace(/\s+/g, ' ');
    
    const timeMatch = text.match(/(\d{1,2}:\d{2}(?::\d{2})?)/);
    const time = timeMatch ? timeMatch[1] : '';
    
    const assetMatch = text.match(/[A-Z]{3}\/[A-Z]{3}/);
    const asset = assetMatch ? assetMatch[0] : '';
    
    // Extract ALL money amounts (investment + payout)
    const moneyMatches = text.match(/[\$€£₽]\s?[+-]?[\d,]+(?:[.,]\d+)?/g) || [];
    const invest = moneyMatches[0] || '';
    const payout = moneyMatches[1] || '';
    
    // MUST include payout — otherwise WIN and LOSS at same time get same sig!
    return `${time}|${asset}|${invest}|${payout}`.trim() || text;
  }

  function syncProcessedTrades() {
    const target = document.querySelector('.sidebar-right') ||
      document.querySelector('.sidebar-content') ||
      document.querySelector('.sidebar') ||
      document.querySelector('[class*="sidebar"]') ||
      document.body;
      
    if (!target) return;
    const existingItems = document.querySelectorAll(DEAL_SELECTORS);
    const oldSigs = [];
    const sigCounts = new Map();

    existingItems.forEach(node => {
      let isNested = false;
      let parent = node.parentElement;
      while (parent && parent !== document.body) {
        if (parent.classList.contains('deals-list__item-first') || 
            parent.classList.contains('deals-list__item') ||
            parent.classList.contains('deals-list__item-short') ||
            parent.classList.contains('deal-item')) {
          isNested = true; break;
        }
        parent = parent.parentElement;
      }
      if (isNested) return;

      const txt = (node.innerText || node.textContent || '').trim().replace(/\s+/g, ' ');
      
      // CRITICAL: Do NOT register open trades as "processed" yet.
      // If we register them now, they will never be counted when they close.
      // FIX: Use DOM elements, not text regex (which was matching close times like "02:35")
      const hasTimerEl = node.querySelector('.timer, [class*="timer"], .progress, [class*="progress"]');
      const isPending = txt.toLowerCase().includes('pending');
      if (hasTimerEl || isPending) return;

      const baseSig = getStaticSig(node);
      const dupIdx = sigCounts.get(baseSig) || 0;
      sigCounts.set(baseSig, dupIdx + 1);
      const sig = dupIdx === 0 ? baseSig : `${baseSig}#${dupIdx}`;

      if (!processedTrades.has(sig)) {
        processedTrades.add(sig);
        oldSigs.push(sig);
      }
    });
    if (oldSigs.length > 0) {
      console.log(`[NMNH] Snapshot: registered ${oldSigs.length} existing trades`);
      safeSendMessage({ type: 'REGISTER_OLD_TRADES', payload: { sigs: oldSigs } });
    }
  }

  function flushScrapers() {
    console.log('[NMNH] Flushing Scrapers (Full Reset)...');
    sessionStartTime = Date.now();
    pendingLosses.clear();
    processedTrades.clear(); 
    // Re-sync immediately to avoid counting existing historical trades as new session trades.
    // Our syncProcessedTrades correctly ignores active trades with timers.
    syncProcessedTrades(); 
  }

  function initHistoryObserver() {
    try {
      const target = document.querySelector('.sidebar-right') ||
        document.querySelector('.sidebar-content') ||
        document.querySelector('.sidebar') ||
        document.querySelector('.right-sidebar') ||
        document.querySelector('.sidebar-right-holder') ||
        document.querySelector('[class*="sidebar"]') ||
        document.body;

      if (!target || !(target instanceof Node)) {
        setTimeout(initHistoryObserver, 1500);
        return;
      }

      // ─── Capture Existing History ───
      syncProcessedTrades();
      
      let initialScanDone = false; // CRITICAL: first parse only registers, does NOT report
      sessionReadyForTrades = true;

      function parseTradeHistory() {
        let items = Array.from(document.querySelectorAll(DEAL_SELECTORS));
        
        // DEEP SCAN: If no standard items, scan for any currency pattern in sidebar
        if (items.length === 0) {
           const sidebar = document.querySelector('.sidebar-right') || document.querySelector('.right-sidebar') || document.body;
           items = Array.from(sidebar.querySelectorAll('div, li')).filter(el => {
              const txt = (el.innerText || '').trim();
              // FIX: Corrected currency regex typo (replaced '9' with '₴' or similar)
              return txt.length < 300 && /[\$€£₽₴]\s?[\d,]+/.test(txt) && /\d{1,2}:\d{2}/.test(txt);
           });
        }

        if (!items.length) return;

        const sigCounts = new Map();
        items.forEach(node => {
          // Avoid nested items
          let isNested = false;
          let p = node.parentElement;
          while (p && p !== document.body) {
            if (p.classList.contains('deals-list__item') || p.classList.contains('deal-item')) { isNested = true; break; }
            p = p.parentElement;
          }
          if (isNested) return;

          const rawText = (node.innerText || '').trim().replace(/\s+/g, ' ');
          if (rawText.length < 5) return;
          
          const baseSig = getStaticSig(node);
          const dupIdx = sigCounts.get(baseSig) || 0;
          sigCounts.set(baseSig, dupIdx + 1);
          const sig = dupIdx === 0 ? baseSig : `${baseSig}#${dupIdx}`;

          if (processedTrades.has(sig)) return;

          const moneyMatches = rawText.match(/[\$€£₽]\s?[+-]?[\d,]+(?:[.,]\d+)?/g) || [];
          if (moneyMatches.length === 0) return;

          const invStr = moneyMatches[0];
          const payStr = moneyMatches[1] || '0';
          const inv = parseFloat(invStr.replace(/[^\d.,]/g, '').replace(',', '.'));
          const pay = parseFloat(payStr.replace(/[^\d.,]/g, '').replace(',', '.'));

          if (isNaN(inv)) return;
          
          // Detect active/open trades
          // FIX: Text-based timer regex was matching trade CLOSE times like "02:35"
          // causing ALL closed trades to be skipped! Now only check for actual timer DOM elements.
          const hasTimerElement = node.querySelector('.timer, [class*="timer"], .progress, [class*="progress"]');
          const isPending = rawText.toLowerCase().includes('pending') || rawText.toLowerCase().includes('ожидание');
          
          if (hasTimerElement || isPending) return;

          // Logical WIN/LOSS/TIE
          // FIX: PocketOption losses show as $1 -> $0 (no minus sign, no $0.00)
          // Old logic looked for '-' or '$0.00' in text which never matched!
          const isWin = pay > inv && moneyMatches.length >= 2;
          const isLoss = !isWin && moneyMatches.length >= 2 && pay < inv;
          const isTie = !isWin && !isLoss && pay === inv && moneyMatches.length >= 2;

          // ALWAYS register sig to prevent re-processing
          processedTrades.add(sig);

          // CRITICAL: On initial scan, ONLY register — do NOT report to background!
          if (!initialScanDone) return;

          // Collect new trade for batch analysis
          if (isWin || isLoss || isTie) {
            if (!parseTradeHistory._batch) parseTradeHistory._batch = [];
            parseTradeHistory._batch.push({ result: isWin ? 'WIN' : isLoss ? 'LOSS' : 'TIE', sig, pnl: isWin ? pay - inv : isLoss ? -inv : 0, invStr, payStr });
          }
        });

        // BULK DETECTION GUARD: If 4+ new trades in a single parse, it's a page/SPA reload
        // Real trading produces 1 trade at a time. Mass appearance = sidebar re-render.
        const batch = parseTradeHistory._batch || [];
        parseTradeHistory._batch = [];

        if (batch.length > 3) {
          console.log(`[NMNH] Bulk detection: ${batch.length} trades appeared at once — treating as page reload, NOT reporting.`);
          return;
        }

        // Report individual genuine trades
        batch.forEach(t => {
          if (t.result === 'WIN') {
            console.log(`%c[NMNH] WIN DETECTED: ${t.invStr} -> ${t.payStr}`, 'background: #22c55e; color: white; padding: 2px;');
          } else if (t.result === 'LOSS') {
            console.log(`%c[NMNH] LOSS DETECTED: ${t.invStr}`, 'background: #ef4444; color: white; padding: 2px;');
          } else {
            console.log(`%c[NMNH] TIE DETECTED: ${t.invStr}`, 'background: #60a5fa; color: white; padding: 2px;');
          }
          safeSendMessage({ type: 'TRADE_DETECTED_CLOSE', payload: { result: t.result, sig: t.sig, pnl: t.pnl } });
        });

        if (batch.length > 0) {
          updateUI();
          updateSessionStats();
        }
      }

      let parsingTimeout = null;
      const observer = new MutationObserver(() => {
        try {
          parseTradeHistory();
          if (parsingTimeout) clearTimeout(parsingTimeout);
          parsingTimeout = setTimeout(parseTradeHistory, 1600);
        } catch (err) { console.error('[NMNH] Observer Error:', err); }
      });

      observer.observe(target, { childList: true, subtree: true });
      if (window.nmnhPolling) clearInterval(window.nmnhPolling);
      
      // FIRST RUN: register all existing trades silently
      parseTradeHistory();
      initialScanDone = true;
      console.log(`[NMNH] Initial scan done. ${processedTrades.size} trades registered. Future trades will be reported.`);
      
      window.nmnhPolling = setInterval(parseTradeHistory, 1000);

      // ADDITIONAL: If target is NOT body, also observe body for on-chart tooltip results
      if (target !== document.body) {
        const bodyObserver = new MutationObserver(() => {
          try { parseTradeHistory(); } catch (err) {}
        });
        bodyObserver.observe(document.body, { childList: true, subtree: true });
      }

      state.historyObserverActive = true;
      console.log('[NMNH] History Monitoring ON:', target.className || 'body');
    } catch (e) {
      if (e.message.includes('Extension context invalidated')) return;
      console.warn('[NMNH] Monitor init failed:', e.message);
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
    
    if (state.isPanelOpen) root.classList.add('open');

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
        right: 105px;
        bottom: 0;
        width: 430px;
        height: 60px;
        background: rgba(11, 15, 24, 0.6);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px 24px 0 0;
        z-index: 2147483647;
        transition: all 1.2s cubic-bezier(0.15, 0, 0, 1);
        color: #f8fafc;
        font-family: 'Outfit', 'Inter', system-ui, sans-serif;
        box-shadow: 0 -10px 40px rgba(0,0,0,0.5);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        cursor: pointer;
        will-change: height, transform, opacity;
      }
      :host(.open) {
        height: auto;
        max-height: calc(100vh - 20px);
        background: rgba(11, 15, 24, 0.7);
        backdrop-filter: blur(30px) saturate(200%);
        box-shadow: 0 -20px 60px -12px rgba(0,0,0,0.85);
        cursor: default;
      }

      .mini-dock {
        position: absolute; top: 0; left: 0; width: 100%; height: 60px;
        display: flex; justify-content: center; align-items: center; gap: 50px;
        opacity: 1; transition: opacity 0.8s ease, transform 1.2s cubic-bezier(0.15, 0, 0, 1);
      }
      :host(.open) .mini-dock { opacity: 0; pointer-events: none; transform: translateY(-20px) scale(0.9); }

      .full-terminal {
        opacity: 0; transition: opacity 0.8s 0.3s, transform 1.2s cubic-bezier(0.15, 0, 0, 1);
        display: flex; flex-direction: column; width: 430px;
        transform: translateY(25px);
        position: relative; /* For lock overlay */
      }
      :host(.open) .full-terminal { opacity: 1; transform: translateY(0); }

      .mini-gauge-item { display: flex; align-items: center; gap: 14px; position: relative; }
      .mini-gauge-label { font-size: 9px; font-weight: 800; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 1px; margin-right: -4px; }
      .mini-gauge-num { font-size: 14px; font-weight: 900; color: #fff; min-width: 42px; transition: all 0.4s ease; }
      
      @keyframes miniPulse {
        0% { filter: drop-shadow(0 0 2px var(--color)) brightness(1); opacity: 0.8; }
        50% { filter: drop-shadow(0 0 10px var(--color)) brightness(1.2); opacity: 1; }
        100% { filter: drop-shadow(0 0 2px var(--color)) brightness(1); opacity: 0.8; }
      }
      .mini-gauge-svg { animation: miniPulse 3s ease-in-out infinite; }
      .mini-gauge-item[style*="#22c55e"] .mini-gauge-num.has-val { color: #22c55e; text-shadow: 0 0 12px rgba(34, 197, 94, 0.6); }
      .mini-gauge-item[style*="#ef4444"] .mini-gauge-num.has-val { color: #ef4444; text-shadow: 0 0 12px rgba(239, 68, 68, 0.6); }

      /* Action Buttons */
      .action-footer { margin-top: 30px; display: flex; flex-direction: column; gap: 12px; }
      .action-btn { 
        width: 100%; padding: 16px; border-radius: 12px; border: none;
        background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff;
        font-weight: 800; font-size: 14px; letter-spacing: 1px; cursor: pointer;
        transition: all 0.2s; box-shadow: 0 10px 20px rgba(99, 102, 241, 0.25);
      }
      .action-btn:hover { transform: translateY(-2px); box-shadow: 0 15px 30px rgba(99, 102, 241, 0.4); }
      .action-btn:active { transform: scale(0.98); }

      /* Locked State */
      .v-lock-container { width: 100%; text-align: center; }
      .v-locked-btn { 
        background: linear-gradient(135deg, #334155, #1e293b) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: none !important;
        display: flex; align-items: center; justify-content: center; gap: 10px;
      }
      .v-lock-icon { font-size: 16px; }
      .v-lock-hint { 
        margin-top: 10px; font-size: 10px; color: rgba(255, 255, 255, 0.4); 
        font-weight: 500; letter-spacing: 0.5px; 
      }
      .lock-stat-lbl { font-size: 9px; font-weight: 800; color: #475569; letter-spacing: 1px; margin-bottom: 4px; }
      .lock-stat-val { font-size: 18px; font-weight: 900; color: #60a5fa; font-family: 'Inter', sans-serif; }

      .tg-btn {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        color: #fff; padding: 16px 32px; border-radius: 16px;
        font-weight: 800; text-decoration: none; display: flex; align-items: center; gap: 10px;
        box-shadow: 0 10px 30px rgba(37,99,235,0.35); border: none;
        cursor: pointer; transition: 0.3s; font-family: inherit; font-size: 14px;
        width: 100%; justify-content: center;
      }
      .tg-btn:hover { transform: translateY(-2px); filter: brightness(1.1); box-shadow: 0 15px 40px rgba(37,99,235,0.5); }
      
      .lock-footer { margin-top: 30px; width: 100%; }
      .v-btn-alt {
        width: 100%; padding: 14px; border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.1);
        background: rgba(255,255,255,0.02); color: #f1f5f9;
        font-weight: 700; cursor: pointer; transition: 0.2s;
        font-family: inherit; font-size: 13px; margin-bottom: 12px;
      }
      .v-btn-alt:hover { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.2); }
      .lock-hint { font-size: 10px; color: #475569; font-weight: 500; }

      /* Full Lock Overlay */
      .v-full-lock-overlay {
        position: absolute; inset: 0;
        background: rgba(11, 15, 24, 0.95);
        backdrop-filter: blur(10px);
        display: flex; align-items: center; justify-content: center;
        z-index: 10;
        border-radius: 24px 24px 0 0;
        flex-direction: column;
        text-align: center;
        padding: 20px;
      }
      .v-lock-badge {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 18px;
        padding: 20px 30px;
        display: flex; flex-direction: column; align-items: center;
        gap: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
      }
      .v-lock-main-icon { font-size: 40px; color: #f59e0b; }
      .v-lock-text { font-size: 18px; font-weight: 900; color: #f1f5f9; letter-spacing: 0.5px; }
      .v-lock-sub { font-size: 12px; font-weight: 500; color: #94a3b8; }


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
      /* Visual AI Animations */
      @keyframes flash { 0% { opacity: 0; } 20% { opacity: 1; } 100% { opacity: 0; } }
      .sr-flash { 
        position: fixed; inset: 0; background: #fff; z-index: 99999; 
        pointer-events: none; opacity: 0; animation: flash 0.5s ease-out; 
      }

      @keyframes scanLine { 0% { top: 0; opacity: 0; } 10% { opacity: 1; } 90% { opacity: 1; } 100% { top: 100%; opacity: 0; } }
      .sr-scanner {
        position: fixed; left: 0; width: 100%; height: 3px;
        background: linear-gradient(90deg, transparent, #3b82f6, #60a5fa, #3b82f6, transparent);
        box-shadow: 0 0 15px #3b82f6, 0 0 30px rgba(59, 130, 246, 0.5); 
        z-index: 99998; animation: scanLine 2.5s ease-in-out infinite; pointer-events: none;
      }

      @keyframes flyIn {
        from { transform: scale(1.5) translate(-30%, -30%); opacity: 0; border-radius: 0; }
        to { transform: scale(1) translate(0, 0); opacity: 1; border-radius: 12px; }
      }
      .sr-preview {
        width: 100%; height: 120px; background-size: cover; background-position: center;
        border-radius: 12px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);
        animation: flyIn 0.6s cubic-bezier(0.22, 1, 0.36, 1);
        display: none;
      }

      .sr-generating {
        display: none; text-align: center; padding: 25px 0;
        animation: fadeIn 0.4s ease;
      }
      @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.95); } }
      .gen-dot { 
        color: #60a5fa; font-weight: 800; font-size: 13px; 
        animation: pulse 1.5s ease-in-out infinite; 
        text-shadow: 0 0 10px rgba(96, 165, 250, 0.5);
      }
      .gen-bar {
        width: 100px; height: 3px; background: rgba(255,255,255,0.05);
        margin: 12px auto; border-radius: 10px; overflow: hidden; position: relative;
      }
      @keyframes barFlow { 0% { left: -100%; } 100% { left: 100%; } }
      .gen-bar-fill {
        position: absolute; width: 60%; height: 100%;
        background: linear-gradient(90deg, transparent, #60a5fa, transparent);
        animation: barFlow 1s infinite linear;
      }

      /* AI Signals List */
      .signals-list {
        margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px;
      }
      .signals-list-title {
        font-size: 10px; font-weight: 800; color: #64748b; text-transform: uppercase;
        letter-spacing: 0.1em; margin-bottom: 12px; padding-left: 5px;
        display: flex; align-items: center; gap: 6px;
      }
      .signals-list-title::after { content: ""; flex-grow: 1; height: 1px; background: rgba(255,255,255,0.05); }
      
      .signal-item {
        background: rgba(255,255,255,0.02); border-radius: 12px;
        padding: 10px 12px; margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.05);
        display: flex; align-items: center; gap: 12px; animation: slideIn 0.4s ease;
        transition: all 0.3s ease;
      }
      .signal-item:hover { background: rgba(255,255,255,0.04); border-color: rgba(255,255,255,0.1); }
      .signal-item.generating { border-color: #3b82f633; background: rgba(59, 130, 246, 0.05); }
      
      .signal-item-name { font-weight: 700; font-size: 13px; min-width: 65px; color: #f8fafc; }
      .signal-item-badge {
        padding: 2px 8px; border-radius: 6px; font-size: 9px; font-weight: 900;
        text-transform: uppercase; letter-spacing: 0.05em;
      }
      .signal-item-badge.buy { background: rgba(34, 197, 94, 0.1); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.2); }
      .signal-item-badge.sell { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
      
      .signal-item-conf-bar {
        flex-grow: 1; height: 3px; background: rgba(255,255,255,0.05);
        border-radius: 10px; overflow: hidden; position: relative;
      }
      .signal-item-conf-fill { height: 100%; transition: width 0.8s ease; }
      .signal-item-pct { font-size: 10px; font-weight: 700; color: #64748b; min-width: 30px; text-align: right; }
      

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
        padding: 3px 8px; border-radius: 6px; font-size: 13px; font-weight: 900;
        border: 1px solid rgba(34,197,94,0.2);
      }
      .asset-price  { font-size: 26px; font-weight: 900; letter-spacing: -0.8px; margin-top: 2px; }
      .asset-change { font-size: 16px; font-weight: 700; color: #22c55e; font-family: 'Inter', sans-serif; text-align: right; line-height: 1.3; }
      
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

      .sig-reason { font-size: 11px; color: #94a3b8; line-height: 1.5; }

      /* Premium Signal Report (Now inside asset-card) */
      .signal-report {
        margin-top: 10px; display: none;
        animation: fadeIn 0.4s ease;
      }
      
      .sr-row { 
        display: flex; justify-content: space-between; align-items: center; 
        margin-bottom: 16px;
      }
      .sr-label { font-size: 13px; font-weight: 600; color: #94a3b8; }
      .sr-value { font-size: 14px; font-weight: 800; color: #f1f5f9; }
      
      .sr-badge {
        padding: 6px 14px; border-radius: 8px; font-size: 11px; font-weight: 900;
        text-transform: uppercase; letter-spacing: 0.5px;
      }
      .sr-badge.buy  { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
      .sr-badge.sell { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

      .sr-conf-container { margin-top: 10px; }
      .sr-conf-bar {
        height: 8px; width: 100%; background: rgba(255,255,255,0.05);
        border-radius: 10px; overflow: hidden; margin-top: 8px;
        position: relative;
      }
      .sr-conf-fill {
        height: 100%; border-radius: 10px; width: 0%;
        transition: width 1s cubic-bezier(0.2, 1, 0.3, 1), background-color 0.4s ease;
        background-color: #6366f1; /* Fallback */
      }

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
      .gauge-val { fill: none; stroke-width: 7; stroke-linecap: round; transition: stroke-dashoffset 1s cubic-bezier(0.22, 1, 0.36, 1); stroke-dasharray: 251.33; stroke-dashoffset: 251.33; }
      .gauge-num { font-size: 13px; font-weight: 900; margin-top: 4px; }
      .gauge-sub { font-size: 9px; font-weight: 600; font-family: 'Inter', sans-serif; }
      
    `;
  }

  /* ─── Panel HTML ─────────────────────────────── */
  function getPanelHTML() {
    const startBtnHTML = !state.isVerified ? `
      <div class="v-lock-container">
        <button class="action-btn v-locked-btn" id="v-verify-redirect">
          <span class="v-lock-icon">🔒</span>
          ПРОЙТИ ВЕРИФИКАЦИЮ
        </button>
        <div class="v-lock-hint">Подтвердите ID <b id="lock-uid">${state.userUID}</b> в боте Академии</div>
      </div>
    ` : `
      <button class="action-btn" id="full-start-trading">
        START SESSION
      </button>
    `;

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

    const html = `
      <div class="mini-dock" id="mini-dock">
        <div class="mini-gauge-item" style="--color: #22c55e;">
          <span class="mini-gauge-label">PROFIT</span>
          <svg class="mini-gauge-svg" width="34" height="34" viewBox="0 0 100 100">
            <circle class="gauge-bg" cx="50" cy="50" r="40"/>
            <circle class="gauge-val" id="mini-profit-gauge" cx="50" cy="50" r="40" stroke="#22c55e" style="stroke-dasharray: 251.2; stroke-dashoffset: 251.2;"/>
          </svg>
          <div class="mini-gauge-num" id="mini-profit-num">0%</div>
        </div>
        <div class="mini-gauge-item" style="--color: #ef4444;">
          <span class="mini-gauge-label">LOSS</span>
          <svg class="mini-gauge-svg" width="34" height="34" viewBox="0 0 100 100">
            <circle class="gauge-bg" cx="50" cy="50" r="40"/>
            <circle class="gauge-val" id="mini-loss-gauge" cx="50" cy="50" r="40" stroke="#ef4444" style="stroke-dasharray: 251.2; stroke-dashoffset: 251.2;"/>
          </svg>
          <div class="mini-gauge-num" id="mini-loss-num">0%</div>
        </div>
      </div>

      <div class="full-terminal">
        ${!state.isVerified ? `
          <div class="v-full-lock-overlay" id="lock-screen">
            <div class="v-lock-badge">
              <span class="v-lock-main-icon">🔒</span>
              <div class="v-lock-text">ДОСТУП ОГРАНИЧЕН</div>
              <div class="v-lock-sub">Пройдите верификацию в Академии</div>
              
              <div class="v-lock-container" style="margin-top: 20px; width: 100%;">
                <button class="action-btn v-locked-btn" id="v-verify-redirect">
                  <span class="v-lock-icon">🔒</span>
                  ПРОЙТИ ВЕРИФИКАЦИЮ
                </button>
                <div class="v-lock-hint" style="color: #94a3b8; margin-top: 10px;">ID: <b id="lock-uid">${state.userUID}</b></div>
              </div>
            </div>
          </div>
        ` : ''}
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
            <div class="acc-val" id="ui-balance">$${state.account.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
            <div class="acc-pnl">
              <span id="ui-pnl-sign">${state.account.pnl >= 0 ? '▲' : '▼'}</span> 
              <span id="ui-pnl-val">${state.account.pnl >= 0 ? '+' : '-'}$${Math.abs(state.account.pnl).toFixed(2)} today</span>
            </div>
          </div>
          <div class="acc-col right">
            <div class="acc-lbl">WIN RATE</div>
            <div class="acc-val blue" id="ui-winrate">${state.isTrading ? state.account.winRate : 0}%</div>
            <div class="acc-pnl dim" id="ui-trades-count">${state.isTrading ? state.account.trades : 0} trades</div>
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
              </div>
              <div class="asset-change" id="ui-asset-change">${state.change}</div>
            </div>
            
            <div class="telemetry-grid" id="ui-telemetry-grid">
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

            <div class="signal-report" id="sr-container">
              <div class="sr-preview" id="sr-preview"></div>
              
              <div class="sr-generating" id="sr-gen">
                 <div class="gen-dot">АНАЛИЗ РЫНКА...</div>
                 <div class="gen-bar"><div class="gen-bar-fill"></div></div>
                 <div style="font-size:10px; color:#64748b; margin-top:4px">Анализируем график...</div>
              </div>

              <div id="sr-content">
                <div class="sr-row">
                  <span class="sr-label">Направление::</span>
                  <span class="sr-badge" id="sr-direction">АНАЛИЗ</span>
                </div>
                
                <div class="sr-row">
                  <span class="sr-label">Экспирация:</span>
                  <span class="sr-value" id="sr-expiration">-- мин</span>
                </div>
                
                <div class="sr-conf-container">
                  <div class="sr-row" style="margin-bottom:0">
                      <span class="sr-label">Уверенность</span>
                      <span class="sr-value" id="sr-confidence">0%</span>
                  </div>
                  <div class="sr-conf-bar">
                      <div class="sr-conf-fill" id="sr-conf-fill"></div>
                  </div>
                </div>
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
          </div>

          <div class="signals-list">
            <div class="signals-list-title">AI SIGNALS</div>
            <div id="ai-signals-list-items">
              <!-- Dynamic items -->
            </div>
          </div>

          <div>
            <div class="sec-title">RISK MANAGEMENT <span style="font-size:8.5px; opacity:0.6; color:#94a3b8; font-weight:500; margin-left:8px;">Risk: 1-2% per trade</span></div>
            <div class="risk-grid">
              <div class="gauge-card">
                <div class="gauge-lbl">PROFIT LIMIT</div>
                <svg class="gauge-svg" width="64" height="64" viewBox="0 0 100 100">
                  <circle class="gauge-bg" cx="50" cy="50" r="40"/>
                  <circle class="gauge-val" id="profit-gauge" cx="50" cy="50" r="40" stroke="#22c55e"/>
                </svg>
                <div class="gauge-num" id="ui-profit-num" style="color:#22c55e">${state.risk.profit}%</div>
                <div class="gauge-sub" id="ui-profit-sub" style="color:#22c55e">+$0.00/$0.00</div>
              </div>
              <div class="gauge-card">
                <div class="gauge-lbl">LOSS LIMIT</div>
                <svg class="gauge-svg" width="64" height="64" viewBox="0 0 100 100">
                  <circle class="gauge-bg" cx="50" cy="50" r="40"/>
                  <circle class="gauge-val" id="loss-gauge" cx="50" cy="50" r="40" stroke="#60a5fa"/>
                </svg>
                <div class="gauge-num" id="ui-loss-num" style="color:#60a5fa">${state.risk.loss}%</div>
                <div class="gauge-sub" id="ui-loss-sub" style="color:#60a5fa">-$0.00/$0.00</div>
              </div>
            </div>
          </div>

        </div>
      </div>`;
      
    return html;
  }

  /* ─── Event Binding ──────────────────────────── */
  function bindEvents(shadow) {
    const miniDock = shadow.getElementById('mini-dock');
    if (miniDock) {
      miniDock.onclick = (e) => {
        if (!state.isPanelOpen) togglePanel(true);
      };
    }

    const header = shadow.querySelector('.header');
    if (header) {
      header.onclick = (e) => {
        togglePanel();
      };
    }

    const sigBtn = shadow.getElementById('ultra-btn-signal');
    
    if (sigBtn) {
      sigBtn.onclick = () => {
        if (Date.now() < state.signalLockUntil) return;

        if (!state.isTrading) {
          flushScrapers();
          state.isTrading = true;
          safeSendMessage({ type: 'RESET_SESSION' });
          safeSendMessage({ type: 'START_TRADING' });
          
          createSessionWindow();
          updateUI();

          sigBtn.style.background = 'rgba(34, 197, 94, 0.2)';
          sigBtn.style.color = '#22c55e';
          sigBtn.innerText = 'ЗАПУСК...';
          setTimeout(() => {
            sigBtn.style.background = '';
            sigBtn.style.color = '';
            sigBtn.innerHTML = `
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
              </svg>
              GET AI SIGNAL
            `;
          }, 2000);
          return;
        }

        sigBtn.innerHTML = '<span class="gen-dot">АНАЛИЗ РЫНКА...</span>';
        sigBtn.disabled = true;

        // UI Elements
        const srContainer = shadow.getElementById('sr-container');
        const telGrid = shadow.getElementById('ui-telemetry-grid');
        const srDir = shadow.getElementById('sr-direction');
        const srExp = shadow.getElementById('sr-expiration');
        const srConf = shadow.getElementById('sr-confidence');
        const srFill = shadow.getElementById('sr-conf-fill');
        const srPreview = shadow.getElementById('sr-preview');
        const srGen = shadow.getElementById('sr-gen');
        const srContent = shadow.getElementById('sr-content');
        const panel = shadow.querySelector('.panel');

        // PREPARE GLOBAL STYLES FOR ANIMATIONS
        if (!document.getElementById('sr-global-styles')) {
          const style = document.createElement('style');
          style.id = 'sr-global-styles';
          style.innerHTML = `
            @keyframes scanLineGlobal { 0% { top: 0; opacity: 0; } 10% { opacity: 1; } 90% { opacity: 1; } 100% { top: 100%; opacity: 0; } }
            .sr-scanner-global { 
              position: fixed; z-index: 2147483646; pointer-events: none;
              background: linear-gradient(90deg, transparent, #3b82f6, #60a5fa, #3b82f6, transparent);
              box-shadow: 0 0 15px #3b82f6, 0 0 30px rgba(59, 130, 246, 0.4);
            }
          `;
          if (document.head) document.head.appendChild(style);
        }

        // DETECT CHART BOX
        const canvas = document.querySelector('canvas.layer.plot') || document.querySelector('.chart-container canvas');
        const box = canvas ? canvas.getBoundingClientRect() : { x:0, y:0, width:window.innerWidth, height:window.innerHeight };

        // START SCANNER ANIMATION
        const scanner = document.createElement('div');
        scanner.className = 'sr-scanner-global';
        scanner.style.left = box.x + 'px';
        scanner.style.top = box.y + 'px';
        scanner.style.width = box.width + 'px';
        scanner.style.height = '4px';

        // Localized Scan Animation
        const scanKey = `scanLocal_${Math.floor(Math.random()*1000)}`;
        const styleTag = document.createElement('style');
        styleTag.innerHTML = `
          @keyframes ${scanKey} { 
            0% { transform: translateY(0); opacity: 0; } 
            10% { opacity: 1; } 90% { opacity: 1; } 
            100% { transform: translateY(${box.height}px); opacity: 0; } 
          }
        `;
        if (document.head) document.head.appendChild(styleTag);
        scanner.style.animation = `${scanKey} 1.8s ease-in-out infinite`;
        if (document.body) document.body.appendChild(scanner);

        // FAILSAFE: Remove scanner after 10 seconds if everything else fails
        setTimeout(() => {
          if (scanner && scanner.parentNode) scanner.parentNode.removeChild(scanner);
        }, 10000);

        // Prepare UI
        telGrid.style.display = 'none';
        srContainer.style.display = 'block';
        srContent.style.display = 'none';
        srGen.style.display = 'block';
        srPreview.style.display = 'none';

        // STEP 1: CAPTURE AND CROP
        state.isGeneratingSignal = true;
        renderAISignals();

        // 15s FAILSAFE to avoid getting stuck in "Analyzing"
        const signalFailsafe = setTimeout(() => {
          if (state.isGeneratingSignal) {
             console.warn('[NMNH] Signal generation TIMEOUT (15s)');
             state.isGeneratingSignal = false;
             renderAISignals();
             const sigBtn = shadow.getElementById('ai-generate-btn');
             if (sigBtn) sigBtn.disabled = false;
             document.querySelectorAll('.sr-scanner-global').forEach(el => el.remove());
          }
        }, 15000);

        safeSendMessage({ type: 'CAPTURE_FULL_TAB' }, async (fullScreenshot) => {
          clearTimeout(signalFailsafe);
          if (!fullScreenshot) {
            console.warn('[NMNH] Base capture failed');
            state.isGeneratingSignal = false;
            renderAISignals();
            const sigBtn = shadow.getElementById('ai-generate-btn');
            if (sigBtn) sigBtn.disabled = false;
            return;
          }

          // CROP TO CHART
          const canvas = document.querySelector('canvas.layer.plot') || document.querySelector('.chart-container canvas');
          let cleanChart = fullScreenshot;
          const box = canvas ? canvas.getBoundingClientRect() : null;
          
          if (canvas) {
            const dpr = window.devicePixelRatio || 1;
            cleanChart = await cropScreenshot(fullScreenshot, {
              x: box.x * dpr,
              y: box.y * dpr,
              w: box.width * dpr,
              h: box.height * dpr
            });
          }

          // PREPARE PREVIEW (SHOW LATER)
          srPreview.style.backgroundImage = `url(${cleanChart})`;

          // GET TIMEFRAME
          let timeframeRaw = '1 мин';
          let rawText = null;
          
          const extractTimeStr = (selectors) => {
             const elements = document.querySelectorAll(selectors);
             for (let i = 0; i < elements.length; i++) {
                let txt = elements[i].innerText.trim();
                if (elements[i].tagName.toLowerCase() === 'input') {
                   txt = elements[i].value.trim();
                } else {
                   const inp = elements[i].querySelector('input');
                   if (inp) txt = inp.value.trim();
                }
                if (txt && (/^\d{2}:\d{2}:\d{2}$/.test(txt) || /^([SMHsmhСМЧсмч])(\d+)$/i.test(txt))) {
                   return txt;
                }
             }
             return null;
          };

          // 1. Prioritize right panel expiration inputs (the big "Time" box)
          // We look for selectors that are more likely to be in the trade panel
          rawText = extractTimeStr('.trade-container .control__value, .right-sidebar .control__value, .expiration-row .value, .block-control__input, [name="time"]');
          if (!rawText) rawText = extractTimeStr('.control__value, .value__val, .block-control__input');
          if (!rawText && !state.isOTC) rawText = extractTimeStr('.timeframe-button, .counter__icon');

          if (!rawText) {
             const pCands = document.querySelectorAll('.counter__icon, .timeframe-button');
             for (let i = 0; i < pCands.length; i++) {
                if (pCands[i].innerText.trim()) {
                   rawText = pCands[i].innerText.trim();
                   break;
                }
             }
          }

          if (rawText) {
             if (/^\d{2}:\d{2}:\d{2}$/.test(rawText)) {
                const pts = rawText.split(':');
                const h = parseInt(pts[0], 10), m = parseInt(pts[1], 10), s = parseInt(pts[2], 10);
                if (h === 0 && m === 0 && s > 0) timeframeRaw = `${s} сек`;
                else if (h === 0 && m > 0 && s === 0) timeframeRaw = `${m} мин`;
                else if (h === 0 && m > 0 && s > 0) timeframeRaw = `${m}м ${s}с`;
                else if (h > 0 && m === 0 && s === 0) timeframeRaw = `${h} час`;
                else timeframeRaw = rawText;
             } else if (/^([SMHsmhСМЧсмч])(\d+)$/i.test(rawText)) {
                const match = rawText.match(/^([SMHsmhСМЧсмч])(\d+)$/i);
                const letter = match[1].toUpperCase();
                const num = match[2];
                // Note: 'С', 'М', 'Ч' are Cyrillic characters here
                if (letter === 'S' || letter === 'С') timeframeRaw = `${num} сек`;
                else if (letter === 'M' || letter === 'М') timeframeRaw = `${num} мин`;
                else if (letter === 'H' || letter === 'Ч') timeframeRaw = `${num} час`;
             } else {
                timeframeRaw = rawText;
             }
          }
          let timeframe = timeframeRaw;

          // STEP 2: RUN AI ANALYSIS
          safeSendMessage({ 
            type: 'REQUEST_AI_SIGNAL', 
            payload: { chartData: cleanChart, timeframe } 
          }, (response) => {
            console.log('[NMNH] Response received:', response ? response.status : 'NULL');
            
            const root = document.getElementById('ultra-terminal-root');
            if (!root || !root.shadowRoot) return;
            const sr = root.shadowRoot;

            const finalizeUI = (resp) => {
              const r_srDir = sr.getElementById('sr-direction');
              const r_srExp = sr.getElementById('sr-expiration');
              const r_srConf = sr.getElementById('sr-confidence');
              const r_srFill = sr.getElementById('sr-conf-fill');
              const r_srGen = sr.getElementById('sr-gen');
              const r_srContent = sr.getElementById('sr-content');
              const r_srPreview = sr.getElementById('sr-preview');

              // Clean up
              document.querySelectorAll('.sr-scanner-global').forEach(el => el.remove());
              state.isGeneratingSignal = false;

              if (resp && resp.status === 'SUCCESS') {
                const { decision, confidence } = resp.data;
                console.log('[NMNH] Update SUCCESS UI:', decision);

                if (r_srGen) r_srGen.style.display = 'none';
                if (r_srContent) r_srContent.style.display = 'block';
                if (r_srPreview) r_srPreview.style.display = 'block';

                if (r_srDir) {
                  const dMap = { 'BUY': 'КУПИТЬ', 'SELL': 'ПРОДАТЬ', 'WAIT': 'ОЖИДАНИЕ' };
                  r_srDir.innerText = dMap[decision] || 'ОЖИДАНИЕ';
                  r_srDir.className = `sr-badge ${decision.toLowerCase()}`;
                }
                if (r_srExp) r_srExp.innerText = timeframeRaw || '-- мин';
                
                const cValue = confidence || 0.85;
                const cPct = (cValue * 100).toFixed(1);

                if (r_srConf) r_srConf.innerText = `${cPct}%`;
                if (r_srFill) {
                  r_srFill.style.width = `${cPct}%`;
                  // Adaptive color logic
                  let color = '#ef4444'; // Red
                  if (cValue >= 0.75) color = '#22c55e'; // Green
                  else if (cValue >= 0.50) color = '#f59e0b'; // Amber/Yellow
                  
                  r_srFill.style.backgroundColor = color;
                  r_srFill.style.boxShadow = `0 0 10px ${color}44`;
                }

                state.signals.unshift({ asset: state.asset, type: decision, conf: Math.round(cValue * 100) });
                state.signals = state.signals.slice(0, 3);
              } else {
                console.log('[NMNH] Update NON-SUCCESS UI:', resp ? resp.status : 'NULL');
                if (r_srGen) r_srGen.style.display = 'none';
                if (r_srContent) r_srContent.style.display = 'block';
                if (r_srPreview) r_srPreview.style.display = 'none'; // Hide preview on error/lock

                if (r_srDir) {
                  if (resp && resp.status === 'LOCKED') {
                    r_srDir.innerText = 'БЛОК';
                    r_srDir.className = 'sr-badge wait';
                  } else {
                    r_srDir.innerText = 'ОШИБКА';
                    r_srDir.className = 'sr-badge';
                  }
                }
                
                if (r_srConf) r_srConf.innerText = '0%';
                if (r_srFill) r_srFill.style.width = '0%';
                if (r_srExp) r_srExp.innerText = '-- мин';
              }

              renderAISignals();
              sigBtn.disabled = false;
              sigBtn.style.pointerEvents = 'auto';
              sigBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                </svg>
                GET AI SIGNAL
              `;
            };

            if (response && response.status === 'SUCCESS') {
               // Analysis feel delay
               setTimeout(() => finalizeUI(response), 4000);
            } else {
               // Immediate feedback for errors/locks
               finalizeUI(response);
            }
          });
        });
      };
    }
 
  // Helper: Render AI Signals List (Hoisted to main scope)
  function renderAISignals() {
    const root = document.getElementById('ultra-terminal-root');
    if (!root || !root.shadowRoot) return;
    const container = root.shadowRoot.getElementById('ai-signals-list-items');
    if (!container) return;

    if (state.signals.length === 0 && !state.isGeneratingSignal) {
      container.innerHTML = `
        <div style="text-align:center; padding:30px 0; color:#4a5568; font-size:11px; font-weight:800; letter-spacing:0.05em; animation:fadeIn 0.5s ease;">
          ОЖИДАНИЕ СИГНАЛОВ...
        </div>
      `;
      return;
    }

    let html = '';
    
    // Generating row
    if (state.isGeneratingSignal) {
      html += `
        <div class="signal-item generating">
          <div class="signal-item-name">${state.asset}</div>
          <div class="signal-item-badge buy" style="opacity:0.5; animation:pulse 1s infinite">AI ANALYZING</div>
          <div class="signal-item-conf-bar">
            <div class="signal-item-conf-fill" style="width:100%; background: linear-gradient(90deg, transparent, #3b82f6, transparent); background-size: 200% 100%; animation: barFlow 1s infinite linear;"></div>
          </div>
          <div class="signal-item-pct">...</div>
        </div>
      `;
    }

    state.signals.forEach(sig => {
      const type = sig.type.toUpperCase();
      const badgeClass = type === 'BUY' ? 'buy' : 'sell';
      const color = type === 'BUY' ? '#22c55e' : '#ef4444';
      
      html += `
        <div class="signal-item">
          <div class="signal-item-name">${sig.asset}</div>
          <div class="signal-item-badge ${badgeClass}">${type}</div>
          <div class="signal-item-conf-bar">
            <div class="signal-item-conf-fill" style="width:${sig.conf}%; background:${color}"></div>
          </div>
          <div class="signal-item-pct">${sig.conf}%</div>
        </div>
      `;
    });

    container.innerHTML = html;
  }

    // Initial render & Sync Persistence from Background
    safeSendMessage({ type: 'GET_STATE' }, (res) => {
      if (res && res.status === 'SUCCESS' && res.data) {
        if (res.data.isVerified !== undefined) state.isVerified = res.data.isVerified;
        if (res.data.aiSignals) state.signals = res.data.aiSignals;
        if (res.data.isTrading !== undefined) state.isTrading = res.data.isTrading;
        chrome.storage.local.get([], (localres) => {
          if (state.isTrading) createSessionWindow(); 
          updateUI();
        });
        if (res.data.timeoutEndTime !== undefined) state.timeoutEndTime = res.data.timeoutEndTime;
        if (res.data.session) {
          if (res.data.session.processed && Array.isArray(res.data.session.processed)) {
            res.data.session.processed.forEach(sig => processedTrades.add(sig));
          }
          state.account.wins = res.data.session.wins || 0;
          state.account.losses = res.data.session.losses || 0;
          state.account.trades = state.account.wins + state.account.losses;
          state.account.winRate = state.account.trades > 0 
            ? (state.account.wins / state.account.trades) * 100 : 0;
        }
        updateUI();
      }
      renderAISignals();
    });

    // Helper: Client-side Cropping
    async function cropScreenshot(dataUrl, area) {
      return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement('canvas');
          canvas.width = area.w;
          canvas.height = area.h;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, area.x, area.y, area.w, area.h, 0, 0, area.w, area.h);
          resolve(canvas.toDataURL('image/jpeg', 0.85));
        };
        img.src = dataUrl;
      });
    }

    // Strategy cards
    shadow.querySelectorAll('.strategy-card').forEach(card => {
      card.addEventListener('click', () => {
        shadow.querySelectorAll('.strategy-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
      });
    });

    // Start Session Button
    const startBtn = shadow.getElementById('full-start-trading');
    if (startBtn) {
      startBtn.onclick = () => {
        if (!state.isTrading) {
          // EXTREMELY IMPORTANT: Clear any pending detections and re-sync everything currently on screen
          // This avoids "phantom trades" where old losses appearing on screen are counted as new.
          flushScrapers();
          
          state.isTrading = true;
          safeSendMessage({ type: 'RESET_SESSION' });
          safeSendMessage({ type: 'START_TRADING' });
          createSessionWindow();
          updateUI();
          
          // Flash button success
          startBtn.style.background = '#22c55e';
          startBtn.innerText = 'STARTED!';
          setTimeout(() => {
             startBtn.style.background = '';
             startBtn.innerText = 'START SESSION';
             updateUI();
          }, 1500);
        }
      };
    }

    // Lock screen
    if (!state.isVerified) {
      const vCheck = shadow.getElementById('v-check-refresh');
      const tgBtn = shadow.getElementById('lock-tg-btn');
      const debugBtn = shadow.getElementById('v-debug');

      if (tgBtn) tgBtn.onclick = () => window.open(state.tgBot);
      
      const vRedirect = shadow.getElementById('v-verify-redirect');
      if (vRedirect) {
        vRedirect.onclick = () => {
          window.open('https://t.me/moneyhoney7_bot');
        };
      }

      // Auto-check on load (if not verified)
      if (!state.isVerified && state.userUID && state.userUID !== 'Searching...') {
         safeSendMessage({ 
           type: 'VERIFY_UID', 
           payload: { uid: state.userUID } 
         }, (res) => {
           if (res && res.isVerified) {
             state.isVerified = true;
             chrome.storage.local.set({ ultra_verified: true });
             // Re-render panel if verified to unlock
             createUltraPanel();
           }
         });
      }

      if (debugBtn) debugBtn.onclick = () => {
        state.isVerified = true;
        chrome.storage.local.set({ ultra_verified: true });
        const ls = shadow.getElementById('lock-screen');
        if (ls) ls.remove();
      };
    }
  }

  /* ─── Gauge Animation ────────────────────────── */
  function animateGauges(shadow) {
    const CIRC = 251.33;
    const pPct = Math.min(100, Math.max(0, state.risk.profit || 0));
    const lPct = Math.min(100, Math.max(0, state.risk.loss || 0));
    const dashP = CIRC - (CIRC * Math.abs(pPct) / 100);
    const dashL = CIRC - (CIRC * Math.abs(lPct) / 100);

    // Full gauges
    const pG = shadow.getElementById('profit-gauge');
    const lG = shadow.getElementById('loss-gauge');
    if (pG) pG.style.strokeDashoffset = dashP;
    if (lG) lG.style.strokeDashoffset = dashL;

    // Mini gauges
    const mpG = shadow.getElementById('mini-profit-gauge');
    const mlG = shadow.getElementById('mini-loss-gauge');
    if (mpG) mpG.style.strokeDashoffset = dashP;
    if (mlG) mlG.style.strokeDashoffset = dashL;
  }

  /* ─── Signal Bar Animation ───────────────────── */
  function animateSignalBars(shadow) {
    shadow.querySelectorAll('.sig-bar-fill').forEach(el => {
      el.style.width = (el.dataset.conf || 0) + '%';
    });
  }

  function showProfitAlert(sr) {
    if (sr.getElementById('profit-target-modal')) return;
    const overlay = document.createElement('div');
    overlay.id = 'profit-target-modal';
    overlay.style.cssText = `
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(2, 6, 23, 0.85); backdrop-filter: blur(12px);
      z-index: 1000; display: flex; align-items: center; justify-content: center;
      transition: 0.4s ease-out; border-radius: 24px;
    `;
    
    overlay.innerHTML = `
      <style>
        .p-modal {
          width: 280px; background: hsla(222, 47%, 12%, 0.95);
          border: 1px solid hsla(145, 63%, 46%, 0.3);
          border-radius: 24px; padding: 24px; text-align: center;
          box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 30px hsla(145, 63%, 46%, 0.1);
          animation: modalSlideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
        }
        @keyframes modalSlideUp { from { opacity: 0; transform: translateY(20px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }
        .p-icon { font-size: 40px; margin-bottom: 16px; display: block; filter: drop-shadow(0 0 10px #22c55e); }
        .p-title { font-size: 18px; font-weight: 800; color: #fff; margin-bottom: 8px; font-family: 'Outfit', sans-serif; }
        .p-desc { font-size: 11px; color: #94a3b8; line-height: 1.5; margin-bottom: 24px; }
        .p-btn-fix { 
          width: 100%; padding: 12px; background: #22c55e; color: #fff; 
          border: none; border-radius: 12px; font-weight: 700; font-size: 12px;
          cursor: pointer; transition: 0.2s; margin-bottom: 10px;
        }
        .p-btn-fix:hover { background: #16a34a; transform: translateY(-1px); }
        .p-btn-cont { 
          width: 100%; padding: 10px; background: transparent; color: #64748b; 
          border: 1px solid #1e293b; border-radius: 12px; font-weight: 600; font-size: 11px;
          cursor: pointer; transition: 0.2s;
        }
        .p-btn-cont:hover { color: #f1f5f9; background: rgba(255,255,255,0.03); }
      </style>
      <div class="p-modal">
        <span class="p-icon">🎯</span>
        <div class="p-title">ЦЕЛЬ ДОСТИГНУТА!</div>
        <div class="p-desc">Вы заработали +10% к балансу за эту сессию. Рекомендуем зафиксировать прибыль и сделать перерыв.</div>
        <button class="p-btn-fix" id="p-fix">ЗАФИКСИРОВАТЬ ПРИБЫЛЬ</button>
        <button class="p-btn-cont" id="p-cont">ПРОДОЛЖИТЬ ТОРГОВЛЮ</button>
      </div>
    `;

    sr.appendChild(overlay);

    sr.getElementById('p-fix').onclick = () => {
      safeSendMessage({ type: 'STOP_TRADING' });
      overlay.style.opacity = '0';
      setTimeout(() => overlay.remove(), 400);
    };
    sr.getElementById('p-cont').onclick = () => {
      overlay.style.opacity = '0';
      setTimeout(() => overlay.remove(), 400);
    };
  }



  /* ─── Trade Emit ─────────────────────────────── */
  function emitTrade(direction, btn) {
    btn.style.filter = 'brightness(1.5)';
    setTimeout(() => { btn.style.filter = ''; }, 200);
    safeSendMessage({ type: 'MANUAL_TRADE', payload: { direction, timestamp: Date.now() } });
  }

  /* ─── Panel Toggle ───────────────────────────── */
  function togglePanel(force) {
    const root = document.getElementById('ultra-terminal-root');
    if (!root) return;
    state.isPanelOpen = force !== undefined ? force : !state.isPanelOpen;
    chrome.storage.local.set({ ultra_panel_open: state.isPanelOpen });
    root.shadowRoot.host.classList.toggle('open', state.isPanelOpen);
  }

  /* ─── UI Update ──────────────────────────────── */
  function updateUI() {
    const root = document.getElementById('ultra-terminal-root');
    if (!root) return;
    const sr = root.shadowRoot;

    const assetN = sr.getElementById('ui-asset-name');
    const balance = sr.getElementById('ui-balance');
    const payout = sr.getElementById('ui-payout');
    const lockUID = sr.getElementById('lock-uid');
    // Sync action button area
    const actionFooter = sr.querySelector('.action-footer');
    if (actionFooter) {
       const isCurrentlyLocked = !!sr.getElementById('v-verify-redirect');
       // If what's on screen doesn't match current state, re-render that block
       if (isCurrentlyLocked && state.isVerified || !isCurrentlyLocked && !state.isVerified) {
          actionFooter.innerHTML = !state.isVerified ? `
            <div class="v-lock-container">
              <button class="action-btn v-locked-btn" id="v-verify-redirect">
                <span class="v-lock-icon">🔒</span>
                ПРОЙТИ ВЕРИФИКАЦИЮ
              </button>
              <div class="v-lock-hint">Подтвердите ID <b id="lock-uid">${state.userUID}</b> в боте Академии</div>
            </div>
          ` : `
            <button class="action-btn" id="full-start-trading">
              START SESSION
            </button>
          `;
          // Re-bind just these specific buttons
          const vRedir = sr.getElementById('v-verify-redirect');
          if (vRedir) vRedir.onclick = () => window.open('https://t.me/moneyhoney7_bot');
          
          const sBtn = sr.getElementById('full-start-trading');
          if (sBtn) {
            sBtn.onclick = () => {
              if (!state.isTrading) {
                flushScrapers();
                state.isTrading = true;
                safeSendMessage({ type: 'RESET_SESSION' });
                safeSendMessage({ type: 'START_TRADING' });
                createSessionWindow();
                updateUI();
              }
            };
          }
       }
    }
    let uiTradesCount = sr.getElementById('ui-trades-count');

    if (assetN) assetN.innerText = state.asset;
    if (payout && state.payout) payout.innerText = state.payout;
    if (balance) balance.innerText = `$${state.account.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    if (lockUID) lockUID.innerText = state.userUID;

    if (uiTradesCount) uiTradesCount.innerText = `${state.account.trades} trades`;
 
    const winrateEl = sr.getElementById('ui-winrate');
    if (winrateEl) winrateEl.innerText = `${state.account.winRate.toFixed(1)}%`;

    const pnlValEl = sr.getElementById('ui-pnl-val');
    const pnlSignEl = sr.getElementById('ui-pnl-sign');

    // Use session PnL for the main display if trading, or daily PnL if not
    // RESILIENCE: If dailyPnl is suspiciously large (> 2k) and balance is small, it's likely corrupted.
    const rawPnl = state.account.pnl;
    const isPnlCorrupted = Math.abs(rawPnl) > 3000 && state.account.balance < 1000;
    const cleanDailyPnl = isPnlCorrupted ? 0 : rawPnl;

    const currentPnl = state.isTrading 
      ? (state.account.balance - (state.account.sessionStartBalance || state.account.balance)) 
      : cleanDailyPnl;
    
    if (pnlValEl) {
      const sign = currentPnl >= 0 ? '+' : '-';
      pnlValEl.innerText = `${sign}$${Math.abs(currentPnl).toFixed(2)} today`;
      pnlValEl.parentElement.style.color = currentPnl >= 0 ? '#22c55e' : '#ef4444';
    }
    if (pnlSignEl) {
      pnlSignEl.innerText = currentPnl >= 0 ? '▲' : '▼';
    }

    // Sync floating session window if exists
    if (sessionWindowRoot) {
      const sw = sessionWindowRoot.shadowRoot;
      const swWins = sw.getElementById('sessionWins');
      const swLosses = sw.getElementById('sessionLosses');
      if (swWins) swWins.textContent = state.account.wins;
      if (swLosses) swLosses.textContent = state.account.losses;
    }
 
    // Risk Management Calculations (Relative to Session Start Balance)
    const currentBalance = state.account.balance;
    const sessionStart = state.account.sessionStartBalance || (currentBalance - state.account.pnl);
    
    // SANITY CHECK: If balance is 0 or extremely low while we have a sessionStart, 
    // it's likely a temporary state before DOM sync. Reset risk to 0 to avoid "100% loss" jump.
    if (currentBalance === 0 && sessionStart !== 0) {
      state.risk.profit = 0;
      state.risk.loss = 0;
    } else {
      // Profit Target (10%) and Loss Limit (5%)
      const profitTarget = Math.max(10, sessionStart * 0.10) || 1000;
      const lossLimitTarget = Math.max(10, sessionStart * 0.05) || 500;
      
      const sessPnL = currentBalance - sessionStart;
      
      state.risk.profit = (sessPnL > 0) ? Math.min(100, (sessPnL / profitTarget) * 100) : 0;
      state.risk.loss = (sessPnL < 0) ? Math.min(100, (Math.abs(sessPnL) / lossLimitTarget) * 100) : 0;
    }

    // Mini dock updates (Always)
    const miniProfNum = sr.getElementById('mini-profit-num');
    const miniLossNum = sr.getElementById('mini-loss-num');
     if (miniProfNum) {
       miniProfNum.innerText = `${state.risk.profit.toFixed(0)}%`;
       miniProfNum.classList.toggle('has-val', state.risk.profit > 0);
     }
     if (miniLossNum) {
       miniLossNum.innerText = `${state.risk.loss.toFixed(0)}%`;
       miniLossNum.classList.toggle('has-val', state.risk.loss > 0);
     }
    
    animateGauges(sr);

    if (!state.isPanelOpen) return;
 
    const profNum = sr.getElementById('ui-profit-num');
    const profSub = sr.getElementById('ui-profit-sub');
    const lossNum = sr.getElementById('ui-loss-num');
    const lossSub = sr.getElementById('ui-loss-sub');
 
    if (profNum) profNum.innerText = `${state.risk.profit.toFixed(0)}%`;
    if (profSub) profSub.innerText = `+$${Math.max(0, sessPnL).toFixed(2)} / $${profitTarget.toFixed(0)}`;
    if (lossNum) lossNum.innerText = `${state.risk.loss.toFixed(0)}%`;
    if (lossSub) lossSub.innerText = `-$${Math.max(0, -sessPnL).toFixed(2)} / $${lossLimitTarget.toFixed(0)}`;
 
    // Profit Alert Notification
    if (sessPnL >= profitTarget && !state.profitAlertShown && state.isTrading) {
      state.profitAlertShown = true;
      showProfitAlert(sr);
    }
 
    animateGauges(sr);

    // Sync Signal Button Visual State
    const sigBtn = sr.getElementById('ultra-btn-signal');
    if (sigBtn && !state.isGeneratingSignal) {
      const now = Date.now();
      if (now < state.signalLockUntil) {
        const diff = state.signalLockUntil - now;
        const mins = Math.floor(diff / 60000);
        const secs = Math.floor((diff % 60000) / 1000);
        const timeStr = `${mins}:${secs.toString().padStart(2, '0')}`;
        
        sigBtn.disabled = true;
        sigBtn.style.pointerEvents = 'none'; // Hard disable
        sigBtn.style.opacity = '0.5';
        sigBtn.style.filter = 'grayscale(1)';
        sigBtn.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          ACTIVE (${timeStr})
        `;
      } else if (!state.isTrading) {
        sigBtn.disabled = false;
        sigBtn.style.pointerEvents = 'auto';
        sigBtn.style.opacity = '0.7';
        sigBtn.style.filter = 'grayscale(0.3)';
        sigBtn.innerText = 'START SESSION';
      } else {
        sigBtn.disabled = false;
        sigBtn.style.pointerEvents = 'auto';
        sigBtn.style.opacity = '';
        sigBtn.style.filter = '';
        sigBtn.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
          </svg>
          GET AI SIGNAL
        `;
      }
    }

    // Show payout dollar amount only (e.g. +$1.92), % is already in the badge
    const changeEl = sr.getElementById('ui-asset-change');
    if (changeEl && state.payoutAmount) {
      const dollarMatch = state.payoutAmount.match(/\+?\$[\d,.]+/);
      changeEl.innerText = dollarMatch ? dollarMatch[0] : state.payoutAmount;
      changeEl.style.color = '#22c55e';
    }


  }

  /* ─── Trigger Button ─────────────────────────── */
  function stitchUltraUI() {
    const triggerId = 'ultra-pro-trigger';
    const existingTrigger = document.getElementById(triggerId);
    
    // Find target
    const target =
      document.querySelector('.right-sidebar nav > ul') ||
      document.querySelector('.sidebar-right') ||
      document.querySelector('#put-call-buttons-chart-1') ||
      document.querySelector('.sidebar-right-holder') ||
      document.querySelector('.sidebar-right__content');
      
    if (!target) return;

    // Check if trigger is actually inside the current target
    if (existingTrigger) {
      if (target.contains(existingTrigger)) return;
      // If it exists but NOT in target (detached or moved), remove it to re-add
      existingTrigger.remove();
    }

    const li = document.createElement(target.tagName === 'UL' ? 'li' : 'div');
    li.id = triggerId;
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
    li.onclick = (e) => { 
      e.stopPropagation();
      createUltraPanel(); 
      setTimeout(() => togglePanel(), 50); 
    };
    target.prepend(li);
    console.log('[NMNH] UI Stitched successfully');
  }

  // Admin Debug Bypass
  window.NMNH_DEBUG_UNLOCK = () => {
    state.isVerified = true;
    const root = document.getElementById('ultra-terminal-root');
    if (root && root.shadowRoot) {
      const ls = root.shadowRoot.getElementById('lock-screen');
      if (ls) {
        ls.style.opacity = '0';
        setTimeout(() => ls.remove(), 500);
        console.log('[NMNH] Admin Bypass Active ✅');
      }
    }
  };

  /* ─── Floating Session Mini-Window ────────────── */
  let sessionWindowRoot = null;
  let sessionTimer = null;

  function createSessionWindow(restoredStartTime = null) {
    if (sessionWindowRoot) return;
    
    // sessionStartTime is declared globally at line 310
    if (restoredStartTime) {
      sessionStartTime = restoredStartTime;
    } else if (!sessionStartTime) {
      sessionStartTime = Date.now();
    }

    sessionWindowRoot = document.createElement('div');
    sessionWindowRoot.id = 'nmnh-session-window';
    if (document.body) document.body.appendChild(sessionWindowRoot);

    const shadow = sessionWindowRoot.attachShadow({ mode: 'open' });
    shadow.innerHTML = `
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

        :host {
          position: fixed;
          top: 16px;
          right: 16px;
          z-index: 2147483647;
          font-family: 'Outfit', 'Inter', system-ui, sans-serif;
        }

        .session-panel {
          width: 240px;
          background: rgba(13, 17, 28, 0.85);
          backdrop-filter: blur(25px) saturate(160%);
          -webkit-backdrop-filter: blur(25px) saturate(160%);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 20px;
          padding: 16px;
          box-shadow: 
            0 24px 60px rgba(0, 0, 0, 0.6),
            0 0 0 1px rgba(255, 255, 255, 0.03);
          cursor: grab;
          user-select: none;
          animation: sessionSlideIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
        }

        .session-panel:active { cursor: grabbing; }

        @keyframes sessionSlideIn {
          from { opacity: 0; transform: translateY(-12px) scale(0.95); }
          to   { opacity: 1; transform: translateY(0) scale(1); }
        }

        .session-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
          padding-bottom: 10px;
          border-bottom: 1px solid hsla(210, 20%, 100%, 0.06);
        }

        .session-title {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 10px;
          font-weight: 700;
          color: hsla(210, 20%, 100%, 0.55);
          letter-spacing: 1px;
          text-transform: uppercase;
          font-family: 'Inter', system-ui, sans-serif;
        }

        .session-dot {
          width: 6px; height: 6px;
          border-radius: 50%;
          background: hsl(262, 83%, 67%);
          box-shadow: 0 0 8px hsl(262, 83%, 67%);
          animation: dotPulse 1.6s ease-in-out infinite;
        }

        @keyframes dotPulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(0.7); }
        }

        .close-btn {
          width: 20px; height: 20px;
          border: none;
          border-radius: 6px;
          background: hsla(210, 20%, 100%, 0.06);
          color: hsla(210, 20%, 100%, 0.4);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
          padding: 0;
          font-size: 12px;
          line-height: 1;
        }

        .close-btn:hover {
          background: hsla(0, 72%, 57%, 0.15);
          color: hsl(0, 72%, 57%);
        }

        .timer-row {
          text-align: center;
          margin-bottom: 12px;
        }

        .timer-value {
          font-size: 32px;
          font-weight: 800;
          color: #f8fafc;
          letter-spacing: -0.5px;
          font-family: 'Inter', monospace;
          line-height: 1;
        }

        .timer-label {
          font-size: 8px;
          color: hsla(210, 20%, 100%, 0.35);
          letter-spacing: 1.5px;
          text-transform: uppercase;
          margin-top: 3px;
          font-family: 'Inter', system-ui, sans-serif;
        }

        .stats-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
        }

        .stat-box {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.05);
          border-radius: 14px;
          padding: 14px 10px;
          text-align: center;
          transition: 0.2s;
        }

        .stat-box.wins {
          border-color: rgba(34, 197, 94, 0.15);
          background: rgba(34, 197, 94, 0.02);
        }

        .stat-box.losses {
          border-color: rgba(239, 68, 68, 0.15);
          background: rgba(239, 68, 68, 0.02);
        }

        .stat-num {
          font-size: 28px;
          font-weight: 800;
          line-height: 1;
          font-family: 'Inter', system-ui, sans-serif;
        }

        .stat-num.green { color: #22c55e; text-shadow: 0 0 15px rgba(34, 197, 94, 0.3); }
        .stat-num.red   { color: #ef4444; text-shadow: 0 0 15px rgba(239, 68, 68, 0.3); }

        .stat-label {
          font-size: 8.5px;
          color: rgba(255, 255, 255, 0.4);
          letter-spacing: 0.8px;
          text-transform: uppercase;
          margin-top: 6px;
          font-weight: 700;
          font-family: 'Inter', system-ui, sans-serif;
        }
      </style>

      <div class="session-panel" id="sessionPanel">
        <div class="session-header">
          <div class="session-title">
            <div class="session-dot"></div>
            СЕССИЯ
          </div>
          <button class="close-btn" id="closeSession" title="Закрыть">✕</button>
        </div>

        <div class="timer-row">
          <div class="timer-value" id="sessionTime">00:00:00</div>
          <div class="timer-label">ВРЕМЯ СЕССИИ</div>
        </div>

        <div class="stats-row">
          <div class="stat-box wins">
            <div class="stat-num green" id="sessionWins">0</div>
            <div class="stat-label">УСПЕШНЫХ</div>
          </div>
          <div class="stat-box losses">
            <div class="stat-num red" id="sessionLosses">0</div>
            <div class="stat-label">ПРОИГРАННЫХ</div>
          </div>
        </div>
      </div>
    `;

    // Close button
    const closeBtn = shadow.getElementById('closeSession');
    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeSessionWindow();
      safeSendMessage({ type: 'STOP_TRADING' });
    });

    // Drag functionality
    const panel = shadow.getElementById('sessionPanel');
    let isDragging = false;
    let dragOffsetX = 0, dragOffsetY = 0;

    panel.addEventListener('mousedown', (e) => {
      if (e.target === closeBtn) return;
      isDragging = true;
      dragOffsetX = e.clientX - sessionWindowRoot.getBoundingClientRect().left;
      dragOffsetY = e.clientY - sessionWindowRoot.getBoundingClientRect().top;
      panel.style.cursor = 'grabbing';
    });

    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      const x = e.clientX - dragOffsetX;
      const y = e.clientY - dragOffsetY;
      sessionWindowRoot.style.left = x + 'px';
      sessionWindowRoot.style.top = y + 'px';
      sessionWindowRoot.style.right = 'auto';
    });

    document.addEventListener('mouseup', () => {
      if (isDragging) {
        isDragging = false;
        if (panel) panel.style.cursor = 'grab';
        
        // Persist coordinates
        const rect = sessionWindowRoot.getBoundingClientRect();
        chrome.storage.local.set({ 
          nmnh_session_pos: { top: rect.top, left: rect.left } 
        });
      }
    });

    // Restore coordinates if available
    chrome.storage.local.get(['nmnh_session_pos'], (res) => {
      if (res.nmnh_session_pos && sessionWindowRoot) {
        sessionWindowRoot.style.top = res.nmnh_session_pos.top + 'px';
        sessionWindowRoot.style.left = res.nmnh_session_pos.left + 'px';
        sessionWindowRoot.style.right = 'auto';
      }
    });

    // Start stats loop
    if (restoredStartTime) {
      sessionStartTime = restoredStartTime;
    } else if (!sessionStartTime) {
      sessionStartTime = Date.now();
    }
    
    sessionReadyForTrades = false; 
    syncProcessedTrades(); // Critical: capture existing history
    setTimeout(() => { sessionReadyForTrades = true; }, 5000); // 5s lock to avoid phantoms
    
    sessionTimer = setInterval(updateSessionTimer, 1000);
    updateSessionTimer();
    updateSessionStats();
  }

  function updateSessionTimer() {
    if (!sessionWindowRoot || !sessionStartTime) return;
    const shadow = sessionWindowRoot.shadowRoot;
    if (!shadow) return;

    const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
    const h = String(Math.floor(elapsed / 3600)).padStart(2, '0');
    const m = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0');
    const s = String(elapsed % 60).padStart(2, '0');

    const timerEl = shadow.getElementById('sessionTime');
    if (timerEl) timerEl.textContent = `${h}:${m}:${s}`;
  }

  function updateSessionStats() {
    if (!sessionWindowRoot || !sessionWindowRoot.shadowRoot) return;
    const shadow = sessionWindowRoot.shadowRoot;
    
    // IDs in the template are 'sessionWins' and 'sessionLosses'
    const winsEl = shadow.getElementById('sessionWins');
    const lossesEl = shadow.getElementById('sessionLosses');
    
    if (winsEl) winsEl.textContent = state.account.wins;
    if (lossesEl) lossesEl.textContent = state.account.losses;
    
    // Safety check for other potential IDs
    const sw = shadow.getElementById('s-wins');
    const sl = shadow.getElementById('s-losses');
    if (sw) sw.textContent = state.account.wins;
    if (sl) sl.textContent = state.account.losses;

    // Trigger full UI refresh to ensure everything is in sync
    updateUI();
  }

  function closeSessionWindow() {
    if (sessionTimer) { clearInterval(sessionTimer); sessionTimer = null; }
    if (sessionWindowRoot) {
      const shadow = sessionWindowRoot.shadowRoot;
      if (shadow) {
        const panel = shadow.getElementById('sessionPanel');
        if (panel) {
          panel.style.animation = 'none';
          panel.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
          panel.style.opacity = '0';
          panel.style.transform = 'translateY(-8px) scale(0.95)';
        }
      }
      setTimeout(() => {
        if (sessionWindowRoot && sessionWindowRoot.parentNode) {
          sessionWindowRoot.parentNode.removeChild(sessionWindowRoot);
        }
        sessionWindowRoot = null;
        sessionStartTime = null;
        sessionReadyForTrades = false;
      }, 280);
    }
  }

  function safeSendMessage(msg, callback) {
    try {
      if (!chrome.runtime || !chrome.runtime.id) return;
      chrome.runtime.sendMessage(msg, (resp) => {
        if (chrome.runtime.lastError) {
          if (chrome.runtime.lastError.message.includes('Extension context invalidated')) {
             return;
          }
          if (callback) callback(null);
        } else {
          if (callback) callback(resp);
        }
      });
    } catch (e) {
      if (e.message.includes('Extension context invalidated')) {
        // Silent stop
      } else {
        console.error('[NMNH] Message Error:', e);
      }
    }
  }



  /* ─── Communication ──────────────────────────── */
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === 'EXTRACT_LOCAL_SIGNAL') {
      try {
        const trend = state.tickerPrices[state.asset]?.trend || 'up';
        const isUp = trend === 'up';

        sendResponse({
          decision: isUp ? 'BUY' : 'SELL',
          confidence: isUp ? 0.81 : 0.85,
          duration: 3,
          source: 'LOCAL_OTC_TREND'
        });
      } catch (err) {
        sendResponse({ decision: 'WAIT', confidence: 0.5, duration: 1 });
      }
      return true;
    } else if (msg.type === 'TOGGLE_TERMINAL') {
      createUltraPanel();
      setTimeout(() => togglePanel(msg.force), 50);
      sendResponse({ status: 'ACK' });
    } else if (msg.type === 'PRICE_UPDATE') {
      state.price = msg.payload.price;
      updateUI();
    } else if (msg.type === 'SESSION_UPDATE') {
      syncStateWithBackground(msg.payload);
    }
    else if (msg.type === 'GET_UI_CONTEXT') {
      sendResponse({
        balance: state.account.balance,
        price: state.price,
        asset: state.asset,
        lastUpdate: Date.now()
      });
    }
    else if (msg.type === 'OPEN_SESSION_WINDOW') {
      state.isTrading = true;
      state.profitAlertShown = false;
      createSessionWindow();
      togglePanel(true); // Open the expanded panel too
      updateUI();
      sendResponse({ status: 'ACK' });
    }
    else if (msg.type === 'CLOSE_SESSION_WINDOW') {
      closeSessionWindow();
      state.isTrading = false; // Sync local state
      state.profitAlertShown = false; // Reset alert
      updateUI();
      sendResponse({ status: 'ACK' });
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
    } else if (msg.type === 'GET_LOCAL_SIGNAL') {
      const signal = calculateLocalSignal();
      sendResponse({ status: 'SUCCESS', data: signal });
    } else if (msg.type === 'SESSION_UPDATE') {
    if (msg.payload) syncStateWithBackground(msg.payload);
    } else if (msg.type === 'VISUAL_CAPTURE_READY') {
      const root = document.getElementById('ultra-terminal-root');
      if (root && root.shadowRoot) {
        const srPreview = root.shadowRoot.getElementById('sr-preview');
        if (srPreview && msg.payload.screenshot) {
          srPreview.style.backgroundImage = `url(${msg.payload.screenshot})`;
          srPreview.style.display = 'block';
        }
      }
    }
    return true;
  });

  /* ─── Local Analytical Engine (OTC) ─────────── */
  function calculateLocalSignal() {
    if (lastPrices.length < 15) {
      return { decision: 'WAIT', reason: 'Collecting...', confidence: 0.5, duration: 3 };
    }

    const current = lastPrices[lastPrices.length - 1];
    const prev = lastPrices[lastPrices.length - 2];
    
    // SMA (10)
    const sma10 = lastPrices.slice(-10).reduce((a, b) => a + b, 0) / 10;
    
    // Momentum
    const momShort = current - lastPrices[lastPrices.length - 5];
    const momLong = current - lastPrices[lastPrices.length - 15];

    // RSI (14)
    let gains = 0, losses = 0;
    for (let i = lastPrices.length - 14; i < lastPrices.length; i++) {
        const diff = lastPrices[i] - lastPrices[i-1];
        if (diff >= 0) gains += diff;
        else losses -= diff;
    }
    const rs = losses === 0 ? 100 : gains / losses;
    const rsi = 100 - (100 / (1 + rs));

    // Decision Logic
    let decision = 'WAIT';
    let duration = 3;
    let confidence = 0.5;

    // 1. Extreme Zones (Overbought/Oversold) - FAST trades
    if (rsi < 30) {
      decision = 'BUY';
      confidence = 0.80 + (30 - rsi) / 150; 
      duration = rsi < 20 ? 1 : 2;
    } 
    else if (rsi > 70) {
      decision = 'SELL';
      confidence = 0.80 + (rsi - 70) / 150;
      duration = rsi > 80 ? 1 : 2;
    }
    // 2. Trend Zones - SLOwer trades
    else if (rsi < 45 && momShort > 0) {
      decision = 'BUY';
      confidence = 0.65 + (45 - rsi) / 200;
      duration = 3;
    }
    else if (rsi > 55 && momShort < 0) {
      decision = 'SELL';
      confidence = 0.65 + (rsi - 55) / 200;
      duration = 3;
    }
    // 3. Momentum Fallback
    else if (Math.abs(momLong) > 0.001) {
      decision = momLong > 0 ? 'BUY' : 'SELL';
      confidence = 0.60;
      duration = 5;
    }
    else {
      decision = 'WAIT';
      confidence = 0.50;
      duration = 2;
    }

    return {
      decision,
      reason: `RSI:${rsi.toFixed(0)} MOM:${momShort.toFixed(5)}`,
      confidence: Math.min(0.98, confidence),
      duration
    };
  }

  /* ─── Inject Custom Watermark ───────────────── */
  function injectWatermark() {
    if (document.getElementById('nmnh-watermark')) return;
    const header = document.querySelector('.site-header');
    if (!header) return;

    header.style.position = 'relative';

    const watermark = document.createElement('div');
    watermark.id = 'nmnh-watermark';
    watermark.style.cssText = `
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      color: rgba(255, 255, 255, 0.4);
      font-size: 14px;
      font-weight: 700;
      font-family: 'Inter', system-ui, sans-serif;
      letter-spacing: 0.5px;
      pointer-events: none;
      z-index: 999;
      white-space: nowrap;
      text-transform: uppercase;
      text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    `;
    watermark.innerHTML = `
      <style>
        @keyframes nmnhLinkPulse {
          0% { color: rgba(34, 197, 94, 0.7); text-shadow: 0 0 5px rgba(34,197,94,0.3); }
          50% { color: #22c55e; text-shadow: 0 0 12px rgba(34,197,94,0.8), 0 0 20px rgba(34,197,94,0.5); }
          100% { color: rgba(34, 197, 94, 0.7); text-shadow: 0 0 5px rgba(34,197,94,0.3); }
        }
        .nmnh-w-link {
          color: #22c55e;
          text-decoration: none;
          pointer-events: auto;
          transition: 0.2s;
          animation: nmnhLinkPulse 2.5s ease-in-out infinite;
        }
        .nmnh-w-link:hover {
          filter: brightness(1.3);
        }
      </style>
      📢 АВТОРСКИЙ СОФТ ОТ <a href="https://t.me/kaktotakxm" target="_blank" class="nmnh-w-link">@KAKTOTAKXM</a>
    `;
    
    header.appendChild(watermark);
  }

  /* ─── Admin Trade Cancellation Sync ─────────── */
  function initAdminCancelSync() {
    if (window.nmnhAdminSyncReady) return;
    window.nmnhAdminSyncReady = true;

    document.addEventListener('click', (e) => {
      const cancelBtn = e.target.closest('a.btn-warn[href*="cancel="]');
      if (cancelBtn) {
        e.preventDefault(); // Prevent page unload before script triggers
        
        const originalText = cancelBtn.innerText;
        cancelBtn.innerText = 'Syncing...';
        
        chrome.runtime.sendMessage({ type: 'DECREMENT_STATS' }, () => {
          console.log('[NMNH Admin] Trade cancelled. Decrementing loss counter.');
          window.location.href = cancelBtn.href; // Resume navigation safely
        });
      }
    });
  }

  /* ─── Bootstrap ──────────────────────────────── */
  function syncWithBackground() {
    return Promise.race([
      new Promise((resolve) => {
        safeSendMessage({ type: 'GET_STATE' }, (resp) => {
          if (resp && resp.status === 'SUCCESS') {
            syncStateWithBackground(resp.data);
            resolve(true);
          } else {
            resolve(false);
          }
        });
      }),
      new Promise((resolve) => setTimeout(() => resolve(false), 2000)) // 2s timeout failsafe
    ]);
  }

  async function init() {
    if (!document.body || state.isInitializing) return;
    state.isInitializing = true;
    
    try {
      // Each section is isolated to prevent one failure from stopping the whole script
      const isTop = window === window.top;
      
      // IMMEDIATE UI: Create everything BEFORE sync so there's zero delay
      try { stitchUltraUI(); } catch (e) { }
      if (isTop) {
        try { 
          if (!document.getElementById('ultra-terminal-root')) createUltraPanel(); 
        } catch (e) { }
        try { injectWatermark(); } catch (e) { }
        try { initAdminCancelSync(); } catch (e) { }
      }

      // Sync state from background (non-blocking for observer)
      const synced = await syncWithBackground();
      if (synced && isTop) {
         if (state.isTrading && !sessionWindowRoot) createSessionWindow();
      }

      // CRITICAL: ALWAYS start history observer regardless of sync status
      // This was the root cause of 0/0: if sync timed out, observer never started
      if (isTop) {
        try { 
          if (!state.historyObserverActive) initHistoryObserver(); 
        } catch (e) { 
          console.warn('[NMNH] Observer start failed, retrying...', e.message);
          setTimeout(initHistoryObserver, 1500);
        }
      }
      
      // Click outside to close (especially for locked mode)
      document.addEventListener('mousedown', (e) => {
        const root = document.getElementById('ultra-terminal-root');
        if (!root || !state.isPanelOpen) return;
        
        // If we are in locked mode, we want easy dismissal
        if (!state.isVerified) {
          const path = e.composedPath();
          if (!path.includes(root)) {
            togglePanel(false);
          }
        }
      }, { passive: true });

      try { updateMarketData(); } catch (e) { }

      // 1. Terminal Persistence (Already created above before sync)
    } finally {
      state.isInitializing = false;
    }
  }

  function syncStateWithBackground(s) {
    if (!s) return;
    
    // 1. Session Counts (Resilient to both Flat and Nested formats)
    const wins = s.wins !== undefined ? s.wins : (s.session ? s.session.wins : undefined);
    const losses = s.losses !== undefined ? s.losses : (s.session ? s.session.losses : undefined);
    const pnl = s.dailyPnl !== undefined ? s.dailyPnl : (s.session ? s.session.dailyPnl : (s.pnl !== undefined ? s.pnl : undefined));

    if (wins !== undefined) state.account.wins = wins;
    if (losses !== undefined) state.account.losses = losses;
    if (pnl !== undefined) state.account.pnl = pnl;
    
    // 2. Win Rate & Trade Count
    state.account.trades = state.account.wins + state.account.losses;
    state.account.winRate = state.account.trades > 0 
      ? (state.account.wins / state.account.trades) * 100 
      : 0;
      
    // 3. Trading Mode & Start Balance
    if (s.isTrading !== undefined) {
      const changed = state.isTrading !== s.isTrading;
      state.isTrading = s.isTrading;
      if (state.isTrading) createSessionWindow();
      else if (changed && !state.isTrading) closeSessionWindow();
    }
    if (s.sessionStartBalance !== undefined) state.account.sessionStartBalance = s.sessionStartBalance;
    if (s.sessionStartTime !== undefined) sessionStartTime = s.sessionStartTime;
    
    // Sync processed trades to avoid double counting on reload
    const processed = s.processed || (s.session ? s.session.processed : null);
    if (processed && Array.isArray(processed)) {
      processed.forEach(sig => processedTrades.add(sig));
    }
    
    // 4. Signal History
    if (s.aiSignals) {
      state.signals = s.aiSignals;
      renderAISignals();
    }

    // 5. Timeouts
    if (s.timeoutEndTime !== undefined) state.timeoutEndTime = s.timeoutEndTime;
    if (s.signalLockUntil !== undefined) state.signalLockUntil = s.signalLockUntil;

    // Trigger UI Refresh
    updateUI();
    updateSessionStats();
  }

  // FAST UI STITCHING — runs independently of init(), NOT blocked by 2s sync
  // This ensures button & watermark appear the INSTANT sidebar DOM loads
  const _uiLoop = setInterval(() => {
    if (!document.body) return;
    try { stitchUltraUI(); } catch(e) {}
    try { injectWatermark(); } catch(e) {}
    // Stop once both are placed
    if (document.getElementById('ultra-pro-trigger')) clearInterval(_uiLoop);
  }, 100);

  init();
  setInterval(init, 300);
  const observer = new MutationObserver(() => init());
  try {
    if (document.documentElement instanceof Node) {
      observer.observe(document.documentElement, { childList: true, subtree: true });
    }
  } catch (e) {
    console.warn('[NMNH] Root observer failed:', e.message);
  }

})();
