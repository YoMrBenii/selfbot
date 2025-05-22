import discord
import asyncio
from discord.ext import tasks
import time
import sys
import os

TOKEN = os.getenv("a")
client = discord.Client()

cooldown_until = 0
your_id = 1118218807694065684

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    msg_loop.start()

@client.event
async def on_message(message):
    global cooldown_until

    if message.author.bot:
        return

    now = time.time()

    if message.author.id == your_id:
        cooldown_until = now + 300

    if "<@1118218807694065684>" in message.content:
        if now >= cooldown_until:
            await message.channel.send("MrBenii is inactive, ask рheо if you have problems")

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

@tasks.loop(seconds=30)
async def msg_loop():
    channel = client.get_channel(1198228961000423486)
    await channel.send("woooo")

client.run('TOKEN')
