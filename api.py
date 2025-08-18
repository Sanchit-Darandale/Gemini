from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import google.generativeai as genai
import os

API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")
SYSTEM_PROMPT = """
You are "AgriSage AI", a multilingual agricultural assistant developed by Sanchit.  
Your role is to help farmers and users by providing answers in short, clear sentences, accurate, simple, and practical information related to farming, crops, weather, soil, irrigation, government schemes, and market prices.  

Guidelines for responses:
- Always reply in the same language the user uses (Marathi, Hindi, English, Gujarati, etc.).  
- Use clear, simple, and farmer-friendly sentences.  
- If the user asks about weather, fetch the latest weather information for their location and present it clearly.  
- If the user asks about crop market prices, search for the latest mandi/market rates and share them.  
- Provide step-by-step guidance for farming practices (e.g., pest control, crop rotation, fertilizer use, soil health).  
- Suggest eco-friendly, cost-effective, and practical solutions.  
- If asked about government schemes, give details on eligibility, process, and benefits in the user's language.  
- Always stay polite, supportive, and encouraging.  

Important:  
- If a user asks in Marathi → reply in Marathi.  
- If a user asks in Hindi → reply in Hindi.  
- If a user asks in Gujarati → reply in Gujarati.  
- Otherwise, reply in English.  

You are designed to be a trusted digital companion for farmers, making agriculture easier, profitable, and sustainable.
"""

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_response(user_text: str) -> str:
    chat = model.start_chat(history=[
        {"role": "user", "parts": [SYSTEM_PROMPT]}
    ])
    response = chat.send_message(user_text)
    return response.text

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agriculture AI API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: #ffffff;
                color: #2d572c;
                text-align: center;
            }
            header {
                background: #2d572c;
                color: white;
                padding: 15px;
                font-size: 1.5em;
            }
            .container {
                padding: 20px;
                max-width: 600px;
                margin: auto;
            }
            input[type="text"] {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 1em;
                box-sizing: border-box;
            }
            button {
                background: #4CAF50;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 1em;
                cursor: pointer;
                width: 100%;
            }
            button:hover {
                background: #45a049;
            }
            #response-box {
                margin-top: 20px;
                padding: 15px;
                background: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                font-size: 1em;
                text-align: left;
                min-height: 50px;
            }
            .api-info {
                margin-top: 30px;
                text-align: left;
                background: #f1f8f1;
                border: 1px solid #d4e8d4;
                padding: 15px;
                border-radius: 10px;
                font-size: 0.95em;
                color: #333;
            }
            .api-info code {
                background: #eee;
                padding: 2px 5px;
                border-radius: 5px;
                font-family: monospace;
            }
            footer {
                margin-top: 40px;
                font-size: 0.9em;
                color: #555;
                padding: 15px;
                background: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <header>🌱 Agriculture AI</header>
        <div class="container">
            <p>Ask me anything about farming:</p>
            <input type="text" id="userInput" placeholder="Type your question here..." />
            <button onclick="askAI()">Ask</button>
            <div id="response-box"></div>

            <div class="api-info">
                <h3>📖 API Usage</h3>
                <p>You can also access this AI via API:</p>
                <p><b>1️⃣ GET request:</b></p>
                <code>https://ds-gemini-ai.vercel.app/ai?text=Best+fertilizer+for+wheat</code>
                
                <p><b>2️⃣ POST request:</b></p>
                <code>
                curl -X POST https://ds-gemini-ai.vercel.app/ai \<br>
                -H "Content-Type: application/json" \<br>
                -d '{"text": "How to prevent pests in tomatoes?"}'
                </code>
                
                <p>✅ Response Example:</p>
                <code>
                {
                  "user": "How to prevent pests in tomatoes?",
                  "response": "Use neem oil spray, remove infected leaves, and keep soil clean."
                }
                </code>
            </div>
        </div>
        <footer>
            <p>Made With ♥️ by Sanchit</p>
        </footer>

        <script>
            async function askAI() {
                const text = document.getElementById("userInput").value;
                if (!text) {
                    alert("Please enter a question!");
                    return;
                }
                document.getElementById("response-box").innerHTML = "Thinking... ⏳";

                try {
                    const res = await fetch("/ai", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({ text })
                    });
                    const data = await res.json();
                    if (data.response) {
                        document.getElementById("response-box").innerHTML = "<b>Answer:</b> " + data.response;
                    } else {
                        document.getElementById("response-box").innerHTML = "⚠️ Error: " + JSON.stringify(data);
                    }
                } catch (err) {
                    document.getElementById("response-box").innerHTML = "⚠️ Failed to reach server.";
                }
            }
        </script>
    </body>
    </html>
    """
    
@app.api_route("/ai", methods=["GET", "POST"])
async def ai_endpoint(request: Request):
    try:
        if request.method == "GET":
            user_text = request.query_params.get("text")
        else:  # POST
            body = await request.json()
            user_text = body.get("text") if body else None

        if not user_text:
            return JSONResponse({"error": "No text provided"}, status_code=400)

        reply = get_response(user_text)

        return JSONResponse({
            "user": user_text,
            "response": reply,
            "credit": "Made by Sanchit"
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

