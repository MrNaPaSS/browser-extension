const { GoogleGenerativeAI } = require("@google/generative-ai");
require('dotenv').config();

async function check() {
  try {
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash-latest" }); 
    const result = await model.generateContent("Hello?");
    console.log("Gemini API is WORKING ✅");
    console.log(result.response.text());
  } catch (e) {
    console.error("Gemini API FAILED ❌");
    console.error(e.message);
  }
}

check();
