import discord
import psycopg2
import requests
import os
from dotenv import load_dotenv
from server import keep_alive

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_STR = os.getenv("DATABASE_STR")
CHANNEL_LOGGIN_ID = os.getenv("CHANNEL_LOGGIN_ID")
CHANNEL_GENERAL_ID = os.getenv("CHANNEL_GENERAL_ID")

# رابط السيرفر في Replit (غيّره باسم مشروعك واسم المستخدم)
BACKEND_URL_AI = "https://yourproject.yourusername.repl.co/chat"

# 📌 دوال قاعدة البيانات
def Insert_DB_Connection(name, message):
    connection = psycopg2.connect(DATABASE_STR)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO messages (name, message) VALUES (%s, %s)", (name, message))
    connection.commit()
    cursor.close()
    connection.close()

def Select_Message_DB_Connection():
    connection = psycopg2.connect(DATABASE_STR)
    cursor = connection.cursor()
    cursor.execute("SELECT name, message, language FROM messages")
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

def Reset_DB_Connection():
    connection = psycopg2.connect(DATABASE_STR)
    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE messages RESTART IDENTITY;")
    connection.commit()
    cursor.close()
    connection.close()

def Length_DB_Connection():
    connection = psycopg2.connect(DATABASE_STR)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(name) FROM messages")
    data = cursor.fetchone()
    cursor.close()
    connection.close()
    return data


# 📌 بوت ديسكورد
class Client(discord.Client):
    async def on_ready(self):
        print(f"✅ Bot is ready! Logged in as {self.user}")
        length = Length_DB_Connection()
        print(f"📊 DB length: {length[0] if length else 0}")
        print(f"📋 DB content: {Select_Message_DB_Connection()}")

    async def on_message(self, message):
        global CHANNEL_LOGGIN_ID, CHANNEL_GENERAL_ID

        if message.author == self.user:
            return

        Channel_Loggin = self.get_channel(int(CHANNEL_LOGGIN_ID))
        Channel_General = self.get_channel(int(CHANNEL_GENERAL_ID))

        # أمر لإعادة تعيين قاعدة البيانات
        if message.content == ">res":
            Reset_DB_Connection()
            await message.channel.send("✅ Database has been reset.")
            return

        # إدخال الرسالة في DB
        Insert_DB_Connection(message.author.name, message.content)

        # التحقق إذا وصلنا 15 رسالة
        if message.channel == Channel_General and Length_DB_Connection()[0] == 15:
            try:
                print("⚡ Processing messages, please wait...")
                text = ""
                for data in Select_Message_DB_Connection():
                    text += f"{data[0]} said: {data[1]}\n"

                respAI = requests.post(BACKEND_URL_AI, json={"text": text})
                bot_response_json = respAI.json()
                bot_response = bot_response_json.get("reply", "No response field in JSON")

                Reset_DB_Connection()
                print("🗑️ Database reset after processing")

            except requests.exceptions.JSONDecodeError as e:
                bot_response = f"❌ Error: Invalid JSON response: {str(e)}"
            except requests.exceptions.RequestException as e:
                bot_response = f"❌ Error: Unable to connect to backend: {str(e)}"
            except Exception as e:
                bot_response = f"❌ Unexpected error: {str(e)}"

            # إرسال الرد
            if Channel_Loggin and bot_response:
                await Channel_Loggin.send(bot_response)
            elif bot_response:
                await message.channel.send("⚠️ Couldn't find logging channel")

        else:
            print(f"ℹ️ DB length is {Length_DB_Connection()[0]}")


# ✅ Intents (لازم message_content عشان تشتغل الرسائل)
intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents)

if __name__ == "__main__":
    keep_alive()  # تشغيل السيرفر 24/7
    client.run(DISCORD_TOKEN)
