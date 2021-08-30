from player_rate.plusminus import *
import pickle

with np.load('lineups.npz') as data:
    player_list = data['player_list']

reg = pickle.load(open('naive_pm.sav', 'rb'))

print('Hi')
