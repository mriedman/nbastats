from pathlib import PurePath
from os import listdir
import csv
from collections import defaultdict
from core.pbpdecoder import decode_file
from core.playindexlook import PlayerGameSelect, lookup
from core.teamcodes import *
import numpy as np


class LineupHolder:
    def __init__(self):
        self.cur_lineup = [set(), set()]
        self.cur_score = [0, 0]
        self.q_starters = [[]]
        self.cur_q = 0
        self.players_to_find = 0
        self.lineup_list = [[]]
        self.cur_seconds = 0


def get_q_from_secs(secs):
    if secs <= 7201 * 4:
        return 1 + (secs - 1) // 7201
    return 5 + (secs - 7201 * 4 - 1) // 3001


def get_secs_from_q(q):
    if q <= 4:
        return (q - 1) * 7200
    return 7200 * 4 + (q - 5) * 3000


yr = '2021'
all_lineups = defaultdict(lambda: np.zeros(3))
all_players = set()
select = PlayerGameSelect(())
l = lookup(select=select, ndup=False, fq=True)

fq_dict = defaultdict(list)
for j in l:
    fq_dict[(j[1], j[3], j[5 - j[2]])].append((j[0][1], j[2]))
fq_dict[(4, '20210311', 'CHO')].append(('washipj01', True))
fq_dict[(4, '20210311', 'DET')].append(('washipj01', False))

fq_dict[(3, '20210110', 'CHI')].append(('leonaka01', False))
fq_dict[(3, '20210110', 'CHI')].append(('ibakase01', False))
fq_dict[(3, '20210110', 'LAC')].append(('leonaka01', True))
fq_dict[(3, '20210110', 'LAC')].append(('ibakase01', True))

fq_dict[(4, '20210528', 'DAL')].append(('georgpa01', False))
fq_dict[(4, '20210528', 'DAL')].append(('rondora01', False))
fq_dict[(4, '20210528', 'LAC')].append(('georgpa01', True))
fq_dict[(4, '20210528', 'LAC')].append(('rondora01', True))

fq_dict[(3, '20210411', 'DET')].append(('morrima03', False))
fq_dict[(3, '20210411', 'LAC')].append(('morrima03', True))

fq_dict[(1, '20210108', 'DET')].append(('grantje01', True))
fq_dict[(1, '20210108', 'PHO')].append(('grantje01', False))

fq_dict[(1, '20210108', 'LAC')].append(('curryst01', False))
fq_dict[(1, '20210108', 'GSW')].append(('curryst01', True))

fq_dict[(4, '20210122', 'ORL')].append(('lambje01', False))
fq_dict[(4, '20210122', 'IND')].append(('lambje01', True))

fq_dict[(1, '20210106', 'NOP')].append(('gilgesh01', False))
fq_dict[(1, '20210106', 'NOP')].append(('bazleda01', False))
fq_dict[(1, '20210106', 'OKC')].append(('bazleda01', True))
fq_dict[(1, '20210106', 'OKC')].append(('gilgesh01', True))

