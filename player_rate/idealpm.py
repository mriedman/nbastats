'''
If my plus-minus model's assumptions perfectly captures each player's true skill,
how would it score in whatever metrics I use to measure it? To find out, I'll use
the results of the model to simulate data following its assumptions and evaluate on
that.
'''

# from player_rate.plusminus import *
import numpy as np
from numpy.random import default_rng
from scipy.special import gamma
from core.playtypes import *
import pickle


def poisson_by_f23(ft, two, three, num=10 ** 3):
    return rng.poisson(three, num) * 3 + rng.poisson(two, num) * 2 + rng.poisson(ft, num)


def binomial_by_f23(ft, two, three, pace=101, num=10 ** 3):
    return rng.binomial(pace, three/pace, num) * 3 + rng.binomial(pace, two/pace, num) * 2 + rng.binomial(pace, ft/pace, num)


def weibull_by_pts(pts, gamma_val=14, num=10 ** 3):
    return rng.weibull(gamma_val, num) * pts / gamma(1 + 1 / gamma_val)


def multinomial_by_stuff(ftp, two, three, twpa, thpa, tov, plays=112, num=10 ** 3):
    def f(x):
        return rng.binomial(x[0], ftp) + 2 * rng.binomial(x[1], two/twpa) + \
               3 * rng.binomial(x[2], three/thpa)
    poss_types = rng.multinomial(plays, [(plays - tov - twpa - thpa)/plays, twpa/plays, thpa/plays, tov/plays], num)
    return np.array([f(i) for i in poss_types])


def poss_pct(pcts, pace=101, num=10 ** 3):
    vals = np.array([[0, 0, 0, 1, 2, 3, 4, 5, 6, 7]])
    return np.sum(rng.multinomial(pace, pcts, num) * vals, axis=1)


rng = default_rng()
STDEV_PER_DSEC = 0.0707
STDEV_PER_GAME = 12

if __name__ == '__main__':
    with np.load('lineups2.npz') as data:
        lineup_array = data['lineup_array']
        performance_array = data['performance_array']
    
    reg = pickle.load(open('naive_pm.sav', 'rb'))
    # print(reg.score(lineup_array, performance_array * 7200 * 4))
    # print(lineup_array[:5, -66:])
    print(reg.coef_.shape)
    print(reg.score(lineup_array, performance_array * 7200 * 4))

    pred = reg.predict(lineup_array)
    alt_pred = pred + rng.normal(scale=STDEV_PER_DSEC * 7200 * 4, size=pred.shape)
    print(reg.score(lineup_array, alt_pred))
    print()
    '''print(np.mean(reg.coef_[:, 1080:]))
    print(np.mean(reg.coef_[:, 540]))
    print(np.mean(reg.coef_[:, 540:1080]))'''

    # jazz = poisson_by_f23(17.1, 24.4, 16.7) - poisson_by_f23(14.5, 29.9, 10.8)
    # jazz = binomial_by_f23(17.1, 24.4, 16.7) - binomial_by_f23(14.5, 29.9, 10.8)
    # jazz = weibull_by_pts(116.4) - weibull_by_pts(107.1)
    # jazz = multinomial_by_stuff(.799, 24.4, 16.7, 44.9, 42.8, 14.1)
    '''opp_pct = [0.34626149540183926, 0.1514061042249767, 0.0, 0.03945088631214181, 0.320005331200853, 0.1407437025189924, 0.001999200319872051, 0.0001332800213248034]
    own_pct = [0.38688102893890675, 0.14083601286173633, 0.0, 0.02765273311897106, 0.2829581993569132, 0.16012861736334405, 0.0014147909967845659, 0.00012861736334405144]
    jazz = poss_pct(own_pct) - poss_pct(opp_pct)
    
    print(np.sort(jazz[:72]))
    # print(np.array([int(i) for i in weibull_by_pts(116.4)])[:30])
    print(np.sum(jazz >= 0))
    print(np.sum(jazz < 0))
    print((np.array(opp_pct) - np.array(own_pct)) @ np.array([0, 0, 0, 1, 2, 3, 4, 5]))'''
    """print(len(foultypelist))
    print(len(tonosclist))
    print(len(tosclist))
    print(len(timeoutlist))
    print(len(violationtypelist))"""
