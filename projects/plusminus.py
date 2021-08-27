import numpy as np
from sklearn.linear_model import LinearRegression

with np.load('lineups.npz') as data:
    lineup_array0 = data['lineup_array']
    performance_array0 = data['performance_array']
    player_list = data['player_list']

lineup_array1 = np.concatenate([lineup_array0 * lineup_array0 == 1, -lineup_array0 * lineup_array0 == -1], axis=1)
performance_array1 = np.concatenate()

sqrts = np.sqrt(performance_array0[:, 2])
sqrts[sqrts == 0] = 1
sqrts = sqrts.reshape((-1, 1))
lineup_array, performance_array = lineup_array1 * sqrts, performance_array0[:, :2] / sqrts - (113 / 7200 / 4) * sqrts

print(np.mean(performance_array, axis=0))

print(performance_array[performance_array[:, 0] > 0.05, :])
# print(lineup_array[:5, :200])

reg = LinearRegression(fit_intercept=False).fit(lineup_array, performance_array * (7200 * 4) ** (1/2))
print(reg.score(lineup_array, performance_array * (7200 * 4) ** (1/2)))
coefs = reg.coef_ - np.mean(reg.coef_, axis=1).reshape((2, 1))
player_list_rev = {player_list[i]: i for i in range(player_list.shape[0])}
print('Hi!')
