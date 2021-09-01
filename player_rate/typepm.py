import numpy as np
import pickle
from collections import defaultdict
import sqlite3
from scipy.special import comb
from sklearn.linear_model import LinearRegression


def calc_tuple_num(num_cats, tup_size):
    return int(comb(tup_size + num_cats - 1, tup_size))


def get_tuple_dict(num_cats, tup_size):
    td = {}
    cur = np.zeros(tup_size, int)
    x = calc_tuple_num(num_cats, tup_size)
    for i in range(x):
        td[tuple(cur)] = i
        k = tup_size - 1
        while True:
            if i == x - 1:
                break
            cur[k] += 1
            if cur[k] < num_cats:
                for k1 in range(k + 1, tup_size):
                    cur[k1] = cur[k]
                break
            k -= 1
    return td


def get_lineups_from_base(base, perf, min_secs=100):
    # min_secs is tenths of a second
    base1, perf1 = base[perf[:, 2] >= min_secs], perf[perf[:, 2] >= min_secs]
    players = base1.shape[1] // 2
    base_flip = np.concatenate([base1[:, players:], base1[:, :players]], axis=1)
    lineups = np.concatenate([base1, base_flip], axis=0)
    perf2 = np.concatenate([perf1[:, 1:], perf1[:, ::2]], axis=0)
    num = calc_tuple_num(TOT_CATS, NUM_PER_COMBO)
    type_lineups = np.concatenate([lineups,
                                   np.zeros((lineups.shape[0], num))], axis=1)
    for row in type_lineups:
        row[-num:] = poss_tuples[tuple(np.sort(type_array[row[len(player_list):-num] != 0]))]
    return type_lineups, perf2


def fit_model():
    print(np.mean(performance_array, axis=0))

    # print(performance_array[performance_array[:, 0] > 0.05, :])
    # print(lineup_array[:5, :200])

    reg = LinearRegression(fit_intercept=False).fit(lineup_array, performance_array * (7200 * 4) ** (1))
    print(reg.score(lineup_array, performance_array * 7200 * 4))

    pickle.dump(reg, open('type_pm.sav', 'wb'))


'''print(get_tuple_dict(5, 3))
for i in range(6):
    print(calc_tuple_num(10, i))
exit(0)'''

'''with np.load('lineups.npz') as data:
    player_list = data['player_list']'''

'''reg = pickle.load(open('naive_pm.sav', 'rb'))

residuals = performance_array - reg.predict(lineup_array)
ranks = np.argsort(residuals[:, 0])'''

NUM_PER_COMBO = 3
TOT_CATS = 11
poss_tuples0 = get_tuple_dict(TOT_CATS, 5)
poss_tuples1 = get_tuple_dict(TOT_CATS, NUM_PER_COMBO)
poss_tuples = {}
new_line = lambda: np.zeros(calc_tuple_num(TOT_CATS, NUM_PER_COMBO))
bits = np.array([2 ** i for i in range(5)])

for i0 in poss_tuples0:
    i = np.array(i0)
    poss_tuples[i0] = new_line()
    for j in range(2 ** 5):
        on_bits = (j & bits) != 0
        if np.sum(on_bits) == NUM_PER_COMBO:
            new_combo = tuple(np.sort(i[np.where(bits & j != 0)]))
            poss_tuples[i0][poss_tuples1[new_combo]] += 1

'''print(poss_tuples[(1, 3, 4, 4, 9)])
exit(0)

off_type_tuples = defaultdict(lambda: np.zeros(3))
for i in range(lineup_array1.shape[0]):
    print(lineup_array1[i])
    print(performance_array1[i])
    if i > 5:
        break'''

with np.load('lineups.npz') as data:
    lineup_array0 = data['lineup_array']
    performance_array0 = data['performance_array']
    player_list = data['player_list']

con = sqlite3.connect('playerinfo.db')
con.row_factory = sqlite3.Row
cur = con.cursor()

type_array = np.zeros(len(player_list))
cur.execute('SELECT * from players')
for row in cur.fetchall():
    type_array[row['lineup_table_id']] = row['k10cat']

con.close()

print('a')
lineup_array1, performance_array1 = get_lineups_from_base(lineup_array0, performance_array0)

print('b')
sqrts = np.sqrt(performance_array1[:, 1:])
lineup_array, performance_array = lineup_array1 * sqrts, performance_array1[:,:1] / sqrts  # - (113 / 7200 / 4) * sqrts
player_list_rev = {player_list[i]: i for i in range(player_list.shape[0])}

print('c')
fit_model()
