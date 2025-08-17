from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import google.generativeai as genai
import os

API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")
SYSTEM_PROMPT = "You are a helpful agriculture expert who answers in short, clear sentences. your owner/ developer is Sanchit"

app = FastAPI()

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
                text-align: center;
                background: linear-gradient(135deg, #d4fcd4, #a8e6a2);
                color: #2d572c;
            }
            header {
                background: #2d572c;
                color: white;
                padding: 15px;
                font-size: 1.5em;
            }
            .container {
                padding: 20px;
                max-width: 500px;
                margin: auto;
            }
            input[type="text"] {
                width: 90%;
                padding: 10px;
                margin: 10px 0;
                border: 2px solid #2d572c;
                border-radius: 8px;
                font-size: 1em;
            }
            button {
                background: #2d572c;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-size: 1em;
                cursor: pointer;
            }
            button:hover {
                background: #1e3d1f;
            }
            #response-box {
                margin-top: 20px;
                padding: 15px;
                background: #ffffffaa;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                font-size: 1em;
                text-align: left;
            }
            footer {
                margin-top: 30px;
                font-size: 0.9em;
                color: #333;
            }
        </style>
    </head>
    <body>
        <header>🌱 Agriculture AI</header>
        <div class="container">
            <p>Ask me anything about farming:</p>
            <input type="text" id="userInput" placeholder="Type your question here..." />
            <br>
            <button onclick="askAI()">Ask</button>
            <div id="response-box"></div>
        </div>
        <footer>
            <p>Made by <b>Sanchit 🚀</b></p>
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

