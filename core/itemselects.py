from typing import Tuple, Callable, List
from core.psl import PlayerStatLine, GameHead


def decode_player_line(line_bytes, game: GameHead):
    date = game.date()
    pl1 = game.pnum1
    pl2 = game.pnum2
    l1 = []
    if line_bytes[1] < 128:
        l1.append(pl1[line_bytes[1]][0])
        l1.append(pl1[line_bytes[1]][1])
    else:
        l1.append(pl2[line_bytes[1] - 128][0])
        l1.append(pl2[line_bytes[1] - 128][1])
    l1.append(date[:4]+'-'+date[4:6]+'-'+date[6:])
    l1.append(game.tm1())
    loc = game.location()
    if loc == 0:
        l1.append('vs')
    elif loc == 1:
        l1.append('@')
    elif loc == 2:
        l1.append('N')
    else:
        l1.append('uk')
    l1.append(game.tm2())
    l1.append(str(line_bytes[2]) + ':' + '0' * (2 - len(str(line_bytes[3]))) + str(line_bytes[3]))
    for i in range(4, 23):
        if i in [6, 9, 12]:
            if line_bytes[i - 1] == 0:
                l1.append(0)
            else:
                l1.append(round(line_bytes[i - 2] / line_bytes[i - 1], 3))
        elif i == 22:
            l1.append(line_bytes[i] - 128)
        elif line_bytes[i] == 255:
            l1.append('')
        else:
            l1.append(line_bytes[i])
    l1.append('https://www.basketball-reference.com/boxscores/' + bytes(game.game[1:13]).decode('ascii'))
    return l1


def decode_full_quarter(l, game: GameHead):
    # Return: [[player_name, player_id], is_cur_team, date, player_team, opp_team]
    pl1 = game.pnum1
    pl2 = game.pnum2
    if l[0] < 128:
        return [pl1[l[0]], l[1], True, game.date(), game.tm1(), game.tm2()]
    return [pl2[l[0] - 128], l[1], False, game.date(), game.tm2(), game.tm1()]


def decode_game(game: GameHead):
    l1 = []
    date = game.date()
    l1.append(date[:4] + '-' + date[4:6] + '-' + date[6:])
    l1.append(str(game.start()//60)+':'+str(game.start() % 60))
    l1.append(game.tm1())
    loc = game.location()
    if loc == 0:
        l1.append('vs')
    elif loc == 1:
        l1.append('@')
    elif loc == 2:
        l1.append('N')
    else:
        l1.append('uk')
    l1.append(game.tm2())
    l1.append(game.tm1score())
    l1.append(game.tm2score())
    return l1


class AllSelect(object):
    def checkgame(self) -> bool:
        pass

    def checkline(self, psl: PlayerStatLine) -> bool:
        pass

    def checkseason(self) -> bool:
        pass

    def resetgame(self, game: GameHead):
        pass

    def resetseason(self):
        pass

    def lineoutput(self, psl: PlayerStatLine):
        pass

    def fqoutput(self, fq):
        pass

    def output(self):
        pass


class PlayerGameSelect(AllSelect):
    def __init__(self, funcs: Tuple[Callable[[PlayerStatLine], bool]]):
        self.funcs = funcs
        self.outputlist = ''
        self.game = None

    def checkgame(self) -> bool:
        return False

    def checkline(self, psl: PlayerStatLine) -> bool:
        result = all(func(psl) for func in self.funcs)
        if result:
            self.outputlist = decode_player_line(psl.stats, self.game)
        return result

    def resetgame(self, game: GameHead):
        self.outputlist = ''
        self.game = game

    def resetseason(self):
        self.outputlist = ''
        self.game = None

    def output(self):
        return self.outputlist

    def lineoutput(self, psl: PlayerStatLine):
        return decode_player_line(psl.stats, self.game)

    def fqoutput(self, fq):
        # Accepts two bytes from binary boxscore
        # Returns [pnum, quarter]
        return decode_full_quarter(fq, self.game)


class GameSelect(AllSelect):
    def __init__(self, pslfuncs: Tuple[Callable[[PlayerStatLine], bool]] = (), gamefuncs: Tuple[Callable[[GameHead, List], bool]] = (),
                 sznfuncs: Tuple[Callable[[List], bool]] = ()):
        self.pslfuncs = pslfuncs
        self.game = None
        self.gamefuncs = gamefuncs
        self.sznfuncs = sznfuncs
        self.gameoutputlist = []
        self.sznoutputlist = []
        self.lines = []

    def checkseason(self):
        return self.sznfuncs != () and all(func(self.sznoutputlist) for func in self.sznfuncs)

    def checkgame(self):
        if self.gamefuncs != () and all(func(self.game, self.gameoutputlist) for func in self.gamefuncs):
            self.sznoutputlist.append(self.output())
            return self.sznfuncs == ()
        return False

    def checkline(self, psl: PlayerStatLine):
        if all(func(psl) for func in self.pslfuncs):
            self.gameoutputlist.append(psl.stats)
            return self.gamefuncs == ()
        return False

    def resetgame(self, game: GameHead):
        self.game = game
        self.gameoutputlist = []

    def resetseason(self):
        self.gameoutputlist = []
        self.sznoutputlist = []
        self.game = None

    def output(self):
        return [decode_game(self.game)] + [decode_player_line(i, self.game) for i in self.gameoutputlist]

    def lineoutput(self, psl: PlayerStatLine):
        return decode_player_line(psl.stats, self.game)
