/**
 * Ultra Trading Robot — Side Panel Controller v2.1.0
 * Tabbed enterprise dashboard: Overview · Signals · Strategies
 */

/* ─── Mock Data ─────────────────────────────────── */

const SP_POSITIONS = [
  { asset: 'ETH/USD',  type: 'BUY',  price: '$3,152.45', pnl: '+$820.20', pos: true  },
  { asset: 'EUR/USD',  type: 'BUY',  price: '1.08542',   pnl: '+$45.00',  pos: true  },
  { asset: 'GBP/USD',  type: 'SELL', price: '1.26731',   pnl: '+$120.00', pos: true  },
];

const SP_SIGNALS = [
  {
    asset: 'ETH/USD', type: 'BUY',  confidence: 87, time: '12:24',
    entry: '$3,152.40', tp: '$3,165.00', sl: '$3,140.00',
  },
  {
    asset: 'EUR/USD', type: 'BUY',  confidence: 72, time: '12:21',
    entry: '1.08540', tp: '1.08720', sl: '1.08350',
  },
  {
    asset: 'GBP/USD', type: 'SELL', confidence: 64, time: '12:19',
    entry: '1.26730', tp: '1.26480', sl: '1.26900',
  },
  {
    asset: 'BTC/USD', type: 'BUY',  confidence: 91, time: '12:15',
    entry: '$67,420', tp: '$68,100', sl: '$66,800',
  },
];

const SP_STRATEGIES = [
  { icon: '📈', name: 'HFT Trend Following',   desc: 'Momentum-based high-frequency execution',   winRate: 81, trades: 312, active: true  },
  { icon: '📊', name: 'Mean Reversion',         desc: 'Statistical price mean-reversion entries',  winRate: 74, trades: 198, active: false },
  { icon: '⚡', name: 'Volatility Breakout',    desc: 'Range expansion & breakout signals',        winRate: 68, trades: 154, active: true  },
  { icon: '🎯', name: 'HFT Prospect',           desc: 'Short-duration scalping opportunities',     winRate: 77, trades: 267, active: true  },
];

/* Sparkline data (mock daily balance) */
const SPARKLINE_DATA = [5100, 5220, 5185, 5360, 5290, 5480, 5440, 5620, 5580, 5750, 5700, 5824];

/* ─── Entry Point ───────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  renderPositions();
  drawSparkline();
  renderSignals();
  renderStrategies();
  initActionButtons();
  syncBackground();
});

/* ─── Tab Switching ─────────────────────────────── */
function initTabs() {
  document.querySelectorAll('.sp-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      document.querySelectorAll('.sp-tab').forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      document.querySelectorAll('.sp-panel').forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      const panel = document.getElementById('panel-' + target);
      if (panel) panel.classList.add('active');

      // Animate signal fills when switching to signals tab
      if (target === 'signals') {
        setTimeout(animateSentiment, 80);
        setTimeout(animateSignalBars, 120);
      }

      // Animate strategy bars when switching to strategies tab
      if (target === 'strategies') {
        setTimeout(animateStrategyBars, 80);
      }
    });
  });
}

