import numpy as np
from sklearn.linear_model import LinearRegression


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
    return [(player_list[i * num_pl], i // num_pl) for i in np.nonzero(lineup_array[row_idx])]


with np.load('lineups.npz') as data:
    lineup_array0 = data['lineup_array']
    performance_array0 = data['performance_array']
    player_list = data['player_list']

lineup_array1, performance_array1 = get_lineups_from_base(lineup_array0, performance_array0)
print(lineup_array1.shape, performance_array1.shape)

sqrts = np.sqrt(performance_array1[:, 1:])
lineup_array, performance_array = lineup_array1 * sqrts, performance_array1[:, :1] / sqrts  # - (113 / 7200 / 4) * sqrts

print(np.mean(performance_array, axis=0))

# print(performance_array[performance_array[:, 0] > 0.05, :])
# print(lineup_array[:5, :200])

reg = LinearRegression(fit_intercept=False).fit(lineup_array, performance_array * (7200 * 4) ** (1))
print(reg.score(lineup_array, performance_array * (7200 * 4) ** (1)))
coefs = reg.coef_ - np.mean(reg.coef_, axis=1).reshape((1, 1))
player_list_rev = {player_list[i]: i for i in range(player_list.shape[0])}

np.savez_compressed('naive_pm.npz', coefs=reg.coef_)
