import numpy as np
from nbacom.k import *
import json
import matplotlib.pyplot as plt


npzfile = np.load('./data/defmatchups/10/matchups-10.npz')
p_list = npzfile.files

with open('./data/k/1.json') as f:
    grps1 = json.load(f)
player_ids = {str(i[2]): i for i in grps1['0'] if not i[2] == 2229}
player_ids['1628455'] = ('Mike James', 'BKN', 1628455)

arr = np.zeros((len(p_list), npzfile[p_list[0]].shape[0]))
print(arr.shape)
for i0, i in enumerate(p_list):
    arr[i0] = npzfile[i][:, 7] / np.sum(npzfile[i][:, 7])

errs = []
for K in range(1, 30):
    cents = []
    for _ in range(50):
        cent = init_centroids(K, arr)
        cent = update_centroids(cent, arr)
        cents.append(cent)
    cent0 = (cents[0], np.infty)
    cs = []
    for cent in cents:
        dist = np.array([np.linalg.norm(arr - mu.reshape(1, -1), axis=1) for mu in cent])
        min_dist_vals = np.sum(np.min(dist, axis=0))
        if min_dist_vals > cent0[1]:
            continue
        cent0 = (cent, min_dist_vals)
        min_dist = np.argmin(dist, axis=0).reshape(-1)
        cs = {i: [] for i in range(K)}
        for i, j in enumerate(min_dist):
            cs[j].append(player_ids[p_list[i]])
    '''for j in cs:
        print(cs[j])'''
    with open('./data/k-def/%d.json' % (K,), 'w') as f:
        f.write(json.dumps(cs))
    np.savetxt('./data/k-def/%d-cents.json' % (K,), cent0[0])
    print([K, cent0[1]])
    errs.append(cent0[1])

fig, ax = plt.subplots()
ax.plot(list(range(1, 30)), errs)
plt.savefig('./data/k-def/def-k-vals.png')
