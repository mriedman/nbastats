from pathlib import PurePath
from typing import Union, Tuple
from core.teamcodes import nameyears
import csv
import os


def decode_play(line, **kwargs):
    return None, False


def decode_file(pbppath, filename: Union[PurePath, str], playparser=decode_play, ppargs={}):
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


def pbplookup(seasonrange: Tuple[int, int] = (1947, 2022),
              league: str = 'NBA', gametype: str = 'reg', gameteam: str = '', ndup=True, playparser=decode_play,
              ppargs={}, gamenumtype: str = 'all', gamenumrange: Tuple[int] = (1, 100), **kwargs):
    """
    :param seasonrange: [start,end] (inclusive)
    :param league: NBA, ABA, Both
    :param gametype: reg, playoff, either
    :param gamenumtype:
        tmszn: team season
        tmpo:  team playoff series
        plszn: player season
        plcar: player career
        all:   all
    :param ndup:
        Only look at each game from one team's perspective
    :param gameteam:
        Team whose records to look through. '' indicates all teams
    :param gamenumrange: [start,end] (inclusive)
    :return: list of pbp events
    """

    print('ALERT: pbplookup is only looking at 2020-21')

    l = {}
    full_quarter_search = 'fq' in kwargs and kwargs.get('fq')

    for yr0 in range(*seasonrange):

        if yr0 != 2021:
            continue

        yr = str(yr0)
        for team in nameyears:
            if yr not in nameyears[team]:
                continue
            if gameteam != team and gameteam != '':
                continue
            teampath = PurePath('..', 'core', 'data', team, 'season', yr, 'pbp')

            for gamefile in os.listdir(teampath):
                if gamefile == '.DS_Store':
                    continue
                l[(team, yr, gamefile)] = decode_file(teampath, gamefile, playparser, ppargs)
    return l
