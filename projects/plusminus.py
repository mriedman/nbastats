import numpy as np
from sklearn.linear_model import LinearRegression

with np.load('lineups.npz') as data:
    lineup_array = data['lineup_array']
    performance_array = data['performance_array'] - 113 / 48 / 600
    player_list = data['player_list']

print(np.mean(performance_array, axis=0))

print(performance_array[performance_array[:, 0] > 0.05, :])
# print(lineup_array[:5, :200])

reg = LinearRegression().fit(lineup_array, performance_array * 7200 * 4)
print(reg.score(lineup_array, performance_array * 7200 * 4))
coefs = reg.coef_ - np.mean(reg.coef_, axis=1).reshape((2, 1))
player_list_rev = {player_list[i]: i for i in range(player_list.shape[0])}
print('Hi!')
