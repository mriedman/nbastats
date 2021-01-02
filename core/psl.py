class GameHead(object):
    def __init__(self, gamehead, pnum1, pnum2):
        self.game = gamehead
        self.pnum1 = pnum1
        self.pnum2 = pnum2

    def date(self):
        return bytes(self.game[1:9]).decode('ascii')

    def tm1(self):
        return bytes(self.game[16:19]).decode('ascii')

    def tm2(self):
        return bytes(self.game[13:16]).decode('ascii')

    def start(self):
        time1 = [i for i in self.game[19:21]]
        return time1[0] * 255 + time1[1]

    def location(self):
        return self.game[21]

    def tm1score(self):
        return self.game[22]

    def tm2score(self):
        return self.game[23]

    def scoremargin(self):
        return self.tm1score() - self.tm2score()


class PlayerStatLine(object):
    '''class FGpct(object):
        def __init__(self, fgm, fga, fgpct):
            self.fgm=fgm
            self.fga=fga
            self.fgpct=fgpct'''

    def __init__(self, binstats, gamehead: GameHead, is_start):
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
        return self.stats[1]

    def date(self):
        return self.game.date()

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

