import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Bot is Alive"
def run_web_server(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

intents = discord.Intents.all() # Enable ALL intents to stop the guessing game
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"--- BOT IS ONLINE AS {bot.user} ---")

@bot.event
async def on_message(message):
    # This will print EVERY message it sees. If you don't see this in logs, 
    # the bot is not in your server or is not receiving events.
    print(f"DEBUG: I SAW A MESSAGE: {message.content} from {message.author}")

    if message.author.bot:
        return

    # Super aggressive keyword check (bypasses AI for now to test connection)
    if "f-word" in message.content.lower():
        print("DEBUG: KEYWORD DETECTED! Attempting to delete...")
        try:
            await message.delete()
            print("DEBUG: MESSAGE DELETED.")
        except Exception as e:
            print(f"DEBUG: DELETE FAILED: {e}")

Thread(target=run_web_server).start()
bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
