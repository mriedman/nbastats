from core.nbapbp import *
from core.teamcodes import *
def maketeam(tm, yrs):
    pass
'''for i in nameyears:
    if '2020' in nameyears[i]:
        a = Team(nameyears[i]['2020'])
        a.newseason('2020')'''
a = Team('BRK')
a.newseason('2020')
a.seasons['2020'].write_game()

