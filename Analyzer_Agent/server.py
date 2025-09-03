from fastapi import FastAPI
import uvicorn
import threading

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Bot is alive!"}

@app.post("/chat")
async def chat(data: dict):
    text = data.get("text", "")
    return {"reply": f"AI reply for: {text[:50]}..."}

def keep_alive():
    def run():
        uvicorn.run(app, host="0.0.0.0", port=8080)

    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
