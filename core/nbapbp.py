# coding: utf-8
from urllib import request
import ssl
from core.brt import get_table
import csv
import os
from pathlib import PurePath
from typing import List
from core.getpbpdata import *
from copy import copy

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
        print('data/' + self.team + '/season/' + yr)
        nspath = self.dirpath / str(yr)
        if os.path.isfile(nspath / 'gs.csv'):
            pass
        else:
            # Add full-season player data
            plpath = self.dirpath / str(yr) / 'players'
            os.makedirs(plpath)
            g1 = str(
                request.urlopen("https://www.basketball-reference.com/teams/" + self.team + "/" + str(yr) + '.html',
                                context=ctx).read())
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
                "https://www.basketball-reference.com/teams/" + self.team + "/" + str(yr) + "_games.html", context=ctx)
            t = s.read()
            g = str(t)
            tm2 = g.split('-' + yr[2:] + ' ')[1].split(' Sched')[0]  # Full team name (g.g. Brooklyn Nets)
            g = (g.split('<caption>Regular Season Table</caption>')[1]).split('</tbody>')[0]
            gl = g.split('<th scope="row"')
            gamelist1 = []
            bxpath = nspath / 'boxscores'
            os.makedirs(bxpath, exist_ok=True)
            for i0 in gl[1:]:  # QQQQQQQQQQ only first 3 games
                i = i0.split("</tr>")[0]
                i1 = i.split('</td>')
                i2 = [j.replace('</a>', '').split('>')[-1] for j in i1]
                i2.append((i0.split('="box_score_text" ><a href="')[1].split('">')[0]))
                i2.append((i0.split('href="/teams/')[1].split('/')[0]))
                gamelist1.append(Game(i2 + [self.team], self, bxpath / i2[15].split('/')[-1][:-5], yr))
            self.gamelist = gamelist1
            write_game(gamelist1, self, tm2)
            if not os.path.isfile(bxpath / 'gs.csv'):
                with open(bxpath / 'gs.csv', mode='w') as csvf:
                    csvw = csv.writer(csvf)
                    for i in gamelist1:
                        csvw.writerow(i.loginfo)


class Game(object):
    def __init__(self, loginfo: List, seasonobj: Season, gamedir: PurePath, yr: str):
        os.makedirs(gamedir, exist_ok=True)
        print([loginfo, seasonobj, yr, str(gamedir)])
        self.yr = yr
        self.loginfo = loginfo
        self.teamobj = seasonobj
        self.gamedir = gamedir
        self.pbp = PBP(self)
        self.bxsc = BoxScore(self)

    def __str__(self):
        l = self.loginfo
        return l[17] + (' vs ' if l[4] == '' else ' @ ') + l[16] + ', ' + l[6] + ' ' + l[8] + '-' + l[9] + (
            ', ' if l[7] == '' else ' (' + l[7] + '), ') + l[0] + ' at ' + l[1] + ', Record: ' + l[10] + '-' + l[
                   11] + ', Streak: ' + l[12]


class BoxScore(object):
    def __init__(self, game: Game):
        self.game = game
        if os.path.isfile(game.gamedir / 'boxscore.csv'):
            pass
        s = request.urlopen("https://www.basketball-reference.com" + self.game.loginfo[15], context=ctx)
        t = str(s.read())
        self.bxsc = get_table(t, mode='Link')


class PBP(object):
    def __init__(self, game: Game):
        self.game = game
        if os.path.isfile(game.gamedir / 'pbp.txt'):
            pass
        print("https://www.basketball-reference.com" + self.game.loginfo[15])
        print("https://www.basketball-reference.com/boxscores/" + self.game.loginfo[15][
                                                                  11:] == "https://www.basketball-reference.com" +
              self.game.loginfo[15])
        # s = request.urlopen("https://www.basketball-reference.com/boxscores" + self.game.l[15][11:], context=ctx)
        s = request.urlopen("https://www.basketball-reference.com/boxscores/pbp/" + self.game.loginfo[15][11:],
                            context=ctx)
        t = str(s.read())
        self.pbp = get_table(t, mode='PBP')


