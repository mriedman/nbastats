from pathlib import PurePath
import csv


def decode_play(line, **kwargs):
    return None, False


def decode_file(pbppath, filename, playparser=decode_play, ppargs={}):
    gamefile = open(pbppath / filename, mode='rb')
    header = gamefile.read(26)
    ishome = header[10:13] == b'ATL'
    pos = 26
    pnumlist = {}

    # List of players on opposing team given at the beginning of the pbp file
    while gamefile.read(1)[0] != 254:
        i = gamefile.read(10)
        maxidx = 10
        if b'\xff' in i[1:]:
            maxidx = i.index(b'\xff')
        pnumlist[i[0]] = i[1:maxidx].decode('ascii')
        pos += 11

    # Get players on own team from playerlist
    with open(pbppath / '..' / 'players' / 'playerlist.csv') as ownpnum:
        csvr = csv.reader(ownpnum)
        for row in csvr:
            pnumlist[int(row[0])] = row[2]
            # print(row)

    body = gamefile.read()
    bodylist = body.split(b'\xff')
    plays = []
    for i in bodylist:
        # Iterate through plays according to given function
        if len(i) > 0:
            p, b = playparser(i, ishome=ishome, pnumlist=pnumlist, **ppargs)
            if b:
                plays.append(p)
    return plays
