from core.nbapbp import *
from core.teamcodes import *


for i in nameyears:
    if '2021' in nameyears[i]:
        if i not in ['ATL', 'PHI', 'BRK', 'MIL', 'UTA', 'LAC', 'PHO', 'DEN']:
            continue
        a = Team(i)
        a.newseason('2021', force=True)
        a.seasons['2021'].write_game(force=True)
