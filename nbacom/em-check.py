import numpy as np
import json
from collections import defaultdict
from copy import deepcopy


# Print cov matrix
def print_cov_matrix(K):
    npzfile = np.load('./data/em-def/%d-params.npz' % (K,))
    for i in list(map(list, npzfile['mu'])):
        print(list(map(lambda x: round(x, 2), i)))

    for i in range(K):
        pass
        # print([round(npzfile['sigma%d' % (i,)][j, j], 3) for j in range(11)])


# Positions by team
def pos_by_team(folder, K: str):
    with open('./data/%s/%s.json' % (folder, K)) as f:
        grps = json.load(f)

    tms = defaultdict(list)
    for i in grps['0']:
        tms[i[1]].append(i[0])
    for j in range(5):
        for i in grps[str(j)]:
            tms[i[1]] += []

    print(len(tms.keys()))
    for i in sorted(tms.keys()):
        print(i, ':', len(tms[i]), tms[i])


# Get overlap
def pairwise_overlap(f1: str, K1, f2: str, K2):
    with open('./data/{}/{}.json'.format(f1, K1)) as f:
        grps1 = json.load(f)

    with open('./data/{}/{}.json'.format(f2, K2)) as f:
        grps2 = json.load(f)

    print(' 1\\2', end='')
    for j in grps2:
        print('%2d ' % (int(j),), end='')

    print()
    print('-' * (4 + 3 * K2))

    fun = []
    for i in grps1:
        print('%2d: ' % (int(i),), end='')
        for j in grps2:
            l = [k for k in grps1[i] if k in grps2[j]]
            print('%2d ' % (len(l)), end='')
            if 0 < len(l) <= 4:
                fun.append(((i, j), l))
        print()
    print()
    for i in fun:
        print(i)


def many_way_overlap(fs, Ks, tol=0):
    grps = []
    for f, K in zip(fs, Ks):
        with open('./data/{}/{}.json'.format(f, K)) as f:
            grps.append(json.load(f))

    players = {tuple(i): [] for j in grps[1] for i in grps[1][j]}
    print(len(players.keys()))
    for grp in grps:
        for j in grp:
            for player in grp[j]:
                players[tuple(player)].append(int(j))

    overlap = defaultdict(list)
    for p in players:
        overlap[tuple(players[p])].append(p)

    ok = list(sorted(overlap.keys(), key=lambda x: len(overlap[x])))

    keylist = {i: i0 for i0, i in enumerate(ok)}
    rkl = {i0: [i] for i0, i in enumerate(ok)}
    tols = {}

    for i in ok:
        for j in ok:
            tols[(i, j)] = sum(1 for k, l in zip(i, j) if k != l) <= tol

    for i0, i in enumerate(ok):
        for j0, j in enumerate(ok):
            if not tols[(i, j)]:
                continue
            if keylist[i] == keylist[j]:
                continue
            klj = keylist[j]
            for k in rkl[klj]:
                keylist[k] = keylist[i]
            rkl[keylist[i]] += rkl[klj]
            del rkl[klj]

    def retrieve_players(i):
        return [p for g in rkl[i] for p in overlap[g]]

    ok2 = list(sorted(rkl.keys(), key=lambda x: len(retrieve_players(x))))
    for i in ok2[-1::-1]:
        rpi = retrieve_players(i)
        print(i, ':', len(rpi), ',', rpi)

def many_way_overlap2(fs, Ks, tol=0):
    grps = []
    for f, K in zip(fs, Ks):
        with open('./data/{}/{}.json'.format(f, K)) as f:
            grps.append(json.load(f))

    players = {tuple(i): [] for j in grps[1] for i in grps[1][j]}
    print(len(players.keys()))
    for grp in grps:
        for j in grp:
            for player in grp[j]:
                players[tuple(player)].append(int(j))

    overlap = defaultdict(list)
    for p in players:
        overlap[(p, tuple(players[p]))].append(p)

    ok = list(sorted(overlap.keys(), key=lambda x: len(overlap[x])))

    keylist = {i: i0 for i0, i in enumerate(ok)}
    rkl = {i: [i] for i0, i in enumerate(ok)}
    tols = {}

    for i in keylist:
        for j in keylist:
            tols[(i, j)] = sum(1 for k, l in zip(i[1], j[1]) if k != l) <= tol
            if tols[(i, j)] and i != j:
                rkl[i].append(j)

    def retrieve_players(i):
        return [p for g in rkl[i] for p in overlap[g]]

    ok2 = list(sorted(rkl.keys(), key=lambda x: len(retrieve_players(x))))
    for i in ok2[-1::-1]:
        rpi = retrieve_players(i)
        print(i[0], ':', len(rpi), ',', rpi)

    final = {}
    player_status = {i: (False,) for i in players}
    # for player in ok2[-1::-1]:


# Print centroids
def print_centroids(folder, K):
    a = np.loadtxt('./data/{}/{}-cents.json'.format(folder, K))
    for i in a:
        print([round(j, 2) for j in i])


# Look for group
def find_group(folder, K1, g):
    with open('./data/{}/{}.json'.format(folder, K1)) as f:
        grps1 = json.load(f)

    for K2 in range(1, 30):
        with open('./data/{}/{}.json'.format(folder, K2)) as f:
            grps2 = json.load(f)
        l = []
        for j in grps2:
            l.append((j, len([k for k in grps1[g] if k in grps2[j]])))
            if l[-1][1] == 0:
                l.pop()
        print("%2d" % (K2,), ':', sorted(l, key=lambda x: -x[1]))

many_way_overlap2(['em'] + ['em-multi'] * 100, [10] + list(range(1, 100)), tol=33)
