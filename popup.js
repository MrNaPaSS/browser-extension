/**
 * NMNH Trading Robot — Popup Controller v3.0
 * Navigation & Start Button Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  initStartButton();
  initResetButton();
  initNavigation();
  syncState();

  // Listen for real-time updates from background
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.type === 'PRICE_UPDATE') {
      const priceEl = document.getElementById('popupPrice');
      const assetEl = document.getElementById('popupAsset');
      if (priceEl) priceEl.textContent = msg.payload.price;
      if (assetEl) assetEl.textContent = `HUB · ${msg.payload.asset}`;
    }
    if (msg.type === 'SESSION_UPDATE') {
      updateFooterStats(msg.payload);
    }
  });

  // Periodic fallback sync
  setInterval(syncState, 2000);
});

/* ─── Navigation ────────────────────────────────── */
function initNavigation() {
  const btnTerminal = document.getElementById('navTerminal');
  if (btnTerminal) {
    btnTerminal.onclick = () => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const tab = tabs[0];
        if (tab && tab.url && (tab.url.includes('pocketoption.com') || tab.url.includes('po.trade'))) {
          // We are on the platform, just toggle
          chrome.tabs.sendMessage(tab.id, { type: 'TOGGLE_TERMINAL' }, () => {
            if (chrome.runtime.lastError) {
              console.warn('Terminal toggle failed.');
              // Fallback: reload/open if content script didn't respond
              chrome.tabs.update(tab.id, { url: 'https://pocketoption.com/en/cabinet/' });
              chrome.storage.local.set({ ultra_panel_open: true });
            } else {
              window.close();
            }
          });
        } else if (tab) {
          // Not on platform, open it and set auto-open flag
          chrome.storage.local.set({ ultra_panel_open: true });
          chrome.tabs.update(tab.id, { url: 'https://pocketoption.com/en/cabinet/' });
          window.close();
        }
      });
    };
  }

  const btnDashboard = document.getElementById('navDashboard');
  if (btnDashboard) {
    btnDashboard.onclick = () => window.open('https://u3.shortink.io/register?utm_campaign=827841&utm_source=affiliate&utm_medium=sr&a=CQQJpdvm2ya9dU&ac=web&code=WELCOME50');
  }

  const btnPromo = document.getElementById('navPromo');
  if (btnPromo) {
    btnPromo.onclick = () => {
      const modal = document.getElementById('promoModal');
      if (modal) modal.classList.add('active');
    };
  }

  const btnClosePromo = document.getElementById('closePromo');
  const promoModal = document.getElementById('promoModal');
  if (btnClosePromo && promoModal) {
    btnClosePromo.onclick = () => promoModal.classList.remove('active');
    promoModal.onclick = (e) => {
      if (e.target === promoModal) promoModal.classList.remove('active');
    };
  }

  // Copy Promo Logic
  document.querySelectorAll('.copy-promo').forEach(btn => {
    btn.onclick = (e) => {
      const code = e.target.getAttribute('data-code');
      navigator.clipboard.writeText(code).then(() => {
        const originalText = e.target.textContent;
        e.target.textContent = 'Готово!';
        e.target.style.background = 'hsla(145, 63%, 46%, 0.2)';
        setTimeout(() => {
          e.target.textContent = originalText;
          e.target.style.background = '';
        }, 2000);
      });
    };
  });

  const btnSupport = document.getElementById('navSupport');
  if (btnSupport) {
    btnSupport.onclick = () => window.open('https://t.me/moneyhoney7_bot');
  }

  const navAcademy = document.getElementById('navAcademy');
  if (navAcademy) {
    navAcademy.onclick = () => window.open('https://t.me/moneyhoney7_bot');
  }

  const navChannel = document.getElementById('navChannel');
  if (navChannel) {
    navChannel.onclick = () => window.open('https://t.me/+avD8ncMHBp4zMzhi');
  }
}

