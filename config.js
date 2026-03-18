/**
 * NMNH CONFIG - Global Parameters v2.1.2
 */
export const ULTRA_CONFIG = {
  PARTNER_ID: '511442168',
  TELEGRAM_BOT: 'https://t.me/moneyhoney7_bot',
  MASSIVE_API_KEY: 'av1mp02tUNimrFMuRrCYLtBnd9rsb6mr'
};

console.log('[NMNH] Config v2.1.2 Loaded');

// For browser global scope (content scripts)
if (typeof self !== 'undefined') {
  self.ULTRA_CONFIG = ULTRA_CONFIG;
}
