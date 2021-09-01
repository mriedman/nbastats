import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
import pickle


def get_lineups_from_base(base, perf, min_secs=100):
    # min_secs is tenths of a second
    base1, perf1 = base[perf[:, 2] >= min_secs], perf[perf[:, 2] >= min_secs]
    players = base1.shape[1] // 2
    base_flip = np.concatenate([base1[:, players:], base1[:, :players]], axis=1)
    lineups = np.concatenate([base1, base_flip], axis=0)
    perf2 = np.concatenate([perf1[:, 1:], perf1[:, ::2]], axis=0)
    return lineups, perf2


def get_pm_from_id(reg, id):
    return reg.coef_[0, player_list_rev[id]::reg.coef_.shape[1] // 2]


def ppg_with_lineup_row(reg, row_idx):
    return reg.predict(lineup_array[row_idx:row_idx + 1]) * 10 / np.sum(lineup_array[row_idx])


def get_players_by_row(reg, row_idx):
    num_pl = reg.coef_.shape[1] // 2
    return [(player_list[i % num_pl], i // num_pl) for i in np.nonzero(lineup_array[row_idx])]


def get_ppg_from_lineups(reg, defs, offs):
    num_pl = reg.coef_.shape[1] // 2
    a = np.zeros(num_pl * 2)
    b = np.array([player_list_rev[i] for i in defs])
    c = np.array([player_list_rev[i] for i in offs])
    if np.any(b):
        a[b] = 1
    if np.any(c):
        a[c + num_pl] = 1
    res = reg.predict(a.reshape((1, -1)))
    return res + np.mean(reg.coef_) * (10 - len(defs + offs))


def fit_model():
    print(np.mean(performance_array, axis=0))

    reg = LinearRegression(fit_intercept=False).fit(lineup_array, performance_array * (7200 * 4) ** (1))
    print(reg.score(lineup_array, performance_array * 7200 * 4))

    pickle.dump(reg, open('naive_pm.sav', 'wb'))


def fit_ridge_model(alpha=1/18):
    print(np.mean(performance_array, axis=0))

    reg = Ridge(alpha=alpha, fit_intercept=True).fit(lineup_array, performance_array * (7200 * 4))
    print(reg.score(lineup_array, performance_array * 7200 * 4))
    print(reg.intercept_)

    pickle.dump(reg, open(f'ridge_pm_{round(1/alpha, 2)}.sav', 'wb'))


def convert_raw_lineups():
    with np.load('lineups.npz') as data:
        lineup_array0 = data['lineup_array']
        performance_array0 = data['performance_array']
        player_list = data['player_list']

    lineup_array1, performance_array1 = get_lineups_from_base(lineup_array0, performance_array0)
    print(lineup_array1.shape, performance_array1.shape)

    sqrts = np.sqrt(performance_array1[:, 1:])
    lineup_array, performance_array = lineup_array1 * sqrts, performance_array1[:,:1] / sqrts  # - (113 / 7200 / 4) * sqrts
    np.savez_compressed('lineups2.npz', lineup_array=lineup_array, performance_array=performance_array)


with np.load('lineups.npz') as data:
    player_list = data['player_list']
player_list_rev = {player_list[i]: i for i in range(player_list.shape[0])}

with np.load('lineups2.npz') as data:
    lineup_array = data['lineup_array']
    performance_array = data['performance_array']

if __name__ == '__main__':
    # fit_model()
    fit_ridge_model()
