from pathlib import PurePath
from os import listdir
import csv
from collections import defaultdict
from core.pbpdecoder import decode_file
from core.playindexlook import PlayerGameSelect, lookup


pbppath = PurePath('..', 'core', 'data', 'CLE', 'season', '2021', 'pbp')
games = listdir(pbppath)

lineups = {}
for filename in games:
    '''select = PlayerGameSelect((lambda x: x.date() == filename[:8], lambda x: x.is_start))
    line_bytes = lookup(select=select, ndup=False)'''
    select = PlayerGameSelect((lambda x: x.date() == filename[:8],))
    print(filename[:8])
    l = lookup(select=select, ndup=False, fq=True)
    print(l)

    exit(0)

    '''def player_swap(x, pnumlist, **kwargs):
        if x[0] == 0:
            return ((pnumlist[x[1]], x[1] < 128), (pnumlist[x[2]], x[2] < 128)), True
        return None, False
    exchanges = decode_file(pbppath, filename, player_swap)
    print(exchanges)
    cur_lineup = ({(i[1], True) for i in line_bytes[:5]}, {(i[1], False) for i in line_bytes[5:]})
    for e in exchanges:
        # print(cur_lineup)
        print(e)
        i = cur_lineup[0 if e[1][1] else 1]
        i.remove(e[1])
        i.add(e[0])
    exit(0)'''
