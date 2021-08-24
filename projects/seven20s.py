from pathlib import PurePath
import os
from core.playindexlook import *

# On 12-30-2020, seven players scored 20 in the Nets' 145-141 win over the Hawks. Has it happened before?

# Eight players did so on 2020-08-15 in POR's win over MEM!

'''netspath = PurePath('..', 'core', 'data', 'BRK', 'season', '2020', 'boxscores')
for game in os.listdir(netspath):
    pass'''

select = GameSelect((lambda x: x.PTS() >= 20,), (lambda x,y: len(y) >= 8,))

for i in lookup(select=select, sortbydir='d', ndup=False):
    for j in i:
        print(j)
    print()