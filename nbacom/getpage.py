import ssl
import requests
import json
import concurrent.futures

ssl._create_default_https_context = ssl._create_unverified_context

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0',
           'Accept': 'application/json, text/plain, */*',
           'Accept-Language': 'en-US,en;q=0.5',
           'Accept-Encoding': 'gzip, deflate, br',
           'x-nba-stats-origin': 'stats',
           'x-nba-stats-token': 'true',
           'Origin': 'https://www.nba.com',
           'Connection': 'keep-alive',
           'Referer': 'https://www.nba.com/'}

def get_info(url):
    req = requests.get(url[1], headers=headers)
    print(req.text)
    return json.loads(req.text)

# Traditional
trd_query_strs = ['College', 'Conference', 'Country', 'DateFrom', 'DateTo', 'Division', 'DraftPick', 'DraftYear', 'GameScope', 'GameSegment', 'Height', 'LastNGames', 'LeagueID', 'Location', 'MeasureType', 'Month', 'OpponentTeamID', 'Outcome', 'PORound', 'PaceAdjust', 'PerMode', 'Period', 'PlayerExperience', 'PlayerPosition', 'PlusMinus', 'Rank', 'Season', 'SeasonSegment', 'SeasonType', 'ShotClockRange', 'StarterBench', 'TeamID', 'TwoWay', 'VsConference', 'VsDivision', 'Weight']

# Playtype
play_types = ['Transition', 'Isolation', 'PRBallHandler', 'PRRollman', 'Postup', 'Spotup', 'Handoff', 'Cut', 'OffScreen', 'OffRebound', 'Misc']
play_type_qs = {'LeagueID': '00', 'PerMode': 'Totals', 'PlayType': 'Isolation', 'PlayerOrTeam': 'P', 'SeasonType': 'Regular Season', 'SeasonYear': '2020-21', 'TypeGrouping': 'defensive'}

play_type_ql = {k: {i: j for i, j in play_type_qs.items()} for k in play_types}
for k in play_types:
    play_type_ql[k]['PlayType'] = k

play_type_vals = ['Regular Season', 'Totals', '']
urls = [(i, 'https://stats.nba.com/stats/synergyplaytypes?%s' % ('&'.join(['%s=%s' % (j, k) for j, k in play_type_ql[i].items()]))) for i in play_types]
for i in urls:
    print(i)

with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    # Start the load operations and mark each future with its URL
    future_to_day = {executor.submit(get_info, url): url for url in urls}
    for future in concurrent.futures.as_completed(future_to_day):
        url = future_to_day[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            with open('./data/synergyplaytypes/%s.json' % (url[1].split('?')[1],), 'w') as f:
                f.write(json.dumps(data))
