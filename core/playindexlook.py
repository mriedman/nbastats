from time import time
from typing import Tuple, Callable, List, Any, Dict, Union
from collections import defaultdict
from pathlib import PurePath
import os
import csv
from core.teamcodes import abbrtocode
from core.itemselects import *
from core.psl import PlayerStatLine

t = time()

def getpnum(tm: str, yr: str):
    path = PurePath('..', 'core', 'data', abbrtocode[tm], 'season', yr)
    pnumlist = {}
    with open(path / 'players' / 'playerlist.csv') as csvf:
        csvr = csv.reader(csvf)
        for row in csvr:
            pnumlist[int(row[0])] = row[1:]
    pnumlist[65] = [tm, tm]
    pnumlist[67] = ['Official', 'Official']
    pnumlist[68] = ['', 'NONE']
    return pnumlist

def lookup(mode: str = 'single', sortbydir: str = 'd', sortbycat: str = 'PTS', seasonrange: Tuple[int] = (1947, 2020),
           league: str = 'NBA', gametype: str = 'reg',
           gamenumtype: str = 'all', gamenumrange: Tuple[int] = (1, 100),
           catfunclist: Tuple[Callable[[PlayerStatLine], bool]] = (), playerfilterlist=(), gamefilterlist=()):
    '''
    :param mode: 
        single: Single Games matching criteria
            (e.g., most points in a game between 2000-01 and 2009-10)
        season: Season Games matching criteria
            (e.g., most games with 20+ points in a season between 2000-01 and 2009-10)
        cumulative: Cumulative Games matching criteria
            (e.g., most points in a team's first 20 games in a season between 2000-01 and 2009-10)
        total: Total Games matching criteria
            (e.g., most games with 20+ points between 2000-01 and 2009-10)
        cumulmulti: Cumulative Multi-Season Games matching criteria
            (e.g., most points at home between 2000-01 and 2009-10)
    :param sortbydir: 
        a: ascending
        d: descending
    :param sortbycat: 
        name date age  GS
        MP   FG   FGMI FGA  
        FG%  2P   2PMI 2PA   
        2P%  3P   3PMI 3PA   
        3P%  FT   FTMI FTA
        FT%  ORB  DRB  TRB
        AST  STL  BLK  TOV
        PF   PTS  +/-
    :param seasonrange: [start,end] (inclusive)
    :param league: NBA, ABA, Both
    :param gametype: reg, playoff, either
    :param gamenumtype: 
        tmszn: team season
        tmpo:  team playoff series
        plszn: player season
        plcar: player career
        all:   all
    :param gamenumrange: [start,end] (inclusive)
    :param catfunclist: list of category functions
        e.g. 'PTS>15' or 'PTS+AST>10*TOV'
    :param playerfilterlist: 
    :param gamefilterlist: 
    :return: list of statlines
    '''
    # TYPE 0:
    # TYPE[0] PLAYER[1:10] MIN:SEC[10:12] FG FGA FG%[14] 3P 3PA 3P%[17] FT FTA FT%[20] ORB DRB TRB[23] AST STL BLK[26] TOV PF PTS +/-[30]
    # TYPE 1:
    # See bincodeinfo.txt for information on file format
    yr = '2020'
    teampath = PurePath('..', 'core', 'data' ,'BRK', 'season', yr, 'boxscores')
    l = []
    ownpnumlist = getpnum('BRK', yr)
    opppnumlist = {}
    for gamefile in os.listdir(teampath):
        f = open(teampath / gamefile, 'rb')
        ct = 0
        gameobj = GameHead(b'', ownpnumlist, opppnumlist)
        psl = PlayerStatLine([], gameobj, 0)
        gamenum = defaultdict(int)
        if sortbydir not in ('a', 'd'):
            raise ValueError('sortbydir invalid: should be "a" or "d", is ' + sortbydir)
        if not gamenumtype in ['tmszn', 'tmpo', 'plszn', 'plcar', 'all']:
            raise ValueError('Invalid gamenumtype')
        if gamenumtype in ['tmpo', 'plcar']:
            raise ValueError('Desired gamenumtype not yet implemented')
        p_num = 0  # Determines if player is starting based on if they're one of the first 5
        while True:
            try:
                f.seek(ct)
                g0 = [i for i in f.read(1)][0]
                if g0 == 1:
                    game = gameobj
                    game.game = [1] + [i for i in f.read(27)]
                    ct += 26
                    opppnumlist = getpnum(game.tm2(), yr)
                    psl.game.pnum2 = opppnumlist
                    gamenum['team'] += 1
                    p_num = 0
                    continue
                elif g0 == 0:
                    game = [0] + [i for i in f.read(22)]
                    ct += 23
                    psl.stats = game
                    gamenum[psl.name()] += 1
                    psl.is_start = 1 if p_num < 5 else 0
                    p_num += 1
                    if gamenumtype == 'all':
                        pass
                    elif gamenumtype == 'tmszn' and gamenum['team'] < gamenumrange[0]:
                        continue
                    elif gamenumtype == 'tmszn' and gamenum['team'] > gamenumrange[1]:
                        break
                    elif gamenumtype == 'plszn' and not gamenumrange[0] <= gamenum[psl.name()] <= gamenumrange[1]:
                        continue
                    if all(i(psl) for i in catfunclist):
                        l.append([decplayerline(game, psl.game), game, psl.game])
                elif g0 == 3:
                    ct += 1
                else:
                    raise ValueError('First index out of range')
            except IndexError:
                break
            if ct > 100000:
                break
        f.close()

    def sortfunc(sl):
        psl.game = sl[2]
        psl.stats = sl[1]
        sign = 1 if sortbydir == 'a' else -1
        return sign * psl.str_to_func[sortbycat]()
    l1 = sorted(l, key=sortfunc)
    return [i[0] for i in l1]






playerselect = None


