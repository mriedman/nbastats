import os
import json
import urllib.parse
from collections import defaultdict
import numpy as np
import warnings
import matplotlib.pyplot as plt
from nbacom.k import *
import sklearn.mixture

warnings.simplefilter('error')

gmkws = {'n_components': 10, 'covariance_type': 'full'}

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

cols = sorted(cols)

kd = [i for i in players if players[i][0] == 'Cory Joseph'][0]
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

folder = 'em-multi'

errs = []
for K in range(1, 100):
    print(K)
    K, J = 10, K
    gmkws['n_components'] = K
    gmm = sklearn.mixture.GaussianMixture(**gmkws)
    preds = gmm.fit_predict(arr)
    cs = {i: [] for i in range(K)}
    for i in range(len(preds)):
        cs[preds[i]].append(p_list[i])
    with open('./data/%s/%d.json' % (folder, J), 'w') as f:
        f.write(json.dumps(cs))
    np.savez('./data/%s/%d-params' % (folder, J),
             phi=gmm.weights_, mu=gmm.means_,
             **{'sigma%d' % (i,): gmm.covariances_[i] for i in range(K)}
             )

# fig, ax = plt.subplots()
# ax.plot(list(range(1, 30)), errs)
# plt.savefig('./data/em/em-vals.png')
