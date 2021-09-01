"""
Get information about the end of possessions
"""

from core.pbpdecoder import pbplookup
import numpy as np
from player_rate.idealpm import poss_pct, weibull_by_pts
import matplotlib.pyplot as plt
from scipy.stats import binom, weibull_min
from scipy.special import gamma


def poss_end(play, **kwargs):
    if 1 <= play[0] <= 6:
        # Made shot
        return [(play[0] - 1) % 3 + 1, play[1] < 128], True
    elif 32 <= play[0] <= 63:
        # Turnover
        return [-1, play[1] < 128, play[1]], True
    elif play[0] == 64:
        # DRB
        return [-2, play[1] >= 128], True
    return None, False


def get_play_pcts(team, seasonrange=(2021, 2022)):
    l = pbplookup(gameteam=team, seasonrange=seasonrange, playparser=poss_end)
    # print(l)
    stats = {}
    transition = [np.zeros((10, 10)) for _ in [0, 1]]
    lasts = [0, 0]
    threes_all = [[] for _ in range(10)]
    for i in l:
        deleted = 0
        for j0 in range(len(l[i]) - 1):
            j = j0 - deleted
            if (not l[i][j][1] ^ l[i][j + 1][1]) and (l[i][j][0] > 0 and l[i][j + 1][0] == 1):
                l[i][j][0] += 1
                del l[i][j + 1]
                deleted += 1
        stats[i] = np.zeros(20)
        for i1 in threes_all:
            i1.append(0)
        for j in l[i]:
            stats[i][j[0] + 2 + 10 * j[1]] += 1
            transition[j[1]][lasts[j[1]]][j[0] + 2] += 1
            lasts[j[1]] = j[0] + 2
            if j[1]:
                threes_all[j[0] + 2][-1] += 1

    s = np.sum(np.array([stats[i] for i in l], int), axis=0)
    opp_pct = s[:10] / np.sum(s[:10])
    own_pct = s[10:] / np.sum(s[10:])
    return threes_all, s, opp_pct, own_pct


def plot_outcomes(own_pct):
    for j in range(10):
        print(j)
        plt.plot(np.sort(np.array(threes_all[j])))
        plt.plot(np.array([binom.ppf((i + .5) / 85, 101, own_pct[j]) for i in range(tot_games)]))
        plt.show()


def plot_points(threes_all):
    pts = np.array(threes_all).T @ vals
    plt.plot(np.sort(pts))
    plt.plot(np.sort(poss_pct(own_pct, pace=np.sum(s[10:] / tot_games), num=tot_games * 1000))[500::1000])
    plt.plot([weibull_min.ppf((i + .5) / (tot_games + 1), 14, scale=np.mean(pts) / gamma(15 / 14)) for i in
              range(tot_games)])
    plt.show()


if __name__ == '__main__':
    vals = np.array([0, 0, 0, 1, 2, 3, 4, 5, 6, 7])
    threes_all, s, opp_pct, own_pct = get_play_pcts('UTA')
    tot_games = len(threes_all[0])
    # jazz = poss_pct(own_pct) - poss_pct(opp_pct)
    # plot_outcomes(own_pct)
    # plot_points(threes_all)
    pts = np.array(threes_all).T @ vals
    print(np.std(poss_pct(own_pct, pace=np.sum(s[10:] / tot_games)/2)))
    print(np.std(pts))
    print(np.std(weibull_by_pts(np.mean(pts))))