/* ─── Positions Table ───────────────────────────── */
function renderPositions() {
  const tbody = document.querySelector('#spPositions tbody');
  if (!tbody) return;

  SP_POSITIONS.forEach(p => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${p.asset}</td>
      <td class="${p.type === 'BUY' ? 'td-buy' : 'td-sell'}">${p.type}</td>
      <td>${p.price}</td>
      <td class="${p.pos ? 'td-pos' : 'td-neg'}">${p.pnl}</td>
    `;
    tbody.appendChild(tr);
  });
}

/* ─── Sparkline Chart ───────────────────────────── */
function drawSparkline() {
  const canvas = document.getElementById('sparklineCanvas');
  if (!canvas) return;

  const dpr  = window.devicePixelRatio || 1;
  const cssW = canvas.offsetWidth  || 300;
  const cssH = canvas.offsetHeight || 50;

  canvas.width  = cssW * dpr;
  canvas.height = cssH * dpr;

  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);

  const data   = SPARKLINE_DATA;
  const n      = data.length;
  const minV   = Math.min(...data) - 50;
  const maxV   = Math.max(...data) + 50;
  const PAD    = 4;
  const W      = cssW;
  const H      = cssH;

  function px(i)   { return PAD + (i / (n - 1)) * (W - PAD * 2); }
  function py(val) { return H - PAD - ((val - minV) / (maxV - minV)) * (H - PAD * 2); }

  const pts = data.map((v, i) => ({ x: px(i), y: py(v) }));

  // Gradient fill
  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, 'rgba(34, 197, 94, 0.18)');
  grad.addColorStop(1, 'rgba(34, 197, 94, 0)');

  ctx.beginPath();
  pts.forEach((p, i) => {
    if (i === 0) ctx.moveTo(p.x, p.y);
    else {
      const prev = pts[i - 1];
      const cpx  = (prev.x + p.x) / 2;
      ctx.bezierCurveTo(cpx, prev.y, cpx, p.y, p.x, p.y);
    }
  });
  ctx.lineTo(pts[n - 1].x, H);
  ctx.lineTo(pts[0].x, H);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // Line
  ctx.beginPath();
  pts.forEach((p, i) => {
    if (i === 0) ctx.moveTo(p.x, p.y);
    else {
      const prev = pts[i - 1];
      const cpx  = (prev.x + p.x) / 2;
      ctx.bezierCurveTo(cpx, prev.y, cpx, p.y, p.x, p.y);
    }
  });
  ctx.strokeStyle = 'hsl(145,63%,46%)';
  ctx.lineWidth   = 1.8;
  ctx.lineJoin    = 'round';
  ctx.stroke();

  // Last point dot
  const last = pts[n - 1];
  ctx.beginPath();
  ctx.arc(last.x, last.y, 3, 0, Math.PI * 2);
  ctx.fillStyle = 'hsl(145,63%,46%)';
  ctx.fill();
}

/* ─── Sentiment Bar ─────────────────────────────── */
function animateSentiment() {
  const fill = document.getElementById('spSentimentFill');
  if (fill) fill.style.width = '78%';
}

/* ─── Signal Cards ──────────────────────────────── */
function renderSignals() {
  const container = document.getElementById('spSignalsList');
  if (!container) return;

  SP_SIGNALS.forEach(s => {
    const div = document.createElement('div');
    div.className = `sp-signal sig-${s.type.toLowerCase()}`;
    div.innerHTML = `
      <div class="sig-top">
        <span class="sig-asset">${s.asset}</span>
        <span class="sig-badge ${s.type.toLowerCase()}">${s.type}</span>
        <span class="sig-time">${s.time}</span>
      </div>
      <div class="sig-conf-row">
        <span class="sig-conf-label">Confidence</span>
        <div class="sig-conf-track">
          <div class="sig-conf-fill ${s.type.toLowerCase()}" data-target="${s.confidence}"></div>
        </div>
        <span class="sig-conf-pct ${s.type.toLowerCase()}">${s.confidence}%</span>
      </div>
      <div class="sig-entry">
        <div class="sig-entry-item">
          <span class="sig-entry-label">ENTRY</span>
          <span class="sig-entry-val">${s.entry}</span>
        </div>
        <div class="sig-entry-item">
          <span class="sig-entry-label">TAKE PROFIT</span>
          <span class="sig-entry-val" style="color:var(--accent-buy)">${s.tp}</span>
        </div>
        <div class="sig-entry-item">
          <span class="sig-entry-label">STOP LOSS</span>
          <span class="sig-entry-val" style="color:var(--accent-sell)">${s.sl}</span>
        </div>
      </div>
    `;
    container.appendChild(div);
  });
}

function animateSignalBars() {
  document.querySelectorAll('#spSignalsList .sig-conf-fill').forEach(el => {
    el.style.width = el.dataset.target + '%';
  });
}

/* ─── Strategy Cards ────────────────────────────── */
function renderStrategies() {
  const container = document.getElementById('spStrategiesList');
  if (!container) return;

  SP_STRATEGIES.forEach((s, idx) => {
    const div = document.createElement('div');
    div.className = 'strat-card';
    div.innerHTML = `
      <div class="strat-top">
        <div class="strat-icon">${s.icon}</div>
        <div class="strat-info">
          <div class="strat-name">${s.name}</div>
          <div class="strat-desc">${s.desc}</div>
        </div>
        <div class="toggle-wrap">
          <label class="toggle" aria-label="Toggle ${s.name}">
            <input type="checkbox" ${s.active ? 'checked' : ''} data-idx="${idx}">
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="strat-stats">
        <div class="strat-stat">
          <span class="strat-stat-label">WIN RATE</span>
          <span class="strat-stat-val">${s.winRate}%</span>
        </div>
        <div class="strat-stat">
          <span class="strat-stat-label">TRADES</span>
          <span class="strat-stat-val">${s.trades}</span>
        </div>
        <div class="strat-bar-wrap">
          <div class="strat-bar-fill" data-target="${s.winRate}"></div>
        </div>
        <span class="strat-bar-pct">${s.winRate}%</span>
      </div>
    `;
    container.appendChild(div);
  });

  // Animate on load (overview is visible first, so trigger immediately)
  requestAnimationFrame(() => setTimeout(animateStrategyBars, 200));
}

function animateStrategyBars() {
  document.querySelectorAll('#spStrategiesList .strat-bar-fill').forEach(el => {
    el.style.width = el.dataset.target + '%';
  });
}

/* ─── Action Buttons ────────────────────────────── */
let isTrading = false;

function initActionButtons() {
  const btnTrade = document.getElementById('spBtnTrade');
  const btnPanel = document.getElementById('spBtnPanel');

  if (btnTrade) {
    btnTrade.addEventListener('click', () => {
      isTrading = !isTrading;
      btnTrade.textContent = isTrading ? '⏹ STOP BOT' : 'ACTIVATE BOT';
      btnTrade.classList.toggle('active', isTrading);

      try {
        chrome.runtime.sendMessage({
          type: isTrading ? 'START_TRADING' : 'STOP_TRADING',
          payload: { mode: 'hft-trend' },
        }, (res) => {
          if (chrome.runtime.lastError) return;
          console.log('[Ultra] Trade state:', res?.status);
        });
      } catch {
        console.log('[Ultra] Background not available');
      }
    });
  }

  if (btnPanel) {
    btnPanel.addEventListener('click', () => {
      try {
        chrome.runtime.sendMessage({ type: 'TOGGLE_SIDEPANEL' });
      } catch {
        console.log('[Ultra] Cannot send message');
      }
    });
  }
}

/* ─── Background Sync ───────────────────────────── */
function syncBackground() {
  try {
    chrome.runtime.sendMessage({ type: 'GET_STATE' }, response => {
      if (chrome.runtime.lastError || !response) return;
      if (response.status === 'SUCCESS') applyState(response.data);
    });
  } catch { /* extension APIs unavailable in preview */ }

  setInterval(() => {
    try {
      chrome.runtime.sendMessage({ type: 'GET_STATE' }, response => {
        if (chrome.runtime.lastError || !response) return;
        if (response.status === 'SUCCESS') applyState(response.data);
      });
    } catch { }
  }, 8000);
}

function applyState(state) {
  if (!state) return;

  const balanceEl = document.getElementById('spBalance');
  const pnlEl     = document.getElementById('spPnlBadge');
  const winRateEl = document.getElementById('spWinRate');
  const tradesEl  = document.getElementById('spTrades');
  const badgeEl   = document.getElementById('spLiveBadge');

  if (balanceEl && state.balance !== undefined) {
    balanceEl.textContent = '$' + state.balance.toLocaleString('en-US', { minimumFractionDigits: 2 });
  }
  if (pnlEl && state.dailyPnl !== undefined) {
    const sign = state.dailyPnl >= 0 ? '+' : '';
    pnlEl.textContent = `${sign}$${Math.abs(state.dailyPnl).toFixed(2)}`;
    pnlEl.className   = `pnl-badge ${state.dailyPnl >= 0 ? 'pos' : 'neg'}`;
  }
  if (winRateEl && state.winRate !== undefined) {
    winRateEl.textContent = state.winRate.toFixed(1) + '%';
  }
  if (tradesEl && state.tradesCount !== undefined) {
    tradesEl.textContent = state.tradesCount;
  }
  if (badgeEl) {
    if (!state.isConnected) {
      badgeEl.innerHTML = '● OFFLINE';
      badgeEl.style.color = 'var(--text-dim)';
    }
  }
}
