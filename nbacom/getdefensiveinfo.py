import ssl
import requests
import json
import concurrent.futures
import numpy as np
import time
import os

ssl._create_default_https_context = ssl._create_unverified_context

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0',
           'Accept': 'application/json, text/plain, */*',
           'Accept-Language': 'en-US,en;q=0.5',
           'Accept-Encoding': 'gzip, deflate, br',
           'x-nba-stats-origin': 'stats',
           'x-nba-stats-token': 'true',
           'Origin': 'https://www.nba.com',
           'Connection': 'keep-alive',
           'Referer': 'https://www.nba.com/'}

def get_info(url):
    # time.sleep(random.random()/2)
    if os.path.isfile('./data/defmatchups/%s-10.txt' % (url[0],)):
        print('Exists:', url[0])
        return True, np.loadtxt('./data/defmatchups/%s-10.txt' % (url[0],))
    time.sleep(1)
    print('hi')
    req = requests.get(url[1], headers=headers)
    print(url[0])
    # print(req.text)
    return False, json.loads(req.text)

def get_group(grps, pid):
    # print(pid)
    for i in grps:
        for j in grps[i]:
            if j[2] == pid:
                return int(i)
    return 10

# print(get_info((1,'https://stats.nba.com/stats/leagueseasonmatchups?DefPlayerID=1630193&LeagueID=00&PORound=0&PerMode=Totals&Season=2020-21&SeasonType=Regular Season')))
# exit(0)
def get_np_array(x):
    m, s = x[6].split(':')
    l = [0] * 6 + [60 * int(m) + int(s)] + x[7:]
    return np.array(l)

# Traditional
trd_query_strs = ['College', 'Conference', 'Country', 'DateFrom', 'DateTo', 'Division', 'DraftPick', 'DraftYear', 'GameScope', 'GameSegment', 'Height', 'LastNGames', 'LeagueID', 'Location', 'MeasureType', 'Month', 'OpponentTeamID', 'Outcome', 'PORound', 'PaceAdjust', 'PerMode', 'Period', 'PlayerExperience', 'PlayerPosition', 'PlusMinus', 'Rank', 'Season', 'SeasonSegment', 'SeasonType', 'ShotClockRange', 'StarterBench', 'TeamID', 'TwoWay', 'VsConference', 'VsDivision', 'Weight']

# Playtype
with open('./data/k/1.json') as f:
    grps1 = json.load(f)

player_ids = list(set([i[2] for i in grps1['0'] if not i[2] == 2229])) + [1628455]
# player_ids = ['1629651', '1628386', '203497', '1628971', '201142']
play_type_qs = {'DateFrom': '', 'DateTo': '', 'DefPlayerID': '1629651', 'LeagueID': '00', 'PORound': '0', 'PerMode': 'Totals', 'Season': '2020-21', 'SeasonType': 'Regular Season'}

play_type_ql = {k: {i: j for i, j in play_type_qs.items()} for k in player_ids}
for k in player_ids:
    play_type_ql[k]['DefPlayerID'] = k

urls = [(i, 'https://stats.nba.com/stats/leagueseasonmatchups?%s' % ('&'.join(['%s=%s' % (j, k) for j, k in play_type_ql[i].items()]))) for i in player_ids]
for i in urls:
    print(i)

defs = {}

with open('./data/k/10.json') as f:
    grps = json.load(f)

pdefs = {}

with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    # Start the load operations and mark each future with its URL
    future_to_day = {executor.submit(get_info, url): url for url in urls}
    for future in concurrent.futures.as_completed(future_to_day):
        url = future_to_day[future]
        try:
            exists, data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            '''with open('./data/synergyplaytypes/%s.json' % (url[1].split('?')[1],), 'w') as f:
                f.write(json.dumps(data))'''
            # defs[url[0]] = data
            if not exists:
                head = data['resultSets'][0]['headers']
                body = data['resultSets'][0]['rowSet']
                pn = head.index('OFF_PLAYER_NAME')
                dpn = head.index('DEF_PLAYER_NAME')
                pid = head.index('OFF_PLAYER_ID')
                pp = head.index('PARTIAL_POSS')
                tp = head.index('TEAM_PTS')

                tot = [np.zeros((len(head))) for i in range(11)]

                for i in body:
                    vals = get_np_array(i)
                    tot[get_group(grps, i[pid])] += vals
                tot2 = np.array(tot)

                # pdefs[body[0][dpn]] = tot2
                pdefs[str(url[0])] = tot2
                if len(body) > 0 and len(body[0]) > dpn:
                    print(body[0][dpn])
                else:
                    print('ALERT', url[0])
                np.savetxt('./data/defmatchups/%s-10.txt' % (url[0],), tot2)
            else:
                pdefs[str(url[0])] = data

for player in defs:
    head = defs[player]['resultSets'][0]['headers']
    body = defs[player]['resultSets'][0]['rowSet']
    pn = head.index('OFF_PLAYER_NAME')
    dpn = head.index('DEF_PLAYER_NAME')
    pid = head.index('OFF_PLAYER_ID')
    pp = head.index('PARTIAL_POSS')
    tp = head.index('TEAM_PTS')

    tot = [np.zeros((len(head))) for i in range(11)]

    for i in body:
        vals = get_np_array(i)
        tot[get_group(grps, i[pid])] += vals
    tot2 = np.array(tot)

    # pdefs[body[0][dpn]] = tot2
    pdefs[str(player)] = tot2

    if len(body) > 0 and len(body[0]) > dpn:
        print(body[0][dpn])
    else:
        print('ALERT', url[0])
    # print(list(enumerate([[round(i[0]/sum(tot[:, 0]), 3), round(i[1] / i[0], 3)] for i in tot])))
    # print(tot2[:, pp])

np.savez('./data/defmatchups/10/matchups-10', **pdefs)
