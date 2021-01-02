# coding: utf-8
from urllib import request
import ssl
# from core.brt import get_table
import csv
import os
from pathlib import PurePath
from typing import List, Dict, Union
from core.getpbpdata import *
from copy import copy
from core.teamcodes import *
from io import BytesIO

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


class Team(object):
    def __init__(self, team):
        self.seasons = {}
        self.team = team
        self.dirpath = PurePath('..', 'core', 'data', team, 'season')
        os.makedirs(self.dirpath, exist_ok=True)
        '''for i in os.listdir(self.dirpath):
            if not i == '.DS_Store':
                self.seasons[i] = Season(self, i)'''

    def newseason(self, yr):
        szn = Season(self, yr)
        self.seasons[yr] = szn


class Season(object):
    def __init__(self, team: Team, yr: str):
        self.teamobj = team
        self.team = team.team
        self.dirpath = team.dirpath
        self.year = yr
        self.gamelist = []
        print('data/' + self.team + '/season/' + yr)
        self.nspath = self.dirpath / str(self.year)
        self.tm2 = abbrtoname[nameyears[self.team][yr]]
        print(self.tm2)
        if os.path.isfile(self.nspath / 'gs.csv'):
            with open(self.nspath / 'gs.csv') as csvf0:
                csvf = csv.reader(csvf0)
                for row in csvf:
                    self.gamelist.append(Game(row, self.year))
        else:
            # Add full-season player data
            plpath = self.dirpath / str(self.year) / 'players'
            os.makedirs(plpath)
            g1 = str(
                request.urlopen("https://www.basketball-reference.com/teams/" + self.team + "/" + str(self.year) + '.html',
                                context=ctx).read(), encoding='utf-8')
            '''t1 = get_table(g1)
            for i in t1:
                with open(plpath / (i + '.csv'), mode='w') as csvf:
                    csvw = csv.writer(csvf)
                    for j in t1[i]:
                        csvw.writerow(j)'''
            t2 = get_table(g1, mode='Link')
            with open(plpath / 'playerlist.csv', mode='w') as csvf:
                csvw = csv.writer(csvf)
                ct = 0
                for row in t2['Per Game Table']:
                    if ct == 0:  # Header
                        ct += 1
                        continue
                    print(row)
                    l = [ct, row[1], row[2].split('/')[-1].split('.html')[0]]
                    csvw.writerow(l)
                    ct += 1
            # Retrieve game logs
            s = request.urlopen(
                "https://www.basketball-reference.com/teams/" + self.team + "/" + str(self.year) + "_games.html", context=ctx)
            t = s.read()
            g = str(t)
            gl1 = get_table(g, mode='Link')
            # self.tm2 = g.split('-' + self.year[2:] + ' ')[1].split(' Sched')[0]  # Full team name (g.g. Brooklyn Nets)
            print(g.split('-' + self.year[2:] + ' ')[1].split(' Sched')[0])  # Full team name (g.g. Brooklyn Nets))
            # g = (g.split('<caption>Regular Season Table</caption>')[1]).split('</tbody>')[0]
            # gl = g.split('<th scope="row"')
            gamelist1 = []
            self.bxpath = self.nspath / 'boxscores'
            os.makedirs(self.bxpath, exist_ok=True)
            print(gl1.keys())
            for game in gl1['Regular Season Table']:
                if game[0] == 'G':
                    continue
                print(game)
                game[2] = ''
                loginfo = game + [0, game[9].split('/')[2], self.team]
                # gamelist1.append(Game(loginfo, (self.nspath / game[6].split('/')[-1][:-5] + '.txt'), self.year))
                gamelist1.append(Game(loginfo, self.year))
            if 'Playoffs Table' in gl1:
                for game in gl1['Playoffs Table']:
                    if game[0] == 'G':
                        continue
                    print(game)
                    game[2] = ''
                    loginfo = game + [1, game[9].split('/')[2], self.team]
                    gamelist1.append(Game(loginfo, self.year, ))
            self.gamelist = gamelist1
            '''for game in gl[1:]:  # QQQQQQQQQQ only first 3 games
                i = game.split("</tr>")[0]
                i1 = i.split('</td>')
                i2 = [j.replace('</a>', '').split('>')[-1] for j in i1]
                i2.append((game.split('="box_score_text" ><a href="')[1].split('">')[0]))
                i2.append((game.split('href="/teams/')[1].split('/')[0]))
                gamelist1.append(Game(i2 + [self.team], self, self.bxpath / i2[15].split('/')[-1][:-5], self.year))
                raise ValueError'''
            if not os.path.isfile(self.nspath / 'gs.csv'):
                with open(self.nspath / 'gs.csv', mode='w') as csvf:
                    csvw = csv.writer(csvf)
                    for i in self.gamelist:
                        csvw.writerow(i.loginfo)
            # filepath = PurePath('..', 'core', 'data', self.team, 'season', self.year)
            os.makedirs(self.nspath / 'pbp', exist_ok=True)
            os.makedirs(self.nspath / 'boxscores', exist_ok=True)
        self.ownpnumlist = {}
        with open(self.nspath / 'players' / 'playerlist.csv') as csvf:
            csvr = csv.reader(csvf)
            for row in csvr:
                self.ownpnumlist[row[2]] = [int(row[0]), row[1]]
    @staticmethod
    def getgameheader(loginfo: List[str]) -> List[int]:
        """
        :param loginfo: game.loginfo
        :return: binary game header
            TYPE (1) [0]
            DATE (20201222) [1:9]
            END OF BBREF URL (0DET) [9:13]
            TEAM1 (BRK) [13:16]
            TEAM2 (GSW) [16:19]
            STARTTIME (7:00p -> 1140 -> 4 120) [19:21]
            LOCATION (HOME -> 0, @ -> 1, N -> 2) [21]
            SCORE ([TM1,TM2], [120,117]) [22:24]
            IS_OT (0,1,2,etc.) [24]
            IS_PLAYOFFS (0,1) [25]
        """
        _gameheader = [1] + [ord(j) for j in loginfo[6].split('/')[-1][:-5]]
        _gameheader += [ord(j) for j in loginfo[-2]] + [ord(j) for j in loginfo[-1]]
        starttime = loginfo[3]
        if starttime == '':
            _gameheader += [255, 255]
        else:
            st1 = starttime.split(':')
            st2 = 60 * int(st1[0]) + int(st1[1][:-1])
            if st1[1][-1] == 'a':
                pass
            elif st1[1][-1] == 'p':
                st2 += 720
            else:
                st2 += 720
                print('Time\'s weird...')
                print(loginfo)
            _gameheader += [st2 // 255, st2 % 255]
        if loginfo[7] == '':
            _gameheader.append(0)
        elif loginfo[7] == '@':
            _gameheader.append(1)
        elif loginfo[7] == 'N':
            _gameheader.append(2)
        else:
            print('Location\'s weird...')
            print(loginfo)
            _gameheader.append(3)
        for i in loginfo[12:14]:
            try:
                _gameheader.append(int(i))
            except ValueError:
                print('Point total\'s weird...')
                print(loginfo)
                _gameheader.append(255)
        if loginfo[11] == '':
            _gameheader.append(0)
        elif loginfo[11] == 'OT':
            _gameheader.append(1)
        elif len(loginfo[11]) == 3 and loginfo[11][-2:] == 'OT':
            _gameheader.append(int(loginfo[11][0]))
        else:
            print('Issue with number of OTs...')
            print(loginfo)
        _gameheader.append(0)  # QQQQQQQ should be IS_PLAYOFFS
        # gameheader += [255] * (31 - len(gameheader))
        return _gameheader

    def write_game(self):
        gamelist = self.gamelist
        tm2 = self.tm2
        team = self.team
        year = self.year

        for game in gamelist:
            pbppath = self.nspath / 'pbp' / (game.loginfo[6].split('/')[-1][:-8] + '.txt')
            bxscpath = self.nspath / 'boxscores' / (game.loginfo[6].split('/')[-1][:-8] + '.txt')
            if os.path.isfile(pbppath) and os.path.isfile(bxscpath):
                continue
            pnumlist = copy(self.ownpnumlist)
            opppath = PurePath('..', 'core', 'data', game.loginfo[-2], 'season', year)
            # Doesn't work unless opponent is initialized first
            with open(opppath / 'players' / 'playerlist.csv') as csvf:
                csvr = csv.reader(csvf)
                for row in csvr:
                    pnumlist[row[2]] = [128 + int(row[0]), row[1]]
            pnumlist['team1'] = [65, game.loginfo[-1]]
            pnumlist['team2'] = [193, game.loginfo[-2]]
            pnumlist['official'] = [67, 'Official']
            pnumlist['NONE'] = [68, '']

            gameheader = self.getgameheader(game.loginfo)

            '''
            for j in Gamebxsc[tmbx] + [-1] + gamebxsc[opptmbx]:
                if j == -1:
                    bxscf.write(bytes(3))
                    continue
                g2 = [0]
                if len(j) < 15 or j[1] == 'MP' or j[0] == 'Team Totals':
                    continue
                for k in range(len(j)):
                    if k == 0:
                        continue
                    if k == 1:
                        # Add player ID-associated pnumlist byte (e.g. duranke01)
                        k1 = j[k].split('/')[-1][:-5]
                        ''''''k2 = [ord(l) for l in k1]
                        while len(k2) < 9:
                            k2.append(255)
                        g2 += k2''''''
                        g2.append(pnumlist[k1][0])
                    elif k == 2:
                        # MP ([Minutes, Seconds])
                        g2 += [int(i) for i in j[k].split(':')]
                    elif j[k] == '':
                        # 255 for null values
                        g2.append(255)
                    elif k in [5, 8, 11]:
                        # Shooting %ages
                        g2.append(int(254 * float(j[k])))
                    elif k == 21:
                        # +/-
                        g2.append(int(j[k]) + 128)
                    else:
                        g2.append(int(j[k]))
                bxscf.write(bytes(g2))'''
            # bxscf = open(self.nspath / 'boxscores' / (game.loginfo[6].split('/')[-1][:-8] + '.txt'), 'wb')
            if not os.path.isfile(bxscpath):
                tmbx = ''
                gamebxsc = game.bxsc()
                for j in gamebxsc:
                    if tm2 in j and j[len(tm2) + 2] != 'H' and j[len(tm2) + 2] != 'Q':
                        # Full Game (not Half/Quarter)
                        tmbx = j
                tm3 = game.loginfo[8]
                opptmbx = ''
                for j in gamebxsc:
                    if tm3 in j and j[len(tm3) + 2] != 'H' and j[len(tm3) + 2] != 'Q':
                        # Full Game (not Half/Quarter)
                        opptmbx = j
                if tmbx == '' or opptmbx == '':
                    print(game.loginfo)
                    raise ValueError('Team or Other team\'s boxscore not found')
                bxscf = open(bxscpath, 'wb')
                bxscf.write(bytes(gameheader))

                bxscinfo = Game.binbxsc(gamebxsc[tmbx] + [-1] + gamebxsc[opptmbx], pnumlist)
                bxscf.write(bytes(bxscinfo))
                bxscf.close()

            if not os.path.isfile(pbppath):
                pbpf = open(pbppath, 'wb')
                pbpf.write(bytes(gameheader))
                '''p_num = 128  # Used to assign player indices (now only opposing team)
                for j in gamebxsc[opptmbx]:
                    p_num += 1
                    k1 = j[1].split('/')[-1][:-5]
                    if k1 == '' or 'Basic Box' in k1:
                        continue
                    k2 = [ord(l) for l in k1]
                    playhead = [2, p_num] + k2 + [255] * (9 - len(k2))
                    pbpf.write(bytes(playhead))
                    pnumlist[k1] = [p_num, j[0]]'''
                for player in pnumlist:
                    if pnumlist[player][0] >= 128:
                        playhead = [2, pnumlist[player][0]] + [ord(i) for i in player] + [255] * (9 - len(player))
                        pbpf.write(bytes(playhead))

                pbpinfo = binpbp(game.pbp()['Play-By-Play Table'], pnumlist, game.loginfo[-2] == game.loginfo[6][-8:-5])
                pbpf.write(bytes([254]))  # Separate header
                pbpf.write(bytes(pbpinfo))
                pbpf.close()

class Game(object):
    '''def __init__(self, loginfo: List, seasonobj: Season, gamedir: PurePath, yr: str):
        os.makedirs(gamedir, exist_ok=True)
        print([loginfo, seasonobj, yr, str(gamedir)])
        self.yr = yr
        self.loginfo = loginfo
        self.teamobj = seasonobj
        self.gamedir = gamedir
        self.pbp = PBP(self)
        self.bxsc = BoxScore(self)'''

    def __init__(self, loginfo: List, yr: str):
        # os.makedirs(gamedir, exist_ok=True)
        print([loginfo, yr])
        self.yr = yr
        self.loginfo = loginfo
        # self.teamobj = seasonobj
        # self.gamedir = gamedir

    def pbp(self):
        # if os.path.isfile(self.gamedir / 'pbp.txt'):
        #    pass
        print("https://www.basketball-reference.com" + self.loginfo[6])
        s = request.urlopen("https://www.basketball-reference.com/boxscores/pbp/" + self.loginfo[6][11:],
                            context=ctx)
        t = str(s.read())
        return get_table(t, mode='PBP')

    def bxsc(self):
        # if os.path.isfile(self.gamedir / 'boxscore.csv'):
        #    return None
        s = request.urlopen("https://www.basketball-reference.com" + self.loginfo[6], context=ctx)
        t = str(s.read())
        return get_table(t, mode='Link')

    @staticmethod
    def binbxsc(gamebxsc: List, pnumlist: Dict[str, List[Union[int, str]]]):
        fullbytes = []
        for j in gamebxsc:
            if j == -1:
                fullbytes.append(3)
                continue
            g2 = [0]
            if len(j) < 15 or j[1] == 'MP' or j[0] == 'Team Totals':
                continue
            for k in range(len(j)):
                if k == 0:
                    continue
                if k == 1:
                    # Add player ID-associated pnumlist byte (e.g. duranke01)
                    k1 = j[k].split('/')[-1][:-5]
                    '''k2 = [ord(l) for l in k1]
                    while len(k2) < 9:
                        k2.append(255)
                    g2 += k2'''
                    g2.append(pnumlist[k1][0])
                elif k == 2:
                    # MP ([Minutes, Seconds])
                    g2 += [int(i) for i in j[k].split(':')]
                elif j[k] == '':
                    # 255 for null values
                    g2.append(255)
                elif k in [5, 8, 11]:
                    # Shooting %ages
                    g2.append(int(254 * float(j[k])))
                elif k == 21:
                    # +/-
                    g2.append(int(j[k]) + 128)
                else:
                    g2.append(int(j[k]))
            fullbytes += g2
        return fullbytes

    def __str__(self):
        l = self.loginfo
        return l[-1] + (' vs ' if l[7] == '' else ' '+l[7]+' ') + l[-2] + ', ' + l[10] + ' ' + l[12] + '-' + l[13] + (
            ', ' if l[11] == '' else ' (' + l[11] + '), ') + l[1] + ' at ' + l[3] + ', Record: ' + l[14] + '-' + l[
                   15] + ', Streak: ' + l[16]


class BoxScore(object):
    def __init__(self, game: Game):
        self.game = game
        if os.path.isfile(game.gamedir / 'boxscore.csv'):
            pass
        s = request.urlopen("https://www.basketball-reference.com" + self.game.loginfo[6], context=ctx)
        t = str(s.read())
        self.bxsc = get_table(t, mode='Link')


class PBP(object):
    def __init__(self, game: Game):
        self.game = game
        if os.path.isfile(game.gamedir / 'pbp.txt'):
            pass
        print("https://www.basketball-reference.com" + self.game.loginfo[6])
        '''print("https://www.basketball-reference.com/boxscores/" + self.game.loginfo[6][
                                                                  11:] == "https://www.basketball-reference.com" +
              self.game.loginfo[6])'''
        # s = request.urlopen("https://www.basketball-reference.com/boxscores" + self.game.l[15][11:], context=ctx)
        s = request.urlopen("https://www.basketball-reference.com/boxscores/pbp/" + self.game.loginfo[6][11:],
                            context=ctx)
        t = str(s.read())
        self.pbp = get_table(t, mode='PBP')



