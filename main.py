import discord
from discord.ext import commands
import os
from groq import AsyncGroq  # Changed to Async client to stop blocking
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "AI Bot is running, boss!"

def run_web_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# Initialize the ASYNC Groq client
ai_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SECRET_LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", 0))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} | AI Mod active, boss.")

@bot.event
async def on_message(message):
    if message.author.bot or message.webhook_id:
        return

    print(f"Processing message from {message.author.name}: {message.content}")

    prompt = f"""
    Analyze the following Discord message. Detect if it contains:
    1. Harsh slangs or slurs.
    2. The start or escalation of an aggressive argument/fight between members.
    3. Discord ToS violations.
    
    Message: "{message.content}"
    
    Respond with exactly ONE word: 'FLAGGED' or 'CLEAN'. Do not explain your reasoning.
    """
    
    try:
        # Using await here keeps the bot responsive and fast
        chat_completion = await ai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        ai_response = chat_completion.choices[0].message.content.strip()
        print(f"AI response received: {ai_response}")
    except Exception as e:
        # CRUCIAL: This will now print the EXACT error to your Render logs if the AI fails
        print(f"GROQ AI ERROR: {e}")
        ai_response = "CLEAN"

    if "FLAGGED" in ai_response:
        log_channel = bot.get_channel(SECRET_LOG_CHANNEL_ID)
        if log_channel:
            try:
                embed = discord.Embed(title="🚨 AI Auto-Mod Deletion", color=discord.Color.red())
                embed.add_field(name="User", value=f"{message.author.mention}", inline=False)
                embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                embed.add_field(name="Flagged Message", value=message.content, inline=False)
                await log_channel.send(embed=embed)
                print("Log sent to private channel.")
            except Exception as log_error:
                print(f"Failed to send log message to channel: {log_error}")
        
        try:
            await message.delete()
        except discord.Forbidden:
            print(f"Discord prevented deletion (This is normal for the Server Owner).")
        except Exception as delete_error:
            print(f"Unexpected deletion error: {delete_error}")
        return

    await bot.process_commands(message)

Thread(target=run_web_server).start()
bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
