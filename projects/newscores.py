from urllib import request
from core.brt import get_table
aa=[]
for i in range(130,141):
    i1=[]
    for j in range(130,i):
        print([i,j])
        a=get_table(str(request.urlopen('https://www.basketball-reference.com/play-index/tgl_finder.cgi?request=1&match=game&lg_id=NBA&is_playoffs=N&team_seed_cmp=eq&opp_seed_cmp=eq&year_min=1947&year_max=2019&is_range=N&game_num_type=team&c1stat=pts&c1comp=eq&c1val='+str(i)+'&c2stat=opp_pts&c2comp=eq&c2val='+str(j)+'&order_by=pts',context=ctx).read()))
        if a=={}:
            i1.append(0)
            continue
        else:
            a1=a['Query Results Table']
            a2=-1
            for i2 in a1:
                if a1[0]!='Rk':
                    a2+=1
            i1.append(a2)
    aa.append(i1)
for i in aa:
    for j in i:
        print(j,end=',')
    print()