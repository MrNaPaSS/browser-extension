/**
 * NMNH CONFIG - Global Parameters v2.1.2
 */
export const ULTRA_CONFIG = {
  PARTNER_ID: '511442168',
  TELEGRAM_BOT: 'https://t.me/moneyhoney7_bot',
  MASSIVE_API_KEY: 'av1mp02tUNimrFMuRrCYLtBnd9rsb6mr',
  FINNHUB_API_KEY: 'd3ncd09r01qo7510fhmgd3ncd09r01qo7510fhn0',
  OPENROUTER_API_KEY: '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',
  MASSIVE_API_KEY: 'av1mp02tUNimrFMuRrCYLtBnd9rsb6mr'
};

console.log('[NMNH] Config v2.1.2 Loaded');

// For browser global scope (content scripts)
if (typeof self !== 'undefined') {
  self.ULTRA_CONFIG = ULTRA_CONFIG;
}
