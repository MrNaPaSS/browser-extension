/**
 * NMNH Trading Robot — Popup Controller v2.1.0
 * Navigation & Settings Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initSettings();
  syncState();
  // Listen for real-time updates from background
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.type === 'PRICE_UPDATE') {
      const priceEl = document.getElementById('popupPrice');
      const assetEl = document.getElementById('popupAsset');
      if (priceEl) priceEl.textContent = msg.payload.price;
      if (assetEl) assetEl.textContent = `HUB · ${msg.payload.asset}`;
    }
  });
  // Periodic fallback sync
  setInterval(syncState, 2000);
});

/* ─── Navigation ────────────────────────────────────── */
function initNavigation() {
  const btnTerminal = document.getElementById('navTerminal');
  if (btnTerminal) {
    btnTerminal.onclick = () => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
          chrome.tabs.sendMessage(tabs[0].id, { type: 'TOGGLE_TERMINAL' }, () => {
             if (chrome.runtime.lastError) {
               console.warn('Terminal toggle failed: Injection may be blocked on this page.');
             } else {
               window.close();
             }
          });
        }
      });
    };
  }

  const btnDashboard = document.getElementById('navDashboard');
  if (btnDashboard) {
    btnDashboard.onclick = () => window.open('https://pocketoption.com/en/cabinet/');
  }

  const btnHistory = document.getElementById('navHistory');
  if (btnHistory) {
    btnHistory.onclick = () => window.open('https://pocketoption.com/en/cabinet/history/');
  }

  const btnSupport = document.getElementById('navSupport');
  if (btnSupport) {
    btnSupport.onclick = () => window.open('https://t.me/moneyhoney7_bot');
  }
}

/* ─── Settings ──────────────────────────────────────── */
function initSettings() {
  const masterToggle = document.getElementById('masterRobotToggle');
  const strategySelect = document.getElementById('strategySelect');
  const riskSegments = document.querySelectorAll('.risk-seg');

  if (masterToggle) {
    masterToggle.onchange = () => {
      const mode = strategySelect ? strategySelect.value : 'hft-trend';
      const type = masterToggle.checked ? 'START_TRADING' : 'STOP_TRADING';
      chrome.runtime.sendMessage({ type, payload: { mode } });
      updateStatusUI(masterToggle.checked);
    };
  }

  if (strategySelect) {
    strategySelect.onchange = () => {
      if (masterToggle && masterToggle.checked) {
        chrome.runtime.sendMessage({ type: 'START_TRADING', payload: { mode: strategySelect.value } });
      }
    };
  }

  riskSegments.forEach(seg => {
    seg.onclick = () => {
      riskSegments.forEach(s => s.classList.remove('active'));
      seg.classList.add('active');
    };
  });

  const btnReset = document.getElementById('btnResetSession');
  if (btnReset) {
    btnReset.onclick = () => {
      if (confirm('Reset session statistics?')) {
        chrome.runtime.sendMessage({ type: 'RESET_SESSION' }, () => syncState());
      }
    };
  }
}

/* ─── State Sync ────────────────────────────────────── */
function syncState() {
  try {
    chrome.runtime.sendMessage({ type: 'GET_STATE' }, response => {
      if (chrome.runtime.lastError || !response || response.status !== 'SUCCESS') return;
      
      const state = response.data;
      const masterToggle = document.getElementById('masterRobotToggle');
      const balanceEl = document.getElementById('footerBalance');
      const wlEl = document.getElementById('footerSessionWL');
      const pnlEl = document.getElementById('footerPnl');

      if (masterToggle) {
        masterToggle.checked = state.isTrading;
        updateStatusUI(state.isTrading);
      }

      if (balanceEl) {
        const bal = state.balance || 0;
        balanceEl.textContent = `$${bal.toLocaleString('en-US', {minimumFractionDigits:2})}`;
      }
      
      if (wlEl && state.session) {
        wlEl.textContent = `${state.session.wins || 0} / ${state.session.losses || 0}`;
      }
      
      if (pnlEl) {
        const pnl = state.dailyPnl || 0;
        const sign = pnl >= 0 ? '+' : '';
        pnlEl.textContent = `${sign}$${Math.abs(pnl).toFixed(2)}`;
        pnlEl.className = `footer-val ${pnl >= 0 ? 'pos' : 'neg'}`;
      }

      const pEl = document.getElementById('popupPrice');
      const aEl = document.getElementById('popupAsset');
      if (pEl) pEl.textContent = state.price;
      if (aEl) aEl.textContent = `HUB · ${state.asset}`;
    });
  } catch (e) {
    console.error('[NMNH] Sync error:', e);
  }
}

function updateStatusUI(isActive) {
  const dot = document.getElementById('globalStatusDot');
  const text = document.getElementById('globalStatusText');
  const desc = document.getElementById('engineStatusDesc');

  if (isActive) {
    if (dot) { dot.style.backgroundColor = 'var(--accent-ai)'; dot.style.boxShadow = '0 0 8px var(--accent-ai)'; }
    if (text) { text.textContent = 'TRADING'; text.style.color = 'var(--accent-ai)'; }
    if (desc) desc.textContent = 'Engine actively monitoring';
  } else {
    if (dot) { dot.style.backgroundColor = 'var(--accent-buy)'; dot.style.boxShadow = '0 0 6px var(--accent-buy)'; }
    if (text) { text.textContent = 'READY'; text.style.color = 'var(--accent-buy)'; }
    if (desc) desc.textContent = 'Currently Inactive';
  }
}
