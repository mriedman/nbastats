import os
import json
import urllib.parse
from collections import defaultdict
import numpy as np
import warnings
import matplotlib.pyplot as plt
from nbacom.k import *

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
players = {}
play_type_qs = {'LeagueID': '00', 'PerMode': 'Totals', 'PlayerOrTeam': 'P', 'SeasonType': 'Regular Season', 'SeasonYear': '2020-21', 'TypeGrouping': 'defensive'}

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

cols = sorted(cols)


kd = [i for i in players if players[i][0] == 'Bruce Brown'][0]
print(playerpcts[kd])
p_list = [i for i in players.keys() if sum(j[1] for j in playerpcts[i].values()) >= 100]
arr = np.zeros((len(p_list), len(cols)))
for i0, i in enumerate(p_list):
    for j, k in enumerate(cols):
        if k in playerpcts[i]:
            arr[i0, j] = playerpcts[i][k][0]
print([players[i] for i in p_list])
print(arr.shape)
print(cols)
# exit(0)

# K = 10
errs = []
for K in range(1, 30):
    cents = []
    for _ in range(50):
        cent = init_centroids(K, arr)
        cent = update_centroids(cent, arr)
        cents.append(cent)
    cent0 = (cents[0], np.infty)
    cs = []
    for cent in cents:
        dist = np.array([np.linalg.norm(arr - mu.reshape(1, -1), axis=1) for mu in cent])
        min_dist_vals = np.sum(np.min(dist, axis=0))
        if min_dist_vals > cent0[1]:
            continue
        cent0 = (cent, min_dist_vals)
        min_dist = np.argmin(dist, axis=0).reshape(-1)
        cs = {i: [] for i in range(K)}
        for i, j in enumerate(min_dist):
            cs[j].append(p_list[i])
    '''for j in cs:
        print(cs[j])'''
    with open('./data/k/%d-d.json' % (K,), 'w') as f:
        f.write(json.dumps(cs))
    np.savetxt('./data/k/%d-d-cents.json' % (K,), cent0[0])
    print([K, cent0[1]])
    errs.append(cent0[1])

fig, ax = plt.subplots()
ax.plot(list(range(1, 30)), errs)
plt.savefig('./data/k/def-k-vals.png')
