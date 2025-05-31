import discord
import asyncio
from discord.ext import tasks
import time
import os
import string
import random

TOKEN = os.getenv("a")
client = discord.Client()

cooldown_until = 0
your_id = 1118218807694065684

# Status message list for rotation
status_messages = [
    "I love you",
    "I love animals",
    "I love food",
    "I love women",
    "I love men"
]
status_index = 0

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    msg_loop.start()
    status_loop.start()

@client.event
async def on_message(message):
    global cooldown_until

    if message.author.bot:
        return

    now = time.time()

    if message.author.id == your_id:
        cooldown_until = now + 300

    if message.content.startswith('$treps'):
        await message.channel.send('t!rep <@1118218807694065684>')

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

@tasks.loop(seconds=30)
async def msg_loop():
    channel = client.get_channel(1198228961000423486)
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    await channel.send(random_string)

@tasks.loop(seconds=30)
async def status_loop():
    global status_index
    # Rotate through custom status messages
    custom_status = discord.CustomActivity(name=status_messages[status_index % len(status_messages)])
    await client.change_presence(activity=custom_status)
    status_index += 1

client.run(TOKEN)