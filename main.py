import discord
from discord.ext import commands
import os
from groq import AsyncGroq

# 1. Define strict, required intents only
intents = discord.Intents.default()
intents.message_content = True 
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 2. Initialize AI client
ai_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

@bot.event
async def on_ready():
    print(f"--- BOT CONNECTED AS {bot.user} ---")
    print(f"--- SERVER COUNT: {len(bot.guilds)} ---")
    # Verify bot can see messages
    for guild in bot.guilds:
        print(f"--- BOT IS INSIDE: {guild.name} ---")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Log every single message heard to verify connection
    print(f"DEBUG: I HEARD: '{message.content}' from {message.author}")

    # Aggressive keyword-based safety net (always works)
    bad_words = ["fuck", "idiot", "hate"] # Add your list here
    if any(word in message.content.lower() for word in bad_words):
        try:
            await message.delete()
            print("DEBUG: DELETE SUCCESSFUL")
        except discord.Forbidden:
            print("DEBUG: PERMISSION DENIED - Bot needs 'Manage Messages' permission!")
        return

    # Advanced AI Analysis (if keyword check passes)
    await bot.process_commands(message)

bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
