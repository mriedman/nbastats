from pathlib import PurePath
import os
from core.playindexlook import *

# On 12-30-2020, seven players scored 20 in the Nets' 145-141 win over the Hawks. Has it happened before?

'''netspath = PurePath('..', 'core', 'data', 'BRK', 'season', '2020', 'boxscores')
for game in os.listdir(netspath):
    pass'''

for i in lookup(catfunclist= \
                        (lambda x: x.MP() > 0,
                         lambda x: x.PTS() > 30),
        sortbydir='d'):
    print(i)