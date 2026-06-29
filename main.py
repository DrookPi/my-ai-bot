import discord
from discord.ext import commands
import os
from groq import AsyncGroq
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "AI Engine Online"
def run_web_server(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

intents = discord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix="!", intents=intents)

ai_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", 0))

@bot.event
async def on_ready():
    print(f"🚀 Bot Ready: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot or message.author.id == bot.user.id:
        return

    # DEBUG: See exactly what the AI is thinking in the logs
    print(f"DEBUG: Processing message from {message.author.name}: {message.content}")

    prompt = f"""
    You are an extremely strict moderator. Analyze this message: "{message.content}"
    If it contains any insults, swearing, F-words, or aggressive tones, you MUST reply with only the word: FLAGGED.
    If it is perfectly friendly, reply with: CLEAN.
    Do not output anything else.
    """
    
    try:
        completion = await ai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        decision = completion.choices[0].message.content.strip().upper()
        print(f"DEBUG: AI Decision for '{message.content}' is {decision}")
    except Exception as e:
        print(f"DEBUG: AI Error: {e}")
        decision = "CLEAN"

    if "FLAGGED" in decision:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"🚨 **FLAGGED MESSAGE**\nUser: {message.author}\nContent: {message.content}")
        try:
            await message.delete()
        except:
            print("DEBUG: Could not delete message (missing permissions?)")

Thread(target=run_web_server).start()
bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
