# coding: utf-8
from urllib import request
import ssl
# from core.brt import get_table
import csv
import os
from pathlib import PurePath
from typing import List, Dict, Union, Tuple
from core.getpbpdata import *
from copy import copy
from core.teamcodes import *
import concurrent.futures

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

    def newseason(self, yr, force=False):
        szn = Season(self, yr, force)
        self.seasons[yr] = szn


class Season(object):
    def __init__(self, team: Team, yr: str, force: bool = False):
        self.teamobj = team
        self.team = nameyears[team.team][yr]
        self.dirpath = team.dirpath
        self.year = yr
        self.gamelist = []
        print('data/' + self.team + '/season/' + yr)
        self.nspath = self.dirpath / str(self.year)
        self.tm2 = abbrtoname[self.team]
        print(self.tm2)
        if os.path.isfile(self.nspath / 'gs.csv') and not force:
            with open(self.nspath / 'gs.csv') as csvf0:
                csvf = csv.reader(csvf0)
                for row in csvf:
                    self.gamelist.append(Game(row, self.year))
        else:
            # Add full-season player data
            plpath = self.dirpath / str(self.year) / 'players'
            if not os.path.isdir(plpath):
                os.makedirs(plpath)
            print(self.team)
            g1 = str(
                request.urlopen(
                    "https://www.basketball-reference.com/teams/" + self.team + "/" + str(self.year) + '.html',
                    context=ctx).read(), encoding='utf-8')
            '''t1 = get_table(g1)
            for i in t1:
                with open(plpath / (i + '.csv'), mode='w') as csvf:
                    csvw = csv.writer(csvf)
                    for j in t1[i]:
                        csvw.writerow(j)'''
            t2 = get_table_by_id(g1, mode='Link')
            with open(plpath / 'playerlist.csv', mode='w') as csvf:
                self.write_playerlist_to_file(csvf, t2)

            # Retrieve game logs
            s = request.urlopen(
                "https://www.basketball-reference.com/teams/" + self.team + "/" + str(self.year) + "_games.html",
                context=ctx)
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
                self.ownpnumlist[row[2], True] = [int(row[0]), row[1]]

    @staticmethod
    def get_id_from_url(url):
        return url.split('/')[-1].split('.html')[0]

    @staticmethod
    def write_playerlist_to_file(csvf, tables):
        csvw = csv.writer(csvf)
        players = []
        count = 0
        for row in tables['per_game']:
            if count == 0:  # Header
                count += 1
                continue
            print(row)
            l = [count, row[1], Season.get_id_from_url(row[2])]
            csvw.writerow(l)
            count += 1
            players.append(row[2])
        if 'playoffs_per_game' in tables:
            for row in tables['playoffs_per_game']:
                if row[2] in players:
                    continue
                if count == 0:  # Header
                    count += 1
                    continue
                print(row)
                l = [count, row[1], Season.get_id_from_url(row[2])]
                csvw.writerow(l)
                count += 1

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
                print('Game has not happened yet:')
                print(loginfo)
                _gameheader.append(255)
                return None
        if loginfo[11] == '':
            _gameheader.append(0)
        elif loginfo[11] == 'OT':
            _gameheader.append(1)
        elif len(loginfo[11]) == 3 and loginfo[11][-2:] == 'OT':
            _gameheader.append(int(loginfo[11][0]))
        else:
            print('Issue with number of OTs...')
            print(loginfo)
        _gameheader.append(int(loginfo[-3]))
        # gameheader += [255] * (31 - len(gameheader))
        return _gameheader

    def write_game(self, boxscore=True, pbp=True, force=False):
        tm2 = self.tm2
        year = self.year

        for game in self.gamelist:
            game.gamefromgameobj(boxscore, pbp, year, self.nspath, copy(self.ownpnumlist), force)

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            # Start the load operations and mark each future with its URL
            future_to_day = {}
            future_to_day.update(
                {executor.submit(game.bxsc): (game, 'bx') for game in self.gamelist if not game.bxbool})
            future_to_day.update(
                {executor.submit(game.pbp): (game, 'pbp') for game in self.gamelist if not game.pbpbool})
            for future in concurrent.futures.as_completed(future_to_day):
                game, t = future_to_day[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('%r and %s generated an exception: %s' % (game, t, exc))
                else:
                    if t == 'bx':
                        self.writebxsc(game)
                    elif t == 'pbp':
                        self.writepbp(game)

    @staticmethod
    def get_bxsc_keys_by_team(gamebxsc, team, ishome):
        tmbx = ''
        full_quarters = []
        for j in gamebxsc:
            # if tm2 in j and j[len(tm2) + 2] != 'H' and j[len(tm2) + 2] != 'Q' and j[len(tm2) + 2] != 'O':
            if j == f'box-{team}-game-basic':
                # Full Game (not Half/Quarter/OT)
                tmbx = j
            # Full Quarters only for own team
            elif team in j and j.split('-')[2][0] == 'q':
                for k in gamebxsc[j]:
                    if len(k) >= 3 and k[2] == '12:00':
                        full_quarters.append(((Season.get_id_from_url(k[1]), ishome), int(j.split('-')[2][-1])))
            elif team in j and j.split('-')[2][0] == 'o':
                for k in gamebxsc[j]:
                    if len(k) >= 3 and k[2] == '5:00':
                        full_quarters.append(((Season.get_id_from_url(k[1]), ishome), int(j.split('-')[2][-1]) + 4))
        return tmbx, full_quarters

    def writebxsc(self, game):
        gamebxsc = get_table_by_id(game.bxsc0, mode='Link')
        tmbx, own_full_quarters = self.get_bxsc_keys_by_team(gamebxsc, self.team, True)
        opptmbx, opp_full_quarters = self.get_bxsc_keys_by_team(gamebxsc, game.loginfo[-2], False)

        full_quarters = own_full_quarters + opp_full_quarters

        if tmbx == '' or opptmbx == '':
            print(game.loginfo)
            raise ValueError('Team or Other team\'s boxscore not found')

        gameheader = Season.getgameheader(game.loginfo)
        if gameheader is None:
            return
        bxscf = open(game.bxscpath, 'wb')
        bxscf.write(bytes(gameheader))

        bxscinfo = Game.binbxsc(gamebxsc[tmbx] + [-1] + gamebxsc[opptmbx], full_quarters, game.pnumlist)
        bxscf.write(bytes(bxscinfo))

        bxscf.close()

    def writepbp(self, game):
        gamepbp = game.pbp2()
        pbpf = open(game.pbppath, 'wb')
        gameheader = Season.getgameheader(game.loginfo)
        pbpf.write(bytes(gameheader))
        for player in game.pnumlist:
            if game.pnumlist[player][0] >= 128:
                playhead = [2, game.pnumlist[player][0]] + [ord(i) for i in player[0]] + [255] * (9 - len(player[0]))
                pbpf.write(bytes(playhead))

        # semaphore.release()
        pbpinfo = binpbp(gamepbp['Play-By-Play Table'], game.pnumlist, game.loginfo[-2] == game.loginfo[6][-8:-5])
        pbpf.write(bytes([254]))  # Separate header
        pbpf.write(bytes(pbpinfo))
        pbpf.close()
        # semaphore.release()


class Game(object):

    def __init__(self, loginfo: List, yr: str):
        print([loginfo, yr])
        self.yr = yr
        self.loginfo = loginfo
        self.pbppath = ''
        self.bxscpath = ''
        self.pnumlist = {}
        self.bxsc0 = None
        self.pbp0 = None

    def pbp(self):
        s = request.urlopen("https://www.basketball-reference.com/boxscores/pbp/" + self.loginfo[6][11:],
                            context=ctx)
        t = str(s.read())
        self.pbp0 = t

    def pbp2(self):
        return get_table(self.pbp0, mode='PBP')

    def bxsc(self):
        s = request.urlopen("https://www.basketball-reference.com" + self.loginfo[6], context=ctx)
        self.bxsc0 = str(s.read())

    def gamefromgameobj(self, boxscore, pbp, year, nspath, pnumlist, force=False):
        self.pbppath = nspath / 'pbp' / (self.loginfo[6].split('/')[-1][:-8] + '.txt')
        self.bxscpath = nspath / 'boxscores' / (self.loginfo[6].split('/')[-1][:-8] + '.txt')
        self.bxbool = (not boxscore) or (os.path.isfile(self.bxscpath) and not force)
        self.pbpbool = (not pbp) or (os.path.isfile(self.pbppath) and not force)
        if self.bxbool and self.pbpbool:
            return
        opppath = PurePath('..', 'core', 'data', abbrtocode[self.loginfo[-2]], 'season', year)
        # Doesn't work unless opponent is initialized first
        with open(opppath / 'players' / 'playerlist.csv') as csvf:
            csvr = csv.reader(csvf)
            for row in csvr:
                pnumlist[row[2], False] = [128 + int(row[0]), row[1]]
        '''pnumlist['team1', True] = [65, self.loginfo[-1]]
        pnumlist['team2', False] = [193, self.loginfo[-2]]
        pnumlist['official', True] = [67, 'Official']
        pnumlist['NONE', True] = [68, '']'''
        pnumlist['team1'] = [65, self.loginfo[-1]]
        pnumlist['team2'] = [193, self.loginfo[-2]]
        pnumlist['official'] = [67, 'Official']
        pnumlist['NONE'] = [68, '']
        self.pnumlist = pnumlist

    @staticmethod
    def binbxsc(gamebxsc: List, full_quarters: List[Tuple], pnumlist: Dict[Tuple[str, bool], List[Union[int, str]]]):
        full_bytes = []
        home = True
        for j in gamebxsc:
            if j == -1:
                full_bytes.append(3)
                home = False
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
                    '''k2 = [ord(line_bytes) for line_bytes in k1]
                    while len(k2) < 9:
                        k2.append(255)
                    g2 += k2'''
                    g2.append(pnumlist[(k1, home)][0])
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
            full_bytes += g2
        full_bytes.append(4)
        for player, quarter in full_quarters:
            full_bytes += [5, pnumlist[player][0], quarter]
        return full_bytes

    def __str__(self):
        l = self.loginfo
        return l[-1] + (' vs ' if l[7] == '' else ' ' + l[7] + ' ') + l[-2] + ', ' + l[10] + ' ' + l[12] + '-' + l[
            13] + (', ' if l[11] == '' else ' (' + l[11] + '), ') + l[1] + ' at ' + l[3] + ', Record: ' + l[14] + '-' \
            + l[15] + ', Streak: ' + l[16]
