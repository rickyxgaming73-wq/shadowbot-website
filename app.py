import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ ShadowBot is online as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

token = os.getenv("DISCORD_TOKEN")

if not token:
    print("❌ DISCORD_TOKEN is missing!")
else:
    bot.run(token)
