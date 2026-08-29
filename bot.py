import os
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load local .env when developing (optional)
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shadowbot")

intents = discord.Intents.default()
intents.message_content = True  # ensure this intent is enabled in Developer Portal

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)


@bot.event
async def on_ready():
    logger.info("✅ ShadowBot is online as %s", bot.user)


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("🏓 Pong!")


@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Respond to "Halo" message
    if message.content.lower() == "halo":
        await message.reply("Hey there! 👋")
    
    # Process commands
    await bot.process_commands(message)


def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("❌ DISCORD_TOKEN is missing! Set it as an environment variable or in a .env file.")
        return

    try:
        bot.run(token)
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user (KeyboardInterrupt).")
    except Exception:
        logger.exception("Bot stopped with an exception.")


if __name__ == "__main__":
    main()
