const { GoogleGenerativeAI } = require("@google/generative-ai");
const WebSocket = require('ws');
require('dotenv').config();

/**
 * NMNH SENTINEL BRAIN v1.2.0
 * Signal Provider & Autonomous Intelligence
 */

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const MODELS = ["gemini-2.0-flash", "gemini-flash-latest"];
let currentModelIndex = 0;

const BRIDGE_URL = 'ws://localhost:3001';

async function startBrain() {
  console.log('--- NMNH SENTINEL BRAIN v1.2.0 ACTIVE ---');
  
  const ws = new WebSocket(BRIDGE_URL);

  ws.on('open', () => {
    console.log('[BRAIN] Connected to Sentinel Bridge ✅');
    // Handshake as Agent
    ws.send(JSON.stringify({ id: 'AUTH_AGENT' }));
  });

  ws.on('message', async (data) => {
    try {
      const msg = JSON.parse(data);
      
      // Handle On-Demand Signal Request
      if (msg.type === 'GET_SIGNAL') {
        console.log(`[SIGNAL] Received Request for ${msg.payload.asset}...`);
        const signalData = await generateSignal(msg.payload);
        ws.send(JSON.stringify({ id: msg.id, data: signalData }));
        console.log(`[SIGNAL] Delivered: ${signalData.decision} (${(signalData.confidence*100).toFixed(0)}%)`);
      }
    } catch (e) {
      console.error('[BRAIN] Message handler error:', e.message);
    }
  });

  ws.on('error', (err) => {
    console.error('[BRAIN] Bridge Error:', err.message);
    process.exit(1);
  });
}

async function generateSignal(context) {
  const prompt = `
    Analyze this trading terminal state and provide a precision signal.
    STATE: ${JSON.stringify(context)}
    
    INSTRUCTIONS:
    - You are a professional HFT Scalper.
    - Analyze the balance vs asset vs current price.
    - Analysis: Trend (BULLISH or BEARISH) and Volatility Risk (LOW or HIGH).
    - Format as JSON: { "decision": "...", "reason": "...", "confidence": 0-1, "trend": "...", "risk": "..." }
  `;

  for (let i = 0; i < MODELS.length; i++) {
    const modelName = MODELS[currentModelIndex];
    try {
      const gModel = genAI.getGenerativeModel({ 
        model: modelName,
        generationConfig: { responseMimeType: "application/json" }
      });
      const result = await gModel.generateContent(prompt);
      return parseGeminiJson(result.response.text());
    } catch (err) {
      console.error(`[BRAIN] Model ${modelName} failed:`, err.message);
      currentModelIndex = (currentModelIndex + 1) % MODELS.length;
    }
  }
  return { decision: 'WAIT', reason: 'AI Core Unavailable', confidence: 0 };
}

function parseGeminiJson(text) {
  try {
    const clean = text.replace(/```json|```/g, '').trim();
    return JSON.parse(clean);
  } catch (e) {
    return { decision: 'WAIT', reason: 'Parse Error', confidence: 0 };
  }
}

startBrain();
