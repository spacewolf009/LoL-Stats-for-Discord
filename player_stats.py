import json
# import asyncio
from urllib.request import urlopen
from urllib.error import HTTPError

base_url = 'https://oce.api.pvp.net/api/lol/oce/'
stats_url = base_url + 'v1.3/stats/by-summoner/{}/ranked?season=SEASON2016&api_key={}'
ids_url = base_url + 'v1.4/summoner/by-name/{}?api_key={}'
ranked_url = base_url + 'v2.5/league/by-summoner/{}/entry?api_key={}'

class PlayerStats:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_player_summary(self, summoner_name):
        try:
            player_summary = {}
            # First get the player's id from their name
            player_info = json.loads(urlopen(ids_url.format(summoner_name, self.api_key)).read().decode())
            if summoner_name  in player_info:
                player_id = player_info[summoner_name]['id']
                player_summary['summoner_name'] = player_info[summoner_name]['name']
            else: # Handle recent name changes - search with the old name but get the new name (can't seach with the new name if the change was recent)
                player_id = player_info[next(k for k in player_info)]['id']
                player_summary['summoner_name'] = player_info[next(k for k in player_info)]['name']

            # Request stats for the player
            stats = json.loads(urlopen(stats_url.format(player_id, self.api_key)).read().decode())
            stats = next(c for c in stats['champions'] if c['id'] == 0)['stats']
            player_summary['wins'] = wins = stats['totalSessionsWon']
            player_summary['losses'] = losses = stats['totalSessionsLost']
            player_summary['winrate'] = wins / (wins + losses) * 100

            # Get ranked league/tier
            ranked_info = json.loads(urlopen(ranked_url.format(player_id, self.api_key)).read().decode())
            player_summary['tier'] = ranked_info[str(player_id)][0]["tier"].capitalize()
            player_summary['division'] = ranked_info[str(player_id)][0]["entries"][0]['division']
            player_summary['current_lp'] = division = ranked_info[str(player_id)][0]["entries"][0]['leaguePoints']

            summary = 'This season {summoner_name} ({tier} {division}) has {wins} wins and {losses} losses ({winrate:1.1f}% winrate)'.format(**player_summary)
            return summary
        except HTTPError as e:
            return 'An error occured getting stats for {}'.format(summoner_name)