def write_game(gamelist: List[Game], seasonobj: Season, tm2: str):
    def getgameheader(loginfo: List[str]) -> List[int]:
        '''
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
        '''
        gameheader = [1] + [ord(j) for j in loginfo[15].split('/')[-1][:-5]]
        gameheader += [ord(j) for j in loginfo[-2]] + [ord(j) for j in loginfo[-1]]
        starttime = loginfo[1]
        if starttime == '':
            gameheader += [255, 255]
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
            gameheader += [st2 // 255, st2 % 255]
        if loginfo[4] == '':
            gameheader.append(0)
        elif loginfo[4] == '@':
            gameheader.append(1)
        elif loginfo[4] == 'N':
            gameheader.append(2)
        else:
            print('Location\'s weird...')
            print(loginfo)
            gameheader.append(3)
        for i in loginfo[8:10]:
            try:
                gameheader.append(int(i))
            except ValueError:
                print('Point total\'s weird...')
                print(loginfo)
                gameheader.append(255)
        if loginfo[7] == '':
            gameheader.append(0)
        elif loginfo[7] == 'OT':
            gameheader.append(1)
        elif len(loginfo[7]) == 3 and loginfo[7][-2:] == 'OT':
            gameheader.append(int(loginfo[7][0]))
        else:
            print('Issue with number of OTs...')
            print(loginfo)
        gameheader.append(0)  # QQQQQQQ should be IS_PLAYOFFS
        # gameheader += [255] * (31 - len(gameheader))
        return gameheader

    team = seasonobj.team
    year = seasonobj.year
    filepath = PurePath('..', 'core', 'data', team, 'season', year)
    bxscf = open(filepath / 'boxscores.txt', 'wb')
    os.makedirs(filepath / 'pbp', exist_ok=True)
    os.makedirs(filepath / 'boxscores', exist_ok=True)
    currloc = 0
    ownpnumlist = {}
    with open(filepath / 'players' / 'playerlist.csv') as csvf:
        csvr = csv.reader(csvf)
        for row in csvr:
            ownpnumlist[row[2]] = [int(row[0]), row[1]]
    for game in gamelist:
        pnumlist = copy(ownpnumlist)
        opppath = PurePath('..', 'core', 'data', game.loginfo[-2], 'season', year)
        # Doesn't work unless opponent is initialized first
        '''with open(opppath / 'players' / 'playerlist.csv') as csvf:
            csvr = csv.reader(csvf)
            for row in csvr:
                ownpnumlist[row[2]] = [int(row[0]), row[1]]'''
        pnumlist['team1'] = [65, game.loginfo[-1]]
        pnumlist['team2'] = [66, game.loginfo[-2]]
        pnumlist['official'] = [67, 'Official']
        pnumlist['NONE'] = [68, '']
        print(currloc)
        currloc += 1
        tmbx = ''
        for j in game.bxsc.bxsc:
            if tm2 in j and j[len(tm2) + 2] != 'H' and j[len(tm2) + 2] != 'Q':
                # Full Game (not Half/Quarter)
                tmbx = j
        tm3 = game.loginfo[5]
        opptmbx = ''
        for j in game.bxsc.bxsc:
            if tm3 in j and j[len(tm3) + 2] != 'H' and j[len(tm3) + 2] != 'Q':
                # Full Game (not Half/Quarter)
                opptmbx = j
        if tmbx == '' or opptmbx == '':
            print(game.loginfo)
            raise ValueError('Team or Other team\'s boxscore not found')
        # Add BBRef box score link ending (e.g. 202010230BRK)
        '''gameheader = [1] + [ord(j) for j in game.loginfo[15].split('/')[-1][:-5]]
        gameheader += [255] * (31 - len(gameheader))'''
        gameheader = getgameheader(game.loginfo)
        bxscf = open(filepath / 'boxscores' / (game.loginfo[15].split('/')[-1][:-8] + '.txt'), 'wb')
        bxscf.write(bytes(gameheader))

        pbpf = open(filepath / 'pbp' / (game.loginfo[15].split('/')[-1][:-8] + '.txt'), 'wb')
        pbpf.write(bytes(gameheader))
        p_num = 128  # Used to assign player indices (now only opposing team)
        for j in game.bxsc.bxsc[opptmbx]:
            p_num += 1
            k1 = j[1].split('/')[-1][:-5]
            if k1 == '' or 'Basic Box' in k1:
                continue
            k2 = [ord(l) for l in k1]
            playhead = [2, p_num] + k2 + [255] * (9 - len(k2))
            pbpf.write(bytes(playhead))
            pnumlist[k1] = [p_num, j[0]]

        for j in game.bxsc.bxsc[tmbx] + [-1] + game.bxsc.bxsc[opptmbx]:
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
            bxscf.write(bytes(g2))
        '''tm3 = ''
        for i in game.bxsc.bxsc.keys():
            if tm2 in i or '(' not in i or ' Table' not in i:
                continue
            tm3 = i.split(' (')[0]
            break
        if tm3 == '':
            raise ValueError('Opposing team name not found')'''

        # ^^ All finding other team's boxscore to index their players. This could be a little neater...

        '''pnumlist = {}
        for j in game.bxsc.bxsc[tmbx] + [-1] + game.bxsc.bxsc[opptmbx]:
            if j == -1:
                pbpf.write(bytes(3))
                continue
            k1 = j[1].split('/')[-1][:-5]
            k2 = [ord(l) for l in k1]
            playhead = [2, p_num] + k2 + [255] * (9 - len(k2))
            pbpf.write(bytes(playhead))
            pnumlist[k1] = p_num
            p_num += 1'''
        '''for j in game.bxsc.bxsc[opptmbx]:
            k1 = j[1].split('/')[-1][:-5]
            k2 = [ord(l) for l in k1]
            playhead = [3, p_num] + k2 + [255] * (9 - len(k2))
            pbpf.write(bytes(playhead))
            pnumlist[k1] = p_num
            p_num += 1'''
        # print(game.pbp.pbp)
        pbpinfo = binpbp(game.pbp.pbp['Play-By-Play Table'], pnumlist, game.loginfo[-2] == game.loginfo[-3][-8:-5])
        pbpf.write(bytes([254])) # Separate geader
        pbpf.write(bytes(pbpinfo))
        pbpf.close()
    bxscf.close()