/* ─── Start Button ──────────────────────────────── */
function initStartButton() {
  const btnStart = document.getElementById('btnStart');
  if (!btnStart) return;

  btnStart.onclick = () => {
    const btnTerminal = document.getElementById('navTerminal');
    const footerContainer = document.getElementById('footerContainer');
    const isActive = btnStart.classList.contains('active');

    if (isActive) {
      // STOP session
      btnStart.classList.remove('active');
      btnStart.querySelector('.start-text').textContent = 'СТАРТ';
      btnStart.querySelector('.start-icon').innerHTML = '<path d="M8 5v14l11-7z"/>';
      chrome.runtime.sendMessage({ type: 'STOP_TRADING' });
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0] && tabs[0].id) chrome.tabs.sendMessage(tabs[0].id, { type: 'CLOSE_SESSION_WINDOW' });
      });
      chrome.storage.local.set({ ultra_start_trading: false });
      
      if (footerContainer) footerContainer.classList.remove('connecting', 'connected');
      if (btnTerminal) btnTerminal.classList.remove('pulse');
      updateStatusUI(false);
    } else {
      // START session
      btnStart.classList.add('active');
      btnStart.querySelector('.start-text').textContent = 'СТОП';
      btnStart.querySelector('.start-icon').innerHTML = '<rect x="6" y="6" width="12" height="12" rx="1"/>';
      
      if (footerContainer) {
        footerContainer.classList.remove('connected');
        footerContainer.classList.add('connecting');
      }

      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const tab = tabs[0];
        const isPlatform = tab && tab.url && (tab.url.includes('pocketoption.com') || tab.url.includes('po.trade'));
        
        if (isPlatform) {
          chrome.runtime.sendMessage({ type: 'START_TRADING', payload: { mode: 'hft-trend' } });
          chrome.tabs.sendMessage(tab.id, { type: 'OPEN_SESSION_WINDOW' });
          
          setTimeout(() => {
            if (footerContainer) {
              footerContainer.classList.remove('connecting');
              footerContainer.classList.add('connected');
            }
            if (btnTerminal) {
              btnTerminal.classList.add('pulse');
            }
          }, 1800);
        } else if (tab) {
          chrome.storage.local.set({ ultra_start_trading: true, ultra_panel_open: true });
          chrome.tabs.update(tab.id, { url: 'https://pocketoption.com/en/cabinet/' });
          window.close();
        }
      });
      updateStatusUI(true);
    }
  };
}

/* ─── Reset Button ──────────────────────────────── */
function initResetButton() {
  const btnReset = document.getElementById('btnResetSession');
  if (btnReset) {
    btnReset.onclick = () => {
      if (confirm('Reset session statistics?')) {
        chrome.runtime.sendMessage({ type: 'RESET_SESSION' }, () => syncState());
      }
    };
  }
}

/* ─── State Sync ────────────────────────────────── */
function syncState() {
  try {
    chrome.runtime.sendMessage({ type: 'GET_STATE' }, response => {
      if (chrome.runtime.lastError || !response || response.status !== 'SUCCESS') return;

      const state = response.data;
      const btnStart = document.getElementById('btnStart');
      const balanceEl = document.getElementById('footerBalance');
      const wlEl = document.getElementById('footerSessionWL');
      const pnlEl = document.getElementById('footerPnl');

      if (btnStart) {
        const fc = document.getElementById('footerContainer');
        const bt = document.getElementById('navTerminal');
        if (state.isTrading) {
          btnStart.classList.add('active');
          btnStart.querySelector('.start-text').textContent = 'СТОП';
          btnStart.querySelector('.start-icon').innerHTML = '<rect x="6" y="6" width="12" height="12" rx="1"/>';
          if (fc) fc.classList.add('connected');
          if (bt) {
            bt.classList.add('pulse');
          }
        } else {
          btnStart.classList.remove('active');
          btnStart.querySelector('.start-text').textContent = 'СТАРТ';
          btnStart.querySelector('.start-icon').innerHTML = '<path d="M8 5v14l11-7z"/>';
          if (fc) fc.classList.remove('connecting', 'connected');
          if (bt) {
            bt.classList.remove('pulse');
          }
        }
        updateStatusUI(state.isTrading);
      }

      if (balanceEl) {
        const bal = state.balance || 0;
        balanceEl.textContent = `$${bal.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      }

      if (wlEl && state.session) {
        wlEl.textContent = `${state.session.wins || 0} / ${state.session.losses || 0}`;
      }

      if (pnlEl) {
        const startBal = state.sessionStartBalance || state.balance || 0;
        const pnl = (state.balance && startBal) ? (state.balance - startBal) : 0;
        const sign = pnl >= 0 ? '+' : '-';
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

function updateFooterStats(payload) {
  if (!payload) return;
  const wlEl = document.getElementById('footerSessionWL');
  const pnlEl = document.getElementById('footerPnl');
  
  if (wlEl && payload.wins !== undefined) {
    wlEl.textContent = `${payload.wins} / ${payload.losses}`;
  }
  
  if (pnlEl && payload.dailyPnl !== undefined) {
    const pnl = payload.dailyPnl;
    const sign = pnl >= 0 ? '+' : '-';
    pnlEl.textContent = `${sign}$${Math.abs(pnl).toFixed(2)}`;
    pnlEl.className = `footer-val ${pnl >= 0 ? 'pos' : 'neg'}`;
  }
}

function updateStatusUI(isActive) {
  const dot = document.getElementById('globalStatusDot');
  const text = document.getElementById('globalStatusText');

  if (isActive) {
    if (dot) { dot.style.backgroundColor = 'var(--accent-ai)'; dot.style.boxShadow = '0 0 8px var(--accent-ai)'; }
    if (text) { text.textContent = 'ACTIVE'; text.style.color = 'var(--accent-ai)'; }
  } else {
    if (dot) { dot.style.backgroundColor = 'var(--accent-buy)'; dot.style.boxShadow = '0 0 6px var(--accent-buy)'; }
    if (text) { text.textContent = 'READY'; text.style.color = 'var(--accent-buy)'; }
  }
}
