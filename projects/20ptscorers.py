from core.playindexlook import *

# Last year, which team had the most players score 20 pts in a game?

select = GameSelect((lambda x: x.PTS() >= 50,))

plist = defaultdict(set)

for i in lookup(select=select, sortbydir='d'):
    #lambda x: x.game[16:19] == [62, 82, 75]
    print(i)
    plist[i[2]].add(i[0])
rlist = sorted([[i, plist[i]] for i in plist], key=lambda i:len(i[1]))
for i in rlist:
    print(i[0])
    print(i[1])
    print(len(i[1]))
    print()