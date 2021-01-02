from typing import Tuple, Callable, List, Any, Dict, Union
from core.psl import PlayerStatLine, GameHead

def decplayerline(l, game: GameHead):
    date = game.date()
    pl1 = game.pnum1
    pl2 = game.pnum2
    l1 = []
    if l[1] < 128:
        l1.append(pl1[l[1]][0])
    else:
        l1.append(pl2[l[1] - 128][0])
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
    l1.append(str(l[2]) + ':' + '0' * (2 - len(str(l[3]))) + str(l[3]))
    for i in range(4, 23):
        if i in [6, 9, 12]:
            if l[i - 1] == 0:
                l1.append(0)
            else:
                l1.append(round(l[i - 2] / l[i - 1], 3))
        elif i == 22:
            l1.append(l[i] - 128)
        elif l[i] == 255:
            l1.append('')
        else:
            l1.append(l[i])
    l1.append('www.basketball-reference.com/boxscores/' + bytes(game.game[1:13]).decode('ascii'))
    return l1

class AllSelect(object):
    def checkgame(self) -> bool:
        pass

    def checkline(self, psl: PlayerStatLine) -> bool:
        pass

    def resetgame(self, game: GameHead):
        pass

    def resetseason(self):
        pass

class PlayerGameSelect(AllSelect):
    def __init__(self, funcs: Tuple[Callable[[PlayerStatLine], bool]]):
        self.funcs = funcs
        self.output = ''
        self.game = None

    def checkgame(self) -> bool:
        return False

    def checkline(self, psl: PlayerStatLine) -> bool:
        result = all(func(psl) for func in self.funcs)
        if result:
            self.output = decplayerline(psl.stats, self.game)
        return result

    def resetgame(self, game: GameHead):
        self.output = ''
        self.game = game

    def resetseason(self):
        self.output = ''
        self.game = None


class GameSelect(AllSelect):
    def __init__(self, pslfuncs: Tuple[Callable[[PlayerStatLine], bool]] = (), gamefuncs: Tuple[Callable[[GameHead, List], bool]] = ()):
        self.pslfuncs = pslfuncs
        self.game = None
        self.gamefuncs = gamefuncs
        self.output = []
        self.lines = []

    def checkgame(self):
        if all(func(self.game, self.output) for func in self.gamefuncs):
            self.output = [self.game] + self.output
            return True

    def checkline(self, psl: PlayerStatLine):
        if all(func(psl) for func in self.pslfuncs):
            self.output.append(psl)
        return False

    def resetgame(self, game: GameHead):
        self.game = game
        self.output = []

    def resetseason(self):
        self.output = []
        self.game = None


