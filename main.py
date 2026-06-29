import discord
from discord.ext import commands
import os
from groq import AsyncGroq
from flask import Flask
from threading import Thread

# Initialize the Flask web application to keep the Render container awake
app = Flask('')

@app.route('/')
def home():
    return "AI Advanced Core Engine is online, boss!"

def run_web_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# Set up explicit intents so Discord passes text message data to our code
intents = discord.Intents.default()
intents.message_content = True  

bot = commands.Bot(command_prefix="!", intents=intents)

# Set up the Async AI connection client
groq_key = os.environ.get("GROQ_API_KEY")
ai_client = AsyncGroq(api_key=groq_key)

# Safely parse the secret logging channel ID from environment variables
LOG_CHANNEL_ENV = os.environ.get("LOG_CHANNEL_ID", "0")
try:
    SECRET_LOG_CHANNEL_ID = int(LOG_CHANNEL_ENV)
except ValueError:
    SECRET_LOG_CHANNEL_ID = 0

@bot.event
async def on_ready():
    print("==================================================")
    print(f"🚀 SUCCESS: Logged in as {bot.user.name}")
    print(f"🎯 Target Log Channel ID Configured: {SECRET_LOG_CHANNEL_ID}")
    print("🧠 Advanced AI Auto-Mod system is fully active, boss.")
    print("==================================================")

@bot.event
async def on_message(message):
    # Ignore background automated bot traffic to avoid loops
    if message.author.bot:
        return

    # Loud Console Logging: Shows exactly what the bot sees in Render logs
    print(f"\n[NEW MESSAGE] Channel: #{message.channel.name} | Author: {message.author.name}: '{message.content}'")

    # Comprehensive structural system prompt for Llama-3 parsing
    prompt = f"""
    Analyze the following Discord message for content moderation. 
    Detect if it matches any of these categories:
    1. Severe toxicity, harsh slangs, personal insults, or slurs.
    2. The initiation, execution, or escalation of an aggressive argument/fight between server members.
    3. Direct violations of Discord Terms of Service.
    
    Message to evaluate: "{message.content}"
    
    Output exactly one word: 'FLAGGED' if it violates the rules, or 'CLEAN' if it is safe. Do not provide any markdown, formatting, punctuation, or explanation.
    """

    print("-> Forwarding text payload to Groq AI engine...")
    try:
        chat_completion = await ai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        raw_response = chat_completion.choices[0].message.content
        # Convert response to uppercase and strip formatting artifacts
        ai_response = raw_response.strip().upper()
        print(f"-> AI Raw Response: '{raw_response}' | Normalized Decision: {ai_response}")
    except Exception as e:
        print(f"❌ AI ENGINE ERROR: Connection failed with Groq backend. Details: {e}")
        ai_response = "CLEAN"

    # Robust matching check that triggers if 'FLAGGED' appears anywhere in the output
    if "FLAGGED" in ai_response:
        print(f"🚨 SEVERE CONTENT DETECTED: Execution action triggered for user {message.author.name}!")
        
        # Check local channel cache first
        log_channel = bot.get_channel(SECRET_LOG_CHANNEL_ID)
        
        # Direct API Fallback: If cache is empty, forcefully download channel object from Discord
        if log_channel is None and SECRET_LOG_CHANNEL_ID != 0:
            print("-> Log channel missing from cache. Querying Discord API directly...")
            try:
                log_channel = await bot.fetch_channel(SECRET_LOG_CHANNEL_ID)
            except Exception as fetch_err:
                print(f"❌ API FETCH ERROR: Cannot resolve target logging channel. Details: {fetch_err}")

        if log_channel:
            try:
                embed = discord.Embed(title="🚨 AI Advanced Auto-Mod Deletion", color=discord.Color.red())
                embed.add_field(name="User", value=message.author.mention, inline=False)
                embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                embed.add_field(name="Flagged Message", value=message.content, inline=False)
                embed.set_footer(text="Context Analysis Engine Core | Llama-3")
                await log_channel.send(embed=embed)
                print("-> Automated log embed successfully transmitted to target channel.")
            except Exception as log_error:
                print(f"❌ DISCORD LOGGING ERROR: Failed to dispatch log embed message. Details: {log_error}")
        else:
            print(f"⚠️ CONFIGURATION ERROR: Invalid or missing LOG_CHANNEL_ID variable. Embed skipped.")

        # Execute target message deletion
        try:
            await message.delete()
            print("-> Message successfully purged from channel history.")
        except discord.Forbidden:
            print("⚠️ PERMISSION DENIED: Unable to delete message. (This is normal when testing as the Server Owner, or if the bot lacks 'Manage Messages' permissions).")
        except Exception as delete_error:
            print(f"❌ PURGE FAILURE: Unexpected deletion error. Details: {delete_error}")
        return

    await bot.process_commands(message)

# Run the system layers concurrently
print("Initializing background web hosting layer...")
Thread(target=run_web_server).start()

print("Launching main Discord Gateway connection...")
bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
