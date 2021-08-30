import numpy as np
from player_rate.plusminus import lineup_array, performance_array, player_list_rev, performance_array1, lineup_array1
import pickle
from collections import defaultdict
import sqlite3

with np.load('lineups.npz') as data:
    player_list = data['player_list']

reg = pickle.load(open('naive_pm.sav', 'rb'))

residuals = performance_array - reg.predict(lineup_array)
ranks = np.argsort(residuals[:, 0])

NUM_PER_COMBO = 2

off_type_tuples = defaultdict(lambda: np.zeros(3))
for i in range(lineup_array1.shape[0]):
    print(lineup_array1[i])
    print(performance_array1[i])
    if i > 5:
        break

con = sqlite3.connect('playerinfo.db')
cur = con.cursor()

for row in cur.execute('SELECT * from players WHERE bbref_id=?', ('hardeja01',)):
    print(row)

con.close()
