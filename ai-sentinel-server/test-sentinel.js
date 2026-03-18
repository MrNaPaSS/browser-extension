const WebSocket = require('ws');

/**
 * NMNH SENTINEL TEST CLIENT v1.1.0
 * Connects as an AGENT and requests browser context.
 */

async function testBridge() {
  console.log('[TEST] Connecting to Sentinel Bridge at ws://localhost:3001...');
  const ws = new WebSocket('ws://localhost:3001');

  ws.on('open', () => {
    console.log('[TEST] Connected! Waiting 2s for extension to be ready...');
    
    setTimeout(() => {
      console.log('[TEST] Sending GET_CONTEXT request...');
      ws.send(JSON.stringify({
        id: 'agent-' + Date.now(),
        type: 'GET_CONTEXT'
      }));
    }, 2000);
  });

  ws.on('message', (data) => {
    try {
      const resp = JSON.parse(data);
      if (resp.error) {
        console.error('[TEST] Remote Error:', resp.error);
      } else {
        console.log('[TEST] Received Context SUCCESS ✅');
        console.log(JSON.stringify(resp.data, null, 2));
      }
    } catch (e) {
      console.error('[TEST] Parse Error:', e.message);
    }
    ws.close();
  });

  ws.on('close', () => console.log('[TEST] Connection closed.'));
  ws.on('error', (err) => console.error('[TEST] Connection Error:', err));
}

testBridge();
