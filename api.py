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
    <html>
        <head>
            <title>Agriculture AI API</title>
        </head>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>🌱 Agriculture AI API</h1>
            <p>Welcome! This is a private API powered by Gemini.</p>
            <p>Try it here:</p>
            <ul style="list-style: none;">
                <li><b>GET</b>: /ai?text=Best fertilizer for wheat</li>
                <li><b>POST</b>: /ai with JSON body {"text": "your question"}</li>
            </ul>
            <p><i>Made by Sanchit 🚀</i></p>
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

