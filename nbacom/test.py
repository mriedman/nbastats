import numpy as np
import json

npzfile = np.load('./data/defmatchups/10/matchups-10.npz')
print(npzfile.files)

with open('./data/em-def/10.json') as f:
    grps = json.load(f)

p_grps = {}
for i in grps:
    for j in grps[i]:
        p_grps[j[0]] = (i, j)

print(p_grps['Giannis Antetokounmpo'])

print([round(i, 2) for i in npzfile['203507'][:, 7] / np.sum(npzfile['203507'][:, 7])])
