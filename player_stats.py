import json
from urllib.request import urlopen
from urllib.error import HTTPError
from functools import reduce

base_url = 'https://oce.api.pvp.net/api/lol/oce/'
stats_url = base_url + 'v1.3/stats/by-summoner/{}/ranked?season=SEASON2016&api_key={}'
ids_url = base_url + 'v1.4/summoner/by-name/{}?api_key={}'
ranked_url = base_url + 'v2.5/league/by-summoner/{}/entry?api_key={}'
current_match_url = 'https://oce.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/OC1/{}?api_key={}'

class PlayerStats:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_player_by_name(self, summoner_name):
        summoner_name = summoner_name.replace(' ', '')
        player_info = json.loads(urlopen(ids_url.format(summoner_name, self.api_key)).read().decode())
        if summoner_name  in player_info:
            return player_info[summoner_name]
        else: # Handle recent name changes - search with the old name but get the new name (can't seach with the new name if the change was recent)
            return player_info[next(k for k in player_info)]

    def get_player_stats(self, player_id):
        stats = json.loads(urlopen(stats_url.format(player_id, self.api_key)).read().decode())
        return next(c for c in stats['champions'] if c['id'] == 0)['stats']

    def get_player_ranking(self, player_id):
        return json.loads(urlopen(ranked_url.format(player_id, self.api_key)).read().decode())

    def get_player_summary(self, summoner_name):
        try:
            player_summary = {}
            # First get the player's id from their name
            player_info = self.get_player_by_name(summoner_name)
            player_id = player_info['id']
            player_summary['summoner_name'] = player_info['name']

            # Request stats for the player
            stats = self.get_player_stats(player_id)
            player_summary['wins'] = wins = stats['totalSessionsWon']
            player_summary['losses'] = losses = stats['totalSessionsLost']
            player_summary['winrate'] = wins / (wins + losses) * 100

            # Get ranked league/tier
            ranked_info = self.get_player_ranking(player_id)
            player_summary['tier'] = ranked_info[str(player_id)][0]["tier"].capitalize()
            player_summary['division'] = ranked_info[str(player_id)][0]["entries"][0]['division']
            player_summary['current_lp'] = ranked_info[str(player_id)][0]["entries"][0]['leaguePoints']

            summary = 'This season {summoner_name} ({tier} {division}) has {wins} wins and {losses} losses ({winrate:1.1f}% winrate)'.format(**player_summary)
            return summary
        except HTTPError as e:
            return 'An error occured getting stats for {}'.format(summoner_name)

    def get_current_match(self, summoner_name):
        try:
            player_info = self.get_player_by_name(summoner_name)
            player_id = player_info['id']

            current_match = json.loads(urlopen(current_match_url.format(player_id, self.api_key)).read().decode())

            # print(current_match)

            players = sorted(current_match['participants'], key=lambda x: x['teamId'])
            output = ''
            for i, p in enumerate(players):
                if i == len(players) // 2:
                    output += '\n'
                try:
                    player_id = self.get_player_by_name(p['summonerName'])['id']
                    ranked_info = self.get_player_ranking(player_id)
                    tier = ranked_info[str(player_id)][0]["tier"].capitalize()
                    division = ranked_info[str(player_id)][0]["entries"][0]['division']
                    current_lp = ranked_info[str(player_id)][0]["entries"][0]['leaguePoints']
                    output += '{} ({} {} {} LP)\n'.format(p['summonerName'], tier, division, current_lp)
                except HTTPError:
                    output += '{}\n'.format(p['summonerName'])

            return output
        except HTTPError as e:
            if e.code == 404:
                return 'Could not find a game in progress for {}'.format(summoner_name)
            else:
                print(e)
                return 'An error occured getting current game data for {}'.format(summoner_name)
