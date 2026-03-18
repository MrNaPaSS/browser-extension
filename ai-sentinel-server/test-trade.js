const WebSocket = require('ws');

/**
 * NMNH SENTINEL TRADE TEST
 * This script sends an EXECUTE_TRADE command to the extension.
 * CAUTION: This will actually click the trade buttons on your screen!
 */

async function testTradeExecution(action = 'BUY') {
  console.log(`[TEST] Connecting to Sentinel Bridge to execute: ${action}...`);
  const ws = new WebSocket('ws://localhost:3001');

  ws.on('open', () => {
    setTimeout(() => {
      console.log(`[TEST] Requesting ${action} execution...`);
      ws.send(JSON.stringify({
        id: 'trade-' + Date.now(),
        type: 'EXECUTE_TRADE',
        payload: { action: action, amount: 1 }
      }));
    }, 1000);
  });

  ws.on('message', (data) => {
    const resp = JSON.parse(data);
    if (resp.data && resp.data.status === 'SUCCESS') {
      console.log(`[TEST] EXECUTION SUCCESS ✅: ${action} button was clicked.`);
    } else {
      console.error('[TEST] EXECUTION FAILED ❌. Details:', JSON.stringify(resp.data || resp, null, 2));
    }
    ws.close();
  });

  ws.on('error', (err) => {
    console.error('[TEST] Connection Error:', err);
    process.exit(1);
  });
}

// Default to a BUY test
testTradeExecution('BUY');
