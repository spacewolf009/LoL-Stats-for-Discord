import discord
import asyncio
import re
import json
import magic8ball
import player_stats

client = discord.Client()

USE_TTS = False

@client.event
async def on_ready():
    print('Logged in as {}'.format(client.user.name))
    print(client.user.id)
    print('------')

bot_commands = {
    '!commands': ('', lambda *_: 'Available commands: ' + ', '.join(bot_commands.keys())),
    '!end': ('', None), # special case
    '!help': ('', lambda *_: 'Use "!commands" to see all available commands'),
}

@client.event
async def on_message(message):
    global USE_TTS, bot_commands
    async def error_message():
        await client.send_message(message.channel, ':middle_finger: Invalid command: {} :middle_finger:'.format(message.content))

    if not message.content.startswith('!'):
        return

    msg = message.content.strip()
    print(msg)

    cmd = msg.split(' ')[0]
    if cmd in bot_commands:
        try:
            if cmd == '!end':
                await client.send_message(message.channel, 'Shutting down...')
                await client.logout()
            else:
                response = bot_commands[cmd][1](msg[len(cmd):])
                if isinstance(response, str) and len(response) > 0:
                    await client.send_message(message.channel, response)
        except Exception as e:
            print(e)
            await client.send_message(message.channel, ':middle_finger: Error executing command: {} :middle_finger:'.format(message.content))
    else:
        await client.send_message(message.channel, ':middle_finger: Unrecognised command: {} :middle_finger:'.format(message.content))
        print(bot_commands)

config = json.loads(open('./config.json').read())

def register_module(module):
    global bot_commands
    cmds = module.register(config)
    for c in cmds:
        if c not in bot_commands:
            assert len(cmds[c]) == 2
            bot_commands[c] = cmds[c]
        else:
            print('Attempted to register duplicate command: "{}"'.format(c))

register_module(magic8ball)
register_module(player_stats)

client.run(config['DiscordToken'])
