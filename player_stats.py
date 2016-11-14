from urllib.error import HTTPError
from functools import reduce
from lol_data.data import DataProvider

BLUE_SIDE, PURPLE_SIDE = 100, 200

class PlayerStats:
    def __init__(self, provider):
        # self.api_key = api_key
        self.provider = provider

    def get_player_summary(self, summoner_name):
        try:
            player_summary = {}
            # First get the player's id from their name
            player_info = self.provider.get_player_by_name(summoner_name)
            player_id = player_info['id']
            player_summary['summoner_name'] = player_info['name']

            # Request stats for the player
            stats = self.provider.get_player_stats(player_id)
            player_summary['wins'] = wins = stats['totalSessionsWon']
            player_summary['losses'] = losses = stats['totalSessionsLost']
            player_summary['winrate'] = wins / (wins + losses) * 100

            # Get ranked league/tier
            ranked_info = self.provider.get_player_ranking(player_id)
            player_summary['tier'] = ranked_info[str(player_id)][0]["tier"].capitalize()
            player_summary['division'] = ranked_info[str(player_id)][0]["entries"][0]['division']
            player_summary['current_lp'] = ranked_info[str(player_id)][0]["entries"][0]['leaguePoints']

            summary = 'This season {summoner_name} ({tier} {division}) has {wins} wins and {losses} losses ({winrate:1.1f}% winrate)'.format(**player_summary)
            return summary
        except HTTPError as e:
            return 'An error occured getting stats for {}'.format(summoner_name)

    def get_current_match(self, summoner_name):
        try:
            current_match = self.provider.get_current_game(summoner_name)

            players = sorted(current_match['participants'], key=lambda x: x['teamId'])
            output = ''
            for i, p in enumerate(players):
                if i == len(players) // 2:
                    output += '\n'
                try:
                    player_id = self.provider.get_player_by_name(p['summonerName'])['id']
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

def register(global_config):
    player_stats = PlayerStats(DataProvider(global_config['RiotApiKey']))

    return {
        '!stats': ('', lambda msg: player_stats.get_player_summary(msg.replace(' ', ''))),
        '!game': ('', lambda msg: player_stats.get_current_match(msg.replace(' ', '')))
        # '!lg: ('')'
    }
