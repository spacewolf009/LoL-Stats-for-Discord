import discord
import asyncio
import re
import json

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

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

config = json.loads(open('./config.json').read())

client.run(config['token'])
