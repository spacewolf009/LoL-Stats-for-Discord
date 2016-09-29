import json
from urllib.request import urlopen
from urllib.error import HTTPError
from functools import reduce

base_url = 'https://oce.api.pvp.net/api/lol/oce/'
stats_url = base_url + 'v1.3/stats/by-summoner/{}/ranked?season=SEASON2016&api_key={}'
ids_url = base_url + 'v1.4/summoner/by-name/{}?api_key={}'
ranked_url = base_url + 'v2.5/league/by-summoner/{}/entry?api_key={}'
current_match_url = 'https://oce.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/OC1/{}?api_key={}'
match_history_url = base_url + 'v2.2/matchlist/by-summoner/{}?rankedQueues=TEAM_BUILDER_DRAFT_RANKED_5x5&seasons=SEASON2016&api_key={}'

class DataProvider:
    def __init__(self, api_key):
        self.api_key = api_key

    # could be cached medium-long term
    def get_player_by_name(self, summoner_name):
        summoner_name = summoner_name.replace(' ', '') # spaces are irrelevant
        player_info = json.loads(urlopen(ids_url.format(summoner_name, self.api_key)).read().decode())
        if len(player_info) == 1:
            return player_info[next(k for k in player_info)]
        else:
            raise Exception("Player \"{}\" not found".format(summoner_name))

    def get_player_stats(self, player_id):
        stats = json.loads(urlopen(stats_url.format(player_id, self.api_key)).read().decode())
        return next(c for c in stats['champions'] if c['id'] == 0)['stats']

    def get_current_game(self, summoner_name):
        player_info = self.get_player_by_name(summoner_name)
        player_id = player_info['id']

        current_match = json.loads(urlopen(current_match_url.format(player_id, self.api_key)).read().decode())
        return current_match

    def get_match_history_by_player(self, player_id):
        matches = match_history = json.loads(urlopen(match_history_url.format(player_id, self.api_key)).read().decode())
        return matches

    def get_player_ranking(self, player_id):
        return json.loads(urlopen(ranked_url.format(player_id, self.api_key)).read().decode())

