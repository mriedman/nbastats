import os
import json
import urllib.parse
from collections import defaultdict
import numpy as np
import warnings
import matplotlib.pyplot as plt

warnings.simplefilter('error')

files = os.scandir('./data/synergyplaytypes')
data = {}
for file in files:
    fn = file.name
    if fn == '.DS_Store':
        continue
    with open('./data/synergyplaytypes/%s' % (fn,)) as f:
        data[fn[:-5]] = json.loads(f.read())

playerpcts = defaultdict(dict)
tms = {}
players = {}
play_type_qs = {'LeagueID': '00', 'PerMode': 'Totals', 'PlayerOrTeam': 'P', 'SeasonType': 'Regular Season', 'SeasonYear': '2020-21', 'TypeGrouping': 'offensive'}

cols = []
for t in data:
    tl = urllib.parse.parse_qs(t)
    # print(tl)
    n = True
    for k in play_type_qs:
        if tl[k][0] != play_type_qs[k]:
            # print('111')
            n = False
    if not n:
        continue
    td = data[t]['resultSets'][0]
    head = td['headers']
    body = td['rowSet']

    pct = head.index('POSS_PCT')
    pid = head.index('PLAYER_ID')
    pn = head.index('PLAYER_NAME')
    pos = head.index('POSS')
    tm = head.index('TEAM_ABBREVIATION')

    cols.append(tl['PlayType'][0])

    for i in body:
        playerpcts[(i[pn], i[tm], i[pid])][tl['PlayType'][0]] = [i[pct], i[pos]]
        players[(i[pn], i[tm], i[pid])] = [i[pn], i[tm]]
        tms[i[tm]] = {j: [] for j in range(10)}

p_list = [i for i in players.keys() if sum(j[1] for j in playerpcts[i].values()) >= 100]
arr = np.zeros((len(p_list), len(cols)))
cols = sorted(cols)
print(cols)
print([playerpcts[i] for i in playerpcts if i[0] == 'Giannis Antetokounmpo'])
# exit(0)
for i0, i in enumerate(p_list):
    for j, k in enumerate(cols):
        if k in playerpcts[i]:
            arr[i0, j] = playerpcts[i][k][0]
with open('./data/k/10.json') as f:
    grps = json.load(f)
'''dist = np.array([np.linalg.norm(arr - mu.reshape(1, -1), axis=1) for mu in cent])
min_dist_vals = np.sum(np.min(dist, axis=0))
cent0 = (cent, min_dist_vals)
min_dist = np.argmin(dist, axis=0).reshape(-1)
grps = {i: [] for i in range(10)}
for i, j in enumerate(min_dist):
    grps[j].append(p_list[i])'''

for i in grps:
    for j in grps[i]:
        tms[players[tuple(j)][1]][int(i)].append(players[tuple(j)][0])

tm_list = sorted(tms.keys())
tm2 = np.zeros((len(tm_list), 10))
for i0, i in enumerate(tm_list):
    for j in range(10):
        tm2[i0, j] = len(tms[i][j])

for i0, i in enumerate(tm_list):
    print(i, ':', tm2[i0])

for i in range(10):
    cur_tm = tm_list[np.argmax(tm2[:, i]).squeeze()]
    print(i, ':', cur_tm, ',', int(np.max(tm2[:, i])), ',', tms[cur_tm][i])

for i in range(10):
    pass

print(tms['BKN'])

print([players[tuple(i)] for i in grps['4']])
