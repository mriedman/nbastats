import numpy as np
import sqlite3
from core.teamcodes import nameyears
import json
import csv

with np.load('lineups.npz') as data:
    player_list = data['player_list']

con = sqlite3.connect('playerinfo.db')
cur = con.cursor()

cur.execute('DROP TABLE players')
cur.execute('''CREATE TABLE players
               (bbref_id, player_name, player_team, nba_com_id, lineup_table_id)''')


def special_char_replace(s: str):
    return s.replace('č', 'c').replace('ć', 'c').replace('ā', 'a').replace('ž', 'z').replace('š', 's')\
        .replace('Š', 'S').replace('ū', 'u').replace('J.J.', 'JJ')\
        .replace('James Ennis', 'James Ennis III').replace('Juan Hern', 'Juancho Hern').replace('ņ', 'n')\
        .replace('İ', 'I').replace('ó', 'o').replace('Otto Porter', 'Otto Porter Jr.').replace('Knox', 'Knox II')\
        .replace('Marcus Morris', 'Marcus Morris Sr.').replace('Danuel House', 'Danuel House Jr.').replace('ö', 'o')\
        .replace('Lonnie Walker', 'Lonnie Walker IV').replace('Sviatoslav', 'Svi').replace('é', 'e').replace('á', 'a')\
        .replace('ý', 'y').replace('Robert Williams', 'Robert Williams III').replace('Tillman Sr.', 'Tillman')\
        .replace('ģ', 'g')


def tms(tm):
    tm_list = {'BKN': 'BRK', 'CHA': 'CHO', 'PHX': 'PHO'}
    if tm in tm_list:
        return tm_list[tm]
    return tm


players = {}

player_list = list(player_list)

for tm in nameyears:
    if '2021' in nameyears[tm]:
        with open(f'../core/data/{tm}/season/2021/players/playerlist.csv') as f:
            csvf = csv.reader(f)
            for row in csvf:
                if row[1] != '&nbsp;':
                    row1 = special_char_replace(row[1])
                    players[(row1, tm)] = {'player_name': row1, 'player_team': tm, 'bbref_id': row[2],
                                             'lineup_table_id': player_list.index(row[2])}

with open('../nbacom/data/em/10.json') as f:
    cats = json.load(f)

for cat in cats:
    for record in cats[cat]:
        players[(record[0], tms(record[1]))]['nba_com_id'] = record[2]

for player in players:
    if 'nba_com_id' not in players[player]:
        players[player]['nba_com_id'] = -1
    cur.execute("INSERT INTO players VALUES (:bbref_id, :player_name, :player_team, :nba_com_id, :lineup_table_id)",
                players[player])

con.commit()
con.close()
