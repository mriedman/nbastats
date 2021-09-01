from player_rate.plusminus import *
import numpy as np
import pickle

with np.load('lineups.npz') as data:
    player_list = data['player_list']

reg = pickle.load(open('ridge_pm_18.0.sav', 'rb'))
# print(reg.score(lineup_array, performance_array * 7200 * 4))
# print(lineup_array[:5, -66:])
print(reg.coef_.shape)
# print(np.mean(reg.coef_[:, 1080:]))
print(np.mean(reg.coef_[:, 540]))
print(np.mean(reg.coef_[:, 540:1080]))

print('Hi')
