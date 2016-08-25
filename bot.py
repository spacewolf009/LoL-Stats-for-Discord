import discord
import asyncio
import re
import json
from player_stats import PlayerStats

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {}'.format(client.user.name))
    print(client.user.id)
    print('------')
    # await client.send_message(message.channel, 'Hello. Hello. Hello')

@client.event
async def on_message(message):
    if message.content.startswith('!'):
        print(message.content)
    if message.content.startswith('!echo'):
        m = re.match('!echo (\d+) (.*)', message.content)
        if m:
            await asyncio.sleep(min(10, int(m.group(1))))
            await client.send_message(message.channel, m.group(2))
        else:
            await client.send_message(message.channel, 'Invalid command: {}'.format(message, content))
    elif message.content.startswith('!end'):
        await client.send_message(message.channel, 'Shutting Down')
        await client.logout()
    elif message.content.startswith('!stats'):
        m = re.match('!stats (.+)$', message.content)
        if m:
            stats = player_stats.get_player_summary(m.group(1))
            await client.send_message(message.channel, stats)
        else:
            await client.send_message(message.channel, 'Invalid command: {}'.format(message, content))

config = json.loads(open('./config.json').read())
player_stats = PlayerStats(config['RiotApiKey'])

client.run(config['DiscordToken'])
