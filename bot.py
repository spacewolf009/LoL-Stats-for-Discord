import discord
import asyncio
import re
import json
import magic8ball
from player_stats import PlayerStats
from lol_data.data import DataProvider

client = discord.Client()

USE_TTS = False

@client.event
async def on_ready():
    print('Logged in as {}'.format(client.user.name))
    print(client.user.id)
    print('------')

def shutdown(*_):
    global client
    # await client.logout()
    return asyncio.get_event_loop().run_until_complete(client.logout())

bot_commands = {
    # '!ask': (''),
    '!commands': ('', lambda *_: 'Available commands: ' + ', '.join(bot_commands.keys())),
    # '!echo': (''),
    '!end': ('', shutdown),
    # '!game': (''),
    '!help': ('', lambda *_: 'Use "!commands" to see all available commands'),
    # '!speak': (''), # one day, maybe
    # '!stats': (''),
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
            response = bot_commands[cmd][1](msg[len(cmd):])
            if isinstance(response, str) and len(response) > 0:
                await client.send_message(message.channel, response)
        except Exception as e:
            print(e)
            await client.send_message(message.channel, ':middle_finger: Error executing command: {} :middle_finger:'.format(message.content))
    else:
        await client.send_message(message.channel, ':middle_finger: Unrecognised command: {} :middle_finger:'.format(message.content))
        print(bot_commands)

    # if msg.startswith('!echo'):
    #     m = re.match('!echo (\d+) (.*)', msg)
    #     if m:
    #         await asyncio.sleep(min(10, int(m.group(1))))
    #         await client.send_message(message.channel, m.group(2))
    #     else:
    #         await error_message()
    # elif msg.startswith('!end'):
    #     await client.send_message(message.channel, 'Shutting Down')
    #     await client.logout()
    # elif msg.startswith('!stats'):
    #     m = re.match('!stats (.+)$', msg)
    #     if m:
    #         stats = player_stats.get_player_summary(m.group(1).replace(' ', ''))
    #         await client.send_message(message.channel, stats, tts=USE_TTS)
    #     else:
    #         await error_message()
    # elif msg.startswith('!game'):
    #     m = re.match('!game (.+)$', msg)
    #     if m:
    #         current = player_stats.get_current_match(m.group(1).replace(' ', ''))
    #         await client.send_message(message.channel, current)
    #     else:
    #         await error_message()
    # elif msg.startswith('!ask') and msg.endswith('?'):
    #     await client.send_message(message.channel, ball.ask(), tts=USE_TTS)
    # elif msg.startswith('!speak'):
    #     USE_TTS = not USE_TTS
    # else:
    #     await error_message()

config = json.loads(open('./config.json').read())
# provider = DataProvider(config['RiotApiKey'])
# player_stats = PlayerStats(provider)

def register_module(cmds):
    global bot_commands
    for c in cmds:
        if c not in bot_commands:
            assert len(cmds[c]) == 2
            bot_commands[c] = cmds[c]
        else:
            print('Attempted to register duplicate command: "{}"'.format(c))

register_module(magic8ball.register(config))

client.run(config['DiscordToken'])
