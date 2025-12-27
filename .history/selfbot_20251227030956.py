import sys
from types import ModuleType

from mongo import getuservar


if 'audioop' not in sys.modules:
    dummy_audioop = ModuleType('audioop')
    dummy_audioop.tostereo = lambda *args: None 
    sys.modules['audioop'] = dummy_audioop

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
    print(f'Logged in as {client.user}')
    msg_loop.start()
    status_loop.start()
    if not bump.is_running():
        bump.start()
    if bump.is_running():
        print("its running")

@client.event
async def on_message(message):
    global cooldown_until

    if message.author.bot:
        return

    now = time.time()

    if message.author.id == 1118218807694065684:
        cooldown_until = now + 300

    if message.content.startswith('$treps'):
        await message.channel.send('t!rep <@1118218807694065684>')

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    if message.content.startswith("$shutdown") and message.author.id == 1118218807694065684:
        await message.channel.send("Shutting down")
        await client.close()
    elif message.content.startswith("$shutdown") and message.author.id != 1118218807694065684:
        await message.channel.send("No perms.")

    if message.content.startswith("$wallet"):
        a = getuservar("usd", message.author.id)
        await message.channel.send(f"{message.author.mention} has {a} usd.")


@tasks.loop(seconds=30)
async def msg_loop():
    channel = client.get_channel(1198228961000423486)

    while True:
        try:
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            await channel.send(random_string)
            break
        except discord.errors.DiscordServerError as e:
            print(f"[msg_loop] DiscordServerError: {e} — Retrying in 5s...")
            await asyncio.sleep(5)
        except discord.HTTPException as e:
            print(f"[msg_loop] HTTPException: {e} — Retrying in 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[msg_loop] Unexpected error: {e} — Retrying in 5s...")
            await asyncio.sleep(5)

@tasks.loop(seconds=30)
async def status_loop():
    global status_index
    custom_status = discord.CustomActivity(name=status_messages[status_index % len(status_messages)])
    await client.change_presence(activity=custom_status)
    status_index += 1

@tasks.loop(seconds=6400)
async def bump():
    channel = client.get_channel(1147929783968223233)
    if not channel:
        try:
            channel = await client.fetch_channel(1147929783968223233)
        except:
            return

    try:
        guild = channel.guild
        commands_payload = await channel.application_commands() 
        target_command = None
        for cmd in commands_payload:
            if cmd.application_id == 302050872383242240 and cmd.name == "bump":
                target_command = cmd
                break
        
        if target_command:
            await target_command()

    except AttributeError:
        async for cmd in channel.slash_commands(query="bump"):
            if cmd.application_id == 302050872383242240:
                await cmd()
                return

    except Exception as e:
        print(f"Error: {e}")

        

client.run(TOKEN)
