from pathlib import PurePath
import os

# On 12-30-2020, seven players scored 20 in the Nets' 145-141 win over the Hawks. Has it happened before?

netspath = PurePath('..', 'core', 'data', 'BRK', 'season', '2020', 'boxscores')
for game in os.listdir(netspath):
    pass