import discord
import asyncio
import re
import json
from player_stats import PlayerStats
from magic8ball import Magic8Ball
from lol_data.data import DataProvider

client = discord.Client()

USE_TTS = False

ball = Magic8Ball()

@client.event
async def on_ready():
    print('Logged in as {}'.format(client.user.name))
    print(client.user.id)
    print('------')
    # await client.send_message(message.channel, 'Hello. Hello. Hello')

@client.event
async def on_message(message):
    global USE_TTS
    async def error_message():
        await client.send_message(message.channel, ':middle_finger: Invalid command: {} :middle_finger:'.format(message.content))

    if not message.content.startswith('!'):
        return

    msg = message.content.strip()
    print(msg)

    if msg.startswith('!echo'):
        m = re.match('!echo (\d+) (.*)', msg)
        if m:
            await asyncio.sleep(min(10, int(m.group(1))))
            await client.send_message(message.channel, m.group(2))
        else:
            await error_message()
    elif msg.startswith('!end'):
        await client.send_message(message.channel, 'Shutting Down')
        await client.logout()
    elif msg.startswith('!stats'):
        m = re.match('!stats (.+)$', msg)
        if m:
            stats = player_stats.get_player_summary(m.group(1).replace(' ', ''))
            await client.send_message(message.channel, stats, tts=USE_TTS)
        else:
            await error_message()
    elif msg.startswith('!game'):
        m = re.match('!game (.+)$', msg)
        if m:
            current = player_stats.get_current_match(m.group(1).replace(' ', ''))
            await client.send_message(message.channel, current)
        else:
            await error_message()
    elif msg.startswith('!ask') and msg.endswith('?'):
        await client.send_message(message.channel, ball.ask(), tts=USE_TTS)
    elif msg.startswith('!speak'):
        USE_TTS = not USE_TTS
    else:
        await error_message()

config = json.loads(open('./config.json').read())
provider = DataProvider(config['RiotApiKey'])
player_stats = PlayerStats(provider)

client.run(config['DiscordToken'])
