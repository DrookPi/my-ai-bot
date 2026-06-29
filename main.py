import discord
from discord.ext import commands
import os
from groq import Groq
from flask import Flask
from threading import Thread

# 1. Trick Render into keeping the bot alive 24/7
app = Flask('')

@app.route('/')
def home():
    return "AI Bot is running, boss!"

def run_web_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# 2. Initialize AI Client and Discord Bot using environment variables
ai_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

SECRET_LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", 0))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} | AI Mod active, boss.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Advanced prompt to check for arguments and toxic slang
    prompt = f"""
    Analyze the following Discord message. Detect if it contains:
    1. Harsh slangs or slurs.
    2. The start or escalation of an aggressive argument/fight between members.
    3. Discord ToS violations.
    
    Message: "{message.content}"
    
    Respond with exactly ONE word: 'FLAGGED' or 'CLEAN'. Do not explain your reasoning.
    """
    
    try:
        chat_completion = ai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        ai_response = chat_completion.choices[0].message.content.strip()
    except Exception:
        ai_response = "CLEAN" # Fail-safe if API hiccups

    if "FLAGGED" in ai_response:
        log_channel = bot.get_channel(SECRET_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="🚨 AI Auto-Mod Deletion", color=discord.Color.red())
            embed.add_field(name="User", value=f"{message.author.mention}", inline=False)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="Flagged Message", value=message.content, inline=False)
            await log_channel.send(embed=embed)
        
        await message.delete()
        return

    await bot.process_commands(message)

# Start the web server thread, then launch the bot
Thread(target=run_web_server).start()
bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
