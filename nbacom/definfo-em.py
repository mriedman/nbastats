import numpy as np
from nbacom.em import *
import json
import matplotlib.pyplot as plt
import sklearn.mixture


npzfile = np.load('./data/defmatchups/10/matchups-10.npz')
p_list = npzfile.files

gmkws = {'n_components': 10, 'covariance_type': 'full'}

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
    if K == 10:
        continue
    print(K)
    gmkws['n_components'] = K
    # preds = main(K, arr)
    gmm = sklearn.mixture.GaussianMixture(**gmkws)
    preds = gmm.fit_predict(arr)
    cs = {i: [] for i in range(K)}
    for i in range(len(preds)):
        cs[preds[i]].append(player_ids[p_list[i]])
    with open('./data/em-def/%d.json' % (K,), 'w') as f:
        f.write(json.dumps(cs))
    np.savez('./data/em-def/%d-params' % (K,),
             phi=gmm.weights_, mu=gmm.means_,
             **{'sigma%d' % (i,): gmm.covariances_[i] for i in range(K)}
             )

    # np.savetxt('./data/em-def/%d-cents.json' % (K,), cent0[0])
    # print([K, cent0[1]])
    # errs.append(cent0[1])
exit(0)
fig, ax = plt.subplots()
ax.plot(list(range(1, 30)), errs)
plt.savefig('./data/em-def/def-k-vals.png')
