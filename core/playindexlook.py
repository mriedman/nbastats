full = ['GSW']
from time import time
from typing import Tuple, Callable
from collections import defaultdict

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

    # TYPE[0] PLAYER[1-9] MIN:SEC[10-11] FG FGA FG%[14] 3P 3PA 3P%[17] FT FTA FT%[20] ORB DRB TRB[23] AST STL BLK[26] TOV PF PTS +/-[30]
    def name(self):
        maxidx = min([10]+[i for i in range(20) if self.stats[i] > 127])
        return bytes(self.stats[1:maxidx]).decode('ascii')

    def date(self):
        return bytes(self.game[1:9]).decode('ascii')

    '''def age(self):
        # QQQQQQQQQQQQ
        return 0'''

    def GS(self):
        return self.is_start

    def MP(self):
        return self.stats[10] + self.stats[11] / 60

    def FG(self):
        return self.stats[12]

    def FGMI(self):
        return self.stats[13] - self.stats[12]

    def FGA(self):
        return self.stats[13]

    def FGpct(self):
        if self.stats[13] == 0:
            return 0
        return self.stats[12] / self.stats[13]

    def TwoP(self):
        return self.stats[12] - self.stats[15]

    def TwoPMI(self):
        return self.TwoPA() - self.TwoP()

    def TwoPA(self):
        return self.stats[13] - self.stats[16]

    def TwoPpct(self):
        if self.TwoPA() == 0:
            return 0
        return self.TwoP() / self.TwoPA()

    def ThrP(self):
        return self.stats[15]

    def ThrPMI(self):
        return self.ThrPA() - self.ThrP()

    def ThrPA(self):
        return self.stats[16]

    def ThrPpct(self):
        if self.ThrPA() == 0:
            return 0
        return self.ThrP() / self.ThrPA()

    def FT(self):
        return self.stats[18]

    def FTMI(self):
        return self.FTA() - self.FTMI()

    def FTA(self):
        return self.stats[19]

    def FTpct(self):
        if self.FTA() == 0:
            return 0
        return self.FT() / self.FTA()

    def ORB(self):
        return self.stats[21]

    def DRB(self):
        return self.stats[22]

    def TRB(self):
        return self.stats[23]

    def AST(self):
        return self.stats[24]

    def STL(self):
        return self.stats[25]

    def BLK(self):
        return self.stats[26]

    def TOV(self):
        return self.stats[27]

    def PF(self):
        return self.stats[28]

    def PTS(self):
        return self.stats[29]

    def PM(self):
        return self.stats[30]


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

    f = open('data/CHO/season/2020/boxscores.txt', 'rb')
    ct = 0
    l = []
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
            game = [i for i in f.read(31)]
            if game[0] == 1:
                ct += 24
                psl.game = game
                date = bytes(game[1:9]).decode('ascii')
                gamenum['team'] += 1
                p_num = 0
                continue
            elif game[0] == 0:
                ct += 31
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
                    l.append([dec(game, date), game, psl.game])
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


def dec(l, date):
    l1 = []
    maxidx = min([10] + [i for i in range(20) if l[i] > 127])
    l1.append(bytes(l[1:maxidx]).decode('ascii'))
    l1.append(date)
    l1.append(str(l[10]) + ':' + '0'*(2-len(str(l[11]))) + str(l[11]))
    for i in range(12, 31):
        if i in [14, 17, 20]:
            if l[i - 1] == 0:
                l1.append(0)
            else:
                l1.append(round(l[i - 2] / l[i - 1],3))
        elif i == 30:
            l1.append(l[i] - 128)
        elif l[i] == 255:
            l1.append('')
        else:
            l1.append(l[i])
    return l1

def f1(psl: PlayerStatLine) -> bool:
    return psl.FGpct() == 1 and psl.FGA() >= 2

for i in lookup(catfunclist= \
                        (lambda x: x.MP() > 20,
                         lambda x: x.GS() == 0),
        sortbydir='d'):
    print(i)
