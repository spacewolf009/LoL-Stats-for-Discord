import json
import asyncio
from urllib.request import urlopen

stats_url = 'https://oce.api.pvp.net/api/lol/oce/v1.3/stats/by-summoner/{}/ranked?season=SEASON2016&api_key={}'
ids_url = 'https://oce.api.pvp.net/api/lol/oce/v1.4/summoner/by-name/{}?api_key={}'

class PlayerStats:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_player_summary(self, summoner_name):
        # First get the player's id from their name
        player_info = json.loads(urlopen(ids_url.format(summoner_name, self.api_key)).read().decode())
        player_id = player_info[summoner_name]['id']
        summoner_name = player_info[summoner_name]['name']

        # Request stats for the player
        stats = json.loads(urlopen(stats_url.format(player_id, self.api_key)).read().decode())
        stats = next(c for c in stats['champions'] if c['id'] == 0)['stats']
        # Return a summary
        wins = stats['totalSessionsWon']
        losses = stats['totalSessionsLost']
        summary = 'This season {} has {} wins and {} losses ({:1.1f}% winrate)'.format(summoner_name, wins, losses, wins / (wins + losses) * 100)
        return summary

