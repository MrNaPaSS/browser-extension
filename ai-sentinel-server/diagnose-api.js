const { GoogleGenerativeAI } = require("@google/generative-ai");
require('dotenv').config();

async function diagnose() {
  console.log('--- GEMINI API DIAGNOSTICS ---');
  try {
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    
    // We try to list models. This doesn't always work with restricted keys, 
    // but it's the best way to see what's available.
    // Note: The SDK might not have a direct listModels top-level, 
    // we use a fetch to the REST endpoint because it's more reliable for diagnostics.
    
    const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${process.env.GEMINI_API_KEY}`;
    const response = await fetch(url);
    const data = await response.json();

    if (data.error) {
      console.error('❌ API ERROR:', data.error.message);
      if (data.error.status === 'PERMISSION_DENIED') {
        console.error('👉 Tip: Ensure "Generative Language API" is ENABLED in Google Cloud Console.');
      }
    } else {
      console.log('✅ API IS ACTIVE. Available Models:');
      data.models.forEach(m => {
        console.log(` - ${m.name} (${m.supportedGenerationMethods.join(', ')})`);
      });
    }
  } catch (e) {
    console.error('❌ DIAGNOSTICS FAILED:', e.message);
  }
}

diagnose();
