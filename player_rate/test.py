from core.teamcodes import nameyears
import csv
import numpy as np

a = np.zeros((30, 72, 3), int)
b = np.zeros((30, 5), float)
j=0
for tm in nameyears:
    if '2021' in nameyears[tm]:
        with open(f'../core/data/{tm}/season/2021/gs.csv') as f:
            csvf = csv.reader(f)
            i = 0
            for row in csvf:
                a[j, i, 0] = row[-9]
                a[j, i, 1] = row[-8]
                a[j, i, 2] = 1 if int(row[-9]) > int(row[-8]) else 0
                i += 1
                if i == 72:
                    break
        b[j] = np.array([np.mean(a[j, :, 0]), np.std(a[j, :, 0]),
                         np.mean(a[j, :, 1]), np.std(a[j, :, 1]), np.mean(a[j, :, 2])])
        j += 1

print(str([list(i) for i in b]).replace('[', '{').replace(']', '}'))
