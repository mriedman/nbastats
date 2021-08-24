import ssl
import requests
import json
import urllib.parse
import numpy as np
from collections import defaultdict

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

lineup_qs = {'ClutchTime': 'Last 5 Minutes',
             'Conference': '',
             'DateFrom': '',
             'DateTo': '',
             'Division': '',
             'GameSegment': '',
             'GroupQuantity': '2',
             'LastNGames': '0',
             'LeagueID': '00',
             'LineupsVisuals': 'NET_RATING',
             'Location': '',
             'MeasureType': 'Base',
             'MinutesMin': '25',
             'Month': '0',
             'OpponentTeamID': '0',
             'Outcome': '',
             'PORound': '0',
             'PaceAdjust': 'N',
             'PerMode': 'PerGame',
             'Period': '0',
             'PlusMinus': 'N',
             'Rank': 'N',
             'Season': '2020-21',
             'SeasonSegment': '',
             'SeasonType': 'Regular Season',
             'ShotClockRange': '',
             'TeamID': '0',
             'VsConference': '',
             'VsDivision': ''}


req = requests.get("https://stats.nba.com/stats/leaguelineupviz?%s" % (urllib.parse.urlencode(lineup_qs),), headers=headers)
res = json.loads(req.text)
print(res['resultSets'][0]['headers'])
# print(res['resultSets'][0]['rowSet'][4])

rows = res['resultSets'][0]['rowSet']
head = res['resultSets'][0]['headers']

mp = head.index('MIN')
nr = head.index('NET_RATING')
ofr = head.index('OFF_RATING')
dr = head.index('DEF_RATING')
pc = head.index('PACE')

K = 10

with open('./data/em/{}.json'.format(K)) as f:
    grps = json.load(f)

p_grps = {}
for i in grps:
    for j in grps[i]:
        p_grps[(j[1], str(j[2]))] = (i, j)

combos = {}

for row in rows:
    ids = row[0].split('-')[1:-1]
    try:
        l_type = tuple(sorted([p_grps[(row[3], i)][0] for i in ids]))
    except:
        continue
    poss = round(row[pc] * row[mp] / 48)
    if l_type not in combos:
        combos[l_type] = [l_type, np.array([row[ofr] / 100 * poss, poss])]
    else:
        combos[l_type][1] += [row[ofr] / 100 * poss, poss]

'''vals = combos.values()
# s_vals = sorted(vals, key=lambda x: -x[1][1])
s_vals = sorted(vals, key=lambda i: i[1][0] / i[1][1] * 100)
for i in [j for j in s_vals if j[1][1] > 200][:10]:
    print(i[0])
    print([i[1][1], round(i[1][0] / i[1][1] * 100, 1)])

print()

for i in p_grps:
    if i[0] == 'BKN':
        print(p_grps[i])'''

print(' ' * 4, end='')
for i in range(K):
    print('%3d  ' % (i, ), end=' ')
print()

for i in range(K):
    print('%2d:' % (i,), end=' ')
    for j in range(K):
        tup = tuple(sorted((str(i), str(j))))
        if tup in combos and combos[tup][1][1] > 5e3:
            print('%5.1f' % (round(combos[tup][1][0] / combos[tup][1][1] * 100, 1)), end=' ')
        else:
            print('%5.1f' % (-1.,), end=' ')
    print()