for team in nameyears:
    if yr not in nameyears[team]:
        continue

    print(team)

    pbppath = PurePath('..', 'core', 'data', team, 'season', yr, 'pbp')
    games = listdir(pbppath)

    ishome = {}

    with open(pbppath / '..' / 'gs.csv') as f:
        csvr = csv.reader(f)
        for row in csvr:
            ishome[row[6][-17:-8]] = row[6][-8:-5] == row[-1]

    for filename in games:
        def player_swap(x, pnumlist, **kwargs):
            if x[0] == 0:
                return [((pnumlist[x[1]], x[1] < 128), (pnumlist[x[2]], x[2] < 128)), x[-2] * 255 + x[-1], 0], True
            elif 1 <= x[0] < 7:
                return list(x[-4:]) + [1], True
            return None, False

        def prep_new_quarter(new_q, state):
            if state.players_to_find != 0:
                print(state.q_starters[-1])
                print(f'Not all players in Q{new_q - 1} of {filename} in {team}, {yr} found.')
                for i in state.q_starters:
                    for j in i:
                        print(j)
                print(f'fq_dict[({new_q - 1}, \'{filename[:8]}\', \'{team}\')].append((\'\', False))')
                print(f'fq_dict[({new_q - 1}, \'{filename[:8]}\', \'{team}\')].append((\'\', True))')
                print('Hi')
                raise Exception(f'Not all players in Q{new_q - 1} of {filename} in {team}, {yr} found.')
            state.cur_q = new_q
            state.players_to_find = 10
            state.cur_lineup = [{i for i in range(state.cur_q * 10, state.cur_q * 10 + 5)},
                          {i for i in range(state.cur_q * 10 + 5, state.cur_q * 10 + 10)}]
            if (state.cur_q, filename[:8], team) in fq_dict:
                cur_q_starters = [[i for i in fq_dict[(state.cur_q, filename[:8], team)] if not i[1]], [i for i in fq_dict[(state.cur_q, filename[:8], team)] if i[1]]]
            else:
                cur_q_starters = [[], []]
            state.q_starters.append(cur_q_starters)
            for i0, i in enumerate(cur_q_starters):
                for idx, j in enumerate(i):
                    state.cur_lineup[i0].remove(state.cur_q * 10 + i0 * 5 + idx)
                    state.cur_lineup[i0].add(j)
                    state.players_to_find -= 1

            state.lineup_list[-1].append(get_secs_from_q(new_q) - state.cur_seconds)
            state.lineup_list.append([*[list(i) for i in state.cur_lineup], state.cur_score])

            state.cur_seconds = get_secs_from_q(new_q)

        if filename == '.DS_Store':
            continue

        exchanges = decode_file(pbppath, filename, player_swap)

        state = LineupHolder()

        for e in exchanges:
            if e[-1] == 0:
                # Pair is swapped
                swap_pair, seconds = e[:-1]

                new_q = get_q_from_secs(seconds)
                if new_q != state.cur_q:
                    prep_new_quarter(new_q, state)

                i0 = swap_pair[1][1]
                if i0 != swap_pair[0][1]:
                    raise Exception('Weird swap')
                if swap_pair[1] in state.cur_lineup[i0]:
                    state.cur_lineup[i0].remove(swap_pair[1])
                    state.cur_lineup[i0].add(swap_pair[0])
                else:
                    state.cur_lineup[i0].remove(state.cur_q * 10 + i0 * 5 + len(state.q_starters[state.cur_q][i0]))
                    state.q_starters[state.cur_q][i0].append(swap_pair[1])
                    state.players_to_find -= 1
                    state.cur_lineup[i0].add(swap_pair[0])

                state.lineup_list[-1].append(seconds - state.cur_q - state.cur_seconds)
                state.lineup_list.append([*[list(i) for i in state.cur_lineup], state.cur_score])

                state.cur_seconds = seconds - state.cur_q
            elif e[-1] == 1:
                # Someone scored
                new_q = get_q_from_secs(255 * e[2] + e[3])
                if new_q != state.cur_q:
                    prep_new_quarter(new_q, state)
                state.cur_score = e[:2]

        # Add on final score, time
        state.lineup_list[-1].append(get_secs_from_q(state.cur_q + 1) - state.cur_seconds)
        state.lineup_list.append([[], [], state.cur_score, 0])
        state.lineup_list.pop(0)

        for i in state.lineup_list:
            for j in i[:2]:
                for k0, k in enumerate(j):
                    if type(k) == int:
                        # Fill in previously unknown starters
                        try:
                            j[k0] = state.q_starters[k // 10][(k % 10) // 5][k % 5]
                        except IndexError:
                            print(f'Not all players in QLast of {filename} in {team}, {yr} found.')
                            for i1 in state.q_starters:
                                for j1 in i1:
                                    print(j1)
                            print(f'fq_dict[({4}, \'{filename[:8]}\', \'{team}\')].append((\'\', False))')
                            print(f'fq_dict[({4}, \'{filename[:8]}\', \'{team}\')].append((\'\', True))')
                            raise IndexError
            # Flip scores around for away games to match lineup_list order
            if not ishome[filename[:9]]:
                i[2] = i[2][-1::-1]
            # print(i)
        for i0, i in enumerate(state.lineup_list[:-1]):
            for j in i[:2]:
                for k in j:
                    all_players.add(k[0])
            all_lineups[(tuple(j[0] for j in i[0]), tuple(j[0] for j in i[1]))] += \
                [state.lineup_list[i0 + 1][2][0] - i[2][0], state.lineup_list[i0 + 1][2][1] - i[2][1], i[3]]

print(len(all_players))
print(len(all_lineups.keys()))
player_list = list(all_players)
player_list_rev = {player_list[i]: i for i in range(len(player_list))}
lineup_list = list(all_lineups.keys())
lineup_array = np.zeros((len(lineup_list), 2 * len(player_list)))
performance_array = np.zeros((len(lineup_list), 3))
for idx1, lineup in enumerate(lineup_list):
    for idx, team in enumerate(lineup):
        for player in team:
            lineup_array[idx1, player_list_rev[player] + idx * len(player_list)] = 1
    performance_array[idx1] = all_lineups[lineup]

'''poss = performance_array[:, 2]
poss[poss == 0] = 1
performance_array2 = performance_array[:, :2] / poss.reshape((-1, 1))'''

np.savez_compressed('lineups.npz', lineup_array=lineup_array, performance_array=performance_array, player_list = np.array(player_list))
