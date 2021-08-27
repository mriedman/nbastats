from pathlib import PurePath
from os import listdir
import csv
from core.pbpdecoder import decode_file
from core.playindexlook import PlayerGameSelect, lookup


pbppath = PurePath('..', 'core', 'data', 'CLE', 'season', '2021', 'pbp')
games = listdir(pbppath)

ishome = {}

with open(pbppath / '..' / 'gs.csv') as f:
    csvr = csv.reader(f)
    for row in csvr:
        ishome[row[6][-17:-8]] = row[6][-8:-5] == row[-1]


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


for filename in games:
    def player_swap(x, pnumlist, **kwargs):
        if x[0] == 0:
            return [((pnumlist[x[1]], x[1] < 128), (pnumlist[x[2]], x[2] < 128)), x[-2] * 255 + x[-1], 0], True
        elif 1 <= x[0] < 7:
            return list(x[-4:]) + [1], True
        return None, False

    def prep_new_quarter(new_q, state):
        if state.players_to_find != 0:
            raise Exception(f'Not all players in Q{new_q - 1} of {filename} found.')
        state.cur_q = new_q
        state.players_to_find = 10
        state.cur_lineup = [{i for i in range(state.cur_q * 10, state.cur_q * 10 + 5)},
                      {i for i in range(state.cur_q * 10 + 5, state.cur_q * 10 + 10)}]
        if state.cur_q in fq_dict:
            cur_q_starters = [[i for i in fq_dict[state.cur_q] if not i[1]], [i for i in fq_dict[state.cur_q] if i[1]]]
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

    if filename[:8] != '20210109':
        continue

    exchanges = decode_file(pbppath, filename, player_swap)

    '''select = PlayerGameSelect((lambda x: x.date() == filename[:8], lambda x: x.is_start))
    line_bytes = lookup(select=select, ndup=False)'''

    select = PlayerGameSelect((lambda x: x.date() == filename[:8],))
    l = lookup(select=select, ndup=False, fq=True)
    fq_dict = {i: [(j[0][1], j[2]) for j in l if j[1] == i] for i in [j[1] for j in l]}

    state = LineupHolder()

    for e in exchanges:
        if e[-1] == 0:
            swap_pair, seconds = e[:-1]

            new_q = get_q_from_secs(seconds)
            # state.cur_seconds = [seconds, new_q]
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
            new_q = get_q_from_secs(255 * e[2] + e[3])
            if new_q != state.cur_q:
                prep_new_quarter(new_q, state)
            state.cur_score = e[:2]

    state.lineup_list[-1].append(get_secs_from_q(state.cur_q + 1) - state.cur_seconds)
    state.lineup_list.append([[], [], state.cur_score, 0])
    state.lineup_list.pop(0)

    for i in state.lineup_list:
        for j in i[:2]:
            for k0, k in enumerate(j):
                if type(k) == int:
                    j[k0] = state.q_starters[k // 10][(k % 10) // 5][k % 5]
        if not ishome[filename[:9]]:
            i[2] = i[2][-1::-1]
        print(i)
    exit(0)
