import psycopg2
import requests
import datetime

from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

#.env
load_dotenv()

API_KEY = os.getenv("API_KEY")
DATABASE_STR = os.getenv("DATABASE_STR")
ADMIN_ID = os.getenv("ADMIN_ID")
OWNERS_ID = os.getenv("OWNERS_ID")
MODEL = "deepseek/deepseek-r1"
URL = "https://openrouter.ai/api/v1/chat/completions"

language = ""

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def Select_Language_DB_Connection():
    connection = psycopg2.connect(DATABASE_STR)
    cursor = connection.cursor()  

    cursor.execute("SELECT language FROM lang")
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    return data

app = FastAPI()
class ChatRequest(BaseModel):
    text: str


async def Deepseek_Request(text):
    data = {
        "model": "deepseek/deepseek-r1",
        "messages": [
            {"role": "system", "content": """
You are a Discord Server Feedback Assistant.
Your task is to analyze member conversations and give admins a short, clear summary that helps them develop the server.

When you process a conversation:

Identify the main topics members talked about.

Extract the interests or needs members expressed.

Suggest one short improvement the admins can make to improve the server.

At the end, list the names of the members who talked about these points.

Output format (example):

📊 Report:
- Topics: gaming, anime, music
- Interests: more voice chat activity, community events
- Suggestion: organize weekly game nights
- Members: @Moatez, @Leon, @Malek
"""},   
            {"role": "user", "content": text}
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Endpoint to receive chat requests
@app.post("/chat")
async def Chat(request: ChatRequest):

    Message_Date = datetime.datetime.now().replace(microsecond=0)
    global language
    global ADMIN_ID
    global OWNERS_ID

    for data in Select_Language_DB_Connection():
        language = data[0]
        print(f"The language is of the bot respond:{language}")

    text = f"""
        just send Summary for Admin in point with {language} language 
        and your limit 8 points to write and the names users write it with english language.
        Analyze this for give it to admin:
        {request.text.strip()}
    """
    
    print(f"Received message: {text}")
    
    print(f"Processing the user_message...")

    result = await Deepseek_Request(text)

    print(f"{'AI Agent'}: {result}")  # Print the final response

    return {"reply": f"{result} \n\n"  f"--> ||| <@&{OWNERS_ID}> -  ||| \n" f"--> |` Report Date: -- {Message_Date} -- `|"} 
