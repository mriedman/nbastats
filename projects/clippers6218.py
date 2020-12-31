from pathlib import PurePath
from os import listdir
import csv
from collections import defaultdict

clipspath20 = PurePath('data', 'BRK', 'season', '2020', 'pbp')
games20 = listdir(clipspath20)
scorelist1 = defaultdict(int)
csvf = open('clippers6218.csv', 'w')
csvw = csv.writer(csvf)
for filename in games20:
    if not filename == '202012270.txt':
        pass
    gamefile = open(clipspath20 / filename, mode='rb')
    header = gamefile.read(26)
    ishome = header[10:13] == b'BRK'
    pos = 26
    pnumlist = {}
    while gamefile.read(1)[0] != 254:
        i = gamefile.read(10)
        maxidx = 10
        if b'\xff' in i[1:]:
            maxidx = i.index(b'\xff')
        pnumlist[i[0]] = i[1:maxidx].decode('ascii')
        pos += 11
    with open(clipspath20 / '..' / 'players' / 'playerlist.csv') as ownpnum:
        for row in ownpnum:
            pnumlist[int(row[0])] = row[2]
    body = gamefile.read()
    bodylist = body.split(b'\xff')
    scorelist = []
    for i in bodylist:
        if len(i) > 0 and 1 <= i[0] < 7:
            # scorelist.append([i[-4],i[-3]])
            if ishome:
                scorelist1[(i[-4], i[-3])] += 1
                csvw.writerow([i[-4],i[-3],255*i[-2]+i[-1]])
            else:
                scorelist1[(i[-3],i[-4])] += 1
                csvw.writerow([i[-3], i[-4], 255 * i[-2] + i[-1]])
    # print(scorelist)
    for i,j in enumerate(scorelist):
        if i == 0:
            continue
        if (j[0]==scorelist[i-1][0] and j[1]>scorelist[i-1][1]) or (j[0]>scorelist[i-1][0] and j[1]==scorelist[i-1][1]):
            pass
        else:
            print('OH NO')
            print(scorelist[i-1:i+1])
csvf.close()
print(str(dict(scorelist1)).replace('{','<|').replace('}','|>').replace('(','{').replace(')','}').replace(':','->'))