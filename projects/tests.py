from core.playindexlook import *

# Last year, which team had the most players score 20 pts in a game?

def mconv(x):
    return 60 * x[2] + x[3]

select = GameSelect((lambda x: x.PTS() >= 0,), (lambda x, y: sum(mconv(i) for i in y) < 5 * 48 * 60-10,))
#select = GameSelect((lambda x: x.PTS() >= 5,), (lambda x, y: len(y) < 5,))

#plist = defaultdict(set)

for i in lookup(select=select, sortbydir='d', ndup=True,
                gamefilterlist=()):
    print(i)
    for j in i:
        print(j)
    '''date = ''.join([j for j in i[0][0] if j != '-']) + '0.txt'
    p = PurePath('..', 'core', 'data', i[0][2], 'season', '2020', 'boxscores', date)
    print(p)
    print(os.path.exists(p))
    os.remove(p)'''
#lambda x: x.tm1() == 'BRK' and x.tm2() == 'PHI' and x.date() == '20200220',
