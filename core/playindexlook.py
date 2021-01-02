full = ['GSW']
from time import time
from typing import Tuple, Callable
from collections import defaultdict
from pathlib import PurePath
import os
import csv
from core.teamcodes import abbrtocode

t = time()


class PlayerStatLine(object):
    '''class FGpct(object):
        def __init__(self, fgm, fga, fgpct):
            self.fgm=fgm
            self.fga=fga
            self.fgpct=fgpct'''

    def __init__(self, binstats, gamehead, is_start):
        self.stats = binstats
        self.game = gamehead
        self.is_start = is_start
        self.str_to_func = {'name': self.name, 'date': self.date, 'MP': self.MP, 'FG': self.FG, 'FGMI': self.FGMI,
                            'FGA': self.FGA, 'FG%': self.FGpct, '2P': self.TwoP, '2PMI': self.TwoPMI, '2PA': self.TwoPA,
                            '2P%': self.TwoPpct, '3P': self.ThrP, '3PMI': self.ThrPMI, '3PA': self.ThrPA,
                            '3P%': self.ThrPpct, 'FT': self.FT, 'FTMI': self.FTMI, 'FTA': self.FTA, 'FT%': self.FTpct,
                            'ORB': self.ORB, 'DRB': self.DRB, 'TRB': self.TRB, 'AST': self.AST, 'STL': self.STL,
                            'BLK': self.BLK, 'TOV': self.TOV, 'PF': self.PF, 'PTS': self.PTS, '+/-': self.PM}

    def name(self):
        if self.stats[1] < 64:
            pass
        return self.stats[1]

    def date(self):
        return bytes(self.game[1:9]).decode('ascii')

    '''def age(self):
        # QQQQQQQQQQQQ
        return 0'''

    def GS(self):
        return self.is_start

    def MP(self):
        return self.stats[2] + self.stats[3] / 60

    def FG(self):
        return self.stats[4]

    def FGMI(self):
        return self.stats[5] - self.stats[4]

    def FGA(self):
        return self.stats[5]

    def FGpct(self):
        if self.stats[5] == 0:
            return 0
        return self.stats[4] / self.stats[5]

    def TwoP(self):
        return self.stats[4] - self.stats[7]

    def TwoPMI(self):
        return self.TwoPA() - self.TwoP()

    def TwoPA(self):
        return self.stats[13] - self.stats[16]

    def TwoPpct(self):
        if self.TwoPA() == 0:
            return 0
        return self.TwoP() / self.TwoPA()

    def ThrP(self):
        return self.stats[7]

    def ThrPMI(self):
        return self.ThrPA() - self.ThrP()

    def ThrPA(self):
        return self.stats[8]

    def ThrPpct(self):
        if self.ThrPA() == 0:
            return 0
        return self.ThrP() / self.ThrPA()

    def FT(self):
        return self.stats[10]

    def FTMI(self):
        return self.FTA() - self.FTA()

    def FTA(self):
        return self.stats[11]

    def FTpct(self):
        if self.FTA() == 0:
            return 0
        return self.FT() / self.FTA()

    def ORB(self):
        return self.stats[13]

    def DRB(self):
        return self.stats[14]

    def TRB(self):
        return self.stats[15]

    def AST(self):
        return self.stats[16]

    def STL(self):
        return self.stats[17]

    def BLK(self):
        return self.stats[18]

    def TOV(self):
        return self.stats[19]

    def PF(self):
        return self.stats[20]

    def PTS(self):
        return self.stats[21]

    def PM(self):
        return self.stats[22]

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
        date = 0
        psl = PlayerStatLine([], [], 0)
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
                    game = [1] + [i for i in f.read(27)]
                    ct += 26
                    psl.game = game
                    date = bytes(game[1:9]).decode('ascii')
                    opptm = bytes(game[13:16]).decode('ascii')
                    opppnumlist = getpnum(opptm, yr)
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
                        l.append([dec(game, date, ownpnumlist, opppnumlist), game, psl.game])
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


def dec(l, date, pl1, pl2):
    l1 = []
    if l[1] < 128:
        l1.append(pl1[l[1]][0])
    else:
        l1.append(pl2[l[1] - 128][0])
    l1.append(date)
    l1.append(str(l[2]) + ':' + '0'*(2-len(str(l[3]))) + str(l[3]))
    for i in range(4, 23):
        if i in [6, 9, 12]:
            if l[i - 1] == 0:
                l1.append(0)
            else:
                l1.append(round(l[i - 2] / l[i - 1],3))
        elif i == 22:
            l1.append(l[i] - 128)
        elif l[i] == 255:
            l1.append('')
        else:
            l1.append(l[i])
    return l1

def f1(psl: PlayerStatLine) -> bool:
    return psl.FGpct() == 1 and psl.FGA() >= 2

for i in lookup(catfunclist= \
                        (lambda x: x.MP() > 0,
                         lambda x: x.PTS() > 30),
        sortbydir='d'):
    print(i)
