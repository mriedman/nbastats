from core.brt import *
from core.nbapbp import *
#Make GSW Team object
g1=Team('GSW')
'''#Add 2018-19 season (only works once)
g1.newseason('2019')
#Print games
for i in g1.s['2019']:
    print(i)'''
#Get box score for 1st game of season
'''
gbxsc=g1.s['2019'][0].bx.bx
print(gbxsc)
for i in gbxsc:
    if 'Golden State' in i:
        print(i)
        for j in gbxsc[i]:
            if j[0]=='Kevin Durant':
                print(j)
l1=[9,15,16,19,20,21,22,24,25,26,27,28,30,31,32,33,34]'''
'''for j in range(11):
    a=gt(str(request.urlopen('https://www.basketball-reference.com/play-index/psl_finder.cgi?request=1&match=single&per_minute_base=36&type=per_poss&per_poss_base=100&season_start=1&season_end=-1&lg_id=NBA&age_min=0&age_max=99&is_playoffs=N&height_min=0&height_max=99&year_min=2015&birth_country_is=Y&as_comp=gt&as_val=0&pos_is_g=Y&pos_is_gf=Y&pos_is_f=Y&pos_is_fg=Y&pos_is_fc=Y&pos_is_c=Y&pos_is_cf=Y&c1stat=fg3_pct&c1comp=gt&c1val=0&c2stat=fg3a&c2comp=gt&c2val=60&c3stat=fta&c3comp=gt&c3val=60&order_by=ws&order_by_asc=&offset='+str(j)+'00',context=ctx).read()))
    for i in a['Query Results Table'][1:]:
        if i[0]!='Rk':
            s='{'
            for k in l1:
                s+=i[k]+','
            s+=i[6]+'},'
            print(s,end='')'''
'''print()
a0='Rk,Player,Season,Age,Tm,Lg,FT%,3PA,FTA,WS,G,GS,MP,FG,FGA,2P,2PA,3P,3PA,FT,FTA,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,FG%,2P%,3P%,eFG%,TS%'.split(',')
a1='1,DeAndre Jordan\jordade01,2018-19,30,TOT,NBA,.705,0,264,7.1,69,69,2047,5.0,7.8,5.0,7.8,0.0,0.0,3.3,4.6,4.0,11.9,15.9,2.7,0.7,1.3,2.7,2.9,13.3,.641,.641,,.641,.674'.split(',')
for i in [a0,a1]:
    print(i)
    s = '{'
    for k in l1:
        s += i[k] + ','
    s += i[6] + '}'
    print(s)'''
#Get Nets lineups that are actually in the bubble!
lu=[]
for i in range(10):
    a=get_table(request.urlopen("https://www.basketball-reference.com/play-index/lineup_finder.cgi?request=1&match=single&player_id=&lineup_type=5-man&output=total&year_id=2020&is_playoffs=&team_id=NJN&opp_id=&game_num_min=0&game_num_max=99&game_month=&game_location=&game_result=&c1stat=&c1comp=&c1val=&c2stat=&c2comp=&c2val=&c3stat=&c3comp=&c3val=&c4stat=&c4comp=&c4val=&order_by=mp&order_by_asc=&offset=" + str(100 * i), context=ctx).read().decode('utf-8'), mode='LU')
    if not 'Query Results Table' in a:
        break
    for i in a['Query Results Table'][1:]:
        if i[0]!='Rk' and i[0]!='':
            nn=True
            #Nets: ['Wilson Chandler', 'Spencer Dinwiddie', 'DeAndre Jordan', 'Nicolas Claxton','Henry Ellenson','Theo Pinson','David Nwaba','Kyrie Irving','Kevin Durant','Taurean Waller-Prince']
            #Wizards: ['John Wall','Bradley Beal','Dāvis Bertāns','C.J. Miles','Isaiah Thomas','Jordan McRae','Chris Chiozza','Justin Robinson']
            for j in ['Wilson Chandler', 'Spencer Dinwiddie', 'DeAndre Jordan', 'Nicolas Claxton','Henry Ellenson','Theo Pinson','David Nwaba','Kyrie Irving','Kevin Durant','Taurean Waller-Prince']:
                if j in i[1]:
                    nn=False
                    break
            if nn:
                lu.append(i)
print(len(lu))
lu2,lu3=[],[]
for i in lu:
    lu2.append([int(i[0]),i[1],float(i[5])])
    print(lu2[-1])
    lu3+=lu2[-1][1]
print(sum(i[2] for i in lu2))
print(list(set(lu3)))
