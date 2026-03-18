/**
 * NMNH Trading Robot — Onboarding Page
 * Enterprise welcome experience with animated particles
 */

document.addEventListener('DOMContentLoaded', () => {

  /* ─── Particle System ──────────────────────────── */
  const grid = document.getElementById('particleGrid');
  if (grid) {
    const colors = ['#60a5fa', '#a855f7', '#22c55e', '#60a5fa', '#60a5fa'];
    for (let i = 0; i < 50; i++) {
      const p = document.createElement('div');
      p.className = 'particle';
      p.style.left   = Math.random() * 100 + '%';
      p.style.bottom = '-6px';
      p.style.animationDuration  = (10 + Math.random() * 18) + 's';
      p.style.animationDelay     = -(Math.random() * 15) + 's';
      const size = 1.5 + Math.random() * 2.5;
      p.style.width   = size + 'px';
      p.style.height  = size + 'px';
      p.style.opacity = (0.08 + Math.random() * 0.22).toFixed(2);
      p.style.background = colors[Math.floor(Math.random() * colors.length)];
      grid.appendChild(p);
    }
  }

  /* ─── Step Indicator ───────────────────────────── */
  const steps = document.querySelectorAll('.step-dot');
  let currentStep = 0;
  if (steps.length) {
    steps[0].classList.add('active');
    setInterval(() => {
      steps[currentStep].classList.remove('active');
      currentStep = (currentStep + 1) % steps.length;
      steps[currentStep].classList.add('active');
    }, 2000);
  }

  /* ─── Start Button ─────────────────────────────── */
  const startBtn = document.getElementById('startBtn');
  if (startBtn) {
    startBtn.addEventListener('click', () => {
      startBtn.textContent = '✓ Ready!';
      startBtn.style.background = 'linear-gradient(135deg, hsl(145,63%,42%), hsl(145,63%,35%))';
      chrome.storage.local.set({ onboardingComplete: true }, () => {
        setTimeout(() => window.close(), 600);
      });
    });
  }
});
